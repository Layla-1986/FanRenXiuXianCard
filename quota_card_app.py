"""凡人额度卡 1.0.0 Windows desktop entry point."""

from __future__ import annotations

import argparse
import ctypes
import sys
import threading
from ctypes import wintypes
from pathlib import Path
from typing import Any, Sequence

from antigravity_quota import PollingService, QuotaStore, UiAutomationCollector, start_server
from mortal_quota.codex import CodexAccountProvider, CodexAppServerClient, CodexSessionReader
from mortal_quota.desktop import (
    APP_NAME, WINDOW_HEIGHT, WINDOW_WIDTH, AppBridge, AppSettings, NativeDragThread, NativeWindowController,
    app_data_dir, clamp_position, is_autostart_enabled, set_autostart, window_visual_options,
)


VERSION = "1.0.0"
MUTEX_NAME = r"Local\MortalQuotaCard.SingleInstance.v1"
SHOW_EVENT_NAME = r"Local\MortalQuotaCard.ShowExisting.v1"


class SingleInstance:
    ERROR_ALREADY_EXISTS = 183
    EVENT_MODIFY_STATE = 0x0002

    def __init__(self) -> None:
        self.kernel32 = ctypes.windll.kernel32
        self.mutex = self.kernel32.CreateMutexW(None, False, MUTEX_NAME)
        self.primary = self.kernel32.GetLastError() != self.ERROR_ALREADY_EXISTS
        self.event = None
        if self.primary:
            self.event = self.kernel32.CreateEventW(None, False, False, SHOW_EVENT_NAME)
        else:
            event = self.kernel32.OpenEventW(self.EVENT_MODIFY_STATE, False, SHOW_EVENT_NAME)
            if event:
                self.kernel32.SetEvent(event)
                self.kernel32.CloseHandle(event)

    def close(self) -> None:
        for handle in (self.event, self.mutex):
            if handle:
                self.kernel32.CloseHandle(handle)
        self.event = self.mutex = None


class HotkeyThread:
    VK_CONTROL = 0x11
    VK_MENU = 0x12
    VK_L = 0x4C

    def __init__(self, callback) -> None:
        self.callback = callback
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True, name="quota-card-hotkey")

    def start(self) -> None:
        self.thread.start()

    def _run(self) -> None:
        user32 = ctypes.windll.user32
        was_pressed = False
        while not self.stop_event.is_set():
            pressed = all(
                user32.GetAsyncKeyState(key) & 0x8000
                for key in (self.VK_CONTROL, self.VK_MENU, self.VK_L)
            )
            if pressed and not was_pressed:
                self.callback()
            was_pressed = pressed
            self.stop_event.wait(0.03)

    def stop(self) -> None:
        self.stop_event.set()
        if self.thread.is_alive():
            self.thread.join(timeout=2)


def monitor_work_areas() -> list[tuple[int, int, int, int]]:
    class MONITORINFO(ctypes.Structure):
        _fields_ = [("cbSize", wintypes.DWORD), ("rcMonitor", wintypes.RECT), ("rcWork", wintypes.RECT), ("dwFlags", wintypes.DWORD)]

    areas: list[tuple[int, int, int, int]] = []
    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HMONITOR, wintypes.HDC, ctypes.POINTER(wintypes.RECT), wintypes.LPARAM)

    def collect(monitor, _dc, _rect, _data):
        info = MONITORINFO(cbSize=ctypes.sizeof(MONITORINFO))
        if ctypes.windll.user32.GetMonitorInfoW(monitor, ctypes.byref(info)):
            rect = info.rcWork
            areas.append((rect.left, rect.top, rect.right, rect.bottom))
        return True

    ctypes.windll.user32.EnumDisplayMonitors(None, None, callback_type(collect), 0)
    return areas


class DesktopApplication:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.data_dir = app_data_dir()
        self.settings = AppSettings(self.data_dir / "settings.json")
        self.stop_event = threading.Event()
        self.window = None
        self.controller = None
        self.bridge = None
        self.server = None
        self.poller_thread = None
        self.tray = None
        self.hotkey = None
        self.drag_thread = None
        self.instance = SingleInstance()

    def start(self) -> int:
        if not self.instance.primary:
            self.instance.close()
            return 0
        import webview

        store = QuotaStore(self.data_dir / "antigravity-quota.json")
        poller = PollingService(store, UiAutomationCollector(), interval_seconds=60)
        self.poller_thread = threading.Thread(target=poller.run_forever, args=(self.stop_event,), daemon=True, name="antigravity-quota-poller")
        provider = CodexAccountProvider(
            CodexAppServerClient(), CodexSessionReader(Path.home() / ".codex" / "sessions"), refresh_seconds=60
        )
        self.server = start_server(store, static_root=self.project_root, port=0, codex_reader=provider)
        threading.Thread(target=self.server.serve_forever, daemon=True, name="quota-card-http").start()
        self.poller_thread.start()

        x, y = clamp_position(self.settings.state["x"], self.settings.state["y"], WINDOW_WIDTH, WINDOW_HEIGHT, monitor_work_areas())
        self.window = webview.create_window(
            "凡人额度卡", f"http://127.0.0.1:{self.server.server_port}/quota-card-app.html",
            width=WINDOW_WIDTH, height=WINDOW_HEIGHT, x=x, y=y, frameless=True,
            easy_drag=False, resizable=False, on_top=True, **window_visual_options(),
        )
        self.controller = NativeWindowController(self.window)
        self.bridge = AppBridge(self.settings, self.controller)
        self.window.expose(self.bridge.set_locked, self.bridge.save_page, self.bridge.get_app_state, self.bridge.begin_drag)
        self.window.events.before_show += self._before_show
        self.window.events.moved += self._moved
        self.window.events.closed += self._closed
        self._start_tray()
        self.hotkey = HotkeyThread(self.unlock)
        self.hotkey.start()
        self.drag_thread = NativeDragThread(self.controller)
        self.drag_thread.start()
        threading.Thread(target=self._watch_second_launch, daemon=True, name="quota-card-single-instance").start()
        webview.start(gui="edgechromium", debug=False, private_mode=True)
        return 0

    def _before_show(self) -> None:
        self.controller.attach()

    def _moved(self, *position: Any) -> None:
        x = position[0] if len(position) > 0 and isinstance(position[0], int) else getattr(self.window, "x", None)
        y = position[1] if len(position) > 1 and isinstance(position[1], int) else getattr(self.window, "y", None)
        if isinstance(x, int) and isinstance(y, int):
            self.settings.update(x=x, y=y)

    def _watch_second_launch(self) -> None:
        if self.instance.event:
            while not self.stop_event.is_set():
                result = ctypes.windll.kernel32.WaitForSingleObject(self.instance.event, 500)
                if result == 0:
                    self.show()

    def show(self) -> None:
        if self.window:
            self.window.show()
            self.window.on_top = True

    def toggle_visible(self) -> None:
        if not self.window:
            return
        if getattr(self.window, "hidden", False):
            self.show()
        else:
            self.window.hide()

    def unlock(self) -> None:
        if self.bridge:
            self.bridge.set_locked(False)
        if self.window:
            self.window.evaluate_js("window.dispatchEvent(new CustomEvent('mortalquota:lock-state',{detail:false}))")

    def toggle_lock(self) -> None:
        if not self.bridge:
            return
        next_value = not self.settings.state["locked"]
        self.bridge.set_locked(next_value)
        if self.window:
            value = "true" if next_value else "false"
            self.window.evaluate_js(f"document.getElementById('lock-button').setAttribute('aria-pressed','{value}')")

    def toggle_autostart(self) -> None:
        enabled = not is_autostart_enabled()
        set_autostart(enabled)
        self.settings.update(autostart=enabled)

    def _start_tray(self) -> None:
        import pystray
        from PIL import Image

        icon_path = self.project_root / "assets" / "mortal-quota-card.ico"
        image = Image.open(icon_path)
        menu = pystray.Menu(
            pystray.MenuItem("显示/隐藏", lambda: self.toggle_visible(), default=True),
            pystray.MenuItem(lambda _item: "解锁" if self.settings.state["locked"] else "锁定", lambda: self.toggle_lock()),
            pystray.MenuItem("开机自启", lambda: self.toggle_autostart(), checked=lambda _item: is_autostart_enabled()),
            pystray.MenuItem("退出", lambda: self.exit()),
        )
        self.tray = pystray.Icon(APP_NAME, image, "凡人额度卡", menu)
        self.tray.run_detached()

    def exit(self) -> None:
        if self.window:
            self.window.destroy()

    def _closed(self) -> None:
        self.stop_event.set()
        if self.hotkey:
            self.hotkey.stop()
        if self.drag_thread:
            self.drag_thread.stop()
        if self.tray:
            self.tray.stop()
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        if self.poller_thread:
            self.poller_thread.join(timeout=2)
        self.instance.close()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=f"凡人额度卡 {VERSION}")
    parser.add_argument("--autostart", action="store_true", help="由当前用户开机自启项启动")
    parser.parse_args(argv)
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return DesktopApplication(root).start()


if __name__ == "__main__":
    raise SystemExit(main())
