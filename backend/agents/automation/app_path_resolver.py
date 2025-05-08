import os
from typing import Optional, List
import winreg
import logging
from pathlib import Path

class AppPathResolver:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.start_menu_paths = [
            os.path.join(os.environ['PROGRAMDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs'),
            os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs')
        ]
        
    def _search_in_directory(self, directory: str, app_name: str) -> Optional[str]:
        """
        Recursively search for a .lnk file in a directory and its subdirectories
        """
        try:
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith('.lnk') and app_name.lower() in file.lower():
                        return os.path.join(root, file)
        except Exception as e:
            self.logger.error(f"Error searching in directory {directory}: {str(e)}")
        return None

    def _get_target_path_from_lnk(self, lnk_path: str) -> Optional[str]:
        """
        Extract the target path from a .lnk file
        """
        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(lnk_path)
            return shortcut.Targetpath
        except Exception as e:
            self.logger.error(f"Error getting target path from {lnk_path}: {str(e)}")
            return None

    def _get_app_path_from_registry(self, app_name: str) -> Optional[str]:
        """
        Try to get the application path from Windows Registry
        """
        try:
            # Common registry locations for application paths
            registry_paths = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths",
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
            ]
            
            for reg_path in registry_paths:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                    try:
                        i = 0
                        while True:
                            subkey_name = winreg.EnumKey(key, i)
                            if app_name.lower() in subkey_name.lower():
                                with winreg.OpenKey(key, subkey_name) as subkey:
                                    try:
                                        path = winreg.QueryValue(subkey, "Path")
                                        if path:
                                            return path
                                    except WindowsError:
                                        pass
                            i += 1
                    except WindowsError:
                        break
        except Exception as e:
            self.logger.error(f"Error searching registry for {app_name}: {str(e)}")
        return None

    def get_app_path(self, app_name: str) -> Optional[str]:
        """
        Get the full path to an application executable
        Args:
            app_name: Name of the application (e.g., "Cursor", "Chrome", etc.)
        Returns:
            Optional[str]: Full path to the application executable if found, None otherwise
        """
        # First try to find in Start Menu
        for start_menu_path in self.start_menu_paths:
            lnk_path = self._search_in_directory(start_menu_path, app_name)
            if lnk_path:
                target_path = self._get_target_path_from_lnk(lnk_path)
                if target_path and os.path.exists(target_path):
                    return target_path

        # If not found in Start Menu, try registry
        registry_path = self._get_app_path_from_registry(app_name)
        if registry_path and os.path.exists(registry_path):
            return registry_path

        # Common application paths to check
        common_paths = [
            os.path.join(os.environ['PROGRAMFILES'], app_name),
            os.path.join(os.environ['PROGRAMFILES(X86)'], app_name),
            os.path.join(os.environ['LOCALAPPDATA'], 'Programs', app_name)
        ]

        for path in common_paths:
            if os.path.exists(path):
                # Look for .exe files in the directory
                for root, _, files in os.walk(path):
                    for file in files:
                        if file.lower().endswith('.exe'):
                            return os.path.join(root, file)

        self.logger.warning(f"Could not find path for application: {app_name}")
        return None

    def get_common_app_paths(self) -> List[str]:
        """
        Get a list of common application paths
        Returns:
            List[str]: List of common application paths
        """
        return [
            os.path.join(os.environ['PROGRAMFILES']),
            os.path.join(os.environ['PROGRAMFILES(X86)']),
            os.path.join(os.environ['LOCALAPPDATA'], 'Programs'),
            *self.start_menu_paths
        ] 