import networkx as nx
import pandas as pd
import random
import numpy as np
import datetime as dt
from sqlalchemy.sql import text, delete
import streamlit as st
import yagmail

def generate_meal_graph(meal_df):
    # Create Graph of Legal Consecutive Meals
    G = nx.Graph()
    legal_edges = []
    for i in range(len(meal_df)):
        for j in range(len(meal_df)):
            if j > i:
                # if same 
                if ((meal_df['protein_id'][i] != meal_df['protein_id'][j]) and (meal_df['carb_id'][i] != meal_df['carb_id'][j])):
                    # print('Legal Sequence: ',(i+1,j+1))
                    legal_edges.append((i+1,j+1))
                    G.add_edge(i+1, j+1)
    # Return the graph object
    return G

def generate_meal_plan(meal_df, G, date_list):
    # Generate meal plan 
    number_of_meals = len(date_list)

    # Produce list of meal suggestions using graph G
    meal_list = []
    while len(meal_list) < number_of_meals:
        if len(meal_list) == 0:
            node = np.random.randint(1,len(meal_df)) # pick a random starting node
        else:
            next_node_list = [n for n in G.neighbors(node) if n not in meal_list] # List the neighbours of the current node which haven't already been picked
            node = random.choice(next_node_list)                                  # Select next node randomly from remaining neighbours
        meal_list.append(node)
    
    # Store list of meal names
    meal_names = [np.array(meal_df['meal_name'])[i-1] for i in meal_list]

    return meal_names

def insert_meals(meal_plan_conn, date_list, meal_names,verbose = True):
    # Get current timestamp to insert into db table
    time_now = dt.datetime.now()
    try:
        with meal_plan_conn.session as s:
            s.execute(text('CREATE TABLE IF NOT EXISTS meal_plan (dt_created DATETIME, date TEXT, meal TEXT);'))
            meals = dict(zip(date_list, meal_names))
        for k in meals:
            # Loop over meals, adding them to the database table
            # st.write(k, meals[k])
            s.execute(text(
                f'INSERT INTO meal_plan (dt_created, date, meal) VALUES (:dt_created, :date, :meal);'),
                params=dict(dt_created = time_now, date=k, meal=meals[k])
            )
            if verbose:
                st.write(f"Successfully added {meals[k]} on {k}")
        s.commit()
    except Exception as e:
        st.write(f"Error inserting meals: {e}")

def insert_shopping_list(shopping_list_conn, meal_shopping_list):
     # Get current timestamp to insert into db table
    time_now = dt.datetime.now()
    # Convert shopping list to a string for storing in database table
    shopping_list_string = str(', '.join([str(item) for item in meal_shopping_list]))
    try:
        with shopping_list_conn.session as s:
            s.execute(text('CREATE TABLE IF NOT EXISTS grocery_list (dt_created DATETIME, groceries TEXT);'))
            s.execute(text(
                f'INSERT INTO grocery_list (dt_created, groceries) VALUES (:dt_created, :shopping_list);'),
                params=dict(dt_created = time_now, shopping_list = shopping_list_string)
            )
            s.commit()
        st.write('Email Meal Plan & Shopping List prepared. **Awaiting review.**')
    except Exception as e:
        st.write(f"Error inserting shopping list: {e}")

def get_latest_meal_plan(meal_plan_conn):
    # Extract meal data generated with latest dt_created
    query = """SELECT *
                FROM meal_plan
                WHERE dt_created = (SELECT MAX(dt_created) AS ts FROM meal_plan)
            """
    db_meals = meal_plan_conn.query(query)

    meal_dates = db_meals['date']
    meal_names = db_meals['meal']

    return db_meals, meal_dates, meal_names

def get_latest_shopping_list(shopping_list_conn):
    # Extract meal data generated with latest dt_created
    st.cache_data.clear()
    query = """SELECT *
                FROM grocery_list
                WHERE dt_created = (SELECT MAX(dt_created) AS ts FROM grocery_list)
            """
    db_shopping_list = shopping_list_conn.query(query)

    shopping_list = db_shopping_list['groceries'][0].split(', ')
   
    return db_shopping_list, shopping_list

def send_email(start_date, meals_df, shopping_df):
    user = st.secrets["EMAIL"]
    app_password = st.secrets["GMAIL_APP_PASSWORD"]
    recipients = st.secrets["EMAIL_RECIPIENTS"]
    recipient_list = [x for x in recipients.split(', ')]
   
    subject = f'Meal Plan: {start_date}'
    content = [ '<br>',
                'Hello,',
                '<br>',
                "Thank you for using our couple's meal planner!", 
                '<br>',
                'Here is our meal plan for the next few days',
                '<br>',
                meals_df,
                '<br>',
                'And here is our corresponding shopping list',
                '<br>',
                shopping_df,
                '<br>',
                'Happy Cooking!',
              ]

    for to in recipient_list:
        with yagmail.SMTP(user, app_password) as yag:
            yag.send(to, subject, content)
            st.write(f'Sent email successfully to {to}')
