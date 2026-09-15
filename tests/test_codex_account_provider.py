"""Contract tests for the Codex account quota provider."""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from mortal_quota.codex import CodexAccountProvider, CodexAppServerClient, CodexSessionReader


UTC = timezone.utc
NOW = datetime(2026, 9, 14, 12, 0, tzinfo=UTC)


class CodexSessionReaderTest(unittest.TestCase):
    def test_classifies_windows_by_duration_when_primary_and_secondary_are_reversed(self):
        with tempfile.TemporaryDirectory() as directory:
            event = {
                "timestamp": "2026-09-14T11:59:00Z",
                "payload": {
                    "type": "token_count",
                    "rate_limits": {
                        "primary": {"used_percent": 21, "window_minutes": 10080, "resets_at": 1790000000},
                        "secondary": {"used_percent": 7, "window_minutes": 300, "resets_at": 1789500000},
                        "credits": {"balance": "2583.7830695000"},
                        "plan_type": "plus",
                    },
                },
            }
            Path(directory, "rollout.jsonl").write_text(json.dumps(event) + "\n", encoding="utf-8")

            payload = CodexSessionReader(directory).public_payload(NOW)

        self.assertEqual(7, payload["fiveHour"]["usedPercent"])
        self.assertEqual(93, payload["fiveHour"]["remainingPercent"])
        self.assertEqual(21, payload["weekly"]["usedPercent"])
        self.assertEqual("2583.7830695000", payload["credits"]["balance"])
        self.assertIsNone(payload["credits"]["availableResetCount"])
        self.assertEqual(7, payload["usedPercent"])

    def test_keeps_latest_known_plan_when_newest_quota_event_omits_it(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "rollout.jsonl")
            events = [
                {"timestamp": "2026-09-14T11:58:00Z", "payload": {"type": "token_count", "rate_limits": {"primary": {"used_percent": 3, "window_minutes": 300}, "plan_type": "plus"}}},
                {"timestamp": "2026-09-14T11:59:00Z", "payload": {"type": "token_count", "rate_limits": {"primary": {"used_percent": 4, "window_minutes": 300}}}},
            ]
            path.write_text("\n".join(json.dumps(event) for event in events) + "\n", encoding="utf-8")

            payload = CodexSessionReader(directory).public_payload(NOW)

        self.assertEqual(4, payload["usedPercent"])
        self.assertEqual("plus", payload["planType"])


class CodexAppServerClientTest(unittest.TestCase):
    def test_normalizes_rate_limits_and_uses_nearest_available_reset_credit(self):
        raw = {
            "rateLimits": {
                "primary": {"usedPercent": 15, "windowDurationMins": 10080, "resetsAt": 1790000000},
                "secondary": {"usedPercent": 4, "windowDurationMins": 300, "resetsAt": 1789500000},
            },
            "credits": {"balance": "2500.0"},
            "planType": "plus",
            "rateLimitResetCredits": {
                "availableCount": 3,
                "credits": [
                    {"status": "consumed", "expiresAt": 1789000000},
                    {"status": "available", "expiresAt": 1791000000},
                    {"status": "available", "expiresAt": 1790500000},
                ],
            },
        }

        payload = CodexAppServerClient.normalize(raw, NOW)

        self.assertEqual(4, payload["fiveHour"]["usedPercent"])
        self.assertEqual(15, payload["weekly"]["usedPercent"])
        self.assertEqual(3, payload["credits"]["availableResetCount"])
        self.assertEqual(1790500000, payload["credits"]["nearestResetCreditExpiresAt"])
        self.assertNotIn("accountId", json.dumps(payload))


class CodexAccountProviderTest(unittest.TestCase):
    def test_falls_back_to_session_reader_when_app_server_is_unavailable(self):
        fallback = {
            "source": "codex-local-session",
            "status": "fresh",
            "usedPercent": 6,
            "remainingPercent": 94,
            "windowMinutes": 300,
            "resetsAt": 1789500000,
            "creditBalance": "100",
            "fiveHour": {"usedPercent": 6, "remainingPercent": 94, "windowMinutes": 300, "resetsAt": 1789500000},
            "weekly": {"usedPercent": 9, "remainingPercent": 91, "windowMinutes": 10080, "resetsAt": 1790000000},
            "credits": {"balance": "100", "availableResetCount": None, "nearestResetCreditExpiresAt": None},
            "planType": "plus",
            "updatedAt": "2026-09-14T11:59:00Z",
        }

        class BrokenClient:
            def read(self, now=None):
                raise TimeoutError("app-server did not answer")

        class FallbackReader:
            def public_payload(self, now=None):
                return fallback

        provider = CodexAccountProvider(BrokenClient(), FallbackReader())

        self.assertEqual(fallback, provider.public_payload(NOW))

    def test_enriches_missing_plan_type_without_replacing_app_server_quota(self):
        live = {
            "source": "codex-app-server", "status": "fresh", "usedPercent": 4,
            "remainingPercent": 96, "windowMinutes": 300, "resetsAt": 1,
            "creditBalance": "2500", "fiveHour": {"usedPercent": 4}, "weekly": {"usedPercent": 15},
            "credits": {"balance": "2500", "availableResetCount": 3, "nearestResetCreditExpiresAt": 9},
            "planType": None, "updatedAt": "2026-09-14T12:00:00Z",
        }

        class Client:
            def read(self, now=None):
                return dict(live)

        class Sessions:
            def public_payload(self, now=None):
                return {"planType": "plus", "usedPercent": 99}

        payload = CodexAccountProvider(Client(), Sessions()).public_payload(NOW)

        self.assertEqual("plus", payload["planType"])
        self.assertEqual(4, payload["usedPercent"])


if __name__ == "__main__":
    unittest.main()
