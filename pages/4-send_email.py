import streamlit as st
import pandas as pd
import numpy as np
from utils import get_latest_meal_plan, get_latest_shopping_list, send_email

st.write("""
          Use 'Send Email Button' to confirm meal plan and shopping list. 
         
         Something missing? Go back to a previous page to update the plan.
        
         """)
# st.cache_data.clear()
meal_plan_conn = st.connection(name = 'meal_plan_db', 
                               type = 'sql',
                               autocommit = True,
                               max_entries = 100,
                               ttl = 0)
# st.cache_data.clear()
shopping_list_conn = st.connection(name = 'shopping_list_db', 
                               type = 'sql',
                               autocommit = True,
                               max_entries = 100,
                               ttl = 0)

db_meals, meal_dates, meal_names = get_latest_meal_plan(meal_plan_conn)
db_shopping_list, shopping_list = get_latest_shopping_list(shopping_list_conn)

# Add in the departments for each item in the shopping list
ingredient_df = pd.read_excel('meals.xlsx',sheet_name='ingredients')
shopping_df = ingredient_df[ingredient_df['food_name'].isin(shopping_list)].sort_values('department_id')[['food_name','department_name']].reset_index(drop=True)

meals_df = db_meals[['date','meal']]  
start_date = meals_df['date'][0]

# Display plan and shopping list (with indices removed)
st.dataframe(meals_df,hide_index=True) 
st.dataframe(shopping_df,hide_index=True) 

# Click button to send emails.
if st.button("Send Email with Meal Plan and Shopping List"):
    st.text("Sending emails...")
    send_email(start_date, meals_df,shopping_df)
