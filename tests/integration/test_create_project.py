#!/usr/bin/env python3
"""
Quick test script to create a project and verify it's stored in Snowflake.
"""

from dotenv import load_dotenv
load_dotenv()

from app.end_to_end_orchestrator import EndToEndOrchestrator

print("=" * 80)
print("Testing Project Creation")
print("=" * 80)

# Create orchestrator
orchestrator = EndToEndOrchestrator(use_local_db=False)

# Initialize services
print("\nInitializing services...")
result = orchestrator.initialize_services()
print(f"Initialization result: {result}")

if not result.get("success"):
    print(f"❌ Failed to initialize: {result.get('error')}")
    exit(1)

# Create a test project
print("\nCreating test project...")
project = orchestrator.create_project(
    "Test Project from Script",
    "This is a test project created from a Python script"
)

print(f"\nProject created: {project}")

# List all projects
print("\nListing all projects...")
projects = orchestrator.get_projects()
print(f"Total projects: {len(projects)}")
for p in projects:
    print(f"  - {p['project_name']} (ID: {p['project_id']})")

print("\n" + "=" * 80)
print("Test completed successfully!")
print("=" * 80)

