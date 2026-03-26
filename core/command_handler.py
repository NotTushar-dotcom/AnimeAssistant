"""
Aara Command Handler
Routes parsed intents to appropriate system modules.
"""

import os
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Callable, Any

import yaml

from core.intent_parser import Intent, IntentType, CommandType
from config.settings import SETTINGS

logger = logging.getLogger(__name__)


@dataclass
class CommandResult:
    """Result of command execution."""
    success: bool
    message: str
    data: Optional[Any] = None
    requires_confirmation: bool = False
    confirmation_callback: Optional[Callable] = None


class CommandHandler:
    """Routes and executes commands based on parsed intents."""

    def __init__(self):
        """Initialize command handler."""
        self.app_registry = self._load_app_registry()
        self.command_patterns = self._load_command_patterns()
        self._handlers = {}
        self._setup_handlers()

    def _load_app_registry(self) -> dict:
        """Load application registry from YAML."""
        registry_path = Path("config/app_registry.yaml")
        if registry_path.exists():
            try:
                with open(registry_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                logger.error(f"Failed to load app registry: {e}")
        return {"applications": {}, "system_commands": {}, "folders": {}, "websites": {}}

    def _load_command_patterns(self) -> dict:
        """Load command patterns from YAML."""
        patterns_path = Path("config/commands.yaml")
        if patterns_path.exists():
            try:
                with open(patterns_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                logger.error(f"Failed to load command patterns: {e}")
        return {}

    def _setup_handlers(self):
        """Set up command type handlers."""
        self._handlers = {
            CommandType.APP_LAUNCH: self._handle_app_launch,
            CommandType.APP_CLOSE: self._handle_app_close,
            CommandType.VOLUME: self._handle_volume,
            CommandType.MEDIA: self._handle_media,
            CommandType.SYSTEM: self._handle_system,
            CommandType.FILE: self._handle_file,
            CommandType.TIMER: self._handle_timer,
            CommandType.NOTES: self._handle_notes,
            CommandType.WEATHER: self._handle_weather,
            CommandType.SEARCH: self._handle_search,
            CommandType.CLIPBOARD: self._handle_clipboard,
        }

    def execute(self, intent: Intent) -> CommandResult:
        """
        Execute a command based on parsed intent.

        Args:
            intent: Parsed intent from user input

        Returns:
            CommandResult with execution status and message
        """
        if intent.type == IntentType.CHAT:
            return CommandResult(
                success=True,
                message="This is a chat message, no command to execute.",
            )

        if intent.command_type is None:
            return CommandResult(
                success=False,
                message="Could not determine command type.",
            )

        handler = self._handlers.get(intent.command_type)
        if handler is None:
            return CommandResult(
                success=False,
                message=f"No handler for command type: {intent.command_type.value}",
            )

        try:
            return handler(intent)
        except Exception as e:
            logger.error(f"Command execution error: {e}", exc_info=True)
            return CommandResult(
                success=False,
                message=f"Command failed: {str(e)}",
            )

    def _find_app(self, name: str) -> Optional[dict]:
        """Find application by name or alias."""
        name_lower = name.lower().strip()
        apps = self.app_registry.get("applications", {})

        for app_id, app_info in apps.items():
            if app_id.lower() == name_lower:
                return app_info
            aliases = [a.lower() for a in app_info.get("aliases", [])]
            if name_lower in aliases:
                return app_info

        return None

    def _handle_app_launch(self, intent: Intent) -> CommandResult:
        """Handle application launch command."""
        try:
            from system.app_launcher import AppLauncher
            launcher = AppLauncher()

            app_name = intent.target
            if not app_name:
                return CommandResult(success=False, message="No application specified.")

            success, message = launcher.launch(app_name)
            return CommandResult(success=success, message=message)
        except ImportError:
            # Fallback if system module not ready
            app_info = self._find_app(intent.target or "")
            if app_info:
                import subprocess
                path = app_info.get("path", "")
                path = path.replace("%USERNAME%", os.environ.get("USERNAME", ""))
                try:
                    subprocess.Popen(path, shell=True)
                    return CommandResult(
                        success=True,
                        message=f"Launching {app_info.get('name', intent.target)}!"
                    )
                except Exception as e:
                    return CommandResult(success=False, message=f"Failed to launch: {e}")
            return CommandResult(
                success=False,
                message=f"I couldn't find an application called '{intent.target}'."
            )

    def _handle_app_close(self, intent: Intent) -> CommandResult:
        """Handle application close command."""
        try:
            from system.app_launcher import AppLauncher
            launcher = AppLauncher()

            app_name = intent.target
            if not app_name:
                return CommandResult(success=False, message="No application specified.")

            success, message = launcher.close(app_name)
            return CommandResult(success=success, message=message)
        except ImportError:
            return CommandResult(
                success=False,
                message="App management not available yet."
            )

    def _handle_volume(self, intent: Intent) -> CommandResult:
        """Handle volume control commands."""
        try:
            from system.system_control import SystemControl
            control = SystemControl()

            action = intent.parameters.get("action")
            level = intent.parameters.get("level")

            if level is not None:
                control.set_volume(level)
                return CommandResult(success=True, message=f"Volume set to {level}%")
            elif action == "up":
                current = control.get_volume()
                new_level = min(100, current + 10)
                control.set_volume(new_level)
                return CommandResult(success=True, message=f"Volume increased to {new_level}%")
            elif action == "down":
                current = control.get_volume()
                new_level = max(0, current - 10)
                control.set_volume(new_level)
                return CommandResult(success=True, message=f"Volume decreased to {new_level}%")
            elif action == "mute":
                control.mute()
                return CommandResult(success=True, message="Volume muted")
            elif action == "unmute":
                control.unmute()
                return CommandResult(success=True, message="Volume unmuted")

            return CommandResult(success=False, message="Unknown volume action")
        except ImportError:
            return CommandResult(
                success=False,
                message="Volume control not available yet."
            )

    def _handle_media(self, intent: Intent) -> CommandResult:
        """Handle media control commands."""
        try:
            from system.media_control import MediaControl
            control = MediaControl()

            action = intent.parameters.get("action")

            if action == "play":
                control.play_pause()
                return CommandResult(success=True, message="Playing media")
            elif action == "pause":
                control.play_pause()
                return CommandResult(success=True, message="Media paused")
            elif action == "next":
                control.next_track()
                return CommandResult(success=True, message="Skipping to next track")
            elif action == "previous":
                control.previous_track()
                return CommandResult(success=True, message="Going to previous track")

            return CommandResult(success=False, message="Unknown media action")
        except ImportError:
            return CommandResult(
                success=False,
                message="Media control not available yet."
            )

    def _handle_system(self, intent: Intent) -> CommandResult:
        """Handle system commands (shutdown, restart, etc.)."""
        action = intent.parameters.get("action")

        # System commands require confirmation
        if action in ["shutdown", "restart"]:
            return CommandResult(
                success=True,
                message=f"Are you sure you want to {action}? This will close all applications.",
                requires_confirmation=True,
                confirmation_callback=lambda: self._execute_system_action(action),
            )

        try:
            from system.system_control import SystemControl
            control = SystemControl()

            if action == "sleep":
                control.sleep()
                return CommandResult(success=True, message="Going to sleep mode")
            elif action == "lock":
                control.lock()
                return CommandResult(success=True, message="Locking the screen")

            return CommandResult(success=False, message="Unknown system action")
        except ImportError:
            return CommandResult(
                success=False,
                message="System control not available yet."
            )

    def _execute_system_action(self, action: str) -> CommandResult:
        """Execute confirmed system action."""
        try:
            from system.system_control import SystemControl
            control = SystemControl()

            if action == "shutdown":
                control.shutdown()
                return CommandResult(success=True, message="Shutting down in 60 seconds...")
            elif action == "restart":
                control.restart()
                return CommandResult(success=True, message="Restarting in 60 seconds...")

            return CommandResult(success=False, message="Unknown action")
        except Exception as e:
            return CommandResult(success=False, message=f"Failed: {e}")

    def _handle_file(self, intent: Intent) -> CommandResult:
        """Handle file operations."""
        try:
            from system.file_manager import FileManager
            manager = FileManager()

            folder = intent.target
            if folder:
                folders = self.app_registry.get("folders", {})
                folder_info = folders.get(folder.lower())
                if folder_info:
                    path = folder_info.get("path", "").replace(
                        "%USERNAME%", os.environ.get("USERNAME", "")
                    )
                    manager.open_folder(path)
                    return CommandResult(success=True, message=f"Opening {folder} folder")

            return CommandResult(success=False, message="Folder not found")
        except ImportError:
            return CommandResult(success=False, message="File manager not available yet.")

    def _handle_timer(self, intent: Intent) -> CommandResult:
        """Handle timer commands."""
        try:
            from skills.timer_skill import TimerSkill
            skill = TimerSkill()

            duration = intent.parameters.get("duration")
            if duration:
                result = skill.execute({"duration": duration})
                return CommandResult(success=True, message=result)

            return CommandResult(success=False, message="No duration specified for timer")
        except ImportError:
            return CommandResult(success=False, message="Timer skill not available yet.")

    def _handle_notes(self, intent: Intent) -> CommandResult:
        """Handle note commands."""
        try:
            from skills.notes_skill import NotesSkill
            skill = NotesSkill()

            action = intent.parameters.get("action")
            content = intent.parameters.get("content")

            if action == "add" and content:
                result = skill.execute({"action": "add", "content": content})
                return CommandResult(success=True, message=result)
            elif action == "list":
                result = skill.execute({"action": "list"})
                return CommandResult(success=True, message=result)

            return CommandResult(success=False, message="Invalid notes command")
        except ImportError:
            return CommandResult(success=False, message="Notes skill not available yet.")

    def _handle_weather(self, intent: Intent) -> CommandResult:
        """Handle weather queries."""
        try:
            from skills.weather_skill import WeatherSkill
            skill = WeatherSkill()

            city = intent.target or SETTINGS.weather.default_city
            result = skill.execute({"city": city})
            return CommandResult(success=True, message=result)
        except ImportError:
            return CommandResult(success=False, message="Weather skill not available yet.")

    def _handle_search(self, intent: Intent) -> CommandResult:
        """Handle web search."""
        try:
            from skills.search_skill import SearchSkill
            skill = SearchSkill()

            query = intent.target
            if not query:
                return CommandResult(success=False, message="No search query provided")

            result = skill.execute({"query": query})
            return CommandResult(success=True, message=result)
        except ImportError:
            return CommandResult(success=False, message="Search skill not available yet.")

    def _handle_clipboard(self, intent: Intent) -> CommandResult:
        """Handle clipboard operations."""
        try:
            from system.clipboard_manager import ClipboardManager
            manager = ClipboardManager()

            action = intent.parameters.get("action")
            if action == "read":
                content = manager.paste()
                return CommandResult(
                    success=True,
                    message=f"Clipboard contains: {content[:100]}..." if len(content) > 100 else f"Clipboard contains: {content}"
                )

            return CommandResult(success=False, message="Invalid clipboard operation")
        except ImportError:
            return CommandResult(success=False, message="Clipboard manager not available yet.")
