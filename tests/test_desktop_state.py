"""Desktop state and bridge behavior without requiring a GUI session."""

from __future__ import annotations

import tempfile
import unittest
from types import SimpleNamespace
from pathlib import Path

import mortal_quota.desktop as desktop
from mortal_quota.desktop import AppBridge, AppSettings, NativeDragThread, NativeWindowController, clamp_position, window_visual_options


class AppSettingsTest(unittest.TestCase):
    def test_persists_page_position_and_autostart_but_always_starts_unlocked(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            settings = AppSettings(path)
            settings.update(page="antigravity", x=2400, y=900, autostart=True, locked=True)

            restarted = AppSettings(path)

        self.assertEqual("antigravity", restarted.state["page"])
        self.assertEqual(2400, restarted.state["x"])
        self.assertEqual(900, restarted.state["y"])
        self.assertTrue(restarted.state["autostart"])
        self.assertFalse(restarted.state["locked"])

    def test_rejects_unknown_page_and_malformed_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            path.write_text('{"page":"demo","x":"left"}', encoding="utf-8")
            settings = AppSettings(path)

        self.assertEqual("codex", settings.state["page"])
        self.assertIsNone(settings.state["x"])


class ClampPositionTest(unittest.TestCase):
    def test_window_uses_per_pixel_transparency_behind_rounded_card(self):
        options = window_visual_options()

        self.assertTrue(options["transparent"])

    def test_keeps_visible_position_and_moves_offscreen_position_to_primary_work_area(self):
        areas = [(0, 0, 1920, 1040), (1920, 0, 3840, 1040)]
        self.assertEqual((2100, 100), clamp_position(2100, 100, 480, 270, areas))
        self.assertEqual((720, 385), clamp_position(6000, 3000, 480, 270, areas))

    def test_native_drag_excludes_only_the_two_top_right_controls(self):
        self.assertTrue(NativeDragThread.is_drag_area(300, 120, 720, 405))
        self.assertTrue(NativeDragThread.is_drag_area(80, 35, 720, 405))
        self.assertFalse(NativeDragThread.is_drag_area(630, 42, 720, 405))
        self.assertFalse(NativeDragThread.is_drag_area(678, 42, 720, 405))


class BridgeTest(unittest.TestCase):
    def test_bridge_delegates_lock_and_exposes_fixed_state_contract(self):
        calls = []

        class Controller:
            def set_locked(self, locked):
                calls.append(locked)

        with tempfile.TemporaryDirectory() as directory:
            settings = AppSettings(Path(directory) / "settings.json")
            bridge = AppBridge(settings, Controller(), autostart_reader=lambda: True)
            self.assertEqual({"locked": True}, bridge.set_locked(True))
            bridge.save_page("antigravity")
            state = bridge.get_app_state()

        self.assertEqual([True], calls)
        self.assertEqual({"locked": True, "page": "antigravity", "autostart": True}, state)


class NativeWindowControllerTest(unittest.TestCase):
    def test_click_through_styles_are_removed_exactly_when_unlocked(self):
        calls = []
        dwm_calls = []
        original = desktop.ctypes.windll

        class User32:
            def GetWindowLongPtrW(self, _hwnd, _index):
                return NativeWindowController.WS_EX_APPWINDOW | 0x100
            GetWindowLongW = GetWindowLongPtrW

            def SetWindowLongPtrW(self, _hwnd, _index, style):
                calls.append(style)
            SetWindowLongW = SetWindowLongPtrW

            def SetWindowPos(self, *_args):
                calls.append(("SetWindowPos", _args))
                return True

            def ReleaseCapture(self):
                calls.append(("ReleaseCapture", ()))
                return True

            def SendMessageW(self, *_args):
                calls.append(("SendMessageW", _args))
                return 0

            def GetWindowRect(self, _hwnd, rect):
                rect._obj.left, rect._obj.top, rect._obj.right, rect._obj.bottom = 0, 0, 697, 350
                return True

            def GetClientRect(self, _hwnd, rect):
                rect._obj.left, rect._obj.top, rect._obj.right, rect._obj.bottom = 0, 0, 697, 348
                return True

            def ClientToScreen(self, _hwnd, point):
                point._obj.x, point._obj.y = 0, 1
                return True

            def SetWindowRgn(self, _hwnd, region, redraw):
                calls.append(("SetWindowRgn", region, redraw))
                return True

            def GetDpiForWindow(self, _hwnd):
                return 144

        class Handle:
            def ToInt32(self):
                return 42

        class Gdi32:
            def CreateRoundRectRgn(self, *args):
                calls.append(("CreateRoundRectRgn", args))
                return 99

            def DeleteObject(self, region):
                calls.append(("DeleteObject", region))

        desktop.ctypes.windll = SimpleNamespace(
            user32=User32(),
            dwmapi=SimpleNamespace(DwmSetWindowAttribute=lambda *args: dwm_calls.append(args) or 0),
            gdi32=Gdi32(),
        )
        try:
            controller = NativeWindowController(SimpleNamespace(native=SimpleNamespace(Handle=Handle())))
            controller.attach()
            base = [entry for entry in calls if isinstance(entry, int)][-1]
            controller.set_locked(True)
            locked = [entry for entry in calls if isinstance(entry, int)][-1]
            controller.set_locked(False)
            restored = [entry for entry in calls if isinstance(entry, int)][-1]
            controller.begin_drag()
        finally:
            desktop.ctypes.windll = original

        self.assertTrue(base & NativeWindowController.WS_EX_TOOLWINDOW)
        self.assertFalse(base & NativeWindowController.WS_EX_APPWINDOW)
        self.assertTrue(locked & NativeWindowController.WS_EX_TRANSPARENT)
        self.assertTrue(locked & NativeWindowController.WS_EX_NOACTIVATE)
        self.assertEqual(base, restored)
        self.assertTrue(any(entry[0] == "ReleaseCapture" for entry in calls if isinstance(entry, tuple)))
        self.assertTrue(any(entry[0] == "SendMessageW" and entry[1][1:3] == (0x00A1, 2) for entry in calls if isinstance(entry, tuple)))
        self.assertEqual([33, 34], [entry[1] for entry in dwm_calls])
        self.assertEqual(-2, dwm_calls[1][2]._obj.value, "the DWM system border must be disabled")
        self.assertIn(("CreateRoundRectRgn", (0, 1, 698, 350, 66, 66)), calls)
        self.assertIn(("SetWindowRgn", 99, True), calls)
        resize_calls = [entry for entry in calls if isinstance(entry, tuple) and entry[0] == "SetWindowPos"]
        self.assertTrue(
            any(entry[1][4:6] == (720, 407) for entry in resize_calls),
            "attach must enlarge the native window until its client area is exactly 480x270",
        )


if __name__ == "__main__":
    unittest.main()
