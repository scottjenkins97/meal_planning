import streamlit as st
from sqlalchemy import create_engine, MetaData
from sqlalchemy.sql import text, delete
import pandas as pd
from utils import generate_meal_graph, generate_meal_plan
import datetime as dt
import numpy as np


meal_plan_conn = st.connection('meal_plan_db', type='sql', autocommit=True, )

# Get latest meal_plan
query = """SELECT *
            FROM meal_plan
            WHERE dt_created = (SELECT MAX(dt_created) AS ts FROM meal_plan)
        """
st.cache_data.clear()
db_meals = meal_plan_conn.query(query) # 'select * from meal_plan where dt_created = (SELECT MAX(dt_created) FROM meal_plan')
st.write('planned_meals table')
st.dataframe(db_meals)


# 1) Extract meal data generated with latest dt_created
# 2) Create a form with drop down boxes for each meal
# 3) When submitting the form, it should also populate the meal_plan table

