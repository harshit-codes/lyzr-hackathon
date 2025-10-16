import streamlit as st
import pandas as pd
from datetime import datetime

def create_entity(tab_name, entity_data):
    df = st.session_state[f'{tab_name}_entities']
    new_df = pd.concat([df, pd.DataFrame([entity_data])], ignore_index=True)
    st.session_state[f'{tab_name}_entities'] = new_df

def read_entity(entity_id):
    for tab in ['tab1', 'tab2', 'tab3', 'tab4']:
        df = st.session_state[f'{tab}_entities']
        # Check if DataFrame is empty or 'id' column doesn't exist
        if df.empty or 'id' not in df.columns:
            continue
        result = df[df['id'] == entity_id]
        if not result.empty:
            return result.iloc[0].to_dict()
    return None

def update_entity(entity_id, updated_data):
    for tab in ['tab1', 'tab2', 'tab3', 'tab4']:
        df = st.session_state[f'{tab}_entities']
        # Check if DataFrame is empty or 'id' column doesn't exist
        if df.empty or 'id' not in df.columns:
            continue
        mask = df['id'] == entity_id
        if mask.any():
            for key, value in updated_data.items():
                df.loc[mask, key] = value
            st.session_state[f'{tab}_entities'] = df
            return True
    return False

def delete_entity(entity_id):
    for tab in ['tab1', 'tab2', 'tab3', 'tab4']:
        df = st.session_state[f'{tab}_entities']
        # Check if DataFrame is empty or 'id' column doesn't exist
        if df.empty or 'id' not in df.columns:
            continue
        df_filtered = df[df['id'] != entity_id]
        if len(df_filtered) < len(df):
            st.session_state[f'{tab}_entities'] = df_filtered
            return True
    return False

def filter_dataframe(df, filters):
    filtered_df = df.copy()
    if filters.get('name'):
        filtered_df = filtered_df[filtered_df['name'].str.contains(filters['name'], case=False, na=False)]
    if filters.get('status'):
        filtered_df = filtered_df[filtered_df['status'].isin(filters['status'])]
    if filters.get('date_from'):
        filtered_df = filtered_df[pd.to_datetime(filtered_df['created']) >= filters['date_from']]
    if filters.get('date_to'):
        filtered_df = filtered_df[pd.to_datetime(filtered_df['created']) <= filters['date_to']]
    return filtered_df

def export_entity_data(entity_id):
    entity = read_entity(entity_id)
    if entity:
        df = pd.DataFrame([entity])
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"entity_{entity_id}.csv",
            mime="text/csv"
        )

def export_tab_data(tab_name):
    df = st.session_state[f'{tab_name}_entities']
    csv = df.to_csv(index=False)
    st.download_button(
        label=f"Export {tab_name} Data",
        data=csv,
        file_name=f"{tab_name}_data.csv",
        mime="text/csv"
    )

@st.cache_data(ttl=3600)
def load_project_data(project_id):
    # Placeholder for actual data loading from database/API
    return {"id": project_id, "name": f"Project {project_id}", "description": "", "created_at": ""}

@st.cache_data
def load_entity_list(project_id, tab_name):
    # Placeholder for actual data loading from database/API
    return pd.DataFrame([
        {"id": 1 , "name": "Entity 1", "status": "Active", "created": "2025-10-15"},
        {"id": 2 , "name": "Entity 2", "status": "Pending", "created": "2025-10-16"},
    ])

@st.cache_resource
def init_database_connection():
    # Placeholder for actual database connection initialization
    return "Database Connection Object"

def lazy_load_entities(tab_name, page=1, page_size=50):
    df = st.session_state[f'{tab_name}_entities']
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    return df.iloc[start_idx:end_idx]
