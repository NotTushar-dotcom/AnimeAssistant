"""
Aara Application Launcher
Launch and close applications on Windows.
"""

import os
import logging
import subprocess
from pathlib import Path
from typing import Tuple, Optional, List

import yaml

logger = logging.getLogger(__name__)


class AppLauncher:
    """Launches and manages applications."""

    def __init__(self):
        """Initialize app launcher."""
        self._registry = self._load_registry()
        self._running_processes = {}

    def _load_registry(self) -> dict:
        """Load application registry from YAML."""
        registry_path = Path("config/app_registry.yaml")
        if registry_path.exists():
            try:
                with open(registry_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                    return data.get("applications", {})
            except Exception as e:
                logger.error(f"Failed to load app registry: {e}")
        return {}

    def _expand_path(self, path: str) -> str:
        """Expand environment variables in path."""
        # Replace %USERNAME% and similar
        path = path.replace("%USERNAME%", os.environ.get("USERNAME", ""))
        path = os.path.expandvars(path)
        return path

    def _find_app(self, name: str) -> Optional[dict]:
        """
        Find application by name or alias.

        Args:
            name: Application name or alias

        Returns:
            Application info dict or None
        """
        name_lower = name.lower().strip()

        for app_id, app_info in self._registry.items():
            # Check exact match
            if app_id.lower() == name_lower:
                return {"id": app_id, **app_info}

            # Check app name
            if app_info.get("name", "").lower() == name_lower:
                return {"id": app_id, **app_info}

            # Check aliases
            aliases = [a.lower() for a in app_info.get("aliases", [])]
            if name_lower in aliases:
                return {"id": app_id, **app_info}

        return None

    def launch(self, app_name: str) -> Tuple[bool, str]:
        """
        Launch an application.

        Args:
            app_name: Name or alias of the application

        Returns:
            Tuple of (success, message)
        """
        app_info = self._find_app(app_name)

        if not app_info:
            return False, f"I couldn't find an application called '{app_name}'."

        app_display_name = app_info.get("name", app_name)
        path = self._expand_path(app_info.get("path", ""))

        if not path:
            return False, f"No path configured for {app_display_name}."

        try:
            # Handle special paths (like ms-settings:)
            if path.startswith("ms-"):
                os.startfile(path)
                return True, f"Opening {app_display_name}!"

            # Check if path exists (for full paths)
            if not Path(path).exists() and not path.endswith(".exe"):
                # Try system PATH
                pass

            # Build command
            args = app_info.get("args", [])
            if args:
                process = subprocess.Popen([path] + args, shell=True)
            else:
                process = subprocess.Popen(path, shell=True)

            self._running_processes[app_info["id"]] = process

            logger.info(f"Launched {app_display_name} (pid: {process.pid})")
            return True, f"Launching {app_display_name}!"

        except FileNotFoundError:
            logger.error(f"Application not found: {path}")
            return False, f"Couldn't find {app_display_name} at the configured path."
        except Exception as e:
            logger.error(f"Failed to launch {app_display_name}: {e}")
            return False, f"Failed to launch {app_display_name}: {str(e)}"

    def close(self, app_name: str) -> Tuple[bool, str]:
        """
        Close an application.

        Args:
            app_name: Name or alias of the application

        Returns:
            Tuple of (success, message)
        """
        app_info = self._find_app(app_name)
        app_display_name = app_info.get("name", app_name) if app_info else app_name

        try:
            # Try to find the process
            process_name = self._get_process_name(app_name, app_info)

            if process_name:
                # Use taskkill on Windows
                result = subprocess.run(
                    ["taskkill", "/IM", process_name, "/F"],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    logger.info(f"Closed {app_display_name}")
                    return True, f"Closed {app_display_name}!"
                else:
                    # Process might not be running
                    if "not found" in result.stderr.lower():
                        return False, f"{app_display_name} doesn't seem to be running."
                    return False, f"Couldn't close {app_display_name}."

            return False, f"I don't know how to close {app_display_name}."

        except Exception as e:
            logger.error(f"Failed to close {app_display_name}: {e}")
            return False, f"Failed to close {app_display_name}."

    def _get_process_name(self, app_name: str, app_info: Optional[dict]) -> Optional[str]:
        """Get process name for an application."""
        if app_info:
            path = app_info.get("path", "")
            if path.endswith(".exe"):
                return Path(path).name

            # Common mappings
            process_map = {
                "chrome": "chrome.exe",
                "firefox": "firefox.exe",
                "edge": "msedge.exe",
                "spotify": "Spotify.exe",
                "discord": "Discord.exe",
                "slack": "slack.exe",
                "vscode": "Code.exe",
                "notepad": "notepad.exe",
                "vlc": "vlc.exe",
            }

            app_id = app_info.get("id", "").lower()
            if app_id in process_map:
                return process_map[app_id]

        # Try direct name
        return f"{app_name.lower()}.exe"

    def is_running(self, app_name: str) -> bool:
        """
        Check if an application is running.

        Args:
            app_name: Application name

        Returns:
            True if running
        """
        app_info = self._find_app(app_name)
        process_name = self._get_process_name(app_name, app_info)

        if not process_name:
            return False

        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"IMAGENAME eq {process_name}"],
                capture_output=True,
                text=True,
            )
            return process_name.lower() in result.stdout.lower()
        except Exception:
            return False

    def get_running_apps(self) -> List[str]:
        """
        Get list of running applications from registry.

        Returns:
            List of running app names
        """
        running = []
        for app_id, app_info in self._registry.items():
            if self.is_running(app_id):
                running.append(app_info.get("name", app_id))
        return running

    def get_available_apps(self) -> List[str]:
        """
        Get list of available applications.

        Returns:
            List of application names
        """
        return [info.get("name", app_id) for app_id, info in self._registry.items()]
