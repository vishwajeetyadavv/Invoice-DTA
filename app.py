import streamlit as st
from streamlit_authenticator import Authenticate

# Convert secrets to plain dicts
def to_plain(d): return {k: to_plain(v) if isinstance(v, dict) else v for k, v in dict(d).items()}

credentials = to_plain(st.secrets["credentials"])
cookie = to_plain(st.secrets["cookie"])

authenticator = Authenticate(
    credentials=credentials,
    cookie_name=cookie["name"],
    key=cookie["key"],
    cookie_expiry_days=int(cookie["expiry_days"]),
)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    st.sidebar.success(f"Welcome {name} 👋")
    authenticator.logout("Logout", "sidebar")
    st.title("Secure Streamlit Dashboard")
elif authentication_status is False:
    st.error("Username or password incorrect")
else:
    st.warning("Please log in to continue.")
