import os
import time
from typing import List, Dict, Union
from pywinauto.application import Application
from pywinauto.findwindows import find_windows
from pywinauto.controls.hwndwrapper import HwndWrapper
import logging
from .app_path_resolver import AppPathResolver

class AutomationAgent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.running_apps: Dict[str, Application] = {}
        self.app_resolver = AppPathResolver()
        
    def open_application(self, app_name: str, app_path: str = None) -> bool:
        """
        Opens an application using its name or path
        Args:
            app_name: Name of the application (e.g., "Cursor", "Chrome")
            app_path: Optional explicit path to the application executable
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # If no explicit path is provided, try to find it
            if not app_path:
                app_path = self.app_resolver.get_app_path(app_name)
                if not app_path:
                    self.logger.error(f"Could not find path for application: {app_name}")
                    return False
            
            if not os.path.exists(app_path):
                self.logger.error(f"Application path does not exist: {app_path}")
                return False
                
            app = Application(backend="uia").start(app_path)
            self.running_apps[app_name] = app
            return True
        except Exception as e:
            self.logger.error(f"Failed to open application {app_name}: {str(e)}")
            return False

    def open_file(self, file_path: str, app_name: str = None) -> bool:
        """
        Opens a file using the default application or specified application
        Args:
            file_path: Path to the file to open
            app_name: Optional name of the application to use
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                self.logger.error(f"File does not exist: {file_path}")
                return False

            if app_name:
                app_path = self.app_resolver.get_app_path(app_name)
                if not app_path:
                    self.logger.error(f"Could not find path for application: {app_name}")
                    return False
                app = Application(backend="uia").start(f'"{app_path}" "{file_path}"')
            else:
                os.startfile(file_path)
            return True
        except Exception as e:
            self.logger.error(f"Failed to open file {file_path}: {str(e)}")
            return False

    def open_workspace(self, workspace_config: Dict[str, Union[str, List[str]]]) -> bool:
        """
        Opens multiple applications and files based on workspace configuration
        Args:
            workspace_config: Dictionary containing apps and files to open
                Format: {
                    "apps": [{"name": "app_name", "path": "optional_app_path"}, ...],
                    "files": [{"path": "file_path", "app": "optional_app_name"}, ...]
                }
        Returns:
            bool: True if all operations successful, False otherwise
        """
        try:
            success = True
            
            # Open applications
            if "apps" in workspace_config:
                for app_config in workspace_config["apps"]:
                    if not self.open_application(
                        app_config["name"],
                        app_config.get("path")
                    ):
                        success = False

            # Open files
            if "files" in workspace_config:
                for file_config in workspace_config["files"]:
                    if not self.open_file(
                        file_config["path"],
                        file_config.get("app")
                    ):
                        success = False

            return success
        except Exception as e:
            self.logger.error(f"Failed to open workspace: {str(e)}")
            return False

    def close_application(self, app_name: str) -> bool:
        """
        Closes a running application by its name
        Args:
            app_name: Name of the application to close
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if app_name in self.running_apps:
                self.running_apps[app_name].kill()
                del self.running_apps[app_name]
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to close application {app_name}: {str(e)}")
            return False

    def get_window_by_title(self, title: str) -> Union[HwndWrapper, None]:
        """
        Finds a window by its title
        Args:
            title: Window title to search for
        Returns:
            HwndWrapper or None: Window handle if found, None otherwise
        """
        try:
            windows = find_windows(title=title)
            if windows:
                return windows[0]
            return None
        except Exception as e:
            self.logger.error(f"Failed to find window with title {title}: {str(e)}")
            return None

    def wait_for_window(self, title: str, timeout: int = 10) -> Union[HwndWrapper, None]:
        """
        Waits for a window to appear
        Args:
            title: Window title to wait for
            timeout: Maximum time to wait in seconds
        Returns:
            HwndWrapper or None: Window handle if found, None otherwise
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            window = self.get_window_by_title(title)
            if window:
                return window
            time.sleep(0.5)
        return None
