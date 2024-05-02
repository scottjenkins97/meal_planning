import streamlit as st
import pandas as pd
from utils import insert_meals, get_latest_meal_plan
import numpy as np


# Load excel sheet of meals
meal_df = pd.read_excel('meals.xlsx',sheet_name='meal_df')

st.cache_data.clear()
meal_plan_conn = st.connection(name = 'meal_plan_db', 
                               type = 'sql',
                               autocommit = True,
                               max_entries = 100,
                               ttl = 0)

# Play with the args: https://docs.streamlit.io/develop/api-reference/connections/st.connection

# Source latest meal plan with utils function
db_meals, meal_dates, meal_names = get_latest_meal_plan(meal_plan_conn)

# Create a form with drop down boxes to edit each meal suggestion
with st.form('Meal Confirmation Form'):
    st.write('Meal suggestions generated. Please confirm selection, or edit below...')
    for i in range(len(db_meals)):
        # Drop downs for each date
        meal_date = meal_dates[i]
        meal_suggestion = meal_names[i]
        meal_index = list(meal_df['meal_name']).index(meal_suggestion)
        if i not in st.session_state:
            st.session_state[i] = meal_index
            # pre-populate with index equal to the meal suggestion
            option = st.selectbox(label = f'{meal_date} Meal:',
                        key = meal_date,
                        options = (np.array(meal_df['meal_name'])),
                        index = meal_index,
                        )
        else:
            # If user edits meal plan, do not rerun suggestions for all other meals. 
            # That is, do not change the session_state / reset the dropdown option)
            option = st.selectbox(label = f'{meal_date} Meal:',
                                key = meal_date,
                                options = (np.array(meal_df['meal_name'])),
                                index = st.session_state[i],
                                )
            # Update the list of meal names with the users selections
            meal_names[i] = option         
    submitted = st.form_submit_button("Confirm Meal Plan")

if submitted:
    # When submitting the form, populate the meal_plan table with updated meals
    meal_plan_df = pd.DataFrame({'Date': meal_dates,
                                 'Meals': meal_names})
    st.write(meal_plan_df)
    insert_meals(meal_plan_conn, meal_dates, meal_names, verbose=False)
    st.write('Meals Confirmed. Shopping List Ready for inspection')
    
    # query = """SELECT *
    #         FROM meal_plan
    #         WHERE dt_created = (SELECT MAX(dt_created) AS ts FROM meal_plan)
    #     """
    # db_meals = meal_plan_conn.query(query)
    # st.write(db_meals)