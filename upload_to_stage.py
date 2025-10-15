import os
import snowflake.connector

# Configuration
DB_NAME = "SUPERSUITE_DB"
SCHEMA_NAME = "SUPERSUITE_SCHEMA"
STAGE_NAME = "SUPERSUITE_STAGE"

def upload_files():
    print("🚀 Starting file upload to Snowflake stage...")
    try:
        conn = snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            database=DB_NAME,
            schema=SCHEMA_NAME,
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            insecure_mode=True  # Bypass SSL certificate issues
        )
        cur = conn.cursor()

        print("✅ Connected to Snowflake.")

        # Upload main file
        print("📤 Uploading main file...")
        cur.execute(f"PUT file://app/streamlit_app.py @{STAGE_NAME}/streamlit_app.py AUTO_COMPRESS=FALSE OVERWRITE=TRUE")
        print("✅ Main file uploaded.")

        # Upload code directory contents recursively
        print("📤 Uploading code directory...")
        # Since app/code is a symlink, we need to upload the target directory
        code_target = os.path.realpath("app/code")
        # Use recursive wildcard pattern to upload all files
        cur.execute(f"PUT file://{code_target}/** @{STAGE_NAME}/code AUTO_COMPRESS=FALSE OVERWRITE=TRUE")
        print("✅ Code directory uploaded.")

        print("🎉 Upload complete!")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    upload_files()