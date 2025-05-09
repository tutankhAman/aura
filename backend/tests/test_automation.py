import pytest
import logging
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from pywinauto.application import Application
from pywinauto.controls.hwndwrapper import HwndWrapper
from ..agents.automation.automation import AutomationAgent
from ..agents.automation.app_path_resolver import AppPathResolver
from ..mcp.mcp import MCP
import asyncio

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture
def mock_mcp():
    mcp = Mock(spec=MCP)
    mcp.initialize = AsyncMock()
    mcp.update_agent_state = AsyncMock()
    mcp.add_command = AsyncMock()
    mcp.log_error = AsyncMock()
    return mcp

@pytest.fixture
def mock_app_resolver():
    resolver = Mock(spec=AppPathResolver)
    resolver.get_app_path = Mock()
    return resolver

@pytest.fixture
def automation_agent(mock_mcp, mock_app_resolver):
    agent = AutomationAgent(mcp=mock_mcp)
    agent.app_resolver = mock_app_resolver
    return agent

@pytest.mark.asyncio
async def test_initialize(automation_agent, mock_mcp):
    await automation_agent.initialize()
    mock_mcp.initialize.assert_called_once()
    mock_mcp.update_agent_state.assert_called_once()

@pytest.mark.asyncio
async def test_open_application_with_resolver(automation_agent, mock_app_resolver):
    app_name = "Postman"
    resolved_path = "C:\\Program Files\\Postman\\Postman.exe"
    mock_app_resolver.get_app_path.return_value = resolved_path
    
    # Create a mock Application class that won't try to create real processes
    mock_app_class = MagicMock()
    mock_app_instance = MagicMock()
    mock_app_class.return_value = mock_app_instance
    
    with patch('os.path.exists', return_value=True), \
         patch('backend.agents.automation.automation.Application', mock_app_class):
        result = await automation_agent.open_application(app_name)
        
        assert result is True
        assert app_name in automation_agent.running_apps
        mock_app_resolver.get_app_path.assert_called_once_with(app_name)
        mock_app_instance.start.assert_called_once_with(resolved_path)

@pytest.mark.asyncio
async def test_open_application_with_explicit_path(automation_agent, mock_app_resolver):
    app_name = "Postman"
    explicit_path = "C:\\Custom\\Path\\Postman.exe"
    
    # Create a mock Application class that won't try to create real processes
    mock_app_class = MagicMock()
    mock_app_instance = MagicMock()
    mock_app_class.return_value = mock_app_instance
    
    with patch('os.path.exists', return_value=True), \
         patch('backend.agents.automation.automation.Application', mock_app_class):
        result = await automation_agent.open_application(app_name, explicit_path)
        
        assert result is True
        assert app_name in automation_agent.running_apps
        mock_app_resolver.get_app_path.assert_not_called()
        mock_app_instance.start.assert_called_once_with(explicit_path)

@pytest.mark.asyncio
async def test_open_application_resolver_failure(automation_agent, mock_app_resolver):
    app_name = "NonExistentApp"
    mock_app_resolver.get_app_path.return_value = None
    
    result = await automation_agent.open_application(app_name)
    
    assert result is False
    assert app_name not in automation_agent.running_apps
    mock_app_resolver.get_app_path.assert_called_once_with(app_name)

@pytest.mark.asyncio
async def test_open_file_with_app_resolver(automation_agent, mock_app_resolver):
    file_path = "test.txt"
    app_name = "Notepad"
    resolved_path = "C:\\Windows\\notepad.exe"
    mock_app_resolver.get_app_path.return_value = resolved_path
    
    # Create a mock Application class that won't try to create real processes
    mock_app_class = MagicMock()
    mock_app_instance = MagicMock()
    mock_app_class.return_value = mock_app_instance
    
    with patch('os.path.exists', return_value=True), \
         patch('backend.agents.automation.automation.Application', mock_app_class):
        result = await automation_agent.open_file(file_path, app_name)
        
        assert result is True
        mock_app_resolver.get_app_path.assert_called_once_with(app_name)
        mock_app_instance.start.assert_called_once_with(f'"{resolved_path}" "{file_path}"')

@pytest.mark.asyncio
async def test_open_file_without_app(automation_agent):
    file_path = "test.txt"
    
    with patch('os.path.exists', return_value=True), \
         patch('os.startfile') as mock_startfile:
        result = await automation_agent.open_file(file_path)
        
        assert result is True
        mock_startfile.assert_called_once_with(file_path)

@pytest.mark.asyncio
async def test_close_application(automation_agent):
    app_name = "TestApp"
    mock_app = Mock()
    automation_agent.running_apps[app_name] = mock_app
    
    result = await automation_agent.close_application(app_name)
    
    assert result is True
    assert app_name not in automation_agent.running_apps
    mock_app.kill.assert_called_once()

@pytest.mark.asyncio
async def test_get_window_by_title(automation_agent):
    title = "Test Window"
    mock_window = Mock(spec=HwndWrapper)
    
    with patch('backend.agents.automation.automation.find_windows', return_value=[mock_window]) as mock_find:
        result = await automation_agent.get_window_by_title(title)
        
        assert result == mock_window
        mock_find.assert_called_once_with(title=title)

@pytest.mark.asyncio
async def test_wait_for_window(automation_agent):
    title = "Test Window"
    mock_window = Mock(spec=HwndWrapper)
    
    with patch('backend.agents.automation.automation.find_windows', return_value=[mock_window]) as mock_find, \
         patch('time.sleep'):  # Mock sleep to speed up the test
        result = await automation_agent.wait_for_window(title, timeout=1)
        
        assert result == mock_window
        mock_find.assert_called_with(title=title)

