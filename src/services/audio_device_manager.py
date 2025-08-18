import sounddevice as sd
from typing import List, Dict, Optional, Tuple


class AudioDeviceInfo:
    """Audio device information container"""

    def __init__(self, device_id: int, name: str, is_default: bool = False):
        self.device_id = device_id
        self.name = name
        self.is_default = is_default

    def __str__(self):
        return f"AudioDeviceInfo(id={self.device_id}, name='{self.name}', default={self.is_default})"


class AudioDeviceManager:
    """Manages audio input device enumeration and selection"""

    def __init__(self):
        pass

    def get_input_devices(self) -> List[AudioDeviceInfo]:
        """Get all available input devices"""
        devices = []

        try:
            # Get all available devices
            all_devices = sd.query_devices()

            # Get default input device
            default_input_id = None
            try:
                default_device = sd.default.device
                if (
                    isinstance(default_device, (list, tuple))
                    and len(default_device) > 0
                ):
                    default_input_id = default_device[0]
                elif isinstance(default_device, int):
                    default_input_id = default_device
            except:
                pass

            # Add "Default" option first
            if default_input_id is not None:
                try:
                    default_device_info = all_devices[default_input_id]
                    default_name = default_device_info.get("name", "Unknown Device")
                    devices.append(
                        AudioDeviceInfo(
                            device_id="default",
                            name=f"Default ({default_name})",
                            is_default=True,
                        )
                    )
                except:
                    devices.append(
                        AudioDeviceInfo(
                            device_id="default", name="Default", is_default=True
                        )
                    )
            else:
                devices.append(
                    AudioDeviceInfo(
                        device_id="default", name="Default", is_default=True
                    )
                )

            # Add all input-capable devices
            for i, device in enumerate(all_devices):
                max_inputs = device.get("max_input_channels", 0)
                if max_inputs > 0:
                    device_name = device.get("name", f"Device {i}")
                    devices.append(
                        AudioDeviceInfo(device_id=i, name=device_name, is_default=False)
                    )

            return devices

        except Exception as e:
            print(f"Error getting input devices: {e}")
            # Return at least the default option
            return [
                AudioDeviceInfo(device_id="default", name="Default", is_default=True)
            ]

    def get_device_by_id(self, device_id) -> Optional[AudioDeviceInfo]:
        """Get device info by ID"""
        devices = self.get_input_devices()
        for device in devices:
            if str(device.device_id) == str(device_id):
                return device
        return None

    def is_device_available(self, device_id) -> bool:
        """Check if a device is currently available"""
        if device_id == "default":
            return True

        try:
            device_id_int = int(device_id)
            devices = sd.query_devices()
            if 0 <= device_id_int < len(devices):
                device = devices[device_id_int]
                return device.get("max_inputs", 0) > 0
        except (ValueError, IndexError):
            pass

        return False

    def get_default_device_info(self) -> Optional[Tuple[int, str]]:
        """Get the current system default input device ID and name"""
        try:
            default_device = sd.default.device
            if isinstance(default_device, (list, tuple)) and len(default_device) > 0:
                default_input_id = default_device[0]
            elif isinstance(default_device, int):
                default_input_id = default_device
            else:
                return None

            devices = sd.query_devices()
            if 0 <= default_input_id < len(devices):
                device_info = devices[default_input_id]
                device_name = device_info.get("name", "Unknown Device")
                return (default_input_id, device_name)

        except Exception as e:
            print(f"Error getting default device info: {e}")

        return None

    def print_device_debug_info(self):
        """Debug: Print all available devices (similar to audio_recorder.py)"""
        try:
            print("\n Available Audio Input Devices:")
            devices = self.get_input_devices()

            for device in devices:
                marker = " ← DEFAULT" if device.is_default else ""
                print(f"  {device.device_id}: {device.name}{marker}")

            # Show current default
            default_info = self.get_default_device_info()
            if default_info:
                print(f" System default: {default_info[1]} (ID: {default_info[0]})")

        except Exception as e:
            print(f" Error listing input devices: {e}")
