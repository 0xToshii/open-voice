from src.interfaces.hotkey import IHotkeyHandler
from pynput import keyboard
from typing import Callable, Optional
import threading
import subprocess
import platform


class FnKeyHandler(IHotkeyHandler):
    """Handles Cmd+Shift+Space key detection for recording activation"""

    def __init__(self):
        self.on_press_callback: Optional[Callable] = None
        self.on_release_callback: Optional[Callable] = None
        self.listener: Optional[keyboard.Listener] = None
        self.is_listening = False
        self.hotkey_pressed = False
        self.cmd_pressed = False
        self.shift_pressed = False
        self.space_pressed = False
        self.captured_app = None  # Store captured app for callback

    def register_hotkey(self, on_press: Callable, on_release: Callable) -> None:
        """Register callbacks for Fn key press and release"""
        self.on_press_callback = on_press
        self.on_release_callback = on_release

    def start_listening(self) -> None:
        """Start listening for Fn key events"""
        if self.is_listening:
            return

        self.is_listening = True
        self.listener = keyboard.Listener(
            on_press=self._on_key_press, on_release=self._on_key_release, suppress=False
        )
        self.listener.start()

    def stop_listening(self) -> None:
        """Stop listening for Fn key events"""
        if not self.is_listening:
            return

        self.is_listening = False
        if self.listener:
            self.listener.stop()
            self.listener = None

    def _on_key_press(self, key):
        """Handle key press events for Cmd+Shift+Space combination"""
        try:
            # Track individual key states
            if key == keyboard.Key.cmd:
                self.cmd_pressed = True
            elif key == keyboard.Key.shift:
                self.shift_pressed = True
            elif key == keyboard.Key.space:
                self.space_pressed = True

            # Check if all three keys are pressed (Cmd+Shift+Space)
            if self.cmd_pressed and self.shift_pressed and self.space_pressed:
                if not self.hotkey_pressed:
                    self.hotkey_pressed = True
                    print("🔴 Hotkey combination detected: Cmd+Shift+Space")
                    if self.on_press_callback:
                        self.on_press_callback()

        except AttributeError:
            # Key doesn't have the expected attributes
            pass

    def _on_key_release(self, key):
        """Handle key release events for Cmd+Shift+Space combination"""
        try:
            # Track individual key release states
            if key == keyboard.Key.cmd:
                self.cmd_pressed = False
            elif key == keyboard.Key.shift:
                self.shift_pressed = False
            elif key == keyboard.Key.space:
                self.space_pressed = False

            # If hotkey was active and any key is released, trigger release callback
            if self.hotkey_pressed and not (
                self.cmd_pressed and self.shift_pressed and self.space_pressed
            ):
                self.hotkey_pressed = False
                print("⚫ Hotkey combination released")
                if self.on_release_callback:
                    self.on_release_callback()

        except AttributeError:
            # Key doesn't have the expected attributes
            pass


class MockHotkeyHandler(IHotkeyHandler):
    """Mock hotkey handler for testing without real key detection"""

    def __init__(self):
        self.on_press_callback: Optional[Callable] = None
        self.on_release_callback: Optional[Callable] = None
        self.is_listening = False

    def register_hotkey(self, on_press: Callable, on_release: Callable) -> None:
        """Register callbacks for hotkey press and release"""
        self.on_press_callback = on_press
        self.on_release_callback = on_release

    def start_listening(self) -> None:
        """Start listening (mock)"""
        self.is_listening = True
        print(
            "Mock hotkey handler started - use simulate_press() and simulate_release() to test"
        )

    def stop_listening(self) -> None:
        """Stop listening (mock)"""
        self.is_listening = False
        print("Mock hotkey handler stopped")

    def simulate_press(self):
        """Simulate hotkey press for testing"""
        if self.on_press_callback:
            self.on_press_callback()

    def simulate_release(self):
        """Simulate hotkey release for testing"""
        if self.on_release_callback:
            self.on_release_callback()
