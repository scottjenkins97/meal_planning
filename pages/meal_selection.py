import streamlit as st
from sqlalchemy import text
import numpy as np

# Create the SQL connection to pets_db as specified in your secrets file.
conn = st.connection('pets_db', type='sql')

# Insert some data with conn.session.
with conn.session as s:
    s.execute(text('CREATE TABLE IF NOT EXISTS pet_owners (person TEXT, pet TEXT);'))
    s.execute(text('DELETE FROM pet_owners;'))
    pet_owners = {'jerry': 'fish', 'barbara': 'cat', 'alex': 'puppy'}
    for k in pet_owners:
        s.execute(
            text('INSERT INTO pet_owners (person, pet) VALUES (:owner, :pet);'),
            params=dict(owner=k, pet=pet_owners[k])
        )
    s.commit()
    s.close()

# Query and display the data you inserted
pet_owners = conn.query('select * from pet_owners')
st.dataframe(pet_owners)

with st.form('Test form'):
    owner = st.text_input(label = 'Owner')
    pet = st.text_input(label = 'Pet')

    submitted = st.form_submit_button("Add")

    if submitted:
        st.write('Adding to Table')
        with conn.session as s:
            s.begin()
            s.execute(text('CREATE TABLE IF NOT EXISTS pet_owners (person TEXT, pet TEXT);'))
            st.write('Create Table')
            s.execute(text('DELETE FROM pet_owners;'))
            pet_owners = {owner: pet}
            for k in pet_owners:
                s.execute(
                    text('INSERT INTO pet_owners (person, pet) VALUES (:owner, :pet);'),
                    params=dict(owner=k, pet=pet_owners[k])
                )
            s.commit()
            s.begin()

        # Query and display the data you inserted
        pet_owners = conn.query('select * from pet_owners')
        st.dataframe(pet_owners)





# # db of the meta information about the meal plan: date range
# meal_plan_conn = st.connection('meal_plan_db', type='sql')

# # Query and display the data you inserted
# db_meals = meal_plan_conn.query('select * from planned_meals')
# st.write('planned_meals table')
# st.dataframe(db_meals)