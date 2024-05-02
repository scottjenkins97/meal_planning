import streamlit as st
from utils import get_latest_shopping_list

st.cache_data.clear()
meal_plan_conn = st.connection(name = 'meal_plan_db', 
                               type = 'sql',
                               autocommit = True,
                               max_entries = 100,
                               ttl = 0)


db_shopping_list, shopping_list = get_latest_shopping_list(meal_plan_conn)

st.write(db_shopping_list)