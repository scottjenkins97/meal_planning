import streamlit as st
import pandas as pd
from utils import get_latest_meal_plan, insert_shopping_list
import numpy as np

# if not st.session_state.get('authentication_status', False):
#     st.info('Please Login from the Home page and try again.')
#     st.stop()

# Select the latest meals
st.cache_data.clear()
meal_plan_conn = st.connection(name = 'meal_plan_db', 
                               type = 'sql',
                               autocommit = True,
                               max_entries = 100,
                               ttl = 0)

# Source latest meal plan with utils function
db_meals, meal_dates, meal_names = get_latest_meal_plan(meal_plan_conn)
st.write(db_meals)

# Create draft shopping list
# Load Meal and ingredient lists from spreadsheet
meal_df = pd.read_excel('meals.xlsx',sheet_name='meal_df')
ingredient_df = pd.read_excel('meals.xlsx',sheet_name='ingredients')
# Create to_buy column, set all values to False 
ingredient_df['to_buy'] = False

# Create initial shopping list of ingredients for selected meals
meal_shopping_list = []
for meal in meal_names:
    ingredients = meal_df[meal_df['meal_name']==meal]['ingredients']
    # Get unique list of required ingredients
    meal_shopping_list = list(set(list(np.concatenate((meal_shopping_list,ingredients.values[0].split(',')), axis=0))))

# Set 'to_buy' value as True for ingredients in meal_shopping_list
for ingredient in meal_shopping_list:
    ingredient_df.loc[ingredient_df['food_name']==ingredient,['to_buy']] = 'True'

# Multiselect Form to modify shopping list
with st.form("Shopping List Form"):
    st.write("Modify Shopping List")
    if meal_shopping_list not in st.session_state:
        st.session_state['shopping_list'] = meal_shopping_list
        final_shopping_list = st.multiselect(label = 'Shopping List',options = ingredient_df['food_name'],default = meal_shopping_list,)   
    else:
        final_shopping_list = st.multiselect(label = 'Shopping List',options = ingredient_df['food_name'],default = st.session_state[meal_shopping_list],)
        meal_shopping_list = final_shopping_list
    submitted = st.form_submit_button("Finalise Shopping List.") 

if submitted:
    insert_shopping_list(meal_plan_conn, meal_shopping_list)

    
