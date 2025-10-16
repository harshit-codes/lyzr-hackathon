import streamlit as st
import pandas as pd
from datetime import datetime

def initialize_session_state():
    if 'initialized' not in st.session_state:
        st.session_state.update({
            'projects': [],
            'active_project': None,
            'tab1_entities': pd.DataFrame(),
            'tab2_entities': pd.DataFrame(),
            'tab3_entities': pd.DataFrame(),
            'tab4_entities': pd.DataFrame(),
            'selected_entity': None,
            'selected_tab': 0,
            'show_filters': False,
            'filter_params': {},
            'user': {
                'name': 'User Name',
                'email': 'user@example.com',
                'avatar': '👤'  # Using emoji instead of image file
            },
            'initialized': True,
            # SuperSuite specific session state
            "orchestrator": None,
            "current_project": None,
            "chat_messages": []
        })

def load_custom_css():
    css = """
    <style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1E1E1E;
    }
    /* Button styling */
    .stButton button {
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    /* Dataframe styling */
    [data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
    }
    /* Container borders */
    [data-testid="stVerticalBlock"] > div:has(> div.element-container) {
        border-radius: 8px;
    }
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def validate_project_name(name):
    if not name or len(name.strip()) == 0:
        return False, "Project name cannot be empty"
    if len(name) > 100:
        return False, "Project name too long (max 100 characters)"
    if name in [p['name'] for p in st.session_state['projects']]:
        return False, "Project name already exists"
    return True, "Valid"

def validate_entity_data(data):
    required_fields = ['name', 'status']
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing required field: {field}"
    return True, "Valid"

def get_entity_by_id(entity_id):
    for tab in ['tab1', 'tab2', 'tab3', 'tab4']:
        df = st.session_state[f'{tab}_entities']
        # Check if DataFrame is empty or 'id' column doesn't exist
        if df.empty or 'id' not in df.columns:
            continue
        result = df[df['id'] == entity_id]
        if not result.empty:
            return result.iloc[0].to_dict()
    return None
