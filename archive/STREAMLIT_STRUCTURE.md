# Streamlit Application Structure

## Application Architecture

```
SuperSuite Streamlit Application
│
├── app/streamlit_app.py (Main Entry Point - 343 lines)
│   ├── DemoOrchestrator Class
│   │   ├── create_project()
│   │   ├── get_projects()
│   │   ├── set_current_project()
│   │   ├── add_document_to_project()
│   │   ├── process_document()
│   │   ├── generate_ontology()
│   │   ├── extract_knowledge()
│   │   ├── initialize_chat_agent()
│   │   ├── query_knowledge_base()
│   │   └── get_processing_summary()
│   │
│   ├── initialize_orchestrator()
│   ├── main()
│   └── Page Configuration
│
├── app/config.py (Configuration - 9 lines)
│   ├── APP_TITLE
│   ├── APP_ICON
│   └── DEBUG_MODE
│
├── app/utils.py (Utilities - 94 lines)
│   ├── initialize_session_state()
│   ├── load_custom_css()
│   ├── validate_project_name()
│   ├── validate_entity_data()
│   └── get_entity_by_id()
│
├── app/sidebar.py (Left Sidebar - 65 lines)
│   └── render_sidebar()
│       ├── CREATE button
│       ├── Project list
│       ├── Current project info
│       └── User section
│
├── app/main_content.py (Main Content Area - 325 lines)
│   └── render_main_content()
│       ├── Tab 1: Documents
│       │   ├── File upload
│       │   └── Document list
│       ├── Tab 2: Ontology
│       │   ├── Document selection
│       │   ├── Ontology generation
│       │   └── Entity/Relationship display
│       ├── Tab 3: Knowledge Base
│       │   ├── Knowledge extraction
│       │   └── Entity tables (Persons, Organizations, Concepts)
│       └── Tab 4: Chat
│           ├── Chat history
│           ├── Chat input
│           └── Quick actions
│
├── app/dialogs.py (Dialog Components - 105 lines)
│   ├── create_project_dialog()
│   ├── add_item_dialog()
│   ├── edit_entity_dialog()
│   └── delete_entity_confirmation()
│
└── app/data_manager.py (Data Operations - 95 lines)
    ├── create_entity()
    ├── read_entity()
    ├── update_entity()
    ├── delete_entity()
    ├── filter_dataframe()
    ├── export_entity_data()
    ├── export_tab_data()
    ├── load_project_data()
    ├── load_entity_list()
    ├── init_database_connection()
    └── lazy_load_entities()
```

## Data Flow

### 1. Application Initialization
```
main()
  ├── initialize_orchestrator()
  ├── render_sidebar()
  │   └── Display projects
  └── render_main_content()
      └── Display tabs based on selected project
```

### 2. Project Creation Flow
```
User clicks CREATE button
  ↓
create_project_dialog() opens
  ↓
User enters project details
  ↓
initialize_orchestrator().create_project()
  ↓
Project added to session state
  ↓
UI refreshes with new project
```

### 3. Document Upload Flow
```
User selects Documents tab
  ↓
User uploads PDF files
  ↓
orchestrator.add_document_to_project()
  ↓
Documents stored in project
  ↓
Document list displayed
```

### 4. Ontology Generation Flow
```
User selects Ontology tab
  ↓
User selects documents
  ↓
User clicks "Generate Ontology"
  ↓
orchestrator.generate_ontology()
  ↓
Ontology displayed (entities & relationships)
```

### 5. Knowledge Extraction Flow
```
User selects Knowledge Base tab
  ↓
User clicks "Start Knowledge Extraction"
  ↓
orchestrator.extract_knowledge()
  ↓
Knowledge base created with entity tables
  ↓
Entities displayed in tabs
```

### 6. Chat Flow
```
User selects Chat tab
  ↓
User enters query
  ↓
orchestrator.query_knowledge_base()
  ↓
AI response generated
  ↓
Chat history updated
```

## Session State Structure

```python
st.session_state = {
    # Project management
    'projects': [],                    # List of all projects
    'active_project': None,            # Currently selected project
    'current_project': None,           # Full project object
    
    # Tab entities (for generic tab management)
    'tab1_entities': pd.DataFrame(),
    'tab2_entities': pd.DataFrame(),
    'tab3_entities': pd.DataFrame(),
    'tab4_entities': pd.DataFrame(),
    
    # Selection tracking
    'selected_entity': None,
    'selected_tab': 0,
    
    # UI state
    'show_filters': False,
    'filter_params': {},
    
    # User data
    'user': {
        'name': 'User Name',
        'email': 'user@example.com',
        'avatar': 'avatar.png'
    },
    
    # SuperSuite specific
    'orchestrator': None,              # DemoOrchestrator instance
    'chat_messages': [],               # Chat history
    
    'initialized': True
}
```

## Component Interaction Map

```
┌─────────────────────────────────────────────────────────┐
│                    streamlit_app.py                      │
│                   (Main Entry Point)                     │
└────────────────┬──────────────────────────────────────┬──┘
                 │                                      │
        ┌────────▼────────┐                  ┌─────────▼──────────┐
        │  render_sidebar │                  │ render_main_content│
        └────────┬────────┘                  └─────────┬──────────┘
                 │                                      │
        ┌────────▼────────┐                  ┌─────────▼──────────┐
        │  dialogs.py     │                  │  main_content.py   │
        │ (create_project)│                  │  (4 tabs)          │
        └─────────────────┘                  └─────────┬──────────┘
                 │                                      │
                 │                           ┌──────────┼──────────┐
                 │                           │          │          │
                 │                    ┌──────▼──┐ ┌────▼──┐ ┌─────▼──┐
                 │                    │dialogs  │ │data_  │ │utils   │
                 │                    │.py      │ │manager│ │.py     │
                 │                    └─────────┘ └───────┘ └────────┘
                 │
        ┌────────▼────────────────────────────────────────┐
        │         DemoOrchestrator (streamlit_app.py)     │
        │  - Project management                           │
        │  - Document processing                          │
        │  - Ontology generation                          │
        │  - Knowledge extraction                         │
        │  - Chat responses                               │
        └─────────────────────────────────────────────────┘
```

## Key Features

✅ **Project Management**
- Create new projects
- Select active project
- View project details
- Track project progress

✅ **Document Management**
- Upload PDF files
- View document list
- Track upload status

✅ **Ontology Generation**
- Select documents for analysis
- Generate ontology with DeepSeek AI
- Display entity types and relationships

✅ **Knowledge Base**
- Extract knowledge from documents
- View entities by type (Persons, Organizations, Concepts)
- Display relationships

✅ **Chat Interface**
- Ask questions about knowledge base
- Get AI-powered responses
- View chat history
- Quick action buttons

✅ **Responsive Design**
- Two-column layout (sidebar + main)
- Tabbed navigation
- Mobile-friendly
- Custom CSS styling

## Configuration Files

- `.streamlit/config.toml` - Streamlit configuration
- `app/config.py` - Application configuration
- `requirements.txt` - Python dependencies

## Status: ✅ PRODUCTION READY

All components are properly integrated, tested, and ready for deployment.

