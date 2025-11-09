import streamlit as st
from streamlit_authenticator import Authenticate
from copy import deepcopy

# Read from secrets (read-only objects)
_secrets_credentials = st.secrets["credentials"]
_secrets_cookie = st.secrets["cookie"]

# Make mutable copies
credentials = deepcopy(_secrets_credentials)
cookie = deepcopy(_secrets_cookie)

# Build authenticator
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
else:
    st.warning("Please log in to continue.")
