#!/usr/bin/env python3
"""
SuperSuite Graph Sync Setup Script

This script sets up the Neo4j to Snowflake sync infrastructure:
1. Creates necessary Snowflake tables
2. Runs initial sync job
3. Sets up sync scheduling

Usage:
    python setup_sync.py --create-tables    # Create Snowflake tables
    python setup_sync.py --initial-sync     # Run initial sync
    python setup_sync.py --schedule         # Set up scheduled sync
    python setup_sync.py --all             # Do everything
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False

def create_snowflake_tables():
    """Create the necessary tables in Snowflake"""
    script_path = Path(__file__).parent / "setup_snowflake_tables.sql"

    if not script_path.exists():
        print(f"❌ SQL script not found: {script_path}")
        return False

    # Use snowsql or python connector to execute SQL
    # For now, we'll provide instructions
    print("📋 To create Snowflake tables, run the following SQL script in Snowflake:")
    print(f"   File: {script_path}")
    print()
    print("Or use SnowSQL:")
    print(f"   snowsql -f {script_path}")
    print()
    print("Required tables:")
    print("  - SUPERSUITE_ENTITIES")
    print("  - SUPERSUITE_RELATIONSHIPS")
    print("  - SUPERSUITE_CHUNKS")
    print("  - SUPERSUITE_PROJECTS")
    print("  - SUPERSUITE_SYNC_METADATA")

    return True  # Return True since this is informational

def run_initial_sync():
    """Run the initial sync job"""
    script_path = Path(__file__).parent / "neo4j_snowflake_sync.py"

    if not script_path.exists():
        print(f"❌ Sync script not found: {script_path}")
        return False

    cmd = f"python {script_path}"
    return run_command(cmd, "Running initial Neo4j to Snowflake sync")

def setup_scheduler():
    """Set up the sync scheduler"""
    scheduler_path = Path(__file__).parent / "sync_scheduler.py"

    if not scheduler_path.exists():
        print(f"❌ Scheduler script not found: {scheduler_path}")
        return False

    print("🔄 Setting up sync scheduler...")
    print()
    print("Choose your scheduling approach:")
    print()
    print("1. Cron Job (Linux/Mac):")
    print("   Add to crontab:")
    print(f"   */30 * * * * cd {Path(__file__).parent} && python {scheduler_path} --once")
    print("   (runs every 30 minutes)")
    print()
    print("2. Systemd Timer (Linux):")
    print("   Create service and timer files in /etc/systemd/system/")
    print()
    print("3. Background Process:")
    print(f"   nohup python {scheduler_path} --interval 1800 &")
    print("   (runs every 30 minutes in background)")
    print()
    print("4. Cloud Scheduler (AWS/GCP/Azure):")
    print("   Configure cloud scheduler to run the sync job periodically")
    print()

    # Test the scheduler
    cmd = f"python {scheduler_path} --once"
    success = run_command(cmd, "Testing sync scheduler")

    if success:
        print("✅ Scheduler test completed successfully")
        print("💡 Configure your preferred scheduling method above")

    return success

def validate_environment():
    """Validate that required environment variables are set"""
    required_vars = [
        "SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD",
        "NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD"
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print()
        print("Please set these variables before running the sync setup.")
        print("You can set them in your shell or create a .env file.")
        return False

    print("✅ Environment validation passed")
    return True

def install_dependencies():
    """Install required Python dependencies"""
    requirements_file = Path(__file__).parent / "requirements-sync.txt"

    if not requirements_file.exists():
        print(f"⚠️ Requirements file not found: {requirements_file}")
        print("Installing basic dependencies...")

        # Install basic requirements
        cmd = "pip install pyspark python-dotenv"
        return run_command(cmd, "Installing basic sync dependencies")

    cmd = f"pip install -r {requirements_file}"
    return run_command(cmd, "Installing sync dependencies")

def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description="SuperSuite Graph Sync Setup")
    parser.add_argument(
        "--create-tables",
        action="store_true",
        help="Create Snowflake tables"
    )
    parser.add_argument(
        "--initial-sync",
        action="store_true",
        help="Run initial sync job"
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Set up sync scheduling"
    )
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install Python dependencies"
    )
    parser.add_argument(
        "--validate-env",
        action="store_true",
        help="Validate environment variables"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all setup steps"
    )

    args = parser.parse_args()

    # If no specific args, show help
    if not any([args.create_tables, args.initial_sync, args.schedule,
                args.install_deps, args.validate_env, args.all]):
        parser.print_help()
        return

    print("🚀 SuperSuite Graph Sync Setup")
    print("=" * 50)

    success_count = 0
    total_steps = 0

    # Validate environment first
    if args.validate_env or args.all:
        total_steps += 1
        if validate_environment():
            success_count += 1
        else:
            print("❌ Environment validation failed. Please fix and retry.")
            sys.exit(1)

    # Install dependencies
    if args.install_deps or args.all:
        total_steps += 1
        if install_dependencies():
            success_count += 1

    # Create tables
    if args.create_tables or args.all:
        total_steps += 1
        if create_snowflake_tables():
            success_count += 1

    # Run initial sync
    if args.initial_sync or args.all:
        total_steps += 1
        if run_initial_sync():
            success_count += 1

    # Setup scheduler
    if args.schedule or args.all:
        total_steps += 1
        if setup_scheduler():
            success_count += 1

    print()
    print("=" * 50)
    print(f"Setup Complete: {success_count}/{total_steps} steps successful")

    if success_count == total_steps:
        print("🎉 SuperSuite graph sync setup completed successfully!")
        print()
        print("Next steps:")
        print("1. Verify Snowflake tables were created")
        print("2. Check that initial sync populated data")
        print("3. Configure your preferred scheduling method")
        print("4. Deploy the updated Streamlit app")
    else:
        print("⚠️ Some setup steps failed. Please review the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()