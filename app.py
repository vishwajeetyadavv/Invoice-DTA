import streamlit as st
import streamlit_authenticator as stauth
from collections.abc import Mapping

# --- Deep-convert st.secrets sections into plain dicts ---
def to_plain_dict(obj):
    if isinstance(obj, Mapping):
        return {k: to_plain_dict(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [to_plain_dict(x) for x in obj]
    return obj

credentials = to_plain_dict(st.secrets["credentials"])
cookie = to_plain_dict(st.secrets["cookie"])
preauth_emails = to_plain_dict(st.secrets.get("preauthorized", {})).get("emails", [])

# --- Init authenticator with MUTABLE dicts ---
authenticator = stauth.Authenticate(
    credentials,
    cookie["name"],
    cookie["key"],
    cookie["expiry_days"],
    preauthorized=preauth_emails,   # optional, safe if empty
)

# --- Login form (API varies by version; this works on 0.3.x/0.4.x) ---
name, authentication_status, username = authenticator.login("Login", location="main")

if authentication_status:
    st.success(f"Welcome, {name}!")
    authenticator.logout("Logout", "sidebar")
elif authentication_status is False:
    st.error("Username or password is incorrect.")
else:
    st.info("Please log in to continue.")
