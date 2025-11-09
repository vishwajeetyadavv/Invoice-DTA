import streamlit as st
from streamlit_authenticator import Authenticate

# Convert st.secrets (read-only proxy) to plain dicts
def to_plain(d):
    return {k: to_plain(v) if isinstance(v, dict) else v for k, v in dict(d).items()}

credentials = to_plain(st.secrets["credentials"])
cookie = to_plain(st.secrets["cookie"])

authenticator = Authenticate(
    credentials=credentials,
    cookie_name=cookie["name"],
    signature_key=cookie["key"], # <-- FIX: The parameter is 'signature_key', not 'key' for v0.3.2
    cookie_expiry_days=int(cookie["expiry_days"]),
)

# 0.3.2 API uses positionals and ALWAYS returns (name, status, username)
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

# Optional: quick diagnostics in the footer
import streamlit_authenticator as stauth
st.caption(f"streamlit-authenticator: {getattr(stauth, '__version__', 'unknown')}")
st.caption(f"secrets keys: {list(st.secrets.keys())}")
