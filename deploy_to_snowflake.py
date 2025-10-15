
import os
import snowflake.connector
from snowflake.connector.errors import ProgrammingError

# --- Configuration ---
DB_NAME = "SUPERSUITE_DB"
SCHEMA_NAME = "SUPERSUITE_SCHEMA"
STAGE_NAME = "SUPERSUITE_STAGE"
APP_NAME = "SUPERSUITE_APP"
WAREHOUSE_NAME = "lyzr"

DEPLOYMENT_DIR = os.path.abspath("snowflake_deployment")

def main():
    """
    Connects to Snowflake and deploys the Streamlit application.
    """
    print("🚀 Starting programmatic deployment to Snowflake...")
    try:
        print("1. Connecting to Snowflake...")
        conn = snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
        )
        print("   ✅ Connection successful.")
        cur = conn.cursor()

        print(f"2. Setting up Database ({DB_NAME}), Schema ({SCHEMA_NAME}), and Stage ({STAGE_NAME})...")
        cur.execute(f"CREATE OR REPLACE DATABASE {DB_NAME};")
        cur.execute(f"USE DATABASE {DB_NAME};")
        cur.execute(f"CREATE OR REPLACE SCHEMA {SCHEMA_NAME};")
        cur.execute(f"USE SCHEMA {SCHEMA_NAME};")
        cur.execute(f"CREATE OR REPLACE STAGE {STAGE_NAME};")
        print("   ✅ Environment setup complete.")

        # --- Step 3: Upload Files and Directories Separately ---
        print(f"3. Uploading files from '{DEPLOYMENT_DIR}' to stage '{STAGE_NAME}'...")

        # Upload loose files in the root of the deployment directory
        root_files_path = os.path.join(DEPLOYMENT_DIR, "*.*")
        if os.name == 'nt':
            root_files_path = root_files_path.replace('\\', '\\\\')

        put_root_command = f"PUT file://{root_files_path} @{STAGE_NAME}/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE"
        print(f"   Executing: {put_root_command}")
        cur.execute(put_root_command)
        print("   ✅ Root files uploaded successfully.")

        # Upload the 'code' directory recursively to the stage root
        code_dir_path = os.path.join(DEPLOYMENT_DIR, "code")
        if os.name == 'nt':
            code_dir_path = code_dir_path.replace('\\', '\\\\')

        put_code_dir_command = f"PUT file://{code_dir_path} @{STAGE_NAME}/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE"
        print(f"   Executing: {put_code_dir_command}")
        cur.execute(put_code_dir_command)
        print("   ✅ 'code' directory uploaded successfully.")

        # --- Step 4: Create Streamlit Application ---
        print(f"4. Creating Streamlit application '{APP_NAME}'...")
        create_app_sql = f'''
        CREATE OR REPLACE STREAMLIT {APP_NAME}
          FROM '@{STAGE_NAME}'
          MAIN_FILE = '/streamlit_app.py'
          QUERY_WAREHOUSE = {WAREHOUSE_NAME};
        '''
        cur.execute(create_app_sql)
        print("   ✅ Streamlit application created successfully.")

        # --- Step 5: Verification ---
        print("5. Verifying deployment...")
        cur.execute(f"SHOW STREAMLITS LIKE '{APP_NAME}';")
        result = cur.fetchone()
        if result:
            print(f"   ✅ Verification successful. Found Streamlit app: {result[1]}")
            print("\n🎉 Deployment Complete! 🎉")
            print(f"You can now access your application in the 'Streamlit' section of Snowsight.")
        else:
            print("   ❌ Verification failed. Could not find the deployed Streamlit app.")

    except ProgrammingError as e:
        print(f"❌ An error occurred: {e}")
        print("   Please ensure your Snowflake credentials (SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_ACCOUNT) are set correctly as environment variables.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            print("\nConnection to Snowflake closed.")

if __name__ == "__main__":
    main()
