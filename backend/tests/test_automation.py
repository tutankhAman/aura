import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import pytest
import pywinauto
from ..agents.automation.automation import AutomationAgent
from ..agents.automation.app_path_resolver import AppPathResolver
from ..mcp.mcp import MCP

@pytest.mark.asyncio
class TestAutomationAgent(unittest.TestCase):
    async def asyncSetUp(self):
        # First patch the critical pywinauto modules
        self.find_windows_patcher = patch('pywinauto.findwindows.find_windows')
        self.mock_find_windows = self.find_windows_patcher.start()
        
        self.application_patcher = patch('pywinauto.application.Application')
        self.mock_application = self.application_patcher.start()
        
        # Create mock MCP
        self.mock_mcp = AsyncMock(spec=MCP)
        
        # Create the agent after patching
        self.agent = AutomationAgent(mcp=self.mock_mcp)
        
        # Then patch the agent's logger to avoid actual logging
        self.logger_patcher = patch.object(self.agent, 'logger')
        self.mock_logger = self.logger_patcher.start()
        
        # Mock the AppPathResolver
        self.path_resolver_patcher = patch.object(
            self.agent, 'app_resolver', autospec=AppPathResolver
        )
        self.mock_resolver = self.path_resolver_patcher.start()
        
        # Initialize the agent
        await self.agent.initialize()

    async def asyncTearDown(self):
        self.path_resolver_patcher.stop()
        self.logger_patcher.stop()
        self.application_patcher.stop()
        self.find_windows_patcher.stop()

    @pytest.fixture(autouse=True)
    async def setup(self):
        await self.asyncSetUp()
        yield
        await self.asyncTearDown()

    @patch('os.path.exists')
    async def test_open_application_with_path(self, mock_exists):
        # Test opening application with explicit path
        mock_exists.return_value = True
        
        # Setup the mock app instance
        mock_app_instance = MagicMock()
        self.mock_application.return_value = mock_app_instance
        mock_app_instance.start.return_value = mock_app_instance
        
        # Call the method under test
        result = await self.agent.open_application("TestApp", "C:\\Program Files\\TestApp\\app.exe")
        
        # Verify results
        self.assertTrue(result)
        self.mock_application.assert_called_once_with(backend="uia")
        mock_app_instance.start.assert_called_once_with("C:\\Program Files\\TestApp\\app.exe")
        self.assertEqual(self.agent.running_apps["TestApp"], mock_app_instance)
        
        # Verify MCP updates
        self.mock_mcp.add_command.assert_called_once()
        self.mock_mcp.update_agent_state.assert_called_once()

    @patch('os.path.exists')
    async def test_open_application_with_name(self, mock_exists):
        # Test opening application by name
        mock_exists.return_value = True
        
        # Setup the mock app instance
        mock_app_instance = MagicMock()
        self.mock_application.return_value = mock_app_instance
        mock_app_instance.start.return_value = mock_app_instance
        
        # Setup resolver
        self.mock_resolver.get_app_path.return_value = "C:\\Program Files\\TestApp\\app.exe"
        
        # Call the method under test
        result = await self.agent.open_application("TestApp")
        
        # Verify results
        self.assertTrue(result)
        self.mock_resolver.get_app_path.assert_called_once_with("TestApp")
        self.mock_application.assert_called_once_with(backend="uia")
        mock_app_instance.start.assert_called_once_with("C:\\Program Files\\TestApp\\app.exe")
        
        # Verify MCP updates
        self.mock_mcp.add_command.assert_called_once()
        self.mock_mcp.update_agent_state.assert_called_once()

    @patch('os.startfile')
    @patch('os.path.exists')
    async def test_open_file_default_app(self, mock_exists, mock_startfile):
        # Test opening file with default application
        mock_exists.return_value = True

        result = await self.agent.open_file("C:\\path\\to\\file.txt")
        
        self.assertTrue(result)
        mock_startfile.assert_called_once_with("C:\\path\\to\\file.txt")
        
        # Verify MCP updates
        self.mock_mcp.add_command.assert_called_once()

    @patch('os.path.exists')
    async def test_open_file_specific_app(self, mock_exists):
        # Test opening file with specific application
        mock_exists.return_value = True
        
        # Setup the mock app instance
        mock_app_instance = MagicMock()
        self.mock_application.return_value = mock_app_instance
        mock_app_instance.start.return_value = mock_app_instance
        
        # Setup resolver
        self.mock_resolver.get_app_path.return_value = "C:\\Program Files\\TestApp\\app.exe"
        
        # Call the method under test
        result = await self.agent.open_file("C:\\path\\to\\file.txt", "TestApp")
        
        # Verify results
        self.assertTrue(result)
        self.mock_resolver.get_app_path.assert_called_once_with("TestApp")
        self.mock_application.assert_called_once_with(backend="uia")
        mock_app_instance.start.assert_called_once_with(
            '"C:\\Program Files\\TestApp\\app.exe" "C:\\path\\to\\file.txt"'
        )
        
        # Verify MCP updates
        self.mock_mcp.add_command.assert_called_once()

    @patch.object(AutomationAgent, 'open_application')
    @patch.object(AutomationAgent, 'open_file')
    async def test_open_workspace(self, mock_open_file, mock_open_app):
        # Test opening a workspace with multiple apps and files
        workspace = {
            "apps": [
                {"name": "App1", "path": "C:\\App1\\app.exe"},
                {"name": "App2"}
            ],
            "files": [
                {"path": "C:\\file1.txt", "app": "App3"},
                {"path": "C:\\file2.txt"}
            ]
        }
        mock_open_app.return_value = True
        mock_open_file.return_value = True

        result = await self.agent.open_workspace(workspace)
        
        self.assertTrue(result)
        self.assertEqual(mock_open_app.call_count, 2)
        self.assertEqual(mock_open_file.call_count, 2)
        
        # Verify MCP updates
        self.mock_mcp.add_command.assert_called_once()
        self.mock_mcp.update_agent_state.assert_called_once()

    async def test_close_application(self):
        # Test closing a running application
        mock_app = MagicMock()
        self.agent.running_apps["TestApp"] = mock_app

        result = await self.agent.close_application("TestApp")
        
        self.assertTrue(result)
        mock_app.kill.assert_called_once()
        self.assertNotIn("TestApp", self.agent.running_apps)
        
        # Verify MCP updates
        self.mock_mcp.add_command.assert_called_once()
        self.mock_mcp.update_agent_state.assert_called_once()

    async def test_get_window_by_title(self):
        # Test finding window by title
        mock_window = MagicMock()
        self.mock_find_windows.return_value = [mock_window]
        
        # Call the method under test
        result = await self.agent.get_window_by_title("Test Window")
        
        # Verify results
        self.assertEqual(result, mock_window)
        self.mock_find_windows.assert_called_once_with(title="Test Window")

    @patch.object(AutomationAgent, 'get_window_by_title')
    async def test_wait_for_window(self, mock_get_window):
        # Test waiting for window to appear
        mock_window = MagicMock()
        mock_get_window.side_effect = [None, None, mock_window]

        result = await self.agent.wait_for_window("Test Window", timeout=2)
        
        self.assertEqual(result, mock_window)
        self.assertEqual(mock_get_window.call_count, 3)

    @patch('os.path.exists')
    async def test_open_figma(self, mock_exists):
        """Test opening Figma application using both name and path."""
        # Test opening Figma by name
        mock_exists.return_value = True
        
        # Setup the mock app instance
        mock_app_instance = MagicMock()
        self.mock_application.return_value = mock_app_instance
        mock_app_instance.start.return_value = mock_app_instance
        
        # Setup resolver to return Figma path
        expected_figma_path = "C:\\Users\\Arsh\\AppData\\Local\\Figma\\Figma.exe"
        self.mock_resolver.get_app_path.return_value = expected_figma_path
        
        # Test opening by name
        result = await self.agent.open_application("Figma")
        self.assertTrue(result)
        self.mock_resolver.get_app_path.assert_called_once_with("Figma")
        self.mock_application.assert_called_once_with(backend="uia")
        mock_app_instance.start.assert_called_once_with(expected_figma_path)
        self.assertEqual(self.agent.running_apps["Figma"], mock_app_instance)
        
        # Verify MCP updates
        self.mock_mcp.add_command.assert_called_once()
        self.mock_mcp.update_agent_state.assert_called_once()
        
        # Reset mocks for path test
        self.mock_application.reset_mock()
        mock_app_instance.start.reset_mock()
        self.mock_mcp.reset_mock()
        
        # Test opening with explicit path
        result = await self.agent.open_application("Figma", expected_figma_path)
        self.assertTrue(result)
        self.mock_application.assert_called_once_with(backend="uia")
        mock_app_instance.start.assert_called_once_with(expected_figma_path)
        
        # Verify MCP updates again
        self.mock_mcp.add_command.assert_called_once()
        self.mock_mcp.update_agent_state.assert_called_once()
        
        # Verify window finding
        mock_window = MagicMock()
        self.mock_find_windows.return_value = [mock_window]
        window = await self.agent.get_window_by_title("Figma")
        self.assertEqual(window, mock_window)
        self.mock_find_windows.assert_called_once_with(title="Figma")

if __name__ == '__main__':
    unittest.main()