import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

def st_authenticator():
    with open('secrets.yml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

    return authenticator


authenticator = st_authenticator()
name, authentication_status, username = authenticator.login(location='main',
                                                            max_concurrent_users = 3,
                                                            max_login_attempts = 3)


if authentication_status:
    st.session_state.authentication_status = True
    authenticator.logout('**Logout**', 'main', key='unique_key')
    st.write(f"Welcome {name}! Please move to the 'generate meal plan' page to get started.")
    
elif authentication_status is False:
    st.session_state.authentication_status = False
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.session_state.authentication_status = None
    st.warning('Please enter your username and password')






