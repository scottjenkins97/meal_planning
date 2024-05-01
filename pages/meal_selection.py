import streamlit as st
import numpy as np


# db of the meta information about the meal plan: date range
meal_plan_conn = st.connection('meal_plan_db', type='sql')

# Query and display the data you inserted
db_meals = meal_plan_conn.query('select * from planned_meals')
st.write('planned_meals table')
st.dataframe(db_meals)