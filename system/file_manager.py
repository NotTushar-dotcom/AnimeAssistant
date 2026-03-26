"""
Aara File Manager
File operations and folder navigation.
"""

import os
import logging
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class FileManager:
    """Manages file operations and folder navigation."""

    def __init__(self):
        """Initialize file manager."""
        self._user_home = Path.home()

    def open_folder(self, path: str) -> Tuple[bool, str]:
        """
        Open a folder in File Explorer.

        Args:
            path: Folder path

        Returns:
            Tuple of (success, message)
        """
        folder_path = Path(path)

        # Expand common shortcuts
        if str(folder_path).lower() in ["downloads", "download"]:
            folder_path = self._user_home / "Downloads"
        elif str(folder_path).lower() in ["documents", "docs"]:
            folder_path = self._user_home / "Documents"
        elif str(folder_path).lower() == "desktop":
            folder_path = self._user_home / "Desktop"
        elif str(folder_path).lower() in ["pictures", "photos"]:
            folder_path = self._user_home / "Pictures"
        elif str(folder_path).lower() == "music":
            folder_path = self._user_home / "Music"
        elif str(folder_path).lower() == "videos":
            folder_path = self._user_home / "Videos"
        elif str(folder_path).lower() == "home":
            folder_path = self._user_home

        if not folder_path.exists():
            return False, f"Folder not found: {path}"

        if not folder_path.is_dir():
            return False, f"Not a folder: {path}"

        try:
            os.startfile(str(folder_path))
            logger.info(f"Opened folder: {folder_path}")
            return True, f"Opening {folder_path.name}"
        except Exception as e:
            logger.error(f"Failed to open folder: {e}")
            return False, f"Failed to open folder"

    def open_file(self, path: str) -> Tuple[bool, str]:
        """
        Open a file with its default application.

        Args:
            path: File path

        Returns:
            Tuple of (success, message)
        """
        file_path = Path(path)

        if not file_path.exists():
            return False, f"File not found: {path}"

        if not file_path.is_file():
            return False, f"Not a file: {path}"

        try:
            os.startfile(str(file_path))
            logger.info(f"Opened file: {file_path}")
            return True, f"Opening {file_path.name}"
        except Exception as e:
            logger.error(f"Failed to open file: {e}")
            return False, f"Failed to open file"

    def search_files(
        self,
        query: str,
        directory: Optional[str] = None,
        extensions: Optional[List[str]] = None,
        max_results: int = 10,
    ) -> List[dict]:
        """
        Search for files by name.

        Args:
            query: Search query
            directory: Directory to search in (default: user home)
            extensions: File extensions to filter
            max_results: Maximum results to return

        Returns:
            List of file info dicts
        """
        search_dir = Path(directory) if directory else self._user_home

        if not search_dir.exists():
            return []

        results = []
        query_lower = query.lower()

        try:
            for root, dirs, files in os.walk(search_dir):
                # Skip hidden and system directories
                dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["node_modules", "__pycache__"]]

                for file in files:
                    if query_lower in file.lower():
                        if extensions:
                            if not any(file.lower().endswith(ext.lower()) for ext in extensions):
                                continue

                        file_path = Path(root) / file
                        try:
                            stat = file_path.stat()
                            results.append({
                                "name": file,
                                "path": str(file_path),
                                "size": stat.st_size,
                                "modified": datetime.fromtimestamp(stat.st_mtime),
                            })
                        except Exception:
                            pass

                        if len(results) >= max_results:
                            return results

        except Exception as e:
            logger.error(f"Search error: {e}")

        return results

    def get_recent_files(self, limit: int = 10) -> List[dict]:
        """
        Get recently modified files.

        Args:
            limit: Maximum files to return

        Returns:
            List of file info dicts
        """
        recent = []

        # Search in common locations
        search_dirs = [
            self._user_home / "Downloads",
            self._user_home / "Documents",
            self._user_home / "Desktop",
        ]

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            try:
                for file_path in search_dir.iterdir():
                    if file_path.is_file() and not file_path.name.startswith("."):
                        try:
                            stat = file_path.stat()
                            recent.append({
                                "name": file_path.name,
                                "path": str(file_path),
                                "size": stat.st_size,
                                "modified": datetime.fromtimestamp(stat.st_mtime),
                            })
                        except Exception:
                            pass
            except Exception:
                pass

        # Sort by modification time (newest first)
        recent.sort(key=lambda x: x["modified"], reverse=True)
        return recent[:limit]

    def create_folder(self, path: str) -> Tuple[bool, str]:
        """
        Create a new folder.

        Args:
            path: Folder path

        Returns:
            Tuple of (success, message)
        """
        folder_path = Path(path)

        try:
            folder_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created folder: {folder_path}")
            return True, f"Created folder: {folder_path.name}"
        except Exception as e:
            logger.error(f"Failed to create folder: {e}")
            return False, f"Failed to create folder"

    def delete_file(self, path: str) -> Tuple[bool, str]:
        """
        Delete a file (move to recycle bin).

        Args:
            path: File path

        Returns:
            Tuple of (success, message)
        """
        file_path = Path(path)

        if not file_path.exists():
            return False, "File not found"

        try:
            # Use send2trash for recycle bin
            try:
                from send2trash import send2trash
                send2trash(str(file_path))
            except ImportError:
                # Fallback to direct delete
                if file_path.is_file():
                    file_path.unlink()
                else:
                    import shutil
                    shutil.rmtree(file_path)

            logger.info(f"Deleted: {file_path}")
            return True, f"Deleted {file_path.name}"
        except Exception as e:
            logger.error(f"Failed to delete: {e}")
            return False, f"Failed to delete file"

    def get_folder_size(self, path: str) -> int:
        """
        Get total size of a folder.

        Args:
            path: Folder path

        Returns:
            Size in bytes
        """
        folder_path = Path(path)
        if not folder_path.exists() or not folder_path.is_dir():
            return 0

        total = 0
        try:
            for file_path in folder_path.rglob("*"):
                if file_path.is_file():
                    total += file_path.stat().st_size
        except Exception:
            pass

        return total

    def format_size(self, size_bytes: int) -> str:
        """Format file size for display."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} PB"
