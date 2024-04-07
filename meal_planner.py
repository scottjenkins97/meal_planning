import streamlit as st
import streamlit_authenticator as stauth
import os
import datetime as dt
import numpy as np
import pandas as pd
import random
import yagmail
import networkx as nx

import yaml
from yaml.loader import SafeLoader
with open('secrets.yml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login(location='main',
                                                            max_concurrent_users = 3,
                                                            max_login_attempts = 3)

# Initialise session states
if 'meals_finalised' not in st.session_state:
    st.session_state['meals_finalised'] = 0

if 'send_email' not in st.session_state:
    st.session_state['send_email'] = 0


def send_email(start_date, meal_plan_df):
    user = os.environ.get('EMAIL')
    app_password = os.environ.get('GMAIL_APP_PASSWORD')
    recipients = ["mealplanner12345@gmail.com", "sjenkins097@gmail.com"]
    # st.write(recipients)
    
    start_date = start_date.strftime('%A %e %B %Y')

    subject = f'Meal Plan: {start_date}'
    content = ['This email was produced and emailed entirely in python :)', 
            ' ',
            'Here is your meal plan for the next few days',
            ' ',
            meal_plan_df
            ]

    for to in recipients:
        with yagmail.SMTP(user, app_password) as yag:
            yag.send(to, subject, content)
            st.write(f'Sent email successfully to {to}')

    
def log_in_successful(name):
    """ 
    Main function used to generate page content following successful login.
    
    """

    st.title('Meal Planner and Shopping List Creator')

    # Load Meal List from Spreadsheet
    meal_df = pd.read_excel('meals.xlsx',sheet_name='meal_df')

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

    meal_planner_container = st.empty()
    with meal_planner_container.container():
        start_date = st.date_input("Meal Plan Start Date", dt.date.today(),key='start_date_selector')
        end_date = st.date_input("Meal Plan End Date", dt.date.today() + dt.timedelta(days=2),key = 'end_date_selector')
        if end_date < start_date:
            st.write("Error: Meal Plan can't end before it has started!")
        else:     
            # Create list of dates between start_date and end_date, and format
            date_list = pd.date_range(start_date, end_date, freq="D").strftime("%A %e %b %Y")
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

            for i in range(number_of_meals): 
                # Generate drop down boxes with meal suggestions from above
                date_string = date_list[i]        
                day_meal = meal_list[i] - 1                             # day_meal is the index of the node of the meal served on the day 

                if i not in st.session_state:                                        
                    # i.e. This is the initial suggested meal
                    st.session_state[i] = day_meal

                    option = st.selectbox(label = f'{date_string} Meal:',
                                        key = date_string,
                                        options = (np.array(meal_df['meal_name'])),
                                        index = day_meal,
                                        )
                else:
                    # If user edits meal plan, do not rerun suggestions for all other meals. 
                    # That is, do not change the session_state / reset the dropdown option)
                    option = st.selectbox(label = f'{date_string} Meal:',
                                        key = date_string,
                                        options = (np.array(meal_df['meal_name'])),
                                        index = st.session_state[i],
                                        )
                    # Update the list of meal names with the users selections
                    meal_names[i] = option

                                    
            if st.button('Finalise Meal Selection...'):
                # Update session state
                st.session_state['meals_finalised'] = 1
                # When Use clicks button to finalise meal selection...
                st.text('Meals Added to Plan. Ingredients Added to Shopping List')

                # Finalise Plan: Extract meals from selectboxes
                meal_plan_df = pd.DataFrame({'Date': date_list,
                                            'Meals': meal_names})
                
                
                # st.write(meal_names)
                st.write(meal_plan_df)
            
                # Tricky... Need to pass the meal_plan_df to the send email code, but only when the send_email button has been clicked!
                if st.session_state['meals_finalised'] == 1:
                    
                    if st.button(label = "Send Email Shopping List", 
                                key = 'send_email_button',
                                    # on_click = send_email(start_date, meal_plan_df),
                                ):
                            # Update session state
                            st.session_state['send_email'] = 1
                    
                    if st.session_state['send_email'] == 1:
                        user = os.environ.get('EMAIL')
                        app_password = os.environ.get('GMAIL_APP_PASSWORD')
                        recipients = ["mealplanner12345@gmail.com", "sjenkins097@gmail.com"]
                        # st.write(recipients)
                        
                        start_date = start_date.strftime('%A %e %B %Y')

                        subject = f'Meal Plan: {start_date}'
                        content = ['This email was produced and emailed entirely in python :)', 
                                ' ',
                                'Here is your meal plan for the next few days',
                                ' ',
                                meal_plan_df
                                ]

                        for to in recipients:
                            with yagmail.SMTP(user, app_password) as yag:
                                yag.send(to, subject, content)
                                st.write(f'Sent email successfully to {to}')
        
         
###############################################
## Login to App

if authentication_status:
    authenticator.logout('Logout', 'main')
    # If successful login, load page content
    st.cache_data()
    log_in_successful(name)

elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')


