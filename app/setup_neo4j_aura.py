#!/usr/bin/env python3
"""
Setup Neo4j Aura Instance

Automatically creates a Neo4j Aura instance using the API and configures
the connection credentials in .env file.

Prerequisites:
- NEO4J_CLIENT_ID and NEO4J_CLIENT_SECRET in .env
- Get these from https://console.neo4j.io -> API Credentials
"""

import sys
import os
import time
import requests
from requests.auth import HTTPBasicAuth
from pathlib import Path
from dotenv import load_dotenv, set_key

# Load environment
load_dotenv()
env_path = Path(__file__).parent / ".env"

print("=" * 80)
print("Neo4j Aura Instance Setup")
print("=" * 80)
print()

# Step 1: Get credentials
print("Step 1: Validate API Credentials")
print("-" * 80)

client_id = os.getenv("NEO4J_CLIENT_ID")
client_secret = os.getenv("NEO4J_CLIENT_SECRET")

if not client_id or not client_secret:
    print("✗ NEO4J_CLIENT_ID and NEO4J_CLIENT_SECRET not found in .env")
    print()
    print("To get API credentials:")
    print("  1. Go to https://console.neo4j.io")
    print("  2. Click your profile (top right)")
    print("  3. Select 'Account Settings'")
    print("  4. Go to 'API Credentials'")
    print("  5. Click 'Create API Credentials'")
    print("  6. Copy Client ID and Client Secret")
    print("  7. Add to .env:")
    print("     NEO4J_CLIENT_ID=your_client_id")
    print("     NEO4J_CLIENT_SECRET=your_client_secret")
    sys.exit(1)

print(f"Client ID: {client_id[:20]}...")
print()

# Step 2: Get OAuth token
print("Step 2: Get OAuth Token")
print("-" * 80)

try:
    token_response = requests.post(
        "https://api.neo4j.io/oauth/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"grant_type": "client_credentials"},
        auth=HTTPBasicAuth(client_id, client_secret),
        timeout=10
    )
    token_response.raise_for_status()
    access_token = token_response.json()["access_token"]
    print("✓ Got OAuth token")
except Exception as e:
    print(f"✗ Failed to get OAuth token: {e}")
    print()
    print("Possible issues:")
    print("  - Invalid CLIENT_ID or CLIENT_SECRET")
    print("  - Credentials expired (regenerate in Aura Console)")
    print("  - Network connectivity issues")
    sys.exit(1)

print()

# Step 3: Get projects
print("Step 3: Get Project ID")
print("-" * 80)

try:
    projects_response = requests.get(
        "https://api.neo4j.io/v1/projects",
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}"
        },
        timeout=10
    )
    projects_response.raise_for_status()
    projects = projects_response.json()["data"]
    
    if not projects:
        print("✗ No projects found")
        print("Please create a project in the Aura Console first")
        sys.exit(1)
    
    # Use first project
    project = projects[0]
    project_id = project["id"]
    project_name = project["name"]
    
    print(f"✓ Using project: {project_name}")
    print(f"  Project ID: {project_id}")
    
except Exception as e:
    print(f"✗ Failed to get projects: {e}")
    sys.exit(1)

print()

# Step 4: Check existing instances
print("Step 4: Check Existing Instances")
print("-" * 80)

try:
    instances_response = requests.get(
        "https://api.neo4j.io/v1/instances",
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}"
        },
        timeout=10
    )
    instances_response.raise_for_status()
    instances = instances_response.json()["data"]
    
    # Check for running instance
    running_instance = None
    for inst in instances:
        if inst.get("status") == "running" and inst.get("tenant_id") == project_id:
            running_instance = inst
            break
    
    if running_instance:
        print(f"✓ Found existing running instance: {running_instance['name']}")
        print(f"  ID: {running_instance['id']}")
        print(f"  Connection URI: {running_instance['connection_url']}")
        print()
        
        use_existing = input("Use existing instance? [Y/n]: ").strip().lower()
        if use_existing != 'n':
            # Use existing instance
            instance_id = running_instance['id']
            connection_url = running_instance['connection_url']
            username = running_instance.get('username', 'neo4j')
            
            print()
            print("⚠️  IMPORTANT: Password Required")
            print("=" * 80)
            print("You need the password for this existing instance.")
            print("If you don't have it, create a new instance instead.")
            print()
            password = input("Enter instance password (or press Enter to create new): ").strip()
            
            if password:
                # Configure with existing instance
                print()
                print("Step 5: Configure .env")
                print("-" * 80)
                
                set_key(env_path, "NEO4J_URI", connection_url)
                set_key(env_path, "NEO4J_USER", username)
                set_key(env_path, "NEO4J_PASSWORD", password)
                
                print("✓ Updated .env with existing instance credentials")
                print()
                print("=" * 80)
                print("Setup Complete!")
                print("=" * 80)
                print()
                print("Configuration:")
                print(f"  NEO4J_URI={connection_url}")
                print(f"  NEO4J_USER={username}")
                print(f"  NEO4J_PASSWORD=***")
                print()
                print("Test the connection:")
                print("  python test_direct_sync.py")
                sys.exit(0)
    
    print("Creating new instance...")
    
except Exception as e:
    print(f"⚠ Could not check existing instances: {e}")
    print("Proceeding with new instance creation...")

print()

# Step 5: Create new instance
print("Step 5: Create Neo4j Aura Instance")
print("-" * 80)

instance_name = f"lyzr-hackathon-{int(time.time())}"
print(f"Instance name: {instance_name}")

instance_config = {
    "version": "5",
    "region": "us-east-1",  # AWS US East (cheapest/fastest for most)
    "memory": "1GB",  # Free tier
    "name": instance_name,
    "type": "free",  # Free tier
    "tenant_id": project_id,
    "cloud_provider": "aws"
}

print("Creating instance (this takes ~2-3 minutes)...")
print()

try:
    create_response = requests.post(
        "https://api.neo4j.io/v1/instances",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}"
        },
        json=instance_config,
        timeout=30
    )
    create_response.raise_for_status()
    result = create_response.json()
    
    instance_id = result["data"]["id"]
    connection_url = result["data"]["connection_url"]
    username = result["data"]["username"]
    password = result["data"]["password"]  # Only returned on creation!
    
    print("✓ Instance created!")
    print(f"  ID: {instance_id}")
    print(f"  Connection URI: {connection_url}")
    print(f"  Username: {username}")
    print(f"  Password: {password}")
    print()
    print("⚠️  SAVE THIS PASSWORD - IT WON'T BE SHOWN AGAIN!")
    print()
    
except Exception as e:
    print(f"✗ Failed to create instance: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response: {e.response.text}")
    print()
    print("Possible issues:")
    print("  - Free tier limit reached (max 1 free instance)")
    print("  - Invalid project ID")
    print("  - API rate limiting")
    sys.exit(1)

# Step 6: Wait for instance to be ready
print("Step 6: Wait for Instance to be Ready")
print("-" * 80)

max_wait = 300  # 5 minutes
start_time = time.time()

while True:
    try:
        status_response = requests.get(
            f"https://api.neo4j.io/v1/instances/{instance_id}",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {access_token}"
            },
            timeout=10
        )
        status_response.raise_for_status()
        status_data = status_response.json()["data"]
        status = status_data.get("status")
        
        elapsed = int(time.time() - start_time)
        print(f"  [{elapsed}s] Status: {status}", end="\r")
        
        if status == "running":
            print()
            print("✓ Instance is running!")
            break
        
        if elapsed > max_wait:
            print()
            print("⚠ Timeout waiting for instance to start")
            print("Check status in Aura Console")
            break
        
        time.sleep(5)
        
    except Exception as e:
        print(f"\n⚠ Error checking status: {e}")
        time.sleep(5)

print()

# Step 7: Configure .env
print("Step 7: Configure .env File")
print("-" * 80)

try:
    set_key(env_path, "NEO4J_URI", connection_url)
    set_key(env_path, "NEO4J_USER", username)
    set_key(env_path, "NEO4J_PASSWORD", password)
    
    print("✓ Updated .env with Neo4j credentials")
    
except Exception as e:
    print(f"⚠ Could not update .env: {e}")
    print("Please manually add to .env:")
    print(f"  NEO4J_URI={connection_url}")
    print(f"  NEO4J_USER={username}")
    print(f"  NEO4J_PASSWORD={password}")

print()
print("=" * 80)
print("Setup Complete!")
print("=" * 80)
print()
print("Your Neo4j Aura Instance:")
print(f"  Name: {instance_name}")
print(f"  URI: {connection_url}")
print(f"  User: {username}")
print(f"  Password: {password}")
print()
print("Next Steps:")
print("  1. Test connection:")
print("     python test_direct_sync.py")
print()
print("  2. View in browser:")
print("     https://console.neo4j.io")
print()
print("  3. Run sync demo:")
print("     python test_direct_sync.py")
print()
print("⚠️  IMPORTANT: Save the password above - it cannot be recovered!")
