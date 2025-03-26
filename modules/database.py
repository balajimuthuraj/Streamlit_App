import os
import snowflake.connector
from dotenv import load_dotenv

# ✅ Load environment variables from .env
load_dotenv()

def get_snowflake_connection():
    try:
        conn = snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            role=os.getenv("SNOWFLAKE_ROLE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA")
        )
        print("✅ Snowflake Connection Successful!")
        return conn
    except Exception as e:
        print(f"❌ Snowflake Connection Failed: {e}")
        return None
