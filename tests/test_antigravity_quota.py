"""Contract tests for the localhost-only Antigravity quota companion."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import threading
import unittest
from datetime import datetime, timedelta, timezone
from http.client import HTTPConnection
from pathlib import Path

from antigravity_quota import PollingService, QuotaStore, UiAutomationCollector, start_server


UTC = timezone.utc
BASE_TIME = datetime(2026, 8, 13, 8, 0, tzinfo=UTC)


def sample_snapshot(**changes):
    data = {
        "aiCredits": 50,
        "gemini": {"weeklyRemaining": 75, "fiveHourRemaining": 25},
        "claudeGpt": {"weeklyRemaining": 100, "fiveHourRemaining": 0},
    }
    data.update(changes)
    return data


class QuotaStoreTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cache_path = Path(self.temp_dir.name) / "antigravity-cache.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_accepts_zero_and_one_hundred_as_real_remaining_values(self):
        store = QuotaStore(self.cache_path)

        store.record(sample_snapshot(aiCredits=0), BASE_TIME)

        payload = store.public_payload(BASE_TIME)
        self.assertEqual(0, payload["aiCredits"])
        self.assertEqual(100, payload["claudeGpt"]["weeklyRemaining"])
        self.assertEqual(0, payload["claudeGpt"]["fiveHourRemaining"])
        self.assertEqual("fresh", payload["status"])

    def test_accepts_nonnegative_credit_balance_above_one_hundred(self):
        """Changing credits back to percentage validation would discard a real balance."""
        store = QuotaStore(self.cache_path)

        store.record(sample_snapshot(aiCredits=1250), BASE_TIME)

        self.assertEqual(1250, store.public_payload(BASE_TIME)["aiCredits"])

    def test_rejects_non_integer_or_negative_credit_balance(self):
        """Changing credit validation to coerce values would misreport unsupported UI data."""
        store = QuotaStore(self.cache_path)

        store.record(sample_snapshot(aiCredits=12.5), BASE_TIME)
        self.assertIsNone(store.public_payload(BASE_TIME)["aiCredits"])
        store.record(sample_snapshot(aiCredits=-1), BASE_TIME)

        self.assertIsNone(store.public_payload(BASE_TIME)["aiCredits"])

    def test_replaces_missing_and_invalid_values_with_null_without_coercion(self):
        store = QuotaStore(self.cache_path)
        malformed = sample_snapshot(
            aiCredits="unknown",
            gemini={"weeklyRemaining": None, "fiveHourRemaining": "25%"},
            claudeGpt={"weeklyRemaining": -1, "fiveHourRemaining": 101},
        )

        store.record(malformed, BASE_TIME)

        payload = store.public_payload(BASE_TIME)
        self.assertIsNone(payload["aiCredits"])
        self.assertIsNone(payload["gemini"]["weeklyRemaining"])
        self.assertIsNone(payload["gemini"]["fiveHourRemaining"])
        self.assertIsNone(payload["claudeGpt"]["weeklyRemaining"])
        self.assertIsNone(payload["claudeGpt"]["fiveHourRemaining"])

    def test_missing_page_keeps_cached_values_and_becomes_pending(self):
        store = QuotaStore(self.cache_path)
        store.record(sample_snapshot(aiCredits=42), BASE_TIME)

        store.record(None, BASE_TIME + timedelta(seconds=60))

        payload = store.public_payload(BASE_TIME + timedelta(seconds=60))
        self.assertEqual(42, payload["aiCredits"])
        self.assertEqual("pending", payload["status"])
        self.assertEqual("2026-08-13T08:00:00Z", payload["syncedAt"])

    def test_status_decays_to_stale_then_expired_from_last_successful_sync(self):
        store = QuotaStore(self.cache_path)
        store.record(sample_snapshot(), BASE_TIME)
        store.record(None, BASE_TIME + timedelta(minutes=1))

        self.assertEqual("stale", store.public_payload(BASE_TIME + timedelta(minutes=10))["status"])
        self.assertEqual("expired", store.public_payload(BASE_TIME + timedelta(hours=24))["status"])

    def test_cache_survives_restart_without_sensitive_or_unapproved_fields(self):
        store = QuotaStore(self.cache_path)
        store.record(
            sample_snapshot(token="secret", email="person@example.com", fullWindowText="do not keep"),
            BASE_TIME,
        )

        cache = json.loads(self.cache_path.read_text(encoding="utf-8"))
        self.assertNotIn("token", json.dumps(cache))
        self.assertNotIn("email", json.dumps(cache))
        self.assertNotIn("fullWindowText", json.dumps(cache))
        restarted = QuotaStore(self.cache_path)
        payload = restarted.public_payload(BASE_TIME)
        self.assertEqual(50, payload["aiCredits"])
        self.assertEqual(
            {"source", "syncedAt", "status", "aiCredits", "gemini", "claudeGpt"},
            set(payload),
        )


class LocalApiTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.store = QuotaStore(Path(self.temp_dir.name) / "cache.json")
        self.store.record(sample_snapshot(aiCredits=17), BASE_TIME)
        self.server = start_server(
            self.store,
            static_root=Path(__file__).resolve().parents[1],
            port=0,
            now=lambda: BASE_TIME,
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.temp_dir.cleanup()

    def test_api_is_loopback_only_and_returns_only_the_public_contract(self):
        host, port = self.server.server_address
        self.assertEqual("127.0.0.1", host)
        connection = HTTPConnection(host, port, timeout=2)
        connection.request("GET", "/api/antigravity-quota")
        response = connection.getresponse()
        payload = json.loads(response.read())

        self.assertEqual(200, response.status)
        self.assertEqual(17, payload["aiCredits"])
        self.assertEqual(
            {"source", "syncedAt", "status", "aiCredits", "gemini", "claudeGpt"},
            set(payload),
        )
        self.assertNotIn("token", json.dumps(payload))

    def test_rejects_non_loopback_bind_requests(self):
        with self.assertRaises(ValueError):
            start_server(self.store, static_root=Path.cwd(), host="0.0.0.0", port=0)


class CollectorTest(unittest.TestCase):
    def test_collector_emits_only_allowed_fields_from_automation_output(self):
        commands = []

        def runner(command):
            commands.append(command)
            return json.dumps(
                sample_snapshot(aiCredits=0, token="must-not-leave-powershell", windowText="must-not-leave-powershell")
            )

        collector = UiAutomationCollector(runner=runner)

        snapshot = collector.collect_once()

        self.assertEqual(0, snapshot["aiCredits"])
        self.assertEqual(100, snapshot["claudeGpt"]["weeklyRemaining"])
        self.assertNotIn("token", json.dumps(snapshot))
        self.assertNotIn("windowText", json.dumps(snapshot))
        self.assertEqual("powershell.exe", Path(commands[0][0]).name.lower())
        self.assertIn("collect_antigravity_quota.ps1", commands[0][-1])

    def test_collector_treats_empty_or_invalid_automation_output_as_absent_page(self):
        self.assertIsNone(UiAutomationCollector(runner=lambda _: "").collect_once())
        self.assertIsNone(UiAutomationCollector(runner=lambda _: "not-json").collect_once())

    def test_all_null_collector_shape_is_absent_and_preserves_prior_fresh_snapshot(self):
        """Removing all-null rejection would replace a real cached reading with page-miss nulls."""
        empty_reading = {
            "aiCredits": None,
            "gemini": {"weeklyRemaining": None, "fiveHourRemaining": None},
            "claudeGpt": {"weeklyRemaining": None, "fiveHourRemaining": None},
        }
        collector = UiAutomationCollector(runner=lambda _: json.dumps(empty_reading))

        self.assertIsNone(collector.collect_once())

        with tempfile.TemporaryDirectory() as directory:
            store = QuotaStore(Path(directory) / "cache.json")
            store.record(sample_snapshot(aiCredits=250), BASE_TIME)
            PollingService(store, collector, interval_seconds=60, now=lambda: BASE_TIME + timedelta(minutes=1)).poll_once()

            payload = store.public_payload(BASE_TIME + timedelta(minutes=1))
            self.assertEqual(250, payload["aiCredits"])
            self.assertEqual("pending", payload["status"])

    def test_collector_keeps_partial_reading_when_one_value_is_valid(self):
        """Treating every incomplete collector response as absent would discard useful partial data."""
        partial_reading = {
            "aiCredits": None,
            "gemini": {"weeklyRemaining": 75, "fiveHourRemaining": None},
            "claudeGpt": {"weeklyRemaining": None, "fiveHourRemaining": None},
        }

        snapshot = UiAutomationCollector(runner=lambda _: json.dumps(partial_reading)).collect_once()

        self.assertEqual(75, snapshot["gemini"]["weeklyRemaining"])

    def test_polling_service_records_a_success_then_retains_cache_on_absence(self):
        with tempfile.TemporaryDirectory() as directory:
            store = QuotaStore(Path(directory) / "cache.json")
            responses = iter([json.dumps(sample_snapshot(aiCredits=33)), ""])
            collector = UiAutomationCollector(runner=lambda _: next(responses))
            service = PollingService(store, collector, interval_seconds=60, now=lambda: BASE_TIME)

            service.poll_once()
            self.assertEqual("fresh", store.public_payload(BASE_TIME)["status"])
            service.poll_once()
            payload = store.public_payload(BASE_TIME)
            self.assertEqual("pending", payload["status"])
            self.assertEqual(33, payload["aiCredits"])

    def test_cache_write_failure_keeps_fresh_snapshot_in_memory(self):
        """Removing nonfatal persistence handling would raise and hide the current reading."""
        with tempfile.TemporaryDirectory() as directory:
            cache_parent = Path(directory) / "not-a-directory"
            cache_parent.write_text("occupied", encoding="utf-8")
            store = QuotaStore(cache_parent / "cache.json")

            store.record(sample_snapshot(aiCredits=250), BASE_TIME)

            payload = store.public_payload(BASE_TIME)
            self.assertEqual(250, payload["aiCredits"])
            self.assertEqual("fresh", payload["status"])

    def test_run_forever_continues_after_one_collection_exception(self):
        """Removing the per-poll exception boundary would stop before the next good reading."""
        class StopAfterTwoWaits:
            def __init__(self):
                self.waits = 0

            def is_set(self):
                return self.waits >= 2

            def wait(self, _timeout):
                self.waits += 1
                return self.is_set()

        with tempfile.TemporaryDirectory() as directory:
            attempts = 0

            def runner(_command):
                nonlocal attempts
                attempts += 1
                if attempts == 1:
                    raise RuntimeError("temporary UIA failure")
                return json.dumps(sample_snapshot(aiCredits=250))

            store = QuotaStore(Path(directory) / "cache.json")
            service = PollingService(
                store,
                UiAutomationCollector(runner=runner),
                interval_seconds=60,
                now=lambda: BASE_TIME,
            )

            service.run_forever(StopAfterTwoWaits())

            self.assertEqual(2, attempts)
            self.assertEqual(250, store.public_payload(BASE_TIME)["aiCredits"])


class CommandLineTest(unittest.TestCase):
    def test_help_exposes_a_localhost_companion_service_command(self):
        completed = subprocess.run(
            [sys.executable, "antigravity_quota.py", "--help"],
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, completed.returncode)
        self.assertIn("127.0.0.1", completed.stdout)
        self.assertIn("--port", completed.stdout)


if __name__ == "__main__":
    unittest.main()
