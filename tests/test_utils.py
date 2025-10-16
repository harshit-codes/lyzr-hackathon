"""
Unit tests for app/utils.py
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils import (
    initialize_session_state,
    load_custom_css,
    validate_project_name,
    validate_entity_data,
    get_entity_by_id
)


class TestInitializeSessionState:
    """Test session state initialization"""

    def test_initialize_session_state_creates_all_keys(self):
        """Test that all required session state keys are created"""
        mock_st = MagicMock()
        # Create a proper mock for session_state that tracks update calls
        mock_session_state = MagicMock()
        mock_session_state.__contains__ = MagicMock(return_value=False)
        mock_st.session_state = mock_session_state

        with patch('app.utils.st', mock_st):
            initialize_session_state()

            # Check that update was called
            assert mock_st.session_state.update.called

            # Get the dict that was passed to update
            update_dict = mock_st.session_state.update.call_args[0][0]

            # Verify all required keys
            required_keys = [
                'projects', 'active_project', 'tab1_entities', 'tab2_entities',
                'tab3_entities', 'tab4_entities', 'selected_entity', 'selected_tab',
                'show_filters', 'filter_params', 'user', 'initialized',
                'orchestrator', 'current_project', 'chat_messages'
            ]

            for key in required_keys:
                assert key in update_dict, f"Missing key: {key}"

    def test_initialize_session_state_sets_correct_types(self):
        """Test that session state values have correct types"""
        mock_st = MagicMock()
        # Create a proper mock for session_state
        mock_session_state = MagicMock()
        mock_session_state.__contains__ = MagicMock(return_value=False)
        mock_st.session_state = mock_session_state

        with patch('app.utils.st', mock_st):
            initialize_session_state()
            update_dict = mock_st.session_state.update.call_args[0][0]

            # Check types
            assert isinstance(update_dict['projects'], list)
            assert isinstance(update_dict['chat_messages'], list)
            assert isinstance(update_dict['user'], dict)
            assert isinstance(update_dict['filter_params'], dict)
            assert update_dict['initialized'] is True

    def test_initialize_session_state_user_has_avatar_emoji(self):
        """Test that user avatar is an emoji, not a file path"""
        mock_st = MagicMock()
        # Create a proper mock for session_state
        mock_session_state = MagicMock()
        mock_session_state.__contains__ = MagicMock(return_value=False)
        mock_st.session_state = mock_session_state

        with patch('app.utils.st', mock_st):
            initialize_session_state()
            update_dict = mock_st.session_state.update.call_args[0][0]

            # Check user has avatar
            assert 'avatar' in update_dict['user']
            # Check it's an emoji (not a file path)
            assert update_dict['user']['avatar'] == '👤'
            assert not update_dict['user']['avatar'].endswith('.png')

    def test_initialize_session_state_only_runs_once(self):
        """Test that initialization only happens once"""
        mock_st = MagicMock()
        # Create a mock that returns True for 'initialized' in session_state
        mock_session_state = MagicMock()
        mock_session_state.__contains__ = MagicMock(return_value=True)
        mock_st.session_state = mock_session_state

        with patch('app.utils.st', mock_st):
            initialize_session_state()

            # Should not call update if already initialized
            assert not mock_st.session_state.update.called


class TestLoadCustomCSS:
    """Test custom CSS loading"""
    
    def test_load_custom_css_calls_markdown(self):
        """Test that CSS is loaded via st.markdown"""
        mock_st = MagicMock()
        
        with patch('app.utils.st', mock_st):
            load_custom_css()
            
            # Check markdown was called
            assert mock_st.markdown.called
            
            # Check it was called with unsafe_allow_html=True
            call_args = mock_st.markdown.call_args
            assert call_args[1]['unsafe_allow_html'] is True
    
    def test_load_custom_css_contains_style_tag(self):
        """Test that CSS contains <style> tag"""
        mock_st = MagicMock()
        
        with patch('app.utils.st', mock_st):
            load_custom_css()
            
            css_content = mock_st.markdown.call_args[0][0]
            assert '<style>' in css_content
            assert '</style>' in css_content


class TestValidateProjectName:
    """Test project name validation"""
    
    def test_validate_project_name_empty_string(self):
        """Test validation fails for empty string"""
        mock_st = MagicMock()
        mock_st.session_state = {'projects': []}
        
        with patch('app.utils.st', mock_st):
            is_valid, message = validate_project_name("")
            assert is_valid is False
            assert "cannot be empty" in message.lower()
    
    def test_validate_project_name_whitespace_only(self):
        """Test validation fails for whitespace only"""
        mock_st = MagicMock()
        mock_st.session_state = {'projects': []}
        
        with patch('app.utils.st', mock_st):
            is_valid, message = validate_project_name("   ")
            assert is_valid is False
            assert "cannot be empty" in message.lower()
    
    def test_validate_project_name_too_long(self):
        """Test validation fails for names > 100 characters"""
        mock_st = MagicMock()
        mock_st.session_state = {'projects': []}
        
        with patch('app.utils.st', mock_st):
            long_name = "a" * 101
            is_valid, message = validate_project_name(long_name)
            assert is_valid is False
            assert "too long" in message.lower()
    
    def test_validate_project_name_duplicate(self):
        """Test validation fails for duplicate names"""
        mock_st = MagicMock()
        mock_st.session_state = {'projects': [{'name': 'Existing Project'}]}
        
        with patch('app.utils.st', mock_st):
            is_valid, message = validate_project_name("Existing Project")
            assert is_valid is False
            assert "already exists" in message.lower()
    
    def test_validate_project_name_valid(self):
        """Test validation passes for valid name"""
        mock_st = MagicMock()
        mock_st.session_state = {'projects': []}
        
        with patch('app.utils.st', mock_st):
            is_valid, message = validate_project_name("New Project")
            assert is_valid is True
            assert message == "Valid"


class TestValidateEntityData:
    """Test entity data validation"""
    
    def test_validate_entity_data_missing_name(self):
        """Test validation fails when name is missing"""
        is_valid, message = validate_entity_data({'status': 'active'})
        assert is_valid is False
        assert "name" in message.lower()
    
    def test_validate_entity_data_missing_status(self):
        """Test validation fails when status is missing"""
        is_valid, message = validate_entity_data({'name': 'Test'})
        assert is_valid is False
        assert "status" in message.lower()
    
    def test_validate_entity_data_empty_name(self):
        """Test validation fails when name is empty"""
        is_valid, message = validate_entity_data({'name': '', 'status': 'active'})
        assert is_valid is False
    
    def test_validate_entity_data_valid(self):
        """Test validation passes for valid data"""
        is_valid, message = validate_entity_data({'name': 'Test', 'status': 'active'})
        assert is_valid is True
        assert message == "Valid"


class TestGetEntityById:
    """Test entity retrieval by ID"""
    
    def test_get_entity_by_id_found(self):
        """Test entity is found when it exists"""
        mock_st = MagicMock()
        df = pd.DataFrame([
            {'id': 1, 'name': 'Entity 1'},
            {'id': 2, 'name': 'Entity 2'}
        ])
        mock_st.session_state = {
            'tab1_entities': df,
            'tab2_entities': pd.DataFrame(),
            'tab3_entities': pd.DataFrame(),
            'tab4_entities': pd.DataFrame()
        }
        
        with patch('app.utils.st', mock_st):
            entity = get_entity_by_id(1)
            assert entity is not None
            assert entity['id'] == 1
            assert entity['name'] == 'Entity 1'
    
    def test_get_entity_by_id_not_found(self):
        """Test returns None when entity doesn't exist"""
        mock_st = MagicMock()
        mock_st.session_state = {
            'tab1_entities': pd.DataFrame(),
            'tab2_entities': pd.DataFrame(),
            'tab3_entities': pd.DataFrame(),
            'tab4_entities': pd.DataFrame()
        }
        
        with patch('app.utils.st', mock_st):
            entity = get_entity_by_id(999)
            assert entity is None
    
    def test_get_entity_by_id_searches_all_tabs(self):
        """Test searches all tabs for entity"""
        mock_st = MagicMock()
        df = pd.DataFrame([{'id': 3, 'name': 'Entity 3'}])
        mock_st.session_state = {
            'tab1_entities': pd.DataFrame(),
            'tab2_entities': pd.DataFrame(),
            'tab3_entities': df,
            'tab4_entities': pd.DataFrame()
        }
        
        with patch('app.utils.st', mock_st):
            entity = get_entity_by_id(3)
            assert entity is not None
            assert entity['id'] == 3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

