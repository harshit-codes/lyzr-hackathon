import streamlit as st
import time
from datetime import datetime
from app.data_manager import create_entity, update_entity, delete_entity, read_entity
from app.utils import validate_project_name

@st.dialog("Create New Project")
def create_project_dialog():
    # Import here to avoid circular imports
    from app.streamlit_app import initialize_orchestrator

    st.write("Enter project details:")
    with st.form("create_project_form"):
        name = st.text_input("Project Name", max_chars=100)
        description = st.text_area("Description", max_chars=500)
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("Create", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("Cancel", use_container_width=True)

        if submit:
            print("=" * 80)
            print("CREATE PROJECT DIALOG: Submit button clicked")
            print(f"Project name: {name}")
            print(f"Description: {description}")
            print("=" * 80)

            is_valid, message = validate_project_name(name)
            if is_valid:
                print("✓ Project name is valid")
                orchestrator = initialize_orchestrator()
                print(f"✓ Orchestrator initialized: {orchestrator}")
                print(f"  Orchestrator type: {type(orchestrator)}")
                print(f"  Orchestrator projects before: {len(orchestrator.projects)}")

                new_project = orchestrator.create_project(
                    name.strip(),
                    description.strip() if description else None
                )

                print(f"✓ create_project returned: {new_project}")
                print(f"  Orchestrator projects after: {len(orchestrator.projects)}")

                if new_project is None:
                    print("❌ Project creation returned None")
                    st.error("Failed to create project. Please check the error message above.")
                else:
                    print(f"✓ Project created successfully: {new_project.get('project_id')}")
                    print(f"  Setting current project...")
                    orchestrator.set_current_project(new_project['project_id'])
                    print(f"  Current project set: {orchestrator.current_project}")
                    print(f"  Session state current_project: {st.session_state.get('current_project')}")
                    st.success(f"Project '{name}' created successfully!")
                    print("  Calling st.rerun()...")
                    time.sleep(1)
                    st.rerun()
            else:
                print(f"❌ Project name validation failed: {message}")
                st.error(message)
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
                'id': len(st.session_state[f'{tab_name}_entities']) + 1,
                'name': name,
                'status': status,
                'description': description,
                'created': datetime.now().date().isoformat()
            }
            create_entity(tab_name, new_item)
            st.success(f"Item '{name}' added successfully!")
            time.sleep(1)
            st.rerun()

@st.dialog("Edit Item")
def edit_entity_dialog(entity_id):
    entity = read_entity(entity_id)
    if entity:
        with st.form("edit_entity_form"):
            name = st.text_input("Name", value=entity['name'])
            status = st.selectbox("Status", ["Active", "Pending", "Completed"],
                                  index=["Active", "Pending", "Completed"].index(entity['status']))
            description = st.text_area("Description", value=entity.get('description', ''))
            submitted = st.form_submit_button("Update")

            if submitted:
                update_entity(entity_id, {
                    'name': name,
                    'status': status,
                    'description': description
                })
                st.success("Item updated successfully!")
                time.sleep(1)
                st.rerun()
    else:
        st.warning("Entity not found for editing.")
        time.sleep(1)
        st.rerun()

@st.dialog("Confirm Delete")
def delete_entity_confirmation(entity_id):
    entity = read_entity(entity_id)
    if entity:
        st.warning(f"Are you sure you want to delete '{entity['name']}'?")
        st.write("This action cannot be undone.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Delete", type="primary", use_container_width=True):
                delete_entity(entity_id)
                st.session_state['selected_entity'] = None
                st.success("Item deleted successfully!")
                time.sleep(1)
                st.rerun()
        with col2:
            if st.button("Cancel", use_container_width=True):
                st.rerun()
    else:
        st.warning("Entity not found for deletion.")
        time.sleep(1)
        st.rerun()
