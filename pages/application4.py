import streamlit as st
from streamlit_ace import st_ace  # Code editor with syntax highlighting
import os
import json
import time
import subprocess
import pandas as pd
import snowflake.connector
from sqlalchemy import create_engine

# File for simulating Azure Storage (Replace this with actual Azure Cosmos DB/Blob Storage)
STORAGE_FILE = "app_data.json"
PAGES_DIRECTORY = "pages"  # Directory where dynamically created apps are stored

# Initialize storage file and pages directory
if not os.path.exists(STORAGE_FILE):
    with open(STORAGE_FILE, "w") as f:
        json.dump({}, f)

if not os.path.exists(PAGES_DIRECTORY):
    os.makedirs(PAGES_DIRECTORY)

# Load and save app data functions
def load_app_data():
    with open(STORAGE_FILE, "r") as f:
        return json.load(f)

def save_app_data(data):
    with open(STORAGE_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Trigger deployment (Saves the app in the pages/ directory)
def trigger_deployment(app_name, app_content):
    app_file = f"{PAGES_DIRECTORY}/{app_name}.py"
    with open(app_file, "w", encoding="utf-8") as f:  # Specify UTF-8 encoding
        f.write(app_content)
    return f"{app_name}.py has been successfully created in the {PAGES_DIRECTORY}/ directory!"

# Timestamp for tracking updates
def format_timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

# Streamlit Configuration
st.set_page_config(page_title="Preferhub App Manager", layout="wide")
st.markdown(
    """
    <div style="text-align: center;">
        <img src="https://preferhub.com/wp-content/uploads/2024/09/logo-preferhun.png" alt="Company Logo" width="200">
    </div>
    """,
    unsafe_allow_html=True
)

# Load stored apps
app_data = load_app_data()

# Sidebar Navigation
menu = st.sidebar.radio(
    "Navigation",
    [
        "🛠️ Advanced App Creator",
        "📂 View/Edit Apps",
        "🔍 Search Apps",
        "ℹ️ About & How to Use",
    ]
)

if menu == "🛠️ Advanced App Creator":
    st.header("Create a New Application")

    app_name = st.text_input("Application Name (no spaces, use underscores)")
    app_tags = st.text_input("Tags (comma-separated, e.g., AI, Analytics)")
    app_description = st.text_area("Application Description")

    # Dataset or Database Connection Option
    st.subheader("Choose Data Source")
    data_source = st.radio(
        "Select Data Source",
        ("Upload Dataset", "Connect to Snowflake", "Connect to MySQL", "Connect to Oracle"),
    )

    file_path = None
    df = None

    if data_source == "Upload Dataset":
        uploaded_file = st.file_uploader("Choose a CSV, Excel, or JSON file", type=["csv", "xlsx", "json"])
        if uploaded_file:
            UPLOAD_DIRECTORY = "uploads"
            if not os.path.exists(UPLOAD_DIRECTORY):
                os.makedirs(UPLOAD_DIRECTORY)
            file_path = os.path.join(UPLOAD_DIRECTORY, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"✅ Uploaded file saved as: `{file_path}`")
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(file_path)
            elif uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(file_path)
            elif uploaded_file.name.endswith(".json"):
                df = pd.read_json(file_path)

    elif data_source == "Connect to Snowflake":
        st.subheader("Snowflake Connection")
        sf_account = st.text_input("Account", value="npb81819.us-east-1")
        sf_user = st.text_input("User", value="STselvan2511")
        sf_password = st.text_input("Password", type="password")
        sf_role = st.text_input("Role", value="AZURE_STREAMLIT")
        sf_database = st.text_input("Database", value="AZURESTREAMLIT")
        sf_schema = st.text_input("Schema", value="AZURE_STREAMLIT")
        sf_warehouse = st.text_input("Warehouse", value="Azurestreamlit")
        sf_query = st.text_area("SQL Query")

        if st.button("Connect to Snowflake"):
            try:
                conn = snowflake.connector.connect(
                    user=sf_user,
                    password=sf_password,
                    account=sf_account,
                    role=sf_role,
                    database=sf_database,
                    schema=sf_schema,
                    warehouse=sf_warehouse,
                )
                df = pd.read_sql(sf_query, conn)
                st.success("✅ Connected to Snowflake successfully!")
                conn.close()  # Close the connection after use
            except Exception as e:
                st.error(f"❌ Connection failed: {e}")

    # File Upload Section for requirements.txt (Moved Above the Code Editor)
    st.subheader("Upload requirements.txt")
    uploaded_requirements = st.file_uploader("Upload requirements.txt file", type="txt")
    if uploaded_requirements:
        # Save the file locally
        with open("requirements.txt", "wb") as f:
            f.write(uploaded_requirements.getbuffer())
        st.success("requirements.txt uploaded successfully.")

        # Install the dependencies
        try:
            subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
            st.success("All libraries installed successfully.")
        except Exception as e:
            st.error(f"Error installing libraries: {e}")

    # Code Editor
    st.subheader("Code Editor")
    default_code = """
import streamlit as st
import snowflake.connector
import pandas as pd

try:
    # Connect to Snowflake
    conn = snowflake.connector.connect(
        user="STselvan2511",
        password="XXXXXX",  # Replace with your Snowflake password
        account="npb81819.us-east-1",
        role="AZURE_STREAMLIT",
        database="AZURESTREAMLIT",
        schema="AZURE_STREAMLIT",
        warehouse="Azurestreamlit"
    )
    
    # SQL Query
    sf_query = "SELECT * FROM "
    df = pd.read_sql(sf_query, conn)
 
    conn.close()

except Exception as e:
    st.error(f"❌ Failed to connect to Snowflake: {e}")


""".strip()

    if df is not None:
        st.session_state["data"] = df  # Store data in session state
        st.dataframe(df)  # Display dataframe preview

    app_content = st_ace(
        language="python",
        theme="monokai",
        value=default_code,
        placeholder="# Write your Streamlit Python code here...",
    )

    if st.button("Save and Deploy"):
        if not app_name.strip():
            st.error("❌ Application Name is required.")
        elif " " in app_name:
            st.error("❌ Application Name cannot contain spaces. Use underscores instead.")
        elif app_name in app_data:
            st.error("❌ Application with this name already exists.")
        else:
            # Save app metadata
            app_data[app_name] = {
                "tags": [tag.strip() for tag in app_tags.split(",")],
                "description": app_description,
                "content": app_content,
                "created_at": format_timestamp(),
                "last_updated": format_timestamp(),
                "data_source": data_source,
            }

        # Include Snowflake configuration if data source is Snowflake
        if data_source == "Connect to Snowflake":
            snowflake_config = {
                "user": sf_user,
                "password": sf_password,
                "account": sf_account,
                "role": sf_role,
                "database": sf_database,
                "schema": sf_schema,
                "warehouse": sf_warehouse,
            }
            app_data[app_name]["snowflake_config"] = snowflake_config



        # Save the app and deploy it
        save_app_data(app_data)
        deployment_status = trigger_deployment(app_name, app_content)
        st.success(f"✅ Application saved and deployed! {deployment_status}")

        # Add "Run Application" button
        if st.button("Run Application"):
            app_url = f"/{PAGES_DIRECTORY}/{app_name}.py"
            st.success(f"🚀 Open the app: [Click Here]({app_url})")


elif menu == "📂 View/Edit Apps":
    st.header("View and Edit Existing Applications")

    if not app_data:
        st.warning("⚠️ No applications found. Please create a new application first.")
    else:
        selected_app = st.selectbox("Select Application", sorted(app_data.keys()))

        if selected_app:
            app = app_data[selected_app]

            st.subheader(f"Editing: **{selected_app}**")
            app_tags = st.text_input(
                "Tags (comma-separated)", value=", ".join(app["tags"])
            )
            app_description = st.text_area("Application Description", value=app["description"])
            app_content = st_ace(
                language="python",
                theme="monokai",
                value=app["content"],
            )

            # Show Snowflake Connection Details if the app uses Snowflake
            if app["data_source"] == "Connect to Snowflake":
                st.subheader("Snowflake Connection Details")
                snowflake_config = app.get("snowflake_config", {})
                for key in ["user", "password", "account", "role", "database", "schema", "warehouse"]:
                    snowflake_config[key] = st.text_input(key.capitalize(), value=snowflake_config.get(key, ""))

                if st.button("Reconnect to Snowflake"):
                    try:
                        conn = snowflake.connector.connect(
                            user=snowflake_config.get("user"),
                            password=snowflake_config.get("password"),
                            account=snowflake_config.get("account"),
                            role=snowflake_config.get("role"),
                            database=snowflake_config.get("database"),
                            schema=snowflake_config.get("schema"),
                            warehouse=snowflake_config.get("warehouse"),
                        )
                        st.success("✅ Snowflake reconnected successfully!")
                        conn.close()
                    except snowflake.connector.errors.Error as e:
                        st.error(f"❌ Failed to reconnect to Snowflake: {e}")
                    except Exception as e:
                        st.error(f"❌ Unexpected error: {e}")

            # Show and edit previously uploaded requirements.txt
            st.subheader("Manage Dependencies")
            requirements_file = app.get("requirements_file", "requirements.txt")
            if os.path.exists(requirements_file):
                with open(requirements_file, "r") as f:
                    requirements_content = f.read()
                updated_requirements = st.text_area(
                    "Edit requirements.txt", value=requirements_content, height=200
                )

                if st.button("Reinstall Requirements"):
                    with open(requirements_file, "w") as f:
                        f.write(updated_requirements)
                    try:
                        subprocess.check_call(["pip", "install", "-r", requirements_file])
                        st.success("✅ Libraries reinstalled successfully!")
                    except subprocess.CalledProcessError as e:
                        st.error(f"❌ Failed to install libraries: {e}")
                    except Exception as e:
                        st.error(f"❌ Unexpected error: {e}")
            else:
                st.warning("⚠️ No requirements.txt file found for this application.")

            # Update the application and save changes
            if st.button("Update Application"):
                app["tags"] = [tag.strip() for tag in app_tags.split(",")]
                app["description"] = app_description
                app["content"] = app_content
                if app["data_source"] == "Connect to Snowflake":
                    app["snowflake_config"] = snowflake_config
                app["last_updated"] = format_timestamp()
                save_app_data(app_data)
                trigger_deployment(selected_app, app_content)
                st.success("✅ Application updated successfully!")

            # Delete Application
            if st.button("Delete Application"):
                del app_data[selected_app]
                save_app_data(app_data)
                os.remove(f"{PAGES_DIRECTORY}/{selected_app}.py")  # Delete the app file
                if os.path.exists(requirements_file):
                    os.remove(requirements_file)  # Delete associated requirements file
                st.success("✅ Application deleted successfully.")
                st.experimental_rerun()



elif menu == "🔍 Search Apps":
    st.header("Search Applications")

    search_term = st.text_input("Search by Name, Tag, or Description")
    search_results = [
        app_name
        for app_name, app_details in app_data.items()
        if search_term.lower() in app_name.lower()
        or any(search_term.lower() in tag.lower() for tag in app_details["tags"])
        or search_term.lower() in app_details["description"].lower()
    ]

    if search_results:
        st.subheader("Search Results")
        for app_name in search_results:
            st.markdown(f"- **{app_name}**: {app_data[app_name]['description']}")
    else:
        if search_term:
            st.warning("⚠️ No matching applications found.")

elif menu == "ℹ️ About & How to Use":
    st.header("QuickStart Guide")
    st.markdown(
        """
        ### About
        - **Purpose**: This app provides a user-friendly interface for managing and deploying multiple Streamlit apps with an advanced UI.
        - **App Structure & Layout**:
            - **Advanced App Creator**: Create new applications by providing an app name, description, tags, and selecting a data source.
            - **View/Edit Apps**: View and edit previously created apps.
            - **Search Apps**: Easily search through existing applications.
            - **About & How to Use**: Provides general information and guidance on using the app.

        ### Key Features:
        - **Application Creation**:
            - Choose a name, description, and tags for your app.
            - Select your data source (CSV, Excel, JSON, or databases like Snowflake and Oracle).
        - **Advanced Code Editor**: Write and edit Python code with syntax highlighting using the built-in code editor (st_ace).
        - **Data Source Integration**:
            - Upload datasets in CSV, Excel, or JSON formats.
            - Connect to Snowflake or Oracle databases to fetch data via SQL queries.
        - **Dynamic Deployment & Running**:
            - After creating your app, it is saved as a `.py` file and can be deployed with a generated URL.
        - **Requirements Management**:
            - Upload a `requirements.txt` file to install dependencies automatically for your app.
        - **App Viewing & Editing**:
            - Modify app metadata, code, and manage the connected database configurations after deployment.
            - Edit SQL queries for Snowflake or Oracle databases.

        ### How to Use
        1. **Navigate to Advanced App Creator**:
            - Enter your app's name, description, and tags.
            - Choose a data source (upload a file or connect to a database).
            - Optionally, upload a `requirements.txt` file to manage dependencies.
        2. **Write and Edit Code**:
            - Use the built-in code editor to write or modify Python code for your app.
        3. **Deploy Your Application**:
            - Once the app is ready, click "Save and Deploy" to make it live. You will receive a URL to access your app.
        4. **View/Edit Existing Apps**:
            - Manage previously created apps by viewing and editing metadata, code, or database connections.
        5. **Search for Apps**:
            - Use the **🔍 Search Apps** feature to find applications by name, tags, or descriptions.
        6. **Preview Data**:
            - After uploading a file or connecting to a database, you can preview the first few rows of data.
        7. **Error Handling & Guidance**:
            - The app provides error handling and user guidance, including helpful tooltips to avoid common mistakes.
        8. **Security Considerations**:
            - For production use, ensure that database credentials (for Snowflake, Oracle, etc.) are securely handled via environment variables or encrypted configurations.
        """
    )