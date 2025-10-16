"""
Unit tests for app/data_manager.py
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import datetime

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.data_manager import (
    create_entity,
    read_entity,
    update_entity,
    delete_entity,
    filter_dataframe,
    export_entity_data,
    export_tab_data,
    load_project_data,
    load_entity_list,
    lazy_load_entities
)


class TestCreateEntity:
    """Test entity creation"""
    
    def test_create_entity_adds_to_dataframe(self):
        """Test that entity is added to the correct tab"""
        mock_st = MagicMock()
        initial_df = pd.DataFrame([{'id': 1, 'name': 'Entity 1'}])
        mock_st.session_state = {'tab1_entities': initial_df}
        
        with patch('app.data_manager.st', mock_st):
            new_entity = {'id': 2, 'name': 'Entity 2'}
            create_entity('tab1', new_entity)
            
            # Check that session state was updated
            updated_df = mock_st.session_state['tab1_entities']
            assert len(updated_df) == 2
    
    def test_create_entity_preserves_existing_data(self):
        """Test that existing entities are preserved"""
        mock_st = MagicMock()
        initial_df = pd.DataFrame([{'id': 1, 'name': 'Entity 1'}])
        mock_st.session_state = {'tab1_entities': initial_df}
        
        with patch('app.data_manager.st', mock_st):
            new_entity = {'id': 2, 'name': 'Entity 2'}
            create_entity('tab1', new_entity)
            
            updated_df = mock_st.session_state['tab1_entities']
            # Check first entity still exists
            assert any(updated_df['id'] == 1)


class TestReadEntity:
    """Test entity reading"""
    
    def test_read_entity_found_in_first_tab(self):
        """Test reading entity from first tab"""
        mock_st = MagicMock()
        df = pd.DataFrame([{'id': 1, 'name': 'Entity 1', 'status': 'active'}])
        mock_st.session_state = {
            'tab1_entities': df,
            'tab2_entities': pd.DataFrame(),
            'tab3_entities': pd.DataFrame(),
            'tab4_entities': pd.DataFrame()
        }
        
        with patch('app.data_manager.st', mock_st):
            entity = read_entity(1)
            assert entity is not None
            assert entity['id'] == 1
            assert entity['name'] == 'Entity 1'
    
    def test_read_entity_not_found(self):
        """Test reading non-existent entity"""
        mock_st = MagicMock()
        mock_st.session_state = {
            'tab1_entities': pd.DataFrame(),
            'tab2_entities': pd.DataFrame(),
            'tab3_entities': pd.DataFrame(),
            'tab4_entities': pd.DataFrame()
        }
        
        with patch('app.data_manager.st', mock_st):
            entity = read_entity(999)
            assert entity is None
    
    def test_read_entity_searches_all_tabs(self):
        """Test that all tabs are searched"""
        mock_st = MagicMock()
        df = pd.DataFrame([{'id': 5, 'name': 'Entity 5'}])
        mock_st.session_state = {
            'tab1_entities': pd.DataFrame(),
            'tab2_entities': pd.DataFrame(),
            'tab3_entities': df,
            'tab4_entities': pd.DataFrame()
        }
        
        with patch('app.data_manager.st', mock_st):
            entity = read_entity(5)
            assert entity is not None
            assert entity['id'] == 5


class TestUpdateEntity:
    """Test entity updating"""
    
    def test_update_entity_modifies_data(self):
        """Test that entity data is updated"""
        mock_st = MagicMock()
        df = pd.DataFrame([{'id': 1, 'name': 'Old Name', 'status': 'pending'}])
        mock_st.session_state = {
            'tab1_entities': df.copy(),
            'tab2_entities': pd.DataFrame(),
            'tab3_entities': pd.DataFrame(),
            'tab4_entities': pd.DataFrame()
        }
        
        with patch('app.data_manager.st', mock_st):
            result = update_entity(1, {'name': 'New Name', 'status': 'active'})
            assert result is True
            
            updated_df = mock_st.session_state['tab1_entities']
            entity = updated_df[updated_df['id'] == 1].iloc[0]
            assert entity['name'] == 'New Name'
            assert entity['status'] == 'active'
    
    def test_update_entity_not_found(self):
        """Test updating non-existent entity"""
        mock_st = MagicMock()
        mock_st.session_state = {
            'tab1_entities': pd.DataFrame(),
            'tab2_entities': pd.DataFrame(),
            'tab3_entities': pd.DataFrame(),
            'tab4_entities': pd.DataFrame()
        }
        
        with patch('app.data_manager.st', mock_st):
            result = update_entity(999, {'name': 'New Name'})
            assert result is False


class TestDeleteEntity:
    """Test entity deletion"""
    
    def test_delete_entity_removes_from_dataframe(self):
        """Test that entity is removed"""
        mock_st = MagicMock()
        df = pd.DataFrame([
            {'id': 1, 'name': 'Entity 1'},
            {'id': 2, 'name': 'Entity 2'}
        ])
        mock_st.session_state = {
            'tab1_entities': df.copy(),
            'tab2_entities': pd.DataFrame(),
            'tab3_entities': pd.DataFrame(),
            'tab4_entities': pd.DataFrame()
        }
        
        with patch('app.data_manager.st', mock_st):
            result = delete_entity(1)
            assert result is True
            
            updated_df = mock_st.session_state['tab1_entities']
            assert len(updated_df) == 1
            assert not any(updated_df['id'] == 1)
    
    def test_delete_entity_not_found(self):
        """Test deleting non-existent entity"""
        mock_st = MagicMock()
        mock_st.session_state = {
            'tab1_entities': pd.DataFrame(),
            'tab2_entities': pd.DataFrame(),
            'tab3_entities': pd.DataFrame(),
            'tab4_entities': pd.DataFrame()
        }
        
        with patch('app.data_manager.st', mock_st):
            result = delete_entity(999)
            assert result is False


class TestFilterDataframe:
    """Test dataframe filtering"""
    
    def test_filter_dataframe_by_name(self):
        """Test filtering by name"""
        df = pd.DataFrame([
            {'name': 'Alice', 'status': 'Active', 'created': '2025-01-01'},
            {'name': 'Bob', 'status': 'Active', 'created': '2025-01-02'},
            {'name': 'Charlie', 'status': 'Pending', 'created': '2025-01-03'}
        ])
        
        filtered = filter_dataframe(df, {'name': 'Alice'})
        assert len(filtered) == 1
        assert filtered.iloc[0]['name'] == 'Alice'
    
    def test_filter_dataframe_by_status(self):
        """Test filtering by status"""
        df = pd.DataFrame([
            {'name': 'Alice', 'status': 'Active', 'created': '2025-01-01'},
            {'name': 'Bob', 'status': 'Active', 'created': '2025-01-02'},
            {'name': 'Charlie', 'status': 'Pending', 'created': '2025-01-03'}
        ])
        
        filtered = filter_dataframe(df, {'status': ['Active']})
        assert len(filtered) == 2
    
    def test_filter_dataframe_no_filters(self):
        """Test that no filters returns original dataframe"""
        df = pd.DataFrame([
            {'name': 'Alice', 'status': 'Active', 'created': '2025-01-01'},
            {'name': 'Bob', 'status': 'Active', 'created': '2025-01-02'}
        ])
        
        filtered = filter_dataframe(df, {})
        assert len(filtered) == len(df)
    
    def test_filter_dataframe_case_insensitive_name(self):
        """Test name filtering is case insensitive"""
        df = pd.DataFrame([
            {'name': 'Alice', 'status': 'Active', 'created': '2025-01-01'},
            {'name': 'Bob', 'status': 'Active', 'created': '2025-01-02'}
        ])
        
        filtered = filter_dataframe(df, {'name': 'alice'})
        assert len(filtered) == 1


class TestLazyLoadEntities:
    """Test lazy loading of entities"""
    
    def test_lazy_load_entities_first_page(self):
        """Test loading first page"""
        mock_st = MagicMock()
        df = pd.DataFrame([{'id': i, 'name': f'Entity {i}'} for i in range(100)])
        mock_st.session_state = {'tab1_entities': df}
        
        with patch('app.data_manager.st', mock_st):
            page_data = lazy_load_entities('tab1', page=1, page_size=10)
            assert len(page_data) == 10
            assert page_data.iloc[0]['id'] == 0
    
    def test_lazy_load_entities_second_page(self):
        """Test loading second page"""
        mock_st = MagicMock()
        df = pd.DataFrame([{'id': i, 'name': f'Entity {i}'} for i in range(100)])
        mock_st.session_state = {'tab1_entities': df}
        
        with patch('app.data_manager.st', mock_st):
            page_data = lazy_load_entities('tab1', page=2, page_size=10)
            assert len(page_data) == 10
            assert page_data.iloc[0]['id'] == 10
    
    def test_lazy_load_entities_custom_page_size(self):
        """Test custom page size"""
        mock_st = MagicMock()
        df = pd.DataFrame([{'id': i, 'name': f'Entity {i}'} for i in range(100)])
        mock_st.session_state = {'tab1_entities': df}
        
        with patch('app.data_manager.st', mock_st):
            page_data = lazy_load_entities('tab1', page=1, page_size=25)
            assert len(page_data) == 25


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

