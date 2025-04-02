import streamlit as st
import pandas as pd
import snowflake.connector
import plotly.express as px
from modules.database import get_snowflake_connection  # Ensure this module exists

# ---- Streamlit App ----
st.set_page_config(page_title="Water Consumption Dashboard", layout="wide")
st.title("💧 Water Consumption Dashboard")

# ---- Snowflake Connection ----
conn = get_snowflake_connection()

if conn:
    st.success("✅ Connected to Snowflake")

    # Fetch Data
    query = "SELECT * FROM water_consumption"
    df = pd.read_sql(query, conn)

    # Convert column names to lowercase for consistency
    df.columns = df.columns.str.lower()

    # ✅ Debug: Display DataFrame
    st.write("### Sample Data from Snowflake:")
    st.dataframe(df)

    # ✅ Ensure required columns exist
    required_columns = [
        "area_code", "monthly_consumption", "main_device_release", "leakage"
    ]
    missing_cols = [col for col in required_columns if col not in df.columns]

    if missing_cols:
        st.error(f"❌ Missing columns: {missing_cols}. Please check your database schema.")
    else:
        # ---- Sidebar Filters ----
        st.sidebar.header("🔍 Filters")

        # ✅ Area Code Filter
        selected_areas = st.sidebar.multiselect(
            "Select Area Code(s)", options=df["area_code"].unique(), default=df["area_code"].unique()
        )

        # ✅ Monthly Water Consumption Filter
        min_val, max_val = int(df["monthly_consumption"].min()), int(df["monthly_consumption"].max())
        water_range = st.sidebar.slider(
            "Monthly Water Consumption Range", min_val, max_val, (min_val, max_val)
        )

        # ✅ Leakage Filter
        min_leak, max_leak = int(df["leakage"].min()), int(df["leakage"].max())
        leak_range = st.sidebar.slider(
            "Leakage Range", min_leak, max_leak, (min_leak, max_leak)
        )

        # ---- Apply Filters ----
        filtered_df = df[
            (df["area_code"].isin(selected_areas)) &
            (df["monthly_consumption"].between(water_range[0], water_range[1])) &
            (df["leakage"].between(leak_range[0], leak_range[1]))
        ]

        # ✅ Debug: Display Filtered DataFrame
        st.write("### Filtered Data")
        st.dataframe(filtered_df)

        # ---- Bar Chart: Monthly Water Consumption by Area ----
        st.subheader("📊 Monthly Water Consumption by Area")
        fig1 = px.bar(filtered_df, x="area_code", y="monthly_consumption", color="area_code",
                      title="Monthly Water Consumption by Area", barmode="group")
        st.plotly_chart(fig1)

        # ---- Scatter Plot: Leakage vs Monthly Water Consumption ----
        st.subheader("🔍 Leakage vs Monthly Water Consumption")
        fig2 = px.scatter(filtered_df, x="monthly_consumption", y="leakage", color="area_code",
                          title="Leakage vs Monthly Water Consumption", size="leakage")
        st.plotly_chart(fig2)

        # ---- Pie Chart: Percentage of Total Water Consumption by Area ----
        #st.subheader("🍩 Total Water Consumption by Area")
        #df_grouped = filtered_df.groupby("area_code")["monthly_consumption"].sum().reset_index()
        #fig3 = px.pie(df_grouped, names="area_code", values="monthly_consumption",
        #              title="Percentage of Total Water Consumption by Area")
        #st.plotly_chart(fig3)

        # ---- Box Plot: Distribution of Monthly Water Consumption ----
        st.subheader("📦 Monthly Water Consumption Distribution")
        fig4 = px.box(filtered_df, x="area_code", y="monthly_consumption", color="area_code",
                      title="Distribution of Monthly Water Consumption")
        st.plotly_chart(fig4)

        # ---- Histogram: Leakage Distribution ----
        st.subheader("📊 Leakage Distribution")
        fig5 = px.histogram(filtered_df, x="leakage", nbins=10, color="area_code",
                            title="Leakage Distribution by Area", barmode="overlay")
        st.plotly_chart(fig5)

    # Close Connection
    conn.close()

else:
    st.error("❌ Failed to connect to Snowflake")
