"""Desktop state, bridge, and bounded Win32 window behavior."""

from __future__ import annotations

import ctypes
import json
import os
import sys
import tempfile
import threading
import time
from pathlib import Path
from ctypes import wintypes
from typing import Any, Callable, Iterable


APP_NAME = "MortalQuotaCard"
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
WINDOW_WIDTH = 480
WINDOW_HEIGHT = 270


def window_visual_options() -> dict[str, Any]:
    """Give DWM an opaque surface to anti-alias at the window edge."""
    return {"background_color": "#07130f", "transparent": False, "shadow": False}


class AppSettings:
    """Store only the user's page, position, and autostart preference."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.state = {"locked": False, "page": "codex", "autostart": False, "x": None, "y": None}
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError, OSError, json.JSONDecodeError):
            raw = {}
        if isinstance(raw, dict):
            self.state["page"] = raw.get("page") if raw.get("page") in {"codex", "antigravity"} else "codex"
            self.state["autostart"] = raw.get("autostart") is True
            self.state["x"] = raw.get("x") if isinstance(raw.get("x"), int) and not isinstance(raw.get("x"), bool) else None
            self.state["y"] = raw.get("y") if isinstance(raw.get("y"), int) and not isinstance(raw.get("y"), bool) else None

    def update(self, **changes: Any) -> None:
        if "page" in changes and changes["page"] in {"codex", "antigravity"}:
            self.state["page"] = changes["page"]
        for key in ("x", "y"):
            if key in changes and isinstance(changes[key], int) and not isinstance(changes[key], bool):
                self.state[key] = changes[key]
        for key in ("autostart", "locked"):
            if key in changes:
                self.state[key] = bool(changes[key])
        self._save()

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        public = {key: self.state[key] for key in ("page", "autostart", "x", "y")}
        descriptor, temporary = tempfile.mkstemp(dir=self.path.parent, prefix=".settings-", suffix=".tmp")
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                json.dump(public, stream, ensure_ascii=False, separators=(",", ":"))
            os.replace(temporary, self.path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)


def clamp_position(
    x: int | None, y: int | None, width: int, height: int,
    work_areas: Iterable[tuple[int, int, int, int]],
) -> tuple[int, int]:
    areas = list(work_areas) or [(0, 0, 1920, 1080)]
    if isinstance(x, int) and isinstance(y, int):
        for left, top, right, bottom in areas:
            if left <= x <= right - width and top <= y <= bottom - height:
                return x, y
    left, top, right, bottom = areas[0]
    return left + max(0, (right - left - width) // 2), top + max(0, (bottom - top - height) // 2)


def app_data_dir() -> Path:
    return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / APP_NAME


def executable_command() -> str:
    executable = Path(sys.executable).resolve()
    if getattr(sys, "frozen", False):
        return f'"{executable}" --autostart'
    entry = Path(__file__).resolve().parents[1] / "quota_card_app.py"
    return f'"{executable}" "{entry}" --autostart'


def is_autostart_enabled() -> bool:
    if os.name != "nt":
        return False
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            value, _ = winreg.QueryValueEx(key, APP_NAME)
        return bool(value)
    except OSError:
        return False


def set_autostart(enabled: bool) -> None:
    if os.name != "nt":
        return
    import winreg
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
        if enabled:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, executable_command())
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass


class NativeWindowController:
    """Apply click-through styles while retaining the original native style."""

    GWL_EXSTYLE = -20
    WS_EX_TRANSPARENT = 0x20
    WS_EX_TOOLWINDOW = 0x80
    WS_EX_APPWINDOW = 0x40000
    WS_EX_NOACTIVATE = 0x08000000
    WM_NCLBUTTONDOWN = 0x00A1
    HTCAPTION = 2
    HWND_TOPMOST = -1
    SWP_NOSIZE = 0x0001
    SWP_NOMOVE = 0x0002
    SWP_NOZORDER = 0x0004
    SWP_NOACTIVATE = 0x0010

    def __init__(self, window: Any) -> None:
        self.window = window
        self.hwnd: int | None = None
        self.base_style: int | None = None
        self.locked = False
        self._lock = threading.Lock()

    def attach(self) -> int:
        native = getattr(self.window, "native", None)
        handle = getattr(native, "Handle", native)
        self.hwnd = int(handle.ToInt32() if hasattr(handle, "ToInt32") else handle)
        user32 = ctypes.windll.user32
        getter = getattr(user32, "GetWindowLongPtrW", user32.GetWindowLongW)
        setter = getattr(user32, "SetWindowLongPtrW", user32.SetWindowLongW)
        style = int(getter(self.hwnd, self.GWL_EXSTYLE))
        style = (style | self.WS_EX_TOOLWINDOW) & ~self.WS_EX_APPWINDOW
        setter(self.hwnd, self.GWL_EXSTYLE, style)
        self.base_style = style
        self._fit_client_size(WINDOW_WIDTH, WINDOW_HEIGHT)
        user32.SetWindowPos(self.hwnd, self.HWND_TOPMOST, 0, 0, 0, 0, self.SWP_NOMOVE | self.SWP_NOSIZE | self.SWP_NOACTIVATE)
        self._round_corners()
        return self.hwnd

    def _fit_client_size(self, width: int, height: int) -> None:
        """Correct pywebview's frameless outer-size subtraction on Windows."""
        if not self.hwnd:
            return
        user32 = ctypes.windll.user32
        window_rect = wintypes.RECT()
        client_rect = wintypes.RECT()
        if not user32.GetWindowRect(self.hwnd, ctypes.byref(window_rect)):
            return
        if not user32.GetClientRect(self.hwnd, ctypes.byref(client_rect)):
            return
        window_width = window_rect.right - window_rect.left
        window_height = window_rect.bottom - window_rect.top
        client_width = client_rect.right - client_rect.left
        client_height = client_rect.bottom - client_rect.top
        dpi_reader = getattr(user32, "GetDpiForWindow", None)
        dpi = int(dpi_reader(self.hwnd)) if dpi_reader else 96
        scale = dpi / 96 if dpi > 0 else 1
        target_client_width = round(width * scale)
        target_client_height = round(height * scale)
        target_width = window_width + target_client_width - client_width
        target_height = window_height + target_client_height - client_height
        if target_width == window_width and target_height == window_height:
            return
        user32.SetWindowPos(
            self.hwnd, 0, 0, 0, target_width, target_height,
            self.SWP_NOMOVE | self.SWP_NOZORDER | self.SWP_NOACTIVATE,
        )

    def _round_corners(self) -> None:
        if not self.hwnd:
            return
        user32 = ctypes.windll.user32
        try:
            # A window region is binary and leaves jagged edges at high DPI.
            user32.SetWindowRgn(self.hwnd, None, True)
            preference = ctypes.c_int(2)
            result = ctypes.windll.dwmapi.DwmSetWindowAttribute(
                self.hwnd, 33, ctypes.byref(preference), ctypes.sizeof(preference)
            )
            if result == 0:
                no_border = ctypes.c_int(-2)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    self.hwnd, 34, ctypes.byref(no_border), ctypes.sizeof(no_border)
                )
                return
        except (AttributeError, OSError):
            pass

        # Windows 10 does not offer DWM corner rounding.
        try:
            window_rect = wintypes.RECT()
            client_rect = wintypes.RECT()
            client_origin = wintypes.POINT(0, 0)
            if not (
                user32.GetWindowRect(self.hwnd, ctypes.byref(window_rect))
                and user32.GetClientRect(self.hwnd, ctypes.byref(client_rect))
                and user32.ClientToScreen(self.hwnd, ctypes.byref(client_origin))
            ):
                return
            left = client_origin.x - window_rect.left
            top = client_origin.y - window_rect.top
            width = client_rect.right - client_rect.left
            height = client_rect.bottom - client_rect.top
            dpi_reader = getattr(user32, "GetDpiForWindow", None)
            dpi = int(dpi_reader(self.hwnd)) if dpi_reader else 96
            diameter = round(16 * (dpi / 96 if dpi > 0 else 1))
            region = ctypes.windll.gdi32.CreateRoundRectRgn(
                left, top, left + width + 1, top + height + 1, diameter, diameter
            )
            if region and not user32.SetWindowRgn(self.hwnd, region, True):
                ctypes.windll.gdi32.DeleteObject(region)
        except (AttributeError, OSError):
            pass

    def set_locked(self, locked: bool) -> None:
        with self._lock:
            self.locked = bool(locked)
            if not self.hwnd or self.base_style is None:
                return
            user32 = ctypes.windll.user32
            setter = getattr(user32, "SetWindowLongPtrW", user32.SetWindowLongW)
            style = self.base_style
            if self.locked:
                style |= self.WS_EX_TRANSPARENT | self.WS_EX_NOACTIVATE
            setter(self.hwnd, self.GWL_EXSTYLE, style)
            user32.SetWindowPos(self.hwnd, self.HWND_TOPMOST, 0, 0, 0, 0, self.SWP_NOMOVE | self.SWP_NOSIZE | self.SWP_NOACTIVATE)

    def begin_drag(self) -> None:
        if not self.hwnd or self.locked:
            return
        user32 = ctypes.windll.user32
        user32.ReleaseCapture()
        user32.SendMessageW(self.hwnd, self.WM_NCLBUTTONDOWN, self.HTCAPTION, 0)


class NativeDragThread:
    """Move the unlocked card from any visible area except its two controls."""

    VK_LBUTTON = 0x01

    def __init__(self, controller: NativeWindowController) -> None:
        self.controller = controller
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True, name="quota-card-native-drag")

    @staticmethod
    def is_drag_area(x: int, y: int, width: int, height: int) -> bool:
        if not (0 <= x < width and 0 <= y < height):
            return False
        return not (x >= round(width * 0.82) and y <= round(height * 0.19))

    def start(self) -> None:
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        if self.thread.is_alive():
            self.thread.join(timeout=2)

    def _run(self) -> None:
        user32 = ctypes.windll.user32
        previous_down = False
        dragging = False
        offset_x = offset_y = 0
        while not self.stop_event.is_set():
            down = bool(user32.GetAsyncKeyState(self.VK_LBUTTON) & 0x8000)
            hwnd = self.controller.hwnd
            point = wintypes.POINT()
            if down and hwnd and user32.GetCursorPos(ctypes.byref(point)):
                rect = wintypes.RECT()
                if user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                    if not previous_down:
                        local_x, local_y = point.x - rect.left, point.y - rect.top
                        dragging = (
                            not self.controller.locked
                            and bool(user32.IsWindowVisible(hwnd))
                            and self.is_drag_area(local_x, local_y, rect.right - rect.left, rect.bottom - rect.top)
                        )
                        offset_x, offset_y = local_x, local_y
                    elif dragging:
                        user32.SetWindowPos(
                            hwnd, 0, point.x - offset_x, point.y - offset_y, 0, 0,
                            NativeWindowController.SWP_NOSIZE
                            | NativeWindowController.SWP_NOZORDER
                            | NativeWindowController.SWP_NOACTIVATE,
                        )
            elif not down:
                dragging = False
            previous_down = down
            time.sleep(0.01)


class AppBridge:
    """The stable JavaScript/Python interface used by the card."""

    def __init__(
        self, settings: AppSettings, controller: NativeWindowController,
        *, autostart_reader: Callable[[], bool] = is_autostart_enabled,
    ) -> None:
        self.settings = settings
        self.controller = controller
        self.autostart_reader = autostart_reader

    def set_locked(self, locked: bool) -> dict[str, bool]:
        value = bool(locked)
        self.controller.set_locked(value)
        self.settings.update(locked=value)
        return {"locked": value}

    def begin_drag(self) -> None:
        """Internal UI hook that starts a native Windows move operation."""
        self.controller.begin_drag()

    def save_page(self, page: str) -> None:
        self.settings.update(page=page)

    def get_app_state(self) -> dict[str, Any]:
        return {
            "locked": bool(self.settings.state["locked"]),
            "page": self.settings.state["page"],
            "autostart": bool(self.autostart_reader()),
        }
