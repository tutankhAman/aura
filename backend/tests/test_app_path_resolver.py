import os
import unittest
from unittest.mock import patch, MagicMock
from ..agents.automation.app_path_resolver import AppPathResolver

class TestAppPathResolver(unittest.TestCase):
    def setUp(self):
        self.resolver = AppPathResolver()
        
    @patch('os.walk')
    @patch('os.path.exists')
    def test_search_in_directory(self, mock_exists, mock_walk):
        # Mock directory structure
        mock_walk.return_value = [
            ('C:\\StartMenu', ['SubDir'], []),
            ('C:\\StartMenu\\SubDir', [], ['TestApp.lnk'])
        ]
        mock_exists.return_value = True

        result = self.resolver._search_in_directory('C:\\StartMenu', 'TestApp')
        self.assertEqual(result, 'C:\\StartMenu\\SubDir\\TestApp.lnk')

    @patch('win32com.client.Dispatch')
    def test_get_target_path_from_lnk(self, mock_dispatch):
        # Mock shortcut object
        mock_shortcut = MagicMock()
        mock_shortcut.Targetpath = 'C:\\Program Files\\TestApp\\app.exe'
        mock_shell = MagicMock()
        mock_shell.CreateShortCut.return_value = mock_shortcut
        mock_dispatch.return_value = mock_shell

        result = self.resolver._get_target_path_from_lnk('dummy.lnk')
        self.assertEqual(result, 'C:\\Program Files\\TestApp\\app.exe')

    @patch('winreg.OpenKey')
    @patch('winreg.EnumKey')
    @patch('winreg.QueryValue')
    def test_get_app_path_from_registry(self, mock_query, mock_enum, mock_open):
        # Mock registry structure
        mock_enum.side_effect = ['TestApp', 'OtherApp']
        mock_query.return_value = 'C:\\Program Files\\TestApp'
        
        result = self.resolver._get_app_path_from_registry('TestApp')
        self.assertEqual(result, 'C:\\Program Files\\TestApp')

    @patch.object(AppPathResolver, '_search_in_directory')
    @patch.object(AppPathResolver, '_get_target_path_from_lnk')
    @patch('os.path.exists')
    def test_get_app_path_start_menu(self, mock_exists, mock_get_target, mock_search):
        # Test finding app in Start Menu
        mock_search.return_value = 'C:\\StartMenu\\TestApp.lnk'
        mock_get_target.return_value = 'C:\\Program Files\\TestApp\\app.exe'
        mock_exists.return_value = True

        result = self.resolver.get_app_path('TestApp')
        self.assertEqual(result, 'C:\\Program Files\\TestApp\\app.exe')

    @patch.object(AppPathResolver, '_search_in_directory')
    @patch.object(AppPathResolver, '_get_app_path_from_registry')
    @patch('os.path.exists')
    def test_get_app_path_registry(self, mock_exists, mock_registry, mock_search):
        # Test finding app in registry when not in Start Menu
        mock_search.return_value = None
        mock_registry.return_value = 'C:\\Program Files\\TestApp\\app.exe'
        mock_exists.return_value = True

        result = self.resolver.get_app_path('TestApp')
        self.assertEqual(result, 'C:\\Program Files\\TestApp\\app.exe')

    @patch.object(AppPathResolver, '_search_in_directory')
    @patch.object(AppPathResolver, '_get_app_path_from_registry')
    @patch('os.walk')
    @patch('os.path.exists')
    def test_get_app_path_common_paths(self, mock_exists, mock_walk, mock_registry, mock_search):
        # Test finding app in common paths when not in Start Menu or registry
        mock_search.return_value = None
        mock_registry.return_value = None
        mock_exists.side_effect = [False, False, True]  # Only last common path exists
        mock_walk.return_value = [
            (os.path.join(os.environ['LOCALAPPDATA'], 'Programs', 'TestApp'), [], ['app.exe'])
        ]

        result = self.resolver.get_app_path('TestApp')
        self.assertEqual(result, os.path.join(os.environ['LOCALAPPDATA'], 'Programs', 'TestApp', 'app.exe'))

    def test_get_common_app_paths(self):
        paths = self.resolver.get_common_app_paths()
        expected_paths = [
            os.path.join(os.environ['PROGRAMFILES']),
            os.path.join(os.environ['PROGRAMFILES(X86)']),
            os.path.join(os.environ['LOCALAPPDATA'], 'Programs'),
            os.path.join(os.environ['PROGRAMDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs'),
            os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs')
        ]
        self.assertEqual(paths, expected_paths)

    def test_find_postman_path(self):
        """
        Temporary test to find and print the Postman application path.
        This test is for debugging purposes only.
        """
        postman_path = self.resolver.get_app_path("Postman")
        print("\nPostman application path:", postman_path)
        
        # Also try with different variations of the name
        postman_path_alt = self.resolver.get_app_path("Postman API Platform")
        print("Postman API Platform path:", postman_path_alt)
        
        # Print all common paths for debugging
        print("\nAll common paths:")
        for path in self.resolver.get_common_app_paths():
            print(f"- {path}")

if __name__ == '__main__':
    unittest.main()