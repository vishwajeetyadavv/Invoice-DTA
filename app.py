import streamlit as st
import streamlit_authenticator as stauth
import yaml
from streamlit_authenticator import Authenticate
# # Load secrets
# secrets = st.secrets["credentials"]
# auth_config = st.secrets["authenticator"]

# credentials = {
#     "usernames": secrets["usernames"]
# }

# # Initialize authenticator
# authenticator = stauth.Authenticate(
#     credentials,
#     auth_config["cookie_name"],
#     auth_config["cookie_key"],
#     auth_config["expiry_days"]
# )


credentials = st.secrets["credentials"]
cookie = st.secrets["cookie"]

authenticator = Authenticate(
    credentials=credentials,
    cookie_name=cookie["name"],
    key=cookie["key"],
    cookie_expiry_days=int(cookie["expiry_days"]),
)
# Login widget
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    st.sidebar.success(f"Welcome {name} 👋")
    authenticator.logout("Logout", "sidebar")
    st.title("Secure Streamlit Dashboard")
    st.write("This page is protected!")
elif authentication_status is False:
    st.error("Username or password incorrect")
elif authentication_status is None:
    st.warning("Please log in to continue.")
