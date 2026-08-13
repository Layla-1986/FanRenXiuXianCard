"""Private, localhost-only cache and HTTP API for Antigravity quota data."""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import tempfile
import threading
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence
from urllib.parse import urlparse


SOURCE = "antigravity-ui-automation"
STALE_AFTER = timedelta(minutes=10)
EXPIRED_AFTER = timedelta(hours=24)
# Credits are an account balance, rather than a percentage.  This cap rejects
# obviously corrupt automation values without imposing a percentage limit.
MAX_AI_CREDITS = 1_000_000_000
LOGGER = logging.getLogger(__name__)


def _timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def _remaining(value: object) -> int | None:
    """Accept only a UI-derived percentage; never guess or coerce a value."""
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 100:
        return None
    return value


def _ai_credits(value: object) -> int | None:
    """Accept a reasonable whole-number account credit balance, never a percentage."""
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= MAX_AI_CREDITS:
        return None
    return value


def _quota_values(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    gemini = snapshot.get("gemini")
    claude_gpt = snapshot.get("claudeGpt")
    gemini = gemini if isinstance(gemini, Mapping) else {}
    claude_gpt = claude_gpt if isinstance(claude_gpt, Mapping) else {}
    return {
        "aiCredits": _ai_credits(snapshot.get("aiCredits")),
        "gemini": {
            "weeklyRemaining": _remaining(gemini.get("weeklyRemaining")),
            "fiveHourRemaining": _remaining(gemini.get("fiveHourRemaining")),
        },
        "claudeGpt": {
            "weeklyRemaining": _remaining(claude_gpt.get("weeklyRemaining")),
            "fiveHourRemaining": _remaining(claude_gpt.get("fiveHourRemaining")),
        },
    }


def _has_any_quota_value(snapshot: Mapping[str, Any]) -> bool:
    """Distinguish an unrecognized Models page from a useful partial reading."""
    values = _quota_values(snapshot)
    return any(
        value is not None
        for value in (
            values["aiCredits"],
            values["gemini"]["weeklyRemaining"],
            values["gemini"]["fiveHourRemaining"],
            values["claudeGpt"]["weeklyRemaining"],
            values["claudeGpt"]["fiveHourRemaining"],
        )
    )


class QuotaStore:
    """Stores only the public quota contract, never raw UI Automation text."""

    def __init__(self, cache_path: Path | str):
        self.cache_path = Path(cache_path)
        self._snapshot = self._read_cache()
        self._last_poll_succeeded = False

    def _read_cache(self) -> dict[str, Any]:
        try:
            cached = json.loads(self.cache_path.read_text(encoding="utf-8"))
        except (FileNotFoundError, OSError, json.JSONDecodeError):
            cached = {}
        cached = cached if isinstance(cached, Mapping) else {}
        values = _quota_values(cached)
        return {"source": SOURCE, "syncedAt": _parse_timestamp(cached.get("syncedAt")), **values}

    def _write_cache(self) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        payload = self._public_fields()
        payload["syncedAt"] = _timestamp(payload["syncedAt"]) if payload["syncedAt"] else None
        descriptor, temporary_name = tempfile.mkstemp(
            dir=self.cache_path.parent, prefix=f".{self.cache_path.name}.", suffix=".tmp"
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as temporary:
                json.dump(payload, temporary, ensure_ascii=False, separators=(",", ":"))
            os.replace(temporary_name, self.cache_path)
        finally:
            if os.path.exists(temporary_name):
                os.unlink(temporary_name)

    def _public_fields(self) -> dict[str, Any]:
        return {
            "source": SOURCE,
            "syncedAt": self._snapshot["syncedAt"],
            "aiCredits": self._snapshot["aiCredits"],
            "gemini": dict(self._snapshot["gemini"]),
            "claudeGpt": dict(self._snapshot["claudeGpt"]),
        }

    def record(self, snapshot: Mapping[str, Any] | None, observed_at: datetime) -> None:
        """Record an allowed snapshot; None means the Settings - Models page was absent."""
        if snapshot is None:
            self._last_poll_succeeded = False
            return
        self._snapshot = {
            "source": SOURCE,
            "syncedAt": observed_at.astimezone(timezone.utc),
            **_quota_values(snapshot),
        }
        self._last_poll_succeeded = True
        try:
            self._write_cache()
        except OSError:
            # The in-memory reading remains safe to serve; do not reveal UI data in logs.
            LOGGER.warning("Antigravity quota cache write failed; retaining the in-memory reading")

    def public_payload(self, now: datetime) -> dict[str, Any]:
        synced_at = self._snapshot["syncedAt"]
        if synced_at is None:
            status = "pending"
        else:
            age = now.astimezone(timezone.utc) - synced_at
            if age >= EXPIRED_AFTER:
                status = "expired"
            elif age >= STALE_AFTER:
                status = "stale"
            elif self._last_poll_succeeded:
                status = "fresh"
            else:
                status = "pending"
        payload = self._public_fields()
        payload["syncedAt"] = _timestamp(synced_at) if synced_at else None
        payload["status"] = status
        return {
            "source": payload["source"],
            "syncedAt": payload["syncedAt"],
            "status": payload["status"],
            "aiCredits": payload["aiCredits"],
            "gemini": payload["gemini"],
            "claudeGpt": payload["claudeGpt"],
        }


class UiAutomationCollector:
    """Runs the bounded PowerShell reader against an already-open settings page."""

    def __init__(
        self,
        *,
        script_path: Path | str | None = None,
        runner: Callable[[Sequence[str]], str] | None = None,
    ):
        self.script_path = Path(script_path or Path(__file__).with_name("scripts") / "collect_antigravity_quota.ps1")
        self.runner = runner or self._run_powershell

    def _run_powershell(self, command: Sequence[str]) -> str:
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                check=False,
                text=True,
                timeout=20,
                encoding="utf-8",
            )
        except (OSError, subprocess.SubprocessError):
            return ""
        return completed.stdout if completed.returncode == 0 else ""

    def collect_once(self) -> dict[str, Any] | None:
        """Return a sanitized reading, or None when the requested page is not available."""
        command = (
            "powershell.exe",
            "-NoLogo",
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(self.script_path),
        )
        try:
            output = self.runner(command)
            raw = json.loads(output) if output and output.strip() else None
        except (TypeError, ValueError, json.JSONDecodeError):
            return None
        if not isinstance(raw, Mapping):
            return None
        snapshot = _quota_values(raw)
        return snapshot if _has_any_quota_value(snapshot) else None


class PollingService:
    """Coordinates one read-only UI Automation poll every configured interval."""

    def __init__(
        self,
        store: QuotaStore,
        collector: UiAutomationCollector,
        *,
        interval_seconds: int = 60,
        now: Callable[[], datetime] | None = None,
    ):
        if interval_seconds <= 0:
            raise ValueError("poll interval must be positive")
        self.store = store
        self.collector = collector
        self.interval_seconds = interval_seconds
        self.now = now or (lambda: datetime.now(timezone.utc))

    def poll_once(self) -> None:
        self.store.record(self.collector.collect_once(), self.now())

    def run_forever(self, stop_event: threading.Event) -> None:
        while not stop_event.is_set():
            try:
                self.poll_once()
            except Exception as error:
                # A transient collector/cache failure must not end the daemon thread.
                LOGGER.warning(
                    "Antigravity quota poll failed (%s); the next scheduled poll will continue",
                    type(error).__name__,
                )
            stop_event.wait(self.interval_seconds)


def start_server(
    store: QuotaStore,
    *,
    static_root: Path | str,
    host: str = "127.0.0.1",
    port: int = 8765,
    now: Callable[[], datetime] | None = None,
) -> ThreadingHTTPServer:
    """Create a server that deliberately cannot be exposed beyond loopback."""
    if host != "127.0.0.1":
        raise ValueError("Antigravity quota service must bind to 127.0.0.1 only")
    root = Path(static_root).resolve()
    clock = now or (lambda: datetime.now(timezone.utc))

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, directory=str(root), **kwargs)

        def do_GET(self) -> None:  # noqa: N802 - required HTTP handler name
            if urlparse(self.path).path == "/api/antigravity-quota":
                body = json.dumps(store.public_payload(clock()), ensure_ascii=False).encode("utf-8")
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)
                return
            super().do_GET()

        def log_message(self, format: str, *args: object) -> None:
            return

    return ThreadingHTTPServer((host, port), Handler)


def main(argv: Sequence[str] | None = None) -> int:
    """Start the card's static host and its 60-second, read-only companion poller."""
    project_root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Serve the Antigravity quota card on 127.0.0.1 only; never opens or focuses Antigravity."
    )
    parser.add_argument("--port", type=int, default=8765, help="loopback TCP port (default: 8765)")
    parser.add_argument(
        "--cache",
        type=Path,
        default=project_root / ".antigravity-quota-cache.json",
        help="local whitelist-only cache path",
    )
    parser.add_argument("--static-root", type=Path, default=project_root, help="directory containing the static card")
    args = parser.parse_args(argv)

    store = QuotaStore(args.cache)
    poller = PollingService(store, UiAutomationCollector(), interval_seconds=60)
    stop_event = threading.Event()
    worker = threading.Thread(target=poller.run_forever, args=(stop_event,), daemon=True, name="antigravity-quota-poller")
    server = start_server(store, static_root=args.static_root, host="127.0.0.1", port=args.port)
    worker.start()
    try:
        print(f"Antigravity quota companion: http://127.0.0.1:{server.server_port}/")
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        stop_event.set()
        server.shutdown()
        server.server_close()
        worker.join(timeout=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
