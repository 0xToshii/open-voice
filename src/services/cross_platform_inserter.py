import pyautogui
import pyperclip
import time
import subprocess
import platform
from typing import Dict, Any, Optional
from src.interfaces.text_insertion import ITextInserter


class CrossPlatformTextInserter(ITextInserter):
    """Cross-platform text insertion using pyautogui and pyperclip"""

    def __init__(self, method: str = "clipboard"):
        """
        Initialize the cross-platform text inserter

        Args:
            method: Insertion method - "typing", "clipboard", or "hybrid"
        """
        self.method = method
        self.typing_delay = 0.005  # Seconds between characters (2x faster)
        self.clipboard_delay = 0.1  # Delay after clipboard operations
        self.short_text_threshold = 50  # Characters threshold for hybrid mode

        # Configure pyautogui
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
        pyautogui.PAUSE = 0.01  # Small delay between operations

    def insert_text(self, text: str) -> bool:
        """Insert text using the configured method with focus preservation"""
        if not text:
            print("⚠️ Empty text provided for insertion")
            return True  # Empty text is "successfully" inserted

        try:
            # Remember which app was focused before we started
            focused_app = self._get_focused_app()
            print(f"🎯 Focused app before insertion: {focused_app}")

            # Perform the text insertion
            success = False
            if self.method == "typing":
                success = self._insert_via_typing_with_focus(text, focused_app)
            elif self.method == "clipboard":
                success = self._insert_via_clipboard_with_focus(text, focused_app)
            elif self.method == "hybrid":
                success = self._insert_via_hybrid_with_focus(text, focused_app)
            else:
                print(f"❌ Unknown insertion method: {self.method}")
                return False

            return success

        except Exception as e:
            print(f"❌ Text insertion failed: {e}")
            return False

    def _get_focused_app(self) -> Optional[str]:
        """Get the name of the currently focused application"""
        try:
            if platform.system() == "Darwin":  # macOS
                result = subprocess.run(
                    [
                        "osascript",
                        "-e",
                        'tell application "System Events" to get name of first application process whose frontmost is true',
                    ],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )

                if result.returncode == 0:
                    app_name = result.stdout.strip()
                    return app_name if app_name else None
                else:
                    print(f"⚠️ Failed to get focused app: {result.stderr}")
                    return None
            else:
                # For non-Mac systems, we can't easily detect focus
                print("⚠️ Focus detection not supported on this platform")
                return None

        except Exception as e:
            print(f"⚠️ Error getting focused app: {e}")
            return None

    def _restore_focus(self, app_name: str) -> bool:
        """Restore focus to the specified application"""
        try:
            if not app_name or platform.system() != "Darwin":
                return False

            print(f"🔄 Restoring focus to: {app_name}")

            result = subprocess.run(
                ["osascript", "-e", f'tell application "{app_name}" to activate'],
                capture_output=True,
                text=True,
                timeout=2,
            )

            if result.returncode == 0:
                print(f"✅ Focus restored to {app_name}")
                return True
            else:
                print(f"⚠️ Failed to restore focus: {result.stderr}")
                return False

        except Exception as e:
            print(f"⚠️ Error restoring focus: {e}")
            return False

    def _insert_via_typing_with_focus(
        self, text: str, focused_app: Optional[str]
    ) -> bool:
        """Insert text by typing with focus restoration"""
        # Restore focus to target app first
        if focused_app:
            self._restore_focus(focused_app)
            time.sleep(0.1)  # Small delay to ensure focus change takes effect

        return self._insert_via_typing(text)

    def _insert_via_clipboard_with_focus(
        self, text: str, focused_app: Optional[str]
    ) -> bool:
        """Insert text via clipboard with focus restoration"""
        # Restore focus to target app first
        if focused_app:
            self._restore_focus(focused_app)
            time.sleep(0.1)  # Small delay to ensure focus change takes effect

        return self._insert_via_clipboard(text)

    def _insert_via_hybrid_with_focus(
        self, text: str, focused_app: Optional[str]
    ) -> bool:
        """Smart insertion with focus restoration"""
        if len(text) <= self.short_text_threshold:
            print(f"🔄 Hybrid mode: Using typing for short text ({len(text)} chars)")
            success = self._insert_via_typing_with_focus(text, focused_app)
            if success:
                return True

            # Fallback to clipboard if typing fails
            print("🔄 Typing failed, falling back to clipboard")
            return self._insert_via_clipboard_with_focus(text, focused_app)
        else:
            print(f"🔄 Hybrid mode: Using clipboard for long text ({len(text)} chars)")
            success = self._insert_via_clipboard_with_focus(text, focused_app)
            if success:
                return True

            # Fallback to typing if clipboard fails
            print("🔄 Clipboard failed, falling back to typing")
            return self._insert_via_typing_with_focus(text, focused_app)

    def _insert_via_typing(self, text: str) -> bool:
        """Insert text by simulating typing"""
        try:
            print(f"⌨️ Typing text: '{text[:50]}{'...' if len(text) > 50 else ''}'")

            # Set typing interval
            original_interval = pyautogui.PAUSE
            pyautogui.PAUSE = self.typing_delay

            # Type the text
            pyautogui.typewrite(text)

            # Restore original interval
            pyautogui.PAUSE = original_interval

            print(f"✅ Successfully typed {len(text)} characters")
            return True

        except Exception as e:
            print(f"❌ Typing insertion failed: {e}")
            return False

    def _insert_via_clipboard(self, text: str) -> bool:
        """Insert text via clipboard and paste"""
        try:
            print(
                f"📋 Clipboard insertion: '{text[:50]}{'...' if len(text) > 50 else ''}'"
            )

            # Backup current clipboard content
            try:
                original_clipboard = pyperclip.paste()
            except Exception:
                original_clipboard = ""  # Clipboard might be empty or inaccessible

            # Copy our text to clipboard
            pyperclip.copy(text)
            time.sleep(self.clipboard_delay)  # Allow clipboard to update

            # Paste using Cmd+V (Mac) or Ctrl+V (others)
            import platform

            if platform.system() == "Darwin":  # macOS
                pyautogui.hotkey("cmd", "v")
            else:
                pyautogui.hotkey("ctrl", "v")

            # Wait for paste to complete
            time.sleep(self.clipboard_delay)

            # Restore original clipboard content
            try:
                pyperclip.copy(original_clipboard)
            except Exception:
                pass  # If restoration fails, don't break the insertion

            print(f"✅ Successfully pasted {len(text)} characters")
            return True

        except Exception as e:
            print(f"❌ Clipboard insertion failed: {e}")
            return False

    def _insert_via_hybrid(self, text: str) -> bool:
        """Smart insertion: typing for short text, clipboard for long text"""
        if len(text) <= self.short_text_threshold:
            print(f"🔄 Hybrid mode: Using typing for short text ({len(text)} chars)")
            success = self._insert_via_typing(text)
            if success:
                return True

            # Fallback to clipboard if typing fails
            print("🔄 Typing failed, falling back to clipboard")
            return self._insert_via_clipboard(text)
        else:
            print(f"🔄 Hybrid mode: Using clipboard for long text ({len(text)} chars)")
            success = self._insert_via_clipboard(text)
            if success:
                return True

            # Fallback to typing if clipboard fails
            print("🔄 Clipboard failed, falling back to typing")
            return self._insert_via_typing(text)

    def is_available(self) -> bool:
        """Check if pyautogui and pyperclip are functional"""
        try:
            # Test pyautogui
            pyautogui.size()  # Should return screen size

            # Test pyperclip
            test_text = "test"
            original = pyperclip.paste()
            pyperclip.copy(test_text)
            copied = pyperclip.paste()
            pyperclip.copy(original)  # Restore

            if copied != test_text:
                print("⚠️ Clipboard test failed")
                return False

            return True

        except Exception as e:
            print(f"❌ Cross-platform inserter not available: {e}")
            return False

    def get_capabilities(self) -> Dict[str, Any]:
        """Get capabilities of this inserter"""
        return {
            "name": self.get_name(),
            "platform": "cross-platform",
            "method": self.method,
            "supports_long_text": True,
            "supports_special_chars": True,
            "supports_unicode": True,
            "advanced_features": False,
            "requires_permissions": False,
            "typing_delay": self.typing_delay,
            "short_text_threshold": self.short_text_threshold,
        }

    def get_name(self) -> str:
        """Get the name of this inserter"""
        return "CrossPlatformInserter"

    def set_typing_speed(self, delay: float) -> None:
        """
        Set the delay between keystrokes for typing mode

        Args:
            delay: Seconds between each character (0.01 = fast, 0.1 = slow)
        """
        self.typing_delay = max(0.001, delay)  # Minimum delay for safety
        print(f"🔧 Typing speed set to {self.typing_delay}s per character")

    def set_method(self, method: str) -> None:
        """
        Change the insertion method

        Args:
            method: "typing", "clipboard", or "hybrid"
        """
        if method in ["typing", "clipboard", "hybrid"]:
            self.method = method
            print(f"🔧 Insertion method changed to: {method}")
        else:
            print(
                f"❌ Invalid method: {method}. Use 'typing', 'clipboard', or 'hybrid'"
            )
