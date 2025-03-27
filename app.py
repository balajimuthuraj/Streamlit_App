import streamlit as st
import os

# Ensure set_page_config is the FIRST command
st.set_page_config(page_title="Project Dashboard", layout="wide")

# Display centered logo
st.markdown(
    """
    <div style="text-align: center;">
        <img src="https://cdni.iconscout.com/illustration/premium/thumb/smart-alternative-energy-illustration-download-in-svg-png-gif-file-formats--source-eco-friendly-green-industrial-pack-science-technology-illustrations-4816401.png?f=webp" alt="Company Logo" width="200">
    </div>
    """,
    unsafe_allow_html=True
)

st.title("Project Dashboard")

#  Get available project dashboards from 'pages/' directory
if not os.path.exists("pages"):
    st.error(" 'pages/' directory not found. Create it and add project files.")
else:
    project_files = [f.replace(".py", "") for f in os.listdir("pages") if f.endswith(".py")]

    if not project_files:
        st.warning(" No projects found in 'pages/' directory.")
    else:
        selected_project = st.selectbox("Select a Project", sorted(project_files))

        if selected_project:
            st.markdown(f"## Launch: **{selected_project}**")

            if st.button("Open Project Dashboard"):
                project_file = f"pages/{selected_project}.py"

                try:
                    with open(project_file, "r", encoding="utf-8") as f:
                        project_code = f.read()

                    #  Remove `st.set_page_config()` from dynamically loaded script
                    project_code = "\n".join(
                        line for line in project_code.split("\n") if "st.set_page_config" not in line
                    )

                    exec(project_code, globals())  # Execute the script safely
                except Exception as e:
                    st.error(f" Error loading project: {e}") #testing purpose

######
