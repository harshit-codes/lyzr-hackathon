Build a Streamlit-based dashboard application featuring project management, tabbed navigation, tabular data views, and contextual
preview functionality.
The application follows a two-column master layout:
Component Type : st.button
Properties :
Product Requirements Document: Multi-Tab Dashboard with
Project Management
1. Overview
1.1 Purpose
1.2 Target Users
Project managers
Team members working across multiple projects
Data analysts requiring structured data views with preview capabilities
1.3 Technology Stack
Framework : Streamlit (Python)
Core Components : st.sidebar, st.tabs, st.columns, st.dataframe, st.button, st.dialog, st.container, st.session_state
2. Layout Architecture
2.1 Application Structure
Left Column : Fixed-width sidebar (20-25% of viewport width)
Right Column : Main content area (75-80% of viewport width)
2.2 Responsive Behavior
Use st.set_page_config(layout="wide") for full-width utilization
Implement use_container_width=True for responsive dataframes
Column ratios adjust proportionally on screen resize
3. Component Specifications
3.1 Left Sidebar
3.1.1 CREATE Button
Label : "CREATE"
Type : type="primary" (for visual emphasis)
Width : use_container_width=True
Key : "create_project_btn"
Styling : Large, visually prominent button with high contrast
Behavior :
if st.button("CREATE", type="primary", use_container_width=True, key="create_project_btn"):
create_project_dialog()
Interaction Flow :
Component Type : Multiple st.button instances in vertical layout
Properties :
Data Structure :
st.session_state['projects'] = [
{"id": 1 , "name": "Proj 1", "created_at": "2025-10-15"},
{"id": 2 , "name": "Proj 2", "created_at": "2025-10-16"},
# ...
]
st.session_state['active_project'] = 1 # Currently selected project ID
Behavior :
for project in st.session_state['projects']:
if st.button(
project['name'],
key=f"proj_{project['id']}",
type="primary" if st.session_state['active_project'] == project['id'] else "secondary",
use_container_width=True
):
st.session_state['active_project'] = project['id']
st.rerun()
Visual States :
1. User clicks CREATE button
2. Opens modal dialog (@st.dialog decorator)
3. Dialog contains project creation form:
Project Name: st.text_input
Project Description: st.text_area
Submit button: st.form_submit_button
4. On submit:
Validate inputs
Store in st.session_state['projects']
Close dialog via st.rerun()
Refresh project list
3.1.2 Project List
Container : Use st.container() or direct sidebar placement
Button Configuration :
Individual button per project
Type: type="secondary"
Width: use_container_width=True
Key: f"proj_{project_id}"
Label: Display project name
Active Project : type="primary" (highlighted)
Layout :
Component Type : st.container with user information display
Properties :
Implementation :
with st.sidebar:
st.divider()
with st.container():
col1, col2 = st.columns([ 1 , 3 ])
with col1:
st.image("user_avatar.png", width= 40 )
with col2:
st.write("**User Name**")
if st.button("⚙ Settings", key="user_settings"):
# Open settings dialog
pass
Component Type : st.tabs
Properties :
tab1, tab2, tab3, tab4 = st.tabs(["Tab 1", "Tab 2", "Tab 3", "Tab 4"])
Behavior :
Session State Management :
# Optional: Track active tab for custom logic
if 'active_tab' not in st.session_state:
st.session_state['active_tab'] = 0
Inactive Projects : type="secondary" (muted)
Vertical stacking with small gaps
Scrollable container if project count exceeds viewport height
Use st.container(height=400) for fixed-height scrollable area
3.1.3 USER Section
Position : Fixed at bottom of sidebar
Content :
User avatar (optional): st.image or icon
Username display: st.write or st.markdown
Settings/logout button: st.button
3.2 Main Area
3.2.1 Tab Navigation
Horizontal tab bar at top of main area
Active tab visually highlighted (built-in Streamlit styling)
Tab content loads below navigation bar
Each tab contains identical layout structure (filters, list, preview)
Component Type : Two-column layout using st.columns
Column Configuration :
with tab1:
col_list, col_preview = st.columns([1.5, 1 ])
Ratio : 60% (left column) to 40% (right column)
Component Type : Button group in horizontal layout
Implementation :
with col_list:
filter_col, add_col = st.columns( 2 )
with filter_col:
if st.button(" Filters", key=f"filters_{tab_name}", use_container_width=True):
st.session_state['show_filters'] = not st.session_state.get('show_filters', False)
with add_col:
if st.button("➕ Add", key=f"add_{tab_name}", use_container_width=True):
add_item_dialog(tab_name)
Filter Panel (Conditional Display):
if st.session_state.get('show_filters', False):
with st.expander("Filter Options", expanded=True):
filter_name = st.text_input("Filter by name")
filter_date = st.date_input("Filter by date")
filter_status = st.multiselect("Status", ["Active", "Pending", "Completed"])
Component Type : st.dataframe with selection enabled
Properties :
event = st.dataframe(
df_entities,
key=f"table_{tab_name}",
on_select="rerun",
selection_mode="single-row",
use_container_width=True,
height= 450 ,
hide_index=True,
column_config={
"name": st.column_config.TextColumn("Name", width="medium"),
"status": st.column_config.TextColumn("Status", width="small"),
"created": st.column_config.DateColumn("Created", width="medium"),
}
)
Data Structure :
st.session_state[f'{tab_name}_entities'] = pd.DataFrame([
{"id": 1 , "name": "Entity 1", "status": "Active", "created": "2025-10-15"},
3.2.2 Tab Content Layout
3.3 Left Column: Tabular List Section
3.3.1 Filter Controls
3.3.2 Tabular List
{"id": 2 , "name": "Entity 2", "status": "Pending", "created": "2025-10-16"},
])
Selection Handling :
if event.selection.rows:
selected_row_index = event.selection.rows[ 0 ]
selected_entity_id = df_entities.iloc[selected_row_index]['id']
st.session_state['selected_entity'] = selected_entity_id
Features :
Component Type : st.container with dynamic content
Layout :
with col_preview:
with st.container(height= 350 , border=True):
st.subheader("Preview Pane")
if 'selected_entity' in st.session_state:
entity = get_entity_by_id(st.session_state['selected_entity'])
# Display entity details
st.markdown(f"**Name:** {entity['name']}")
st.markdown(f"**Status:** {entity['status']}")
st.markdown(f"**Created:** {entity['created']}")
st.markdown(f"**Description:** {entity.get('description', 'N/A')}")
# Additional metadata display
with st.expander("More Details"):
st.json(entity)
else:
st.info("Select an item from the list to preview")
Behavior :
Component Type : st.container with action buttons
Layout :
with col_preview:
with st.container(border=True):
Sortable columns (click header to sort)
Single-row selection mode
Scrollable if data exceeds container height
Column resizing enabled
Search functionality in toolbar
3.4 Right Column: Preview and Action Section
3.4.1 Preview Pane
Updates automatically when user selects row from tabular list
Displays detailed information about selected entity
Empty state message when no selection
Bordered container for visual separation
3.4.2 Action Panel
st.subheader("Action Panel")
if 'selected_entity' in st.session_state:
col1, col2 = st.columns( 2 )
with col1:
if st.button("✏ Edit", key=f"edit_{st.session_state['selected_entity']}", use_container_wi
edit_entity_dialog(st.session_state['selected_entity'])
with col2:
if st.button(" Delete", key=f"delete_{st.session_state['selected_entity']}", use_container
delete_entity_confirmation(st.session_state['selected_entity'])
st.divider()
if st.button(" Export", key=f"export_{st.session_state['selected_entity']}", use_container_wid
export_entity_data(st.session_state['selected_entity'])
if st.button(" Duplicate", key=f"duplicate_{st.session_state['selected_entity']}", use_contain
duplicate_entity(st.session_state['selected_entity'])
else:
st.info("Select an item to view available actions")
Action Types :
Component Type : Custom footer using st.markdown with HTML/CSS
Implementation :
footer_html = """
&lt;style&gt;
.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: #0E1117;
color: #FAFAFA;
text-align: center;
padding: 10px;
font-size: 14px;
border-top: 1px solid #262730;
}
&lt;/style&gt;
<div>
<p>© 2025 Dashboard App | Version 1.0.0 | <a href="/help">Help</a> | <a href="/privacy">Privacy Policy<
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
Content :
1. Edit : Opens dialog with editable form
2. Delete : Shows confirmation dialog
3. Export : Downloads entity data as CSV/JSON
4. Duplicate : Creates copy of selected entity
5. Custom Actions : Tab-specific operations
3.5 Footer Section
Copyright information
Version number
Help/documentation links
Privacy policy link
Positioning :
# Initialize session state
if 'initialized' not in st.session_state:
st.session_state.update({
# Project management
'projects': [],
'active_project': None,
# Tab entities (one per tab)
'tab1_entities': pd.DataFrame(),
'tab2_entities': pd.DataFrame(),
'tab3_entities': pd.DataFrame(),
'tab4_entities': pd.DataFrame(),
# Selection tracking
'selected_entity': None,
'selected_tab': 0 ,
# UI state
'show_filters': False,
'filter_params': {},
# User data
'user': {
'name': 'User Name',
'email': 'user@example.com',
'avatar': 'avatar.png'
},
'initialized': True
})
Project Selection :
def select_project(project_id):
st.session_state['active_project'] = project_id
# Load project-specific data
load_project_data(project_id)
st.rerun()
Entity Selection :
def select_entity(entity_id):
st.session_state['selected_entity'] = entity_id
# No rerun needed - preview updates automatically
Filter Application :
Contact information
Fixed at bottom of viewport
Full width
Always visible (does not scroll)
Styled to match app theme
4. State Management
4.1 Session State Structure
4.2 State Update Patterns
def apply_filters(tab_name, filters):
st.session_state[f'{tab_name}_filters'] = filters
# Filter dataframe
df_filtered = filter_dataframe(st.session_state[f'{tab_name}_entities'], filters)
st.session_state[f'{tab_name}_filtered'] = df_filtered
@st.dialog("Create New Project")
def create_project_dialog():
st.write("Enter project details:")
with st.form("create_project_form"):
name = st.text_input("Project Name", max_chars= 100 )
description = st.text_area("Description", max_chars= 500 )
col1, col2 = st.columns( 2 )
with col1:
submit = st.form_submit_button("Create", use_container_width=True)
with col2:
cancel = st.form_submit_button("Cancel", use_container_width=True)
if submit:
if name:
# Add to projects list
new_project = {
'id': len(st.session_state['projects']) + 1 ,
'name': name,
'description': description,
'created_at': datetime.now().isoformat()
}
st.session_state['projects'].append(new_project)
st.session_state['active_project'] = new_project['id']
st.success(f"Project '{name}' created successfully!")
time.sleep( 1 )
st.rerun()
else:
st.error("Project name is required")
if cancel:
st.rerun()
@st.dialog("Add New Item")
def add_item_dialog(tab_name):
st.write(f"Add new item to {tab_name}")
with st.form("add_item_form"):
name = st.text_input("Name")
status = st.selectbox("Status", ["Active", "Pending", "Completed"])
description = st.text_area("Description")
submitted = st.form_submit_button("Add Item")
if submitted and name:
new_item = {
'id': len(st.session_state[f'{tab_name}_entities']) + 1 ,
'name': name,
'status': status,
'description': description,
'created': datetime.now().date().isoformat()
}
5. Dialog Interactions
5.1 Create Project Dialog
5.2 Add Entity Dialog
# Append to dataframe
st.session_state[f'{tab_name}_entities'] = pd.concat([
st.session_state[f'{tab_name}_entities'],
pd.DataFrame([new_item])
], ignore_index=True)
st.success(f"Item '{name}' added successfully!")
time.sleep( 1 )
st.rerun()
@st.dialog("Edit Item")
def edit_entity_dialog(entity_id):
entity = get_entity_by_id(entity_id)
with st.form("edit_entity_form"):
name = st.text_input("Name", value=entity['name'])
status = st.selectbox("Status", ["Active", "Pending", "Completed"],
index=["Active", "Pending", "Completed"].index(entity['status']))
description = st.text_area("Description", value=entity.get('description', ''))
submitted = st.form_submit_button("Update")
if submitted:
# Update entity in dataframe
update_entity(entity_id, {
'name': name,
'status': status,
'description': description
})
st.success("Item updated successfully!")
time.sleep( 1 )
st.rerun()
@st.dialog("Confirm Delete")
def delete_entity_confirmation(entity_id):
entity = get_entity_by_id(entity_id)
st.warning(f"Are you sure you want to delete '{entity['name']}'?")
st.write("This action cannot be undone.")
col1, col2 = st.columns( 2 )
with col1:
if st.button("Delete", type="primary", use_container_width=True):
delete_entity(entity_id)
st.session_state['selected_entity'] = None
st.success("Item deleted successfully!")
time.sleep( 1 )
st.rerun()
with col2:
if st.button("Cancel", use_container_width=True):
st.rerun()
5.3 Edit Entity Dialog
5.4 Delete Confirmation Dialog
6. Data Operations
def create_entity(tab_name, entity_data):
"""Create new entity in specified tab"""
df = st.session_state[f'{tab_name}_entities']
new_df = pd.concat([df, pd.DataFrame([entity_data])], ignore_index=True)
st.session_state[f'{tab_name}_entities'] = new_df
def read_entity(entity_id):
"""Get entity by ID from current tab"""
# Search across all tab dataframes
for tab in ['tab1', 'tab2', 'tab3', 'tab4']:
df = st.session_state[f'{tab}_entities']
result = df[df['id'] == entity_id]
if not result.empty:
return result.iloc[ 0 ].to_dict()
return None
def update_entity(entity_id, updated_data):
"""Update entity with new data"""
for tab in ['tab1', 'tab2', 'tab3', 'tab4']:
df = st.session_state[f'{tab}_entities']
mask = df['id'] == entity_id
if mask.any():
for key, value in updated_data.items():
df.loc[mask, key] = value
st.session_state[f'{tab}_entities'] = df
return True
return False
def delete_entity(entity_id):
"""Delete entity by ID"""
for tab in ['tab1', 'tab2', 'tab3', 'tab4']:
df = st.session_state[f'{tab}_entities']
df_filtered = df[df['id'] != entity_id]
if len(df_filtered) &lt; len(df):
st.session_state[f'{tab}_entities'] = df_filtered
return True
return False
def filter_dataframe(df, filters):
"""Apply filters to dataframe"""
filtered_df = df.copy()
if filters.get('name'):
filtered_df = filtered_df[filtered_df['name'].str.contains(filters['name'], case=False, na=False)]
if filters.get('status'):
filtered_df = filtered_df[filtered_df['status'].isin(filters['status'])]
if filters.get('date_from'):
filtered_df = filtered_df[pd.to_datetime(filtered_df['created']) &gt;= filters['date_from']]
if filters.get('date_to'):
filtered_df = filtered_df[pd.to_datetime(filtered_df['created']) &lt;= filters['date_to']]
return filtered_df
6.1 CRUD Functions
6.2 Filter Operations
def export_entity_data(entity_id):
"""Export entity as CSV"""
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
"""Export entire tab dataframe"""
df = st.session_state[f'{tab_name}_entities']
csv = df.to_csv(index=False)
st.download_button(
label=f"Export {tab_name} Data",
data=csv,
file_name=f"{tab_name}_data.csv",
mime="text/csv"
)
def load_custom_css():
"""Load custom CSS styling"""
css = """
&lt;style&gt;
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
[data-testid="stVerticalBlock"] &gt; div:has(&gt; div.element-container) {
border-radius: 8px;
}
/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
6.3 Export Operations
7. Styling and Customization
7.1 Custom CSS
gap: 8px;
}
.stTabs [data-baseweb="tab"] {
border-radius: 8px 8px 0 0;
padding: 10px 20px;
}
&lt;/style&gt;
"""
st.markdown(css, unsafe_allow_html=True)
Create .streamlit/config.toml:
[theme]
primaryColor = "#4CAF50"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
font = "sans serif"
[server]
headless = true
port = 8501
enableCORS = false
@st.cache_data(ttl= 3600 )
def load_project_data(project_id):
"""Cache project data for 1 hour"""
# Load from database/API
return fetch_project_from_db(project_id)
@st.cache_data
def load_entity_list(project_id, tab_name):
"""Cache entity lists"""
return fetch_entities_from_db(project_id, tab_name)
@st.cache_resource
def init_database_connection():
"""Cache database connection"""
return create_db_connection()
def lazy_load_entities(tab_name, page= 1 , page_size= 50 ):
"""Load entities in batches"""
start_idx = (page - 1 ) * page_size
end_idx = start_idx + page_size
df = st.session_state[f'{tab_name}_entities']
return df.iloc[start_idx:end_idx]
7.2 Theme Configuration
8. Performance Optimization
8.1 Caching Strategies
8.2 Lazy Loading
@st.fragment(run_every="30s")
def auto_refresh_preview():
"""Auto-refresh preview pane every 30 seconds"""
if 'selected_entity' in st.session_state:
entity = read_entity(st.session_state['selected_entity'])
display_entity_preview(entity)
def validate_project_name(name):
"""Validate project name"""
if not name or len(name.strip()) == 0 :
return False, "Project name cannot be empty"
if len(name) &gt; 100 :
return False, "Project name too long (max 100 characters)"
if name in [p['name'] for p in st.session_state['projects']]:
return False, "Project name already exists"
return True, "Valid"
def validate_entity_data(data):
"""Validate entity data"""
required_fields = ['name', 'status']
for field in required_fields:
if field not in data or not data[field]:
return False, f"Missing required field: {field}"
return True, "Valid"
try:
# Operation
create_entity(tab_name, entity_data)
st.success("✅ Entity created successfully!")
except ValueError as e:
st.error(f"❌ Validation Error: {str(e)}")
except Exception as e:
st.error(f"❌ Unexpected Error: {str(e)}")
st.exception(e) # Show full traceback in development
st.markdown("""
&lt;style&gt;
[data-testid="stButton"] button {
aria-label: "Create new project";
}
8.3 Fragment Usage
9. Error Handling
9.1 Input Validation
9.2 Error Display
10. Accessibility
10.1 Keyboard Navigation
Ensure all buttons are keyboard accessible
Tab order follows logical flow (left to right, top to bottom)
Use st.button with proper labels for screen readers
10.2 ARIA Labels
&lt;/style&gt;
""", unsafe_allow_html=True)
def test_create_entity():
"""Test entity creation"""
entity_data = {'name': 'Test', 'status': 'Active'}
create_entity('tab1', entity_data)
assert len(st.session_state['tab1_entities']) &gt; 0
def test_filter_dataframe():
"""Test filtering functionality"""
df = pd.DataFrame([
{'name': 'Item A', 'status': 'Active'},
{'name': 'Item B', 'status': 'Pending'}
])
filtered = filter_dataframe(df, {'status': ['Active']})
assert len(filtered) == 1
# requirements.txt
streamlit==1.37.
pandas==2.1.
numpy==1.24.
python-dotenv==1.0.
10.3 Color Contrast
Ensure minimum 4.5:1 contrast ratio for text
Use Streamlit's built-in theme system for consistent contrast
Provide visual indicators beyond color (icons, text labels)
11. Testing Strategy
11.1 Unit Tests
11.2 Integration Tests
Test project creation → entity creation → selection → preview flow
Test tab switching with data persistence
Test filter application and reset
11.3 UI Tests
Use Selenium for automated UI testing
Test responsive behavior at different viewport sizes
Verify dialog interactions
12. Deployment
12.1 Environment Setup
# config.py
import os
from dotenv import load_dotenv
load_dotenv()
APP_TITLE = os.getenv("APP_TITLE", "Multi-Tab Dashboard")
APP_ICON = os.getenv("APP_ICON", "")
DEBUG_MODE = os.getenv("DEBUG_MODE", "False") == "True"
# .streamlit/secrets.toml
[database]
host = "localhost"
port = 5432
username = "admin"
password = "secret"
[api]
key = "api_key_here"
12.2 Configuration
12.3 Streamlit Cloud Deployment
13. Future Enhancements
13.1 Planned Features
Multi-select for batch operations
Drag-and-drop reordering of entities
Real-time collaboration (multiple users)
Advanced search with filters
Export to multiple formats (Excel, JSON, PDF)
Data visualization charts per tab
User roles and permissions
Activity log/audit trail
Dark/light mode toggle
Internationalization (i18n)
13.2 Technical Improvements
Backend API integration (REST/GraphQL)
Database persistence (PostgreSQL, MongoDB)
WebSocket for real-time updates
Custom Streamlit components for advanced UI
Progressive Web App (PWA) capabilities
14. Appendix
See attached full implementation file: dashboard_app.py
Refer to attached wireframe image for visual reference.
14.1 Complete Code Example
14.2 API Reference
Streamlit Documentation: https://docs.streamlit.io
Pandas Documentation: https://pandas.pydata.org
Session State Guide: https://docs.streamlit.io/library/api-reference/session-state
