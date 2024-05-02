import streamlit as st
import pandas as pd
import datetime as dt

from utils import generate_meal_graph, generate_meal_plan, insert_meals

# if not st.session_state.get('authentication_status', False):
#     st.info('Please Login from the Home page and try again.')
#     st.stop()

if not st.session_state.get("password_correct"):
    st.info('Please Login from the Home page and try again.')
    st.stop()  # Do not continue

# Initialise connection to sqlite database
meal_plan_conn = st.connection(name = 'meal_plan_db', 
                            type = 'sql',
                            autocommit = True,
                            max_entries = 100,
                            ttl = 0)

# Load Meal List from Spreadsheet
meal_df = pd.read_excel('meals.xlsx',sheet_name='meal_df')
# Generate meal graph
G = generate_meal_graph(meal_df=meal_df)

# Form to select meal plan date range
with st.form('meal_plan_date_selector_form'):
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
    # Generate the meal plan using logic on meal graph G
    meal_names = generate_meal_plan(meal_df, G, date_list)
    # Insert meal plan into meal_plan database table
    insert_meals(meal_plan_conn, date_list, meal_names, verbose=True)




