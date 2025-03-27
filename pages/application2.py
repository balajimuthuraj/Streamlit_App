import streamlit as st

import snowflake.connector

import pandas as pd



# Function to connect to Snowflake

def get_snowflake_connection():

    return snowflake.connector.connect(

        user="ADMINSNOWTEST",

        password="Preferhub@00000",  # Replace with your Snowflake password

        account="aab21259.us-east-1",

        role="ACCOUNTADMIN",

        database="my_db1",

        schema="my_sch1",

        warehouse="my_wh1"

    )



# Streamlit App

st.title("Snowflake Data Dashboard")



try:

    # Connect to Snowflake

    conn = get_snowflake_connection()

    

    # Fetch data from both tables

    st.subheader("Fetching data from Water_consumption")

    sales_data_query = "SELECT * FROM Water_consumption"

    sales_data = pd.read_sql_query(sales_data_query, conn)

    st.dataframe(sales_data)

    

    st.subheader("Fetching data from Water_consumption")

    sales_data1_query = "SELECT * FROM water_consumption"

    sales_data1 = pd.read_sql_query(sales_data1_query, conn)

    st.dataframe(sales_data1)



except Exception as e:

    st.error(f"❌ Failed to connect to Snowflake: {e}")



finally:

    # Close connection

    if 'conn' in locals():

        conn.close()

