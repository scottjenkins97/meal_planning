import streamlit as st
from sqlalchemy import create_engine, MetaData
from sqlalchemy.sql import text, delete
import pandas as pd
from utils import generate_meal_graph, generate_meal_plan, insert_meals
import datetime as dt
import numpy as np


meal_plan_conn = st.connection(name = 'meal_plan_db', 
                               type = 'sql',
                               autocommit = True,
                               max_entries = 100,
                               ttl = 0)

# DATABASE_URL = 'sqlite:///meal_plan.db'  # Replace with your actual connection string
# engine = create_engine(DATABASE_URL)

# Unable to delete rows from the database
# Also want to view the tables in the database.

# Load Meal List from Spreadsheet
meal_df = pd.read_excel('meals.xlsx',sheet_name='meal_df')
# Generate meal graph
G = generate_meal_graph(meal_df=meal_df)

with st.form('Meal Planner Form'):
    st.write("Select Date Range for Meals")
    start_date = st.date_input("Meal Plan Start Date", dt.date.today(),key='start_date_selector')
    end_date = st.date_input("Meal Plan End Date", dt.date.today() + dt.timedelta(days=2),key = 'end_date_selector')
    if end_date < start_date:
        st.write("Error: Meal Plan can't end before it has started!")
    else:     
        # Create list of dates between start_date and end_date, and format
        date_list = pd.date_range(start_date, end_date, freq="D").strftime("%A %e %b %Y")
        number_of_meals = len(date_list)

    # Form submission button
    submitted = st.form_submit_button("Generate Meal Plan")

if submitted:
    meal_names = generate_meal_plan(meal_df, G, date_list)
    insert_meals(meal_plan_conn, date_list, meal_names)


