"""
Aara System Control
Volume, brightness, power management for Windows.
"""

import os
import logging
import subprocess
from typing import Tuple

logger = logging.getLogger(__name__)


class SystemControl:
    """Controls system settings like volume, power, etc."""

    def __init__(self):
        """Initialize system control."""
        self._pycaw_available = False
        self._volume_interface = None
        self._init_volume_control()

    def _init_volume_control(self) -> None:
        """Initialize volume control using pycaw."""
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self._volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
            self._pycaw_available = True
            logger.info("Volume control initialized (pycaw)")
        except ImportError:
            logger.warning("Pycaw not installed. Run: pip install pycaw")
        except Exception as e:
            logger.warning(f"Failed to initialize volume control: {e}")

    def get_volume(self) -> int:
        """
        Get current volume level.

        Returns:
            Volume level (0-100)
        """
        if self._pycaw_available and self._volume_interface:
            try:
                volume = self._volume_interface.GetMasterVolumeLevelScalar()
                return int(volume * 100)
            except Exception as e:
                logger.error(f"Failed to get volume: {e}")
        return 50  # Default

    def set_volume(self, level: int) -> bool:
        """
        Set volume level.

        Args:
            level: Volume level (0-100)

        Returns:
            True if successful
        """
        level = max(0, min(100, level))

        if self._pycaw_available and self._volume_interface:
            try:
                self._volume_interface.SetMasterVolumeLevelScalar(level / 100, None)
                logger.info(f"Volume set to {level}%")
                return True
            except Exception as e:
                logger.error(f"Failed to set volume: {e}")
                return False

        # Fallback: use nircmd if available
        try:
            subprocess.run(
                ["nircmd", "setsysvolume", str(int(level * 655.35))],
                capture_output=True,
            )
            return True
        except FileNotFoundError:
            logger.error("No volume control available")
            return False

    def mute(self) -> bool:
        """Mute system volume."""
        if self._pycaw_available and self._volume_interface:
            try:
                self._volume_interface.SetMute(1, None)
                logger.info("Volume muted")
                return True
            except Exception as e:
                logger.error(f"Failed to mute: {e}")
                return False
        return False

    def unmute(self) -> bool:
        """Unmute system volume."""
        if self._pycaw_available and self._volume_interface:
            try:
                self._volume_interface.SetMute(0, None)
                logger.info("Volume unmuted")
                return True
            except Exception as e:
                logger.error(f"Failed to unmute: {e}")
                return False
        return False

    def is_muted(self) -> bool:
        """Check if volume is muted."""
        if self._pycaw_available and self._volume_interface:
            try:
                return bool(self._volume_interface.GetMute())
            except Exception:
                pass
        return False

    def volume_up(self, amount: int = 10) -> int:
        """
        Increase volume.

        Args:
            amount: Amount to increase (0-100)

        Returns:
            New volume level
        """
        current = self.get_volume()
        new_level = min(100, current + amount)
        self.set_volume(new_level)
        return new_level

    def volume_down(self, amount: int = 10) -> int:
        """
        Decrease volume.

        Args:
            amount: Amount to decrease (0-100)

        Returns:
            New volume level
        """
        current = self.get_volume()
        new_level = max(0, current - amount)
        self.set_volume(new_level)
        return new_level

    def shutdown(self, delay: int = 60) -> Tuple[bool, str]:
        """
        Shutdown the computer.

        Args:
            delay: Delay in seconds before shutdown

        Returns:
            Tuple of (success, message)
        """
        try:
            subprocess.run(["shutdown", "/s", "/t", str(delay)], check=True)
            logger.info(f"Shutdown scheduled in {delay} seconds")
            return True, f"Computer will shut down in {delay} seconds."
        except Exception as e:
            logger.error(f"Failed to schedule shutdown: {e}")
            return False, "Failed to schedule shutdown."

    def restart(self, delay: int = 60) -> Tuple[bool, str]:
        """
        Restart the computer.

        Args:
            delay: Delay in seconds before restart

        Returns:
            Tuple of (success, message)
        """
        try:
            subprocess.run(["shutdown", "/r", "/t", str(delay)], check=True)
            logger.info(f"Restart scheduled in {delay} seconds")
            return True, f"Computer will restart in {delay} seconds."
        except Exception as e:
            logger.error(f"Failed to schedule restart: {e}")
            return False, "Failed to schedule restart."

    def cancel_shutdown(self) -> Tuple[bool, str]:
        """Cancel pending shutdown or restart."""
        try:
            subprocess.run(["shutdown", "/a"], check=True)
            logger.info("Shutdown cancelled")
            return True, "Shutdown cancelled."
        except Exception as e:
            logger.error(f"Failed to cancel shutdown: {e}")
            return False, "No shutdown to cancel."

    def sleep(self) -> Tuple[bool, str]:
        """Put computer to sleep."""
        try:
            subprocess.run(
                ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"],
                check=True,
            )
            logger.info("Computer going to sleep")
            return True, "Going to sleep..."
        except Exception as e:
            logger.error(f"Failed to sleep: {e}")
            return False, "Failed to put computer to sleep."

    def lock(self) -> Tuple[bool, str]:
        """Lock the screen."""
        try:
            subprocess.run(
                ["rundll32.exe", "user32.dll,LockWorkStation"],
                check=True,
            )
            logger.info("Screen locked")
            return True, "Locking screen..."
        except Exception as e:
            logger.error(f"Failed to lock: {e}")
            return False, "Failed to lock screen."

    def get_battery_status(self) -> dict:
        """
        Get battery status (for laptops).

        Returns:
            Dict with battery info
        """
        try:
            import psutil

            battery = psutil.sensors_battery()
            if battery:
                return {
                    "percent": battery.percent,
                    "charging": battery.power_plugged,
                    "time_left": battery.secsleft if battery.secsleft > 0 else None,
                }
        except ImportError:
            pass
        except Exception as e:
            logger.error(f"Failed to get battery status: {e}")

        return {"percent": None, "charging": None, "time_left": None}
