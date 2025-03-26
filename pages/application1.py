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

    try:
        # Fetch Data
        query = "SELECT * FROM water_consumption"
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()

        # Fetch column names
        columns = [desc[0].lower() for desc in cursor.description]  # Convert to lowercase
        df = pd.DataFrame(data, columns=columns)

        # ✅ Ensure correct column names exist
        expected_columns = [
            "user_id", "user_name", "area_code", "device_id", "hourly_consumption", "daily_consumption",
            "monthly_consumption", "yearly_consumption", "leakage", "main_device_release"
        ]
        missing_cols = [col for col in expected_columns if col not in df.columns]

        if missing_cols:
            st.error(f"❌ Missing columns: {missing_cols}. Please check your database schema.")
        else:
            # ✅ Debug: Display Sample Data
            st.write("### Sample Data from Snowflake:")
            st.dataframe(df.head())

            # ---- Bar Chart: Monthly Water Consumption by Area ----
            st.subheader("📊 Monthly Water Consumption by Area")
            fig1 = px.bar(df, x="area_code", y="monthly_consumption", color="area_code",
                          title="Monthly Water Consumption by Area", barmode="group")
            st.plotly_chart(fig1, use_container_width=True)

            # ---- Line Chart: Yearly Water Consumption by Area ----
            st.subheader("📈 Yearly Water Consumption by Area")
            fig2 = px.line(df, x="area_code", y="yearly_consumption", color="area_code",
                           title="Yearly Water Consumption Trend", markers=True)
            st.plotly_chart(fig2, use_container_width=True)

            # ---- Scatter Plot: Leakage vs Monthly Consumption ----
            st.subheader("🔍 Leakage vs Monthly Water Consumption")
            fig3 = px.scatter(df, x="monthly_consumption", y="leakage", color="area_code",
                              title="Leakage vs Monthly Water Consumption", size="leakage")
            st.plotly_chart(fig3, use_container_width=True)

            # ---- Pie Chart: Total Water Consumption by Area ----
            st.subheader("🍩 Total Water Consumption by Area")
            df_grouped = df.groupby("area_code", as_index=False)["monthly_consumption"].sum()
            fig4 = px.pie(df_grouped, names="area_code", values="monthly_consumption",
                          title="Percentage of Total Water Consumption by Area")
            st.plotly_chart(fig4, use_container_width=True)

            # ---- Box Plot: Hourly Consumption Distribution ----
            st.subheader("📦 Hourly Water Consumption Distribution")
            fig5 = px.box(df, x="area_code", y="hourly_consumption", color="area_code",
                          title="Distribution of Hourly Water Consumption")
            st.plotly_chart(fig5, use_container_width=True)

            # ---- Histogram: Leakage Distribution ----
            st.subheader("📊 Leakage Distribution")
            fig6 = px.histogram(df, x="leakage", nbins=10, color="area_code",
                                title="Leakage Distribution by Area", barmode="overlay")
            st.plotly_chart(fig6, use_container_width=True)

            # ---- Bar Chart: Main Device Release per Area ----
            st.subheader("🚰 Main Device Release by Area")
            fig7 = px.bar(df, x="area_code", y="main_device_release", color="area_code",
                          title="Main Device Release by Area")
            st.plotly_chart(fig7, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error fetching data: {e}")

    finally:
        # Close Connection
        conn.close()
else:
    st.error("❌ Failed to connect to Snowflake")
