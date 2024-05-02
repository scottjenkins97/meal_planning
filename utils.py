import networkx as nx
import pandas as pd
import random
import numpy as np
import datetime as dt
from sqlalchemy.sql import text, delete
import streamlit as st

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