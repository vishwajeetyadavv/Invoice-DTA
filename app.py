import streamlit as st
from streamlit_authenticator import Authenticate
from collections.abc import Mapping

def to_plain_dict(x):
    if isinstance(x, Mapping):
        return {k: to_plain_dict(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [to_plain_dict(i) for i in x]
    return x

# Read from secrets (read-only Mapping) → convert to plain dicts
credentials = to_plain_dict(st.secrets["credentials"])
cookie = to_plain_dict(st.secrets["cookie"])

authenticator = Authenticate(
    credentials=credentials,
    cookie_name=cookie["name"],
    key=cookie["key"],
    cookie_expiry_days=int(cookie["expiry_days"]),
)

# name, authentication_status, username = authenticator.login("Login", "main")
name, authentication_status, username = authenticator.login("Login", location="sidebar")

if authentication_status:
    st.sidebar.success(f"Welcome {name} 👋")
    authenticator.logout("Logout", "sidebar")
    st.title("Secure Streamlit Dashboard")
    st.write("This page is protected!")
elif authentication_status is False:
    st.error("Username or password incorrect")
else:
    st.warning("Please log in to continue.")
