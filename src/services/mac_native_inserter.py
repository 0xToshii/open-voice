import platform
import time
from typing import Dict, Any
from src.interfaces.text_insertion import ITextInserter

# Only import macOS-specific modules on macOS
if platform.system() == "Darwin":
    try:
        import objc
        from Cocoa import NSWorkspace, NSPasteboard, NSApplication, NSString
        from Quartz import (
            CGEventCreateKeyboardEvent,
            CGEventPost,
            kCGHIDEventTap,
            CGEventSetFlags,
            kCGEventFlagMaskCommand,
        )
        from ApplicationServices import AXIsProcessTrusted

        MAC_DEPENDENCIES_AVAILABLE = True
    except ImportError as e:
        print(f"⚠️ Mac dependencies not available: {e}")
        MAC_DEPENDENCIES_AVAILABLE = False
else:
    MAC_DEPENDENCIES_AVAILABLE = False


class MacNativeTextInserter(ITextInserter):
    """Mac-native text insertion using PyObjC and macOS APIs"""

    def __init__(self):
        self.clipboard_delay = 0.1
        self.key_event_delay = 0.05

    def insert_text(self, text: str) -> bool:
        """Insert text using Mac-native APIs"""
        if not self.is_available():
            print("❌ Mac native inserter not available")
            return False

        if not text:
            print("⚠️ Empty text provided for insertion")
            return True

        try:
            print(f"🍎 Mac Native: Inserting text ({len(text)} chars)")

            # Step 1: Check accessibility permissions
            if not self._check_accessibility_permissions():
                print("❌ Accessibility permissions required for text insertion")
                return False

            # Step 2: Get current app for focus context
            focused_app = self._get_focused_app()
            print(f"🎯 Focused app: {focused_app}")

            # Step 3: Copy text to clipboard using native pasteboard
            if not self._copy_to_pasteboard(text):
                print("❌ Failed to copy text to pasteboard")
                return False

            # Step 4: Send Cmd+V using CGEvent (most reliable)
            if not self._send_paste_command():
                print("❌ Failed to send paste command")
                return False

            print(
                f"✅ Successfully inserted {len(text)} characters using Mac native APIs"
            )
            return True

        except Exception as e:
            print(f"❌ Mac native text insertion failed: {e}")
            return False

    def _check_accessibility_permissions(self) -> bool:
        """Check if accessibility permissions are granted"""
        try:
            return AXIsProcessTrusted()
        except Exception as e:
            print(f"⚠️ Could not check accessibility permissions: {e}")
            return False

    def _get_focused_app(self) -> str:
        """Get the currently focused application using NSWorkspace"""
        try:
            workspace = NSWorkspace.sharedWorkspace()
            active_app = workspace.frontmostApplication()

            if active_app:
                app_name = active_app.localizedName()
                bundle_id = active_app.bundleIdentifier()
                print(f"🎯 Active app: {app_name} ({bundle_id})")
                return app_name
            else:
                print("⚠️ No active app detected")
                return "Unknown"

        except Exception as e:
            print(f"⚠️ Failed to get focused app: {e}")
            return "Unknown"

    def _copy_to_pasteboard(self, text: str) -> bool:
        """Copy text to macOS pasteboard (clipboard) using native APIs"""
        try:
            # Get the general pasteboard
            pasteboard = NSPasteboard.generalPasteboard()

            # Clear existing content
            pasteboard.clearContents()

            # Set the string content
            ns_string = NSString.stringWithString_(text)
            success = pasteboard.setString_forType_(ns_string, "public.utf8-plain-text")

            if success:
                print(f"📋 Successfully copied {len(text)} chars to pasteboard")
                time.sleep(self.clipboard_delay)  # Allow pasteboard to update
                return True
            else:
                print("❌ Failed to set pasteboard content")
                return False

        except Exception as e:
            print(f"❌ Pasteboard copy failed: {e}")
            return False

    def _send_paste_command(self) -> bool:
        """Send Cmd+V using CGEvent for reliable paste operation"""
        try:
            # Key codes for macOS
            CMD_KEY = 0x37  # Left Command key
            V_KEY = 0x09  # V key

            # Create key down events
            cmd_down = CGEventCreateKeyboardEvent(None, CMD_KEY, True)
            v_down = CGEventCreateKeyboardEvent(None, V_KEY, True)

            # Set command flag on V key press
            CGEventSetFlags(v_down, kCGEventFlagMaskCommand)

            # Create key up events
            v_up = CGEventCreateKeyboardEvent(None, V_KEY, False)
            cmd_up = CGEventCreateKeyboardEvent(None, CMD_KEY, False)

            # Post events in correct sequence
            CGEventPost(kCGHIDEventTap, cmd_down)
            time.sleep(self.key_event_delay)

            CGEventPost(kCGHIDEventTap, v_down)
            time.sleep(self.key_event_delay)

            CGEventPost(kCGHIDEventTap, v_up)
            time.sleep(self.key_event_delay)

            CGEventPost(kCGHIDEventTap, cmd_up)

            print("⌨️ Sent Cmd+V using CGEvent")
            return True

        except Exception as e:
            print(f"❌ Failed to send paste command: {e}")
            return False

    def is_available(self) -> bool:
        """Check if Mac-native inserter is available"""
        if platform.system() != "Darwin":
            return False

        if not MAC_DEPENDENCIES_AVAILABLE:
            return False

        try:
            # Test basic PyObjC functionality
            workspace = NSWorkspace.sharedWorkspace()
            pasteboard = NSPasteboard.generalPasteboard()
            return True

        except Exception as e:
            print(f"❌ Mac native inserter test failed: {e}")
            return False

    def get_capabilities(self) -> Dict[str, Any]:
        """Get capabilities of the Mac-native inserter"""
        return {
            "name": self.get_name(),
            "platform": "macOS",
            "method": "native_pasteboard_cgevent",
            "supports_long_text": True,
            "supports_special_chars": True,
            "supports_unicode": True,
            "advanced_features": True,
            "requires_permissions": True,
            "permission_type": "accessibility",
            "reliability": "high",
            "focus_aware": True,
        }

    def get_name(self) -> str:
        """Get the name of this inserter"""
        return "MacNativeInserter"

    def request_permissions(self) -> bool:
        """Request accessibility permissions from the user"""
        try:
            if self._check_accessibility_permissions():
                print("✅ Accessibility permissions already granted")
                return True

            print("🔐 Accessibility permissions required")
            print(
                "   Please grant accessibility permissions in System Preferences > Security & Privacy > Privacy > Accessibility"
            )

            # We can't programmatically request permissions, but we can guide the user
            return False

        except Exception as e:
            print(f"❌ Permission request failed: {e}")
            return False


class MockMacNativeInserter(ITextInserter):
    """Mock Mac-native inserter for testing on non-Mac systems"""

    def __init__(self):
        pass

    def insert_text(self, text: str) -> bool:
        """Mock text insertion"""
        print(
            f"🍎 Mock Mac Native: Would insert '{text[:50]}{'...' if len(text) > 50 else ''}' ({len(text)} chars)"
        )
        return True

    def is_available(self) -> bool:
        """Mock is always available for testing"""
        return True

    def get_capabilities(self) -> Dict[str, Any]:
        """Get mock capabilities"""
        return {
            "name": self.get_name(),
            "platform": "mock_macOS",
            "method": "mock_native",
            "supports_long_text": True,
            "supports_special_chars": True,
            "supports_unicode": True,
            "advanced_features": True,
            "requires_permissions": False,
            "reliability": "mock",
        }

    def get_name(self) -> str:
        """Get the name of this mock inserter"""
        return "MockMacNativeInserter"
