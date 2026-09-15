"""Read-only Codex quota sources and their public data contract."""

from __future__ import annotations

import json
import os
import queue
import shutil
import subprocess
import threading
import time
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping, Sequence


SESSION_TAIL_BYTES = 512 * 1024
SESSION_CANDIDATES = 32
STALE_AFTER = timedelta(minutes=10)
FIVE_HOUR_MINUTES = 300
WEEKLY_MINUTES = 10080


def _timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def _number(value: object, *, minimum: float = 0, maximum: float | None = None) -> int | float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < minimum:
        return None
    if maximum is not None and value > maximum:
        return None
    return value


def _first(mapping: Mapping[str, Any], *names: str) -> Any:
    for name in names:
        if name in mapping:
            return mapping[name]
    return None


def _balance(value: object) -> str | None:
    if value is None:
        return None
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    return str(value) if parsed.is_finite() and parsed >= 0 else None


def _window(value: object) -> dict[str, Any]:
    item = value if isinstance(value, Mapping) else {}
    used = _number(_first(item, "usedPercent", "used_percent"), maximum=100)
    minutes = _number(_first(item, "windowDurationMins", "windowMinutes", "window_minutes"))
    resets = _number(_first(item, "resetsAt", "resets_at"))
    return {
        "usedPercent": used,
        "remainingPercent": 100 - used if used is not None else None,
        "windowMinutes": minutes,
        "resetsAt": resets,
    }


def _classify_windows(limits: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    blank = _window({})
    five_hour = dict(blank)
    weekly = dict(blank)
    candidates: list[Mapping[str, Any]] = []
    for name in ("primary", "secondary"):
        candidate = limits.get(name)
        if isinstance(candidate, Mapping):
            candidates.append(candidate)
    extra = limits.get("windows")
    if isinstance(extra, Sequence) and not isinstance(extra, (str, bytes)):
        candidates.extend(item for item in extra if isinstance(item, Mapping))
    for candidate in candidates:
        normalized = _window(candidate)
        if normalized["windowMinutes"] == FIVE_HOUR_MINUTES:
            five_hour = normalized
        elif normalized["windowMinutes"] == WEEKLY_MINUTES:
            weekly = normalized
    return five_hour, weekly


def _public_payload(
    *, source: str, status: str, limits: Mapping[str, Any], credits: Mapping[str, Any] | None,
    plan_type: object, updated_at: datetime | None, reset_credits: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    five_hour, weekly = _classify_windows(limits)
    credits = credits if isinstance(credits, Mapping) else {}
    reset_credits = reset_credits if isinstance(reset_credits, Mapping) else {}
    raw_details = _first(reset_credits, "credits", "details")
    details = raw_details if isinstance(raw_details, Sequence) and not isinstance(raw_details, (str, bytes)) else []
    expiries = [
        _number(_first(item, "expiresAt", "expires_at"))
        for item in details
        if isinstance(item, Mapping) and item.get("status") == "available"
    ]
    expiries = [value for value in expiries if value is not None]
    available_count = _number(_first(reset_credits, "availableCount", "available_count"))
    balance = _balance(credits.get("balance"))
    return {
        "source": source,
        "status": status,
        # Compatibility fields used by the browser prototype.
        "usedPercent": five_hour["usedPercent"],
        "remainingPercent": five_hour["remainingPercent"],
        "windowMinutes": five_hour["windowMinutes"],
        "resetsAt": five_hour["resetsAt"],
        "creditBalance": balance,
        "fiveHour": five_hour,
        "weekly": weekly,
        "credits": {
            "balance": balance,
            "availableResetCount": available_count,
            "nearestResetCreditExpiresAt": min(expiries) if expiries else None,
        },
        "planType": plan_type if isinstance(plan_type, str) else None,
        "updatedAt": _timestamp(updated_at) if updated_at else None,
    }


class CodexSessionReader:
    """Read the newest public rate-limit event from local Codex sessions."""

    def __init__(self, sessions_root: Path | str) -> None:
        self.sessions_root = Path(sessions_root)

    @staticmethod
    def _tail_lines(path: Path) -> list[str]:
        try:
            with path.open("rb") as stream:
                stream.seek(0, os.SEEK_END)
                size = stream.tell()
                stream.seek(max(0, size - SESSION_TAIL_BYTES))
                data = stream.read()
        except OSError:
            return []
        if size > SESSION_TAIL_BYTES:
            data = data.split(b"\n", 1)[-1]
        return data.decode("utf-8", errors="ignore").splitlines()

    @staticmethod
    def _event_payload(line: str) -> tuple[datetime, Mapping[str, Any]] | None:
        try:
            event = json.loads(line)
        except (TypeError, json.JSONDecodeError):
            return None
        payload = event.get("payload") if isinstance(event, Mapping) else None
        limits = payload.get("rate_limits") if isinstance(payload, Mapping) and payload.get("type") == "token_count" else None
        timestamp = _parse_timestamp(event.get("timestamp")) if isinstance(event, Mapping) else None
        if timestamp is None or not isinstance(limits, Mapping):
            return None
        five_hour, weekly = _classify_windows(limits)
        if five_hour["usedPercent"] is None and weekly["usedPercent"] is None:
            return None
        return timestamp, limits

    def public_payload(self, now: datetime | None = None) -> dict[str, Any]:
        clock = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        newest: tuple[datetime, Mapping[str, Any]] | None = None
        newest_credits: tuple[datetime, Mapping[str, Any]] | None = None
        newest_plan: tuple[datetime, str] | None = None
        try:
            files = sorted(self.sessions_root.rglob("*.jsonl"), key=lambda path: path.stat().st_mtime, reverse=True)[:SESSION_CANDIDATES]
        except OSError:
            files = []
        for path in files:
            for line in reversed(self._tail_lines(path)):
                candidate = self._event_payload(line)
                if candidate is not None:
                    if newest is None or candidate[0] > newest[0]:
                        newest = candidate
                    timestamp, limits = candidate
                    credits = limits.get("credits")
                    if isinstance(credits, Mapping) and _balance(credits.get("balance")) is not None:
                        if newest_credits is None or timestamp > newest_credits[0]:
                            newest_credits = (timestamp, credits)
                    plan_type = limits.get("plan_type")
                    if isinstance(plan_type, str) and (newest_plan is None or timestamp > newest_plan[0]):
                        newest_plan = (timestamp, plan_type)
        if newest is None:
            return _public_payload(source="codex-local-session", status="unavailable", limits={}, credits={}, plan_type=None, updated_at=None)
        observed_at, raw_limits = newest
        limits = dict(raw_limits)
        if not isinstance(limits.get("credits"), Mapping) and newest_credits is not None:
            limits["credits"] = newest_credits[1]
        if not isinstance(limits.get("plan_type"), str) and newest_plan is not None:
            limits["plan_type"] = newest_plan[1]
        return _public_payload(
            source="codex-local-session",
            status="stale" if clock - observed_at >= STALE_AFTER else "fresh",
            limits=limits,
            credits=limits.get("credits") if isinstance(limits.get("credits"), Mapping) else {},
            plan_type=limits.get("plan_type"),
            updated_at=observed_at,
        )


class CodexAppServerClient:
    """Make one bounded, read-only account/rateLimits/read request."""

    def __init__(self, executable: str | None = None, *, timeout_seconds: float = 8.0) -> None:
        self.executable = executable or shutil.which("codex") or "codex"
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def normalize(raw: Mapping[str, Any], now: datetime | None = None) -> dict[str, Any]:
        clock = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        result = raw.get("result") if isinstance(raw.get("result"), Mapping) else raw
        limits = result.get("rateLimits") if isinstance(result.get("rateLimits"), Mapping) else result
        credits = result.get("credits") if isinstance(result.get("credits"), Mapping) else limits.get("credits", {})
        reset_credits = result.get("rateLimitResetCredits")
        return _public_payload(
            source="codex-app-server", status="fresh", limits=limits, credits=credits,
            plan_type=_first(result, "planType", "plan_type"), updated_at=clock,
            reset_credits=reset_credits if isinstance(reset_credits, Mapping) else {},
        )

    def read(self, now: datetime | None = None) -> dict[str, Any]:
        process = subprocess.Popen(
            [self.executable, "app-server"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, encoding="utf-8", bufsize=1,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        output: queue.Queue[str | None] = queue.Queue()

        def pump() -> None:
            assert process.stdout is not None
            for line in process.stdout:
                output.put(line)
            output.put(None)

        threading.Thread(target=pump, daemon=True).start()
        deadline = time.monotonic() + self.timeout_seconds
        try:
            assert process.stdin is not None
            messages = (
                {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"clientInfo": {"name": "mortal-quota-card", "version": "1.0.0"}, "capabilities": {}}},
                {"jsonrpc": "2.0", "method": "initialized", "params": {}},
                {"jsonrpc": "2.0", "id": 2, "method": "account/rateLimits/read", "params": {"excludeResetCreditDetails": False}},
            )
            for message in messages:
                process.stdin.write(json.dumps(message, separators=(",", ":")) + "\n")
            process.stdin.flush()
            while time.monotonic() < deadline:
                try:
                    line = output.get(timeout=max(0.01, deadline - time.monotonic()))
                except queue.Empty as error:
                    raise TimeoutError("Codex app-server did not answer") from error
                if line is None:
                    break
                try:
                    message = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(message, Mapping) and message.get("id") == 2:
                    if "error" in message:
                        raise RuntimeError("Codex account quota is unavailable")
                    return self.normalize(message, now)
            raise TimeoutError("Codex app-server did not answer")
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    process.kill()


class CodexAccountProvider:
    """Prefer app-server and use the session snapshot when it cannot authenticate."""

    def __init__(self, app_server: CodexAppServerClient, fallback: CodexSessionReader, *, refresh_seconds: int = 60) -> None:
        self.app_server = app_server
        self.fallback = fallback
        self.refresh_seconds = refresh_seconds
        self._cached: dict[str, Any] | None = None
        self._cached_at = 0.0
        self._lock = threading.Lock()

    def public_payload(self, now: datetime | None = None) -> dict[str, Any]:
        with self._lock:
            current = time.monotonic()
            if self._cached is not None and current - self._cached_at < self.refresh_seconds:
                return dict(self._cached)
            try:
                payload = self.app_server.read(now)
                if payload.get("planType") is None:
                    fallback = self.fallback.public_payload(now)
                    if isinstance(fallback.get("planType"), str):
                        payload["planType"] = fallback["planType"]
            except (OSError, RuntimeError, TimeoutError, subprocess.SubprocessError):
                payload = self.fallback.public_payload(now)
            self._cached = payload
            self._cached_at = current
            return dict(payload)
