import streamlit as st
from sqlalchemy import text

# Create the SQL connection to pets_db as specified in secrets.toml file.
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

def get_pet_owners(conn):
  # Function to query pet_owners table
  query = "select * from pet_owners"
  all_owners = conn.query(sql=query)
  return all_owners

# Display table contents
all_owners = get_pet_owners(conn)
st.dataframe(all_owners)

# Form to submit new pet-owner relationships
with st.form('Test form'):
    owner = st.text_input(label = 'Owner')
    pet = st.text_input(label = 'Pet')

    submitted = st.form_submit_button("Add")
    st.write(submitted)

def insert_pet_owner(conn, person, pet):
    # Function to add pet-owner to pet_owners table
    try:
        with conn.session as s:
            s.execute(text('INSERT INTO pet_owners (person, pet) VALUES (:owner, :pet);'),
                        params=dict(owner=person, pet=pet))
            s.commit()
            st.write(f"Successfully added {person} and {pet}")  # Confirmation message
    except Exception as e:
        st.write(f"Error inserting pet owner: {e}")

if submitted:
  print("Form submitted")  # Confirmation message for form submission
  insert_pet_owner(conn, owner, pet)
  # Update query and display
  all_owners = get_pet_owners(conn)
  st.dataframe(all_owners)
