import streamlit as st
import pandas as pd
from utils import get_latest_meal_plan, get_latest_shopping_list

st.cache_data.clear()
meal_plan_conn = st.connection(name = 'meal_plan_db', 
                               type = 'sql',
                               autocommit = True,
                               max_entries = 100,
                               ttl = 0)
st.cache_data.clear()
shopping_list_conn = st.connection(name = 'shopping_list_db', 
                               type = 'sql',
                               autocommit = True,
                               max_entries = 100,
                               ttl = 0)


db_meals, meal_dates, meal_names = get_latest_meal_plan(meal_plan_conn)
db_shopping_list, shopping_list = get_latest_shopping_list(shopping_list_conn)

st.write(db_meals)
st.write(db_shopping_list)
st.write(shopping_list)

# Now, need to link back to departments

meal_df = pd.read_excel('meals.xlsx',sheet_name='meal_df')
ingredient_df = pd.read_excel('meals.xlsx',sheet_name='ingredients')

