import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd

def authenticate_user(users_df):
    """
    handles user authentication using Streamlit Authenticator.
    """
    # users_df = pd.read_csv('data/users2.csv')

    names = list(users_df['Name'].str.strip())
    usernames = list(users_df['Email'].str.strip())
    passwords = list(users_df['Hashed_Password'].str.strip())

    authenticator = stauth.Authenticate(
        names,
        usernames,
        passwords,
        cookie_name='leads-cookie',
        key='cookie',
        cookie_expiry_days=1
    )

    name, authentication_status, username = authenticator.login('Login', 'main')

    return authenticator, authentication_status, name, username


def handle_authentication_status(authenticator, authentication_status, name):
    """
    handles the display of the authentication state.
    """
    if authentication_status:
        with st.sidebar:
            st.write(f"Welcome {name}")
            try:
                authenticator.logout("Logout", location='main')
            except KeyError:
                st.rerun()
                pass
            except Exception as err:
                st.error(f'Unexpected exception {err}')
                raise Exception(err)
    elif authentication_status is False:
        st.error('Username/password is incorrect')
    elif authentication_status is None:
        pass
        # st.warning('Please enter your username and password')
