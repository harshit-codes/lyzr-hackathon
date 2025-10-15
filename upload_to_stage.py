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

        # Note: Code directory is now uploaded via Snowflake CLI in the workflow
        print("📤 Code directory will be uploaded via Snowflake CLI...")

        print("🎉 Upload complete!")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    upload_files()