import streamlit as st
from streamlit_authenticator import Authenticate
from collections.abc import Mapping
import inspect

# --- helpers ---
def to_plain_dict(x):
    if isinstance(x, Mapping):
        return {k: to_plain_dict(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [to_plain_dict(i) for i in x]
    return x

def login_compat(authenticator, form_name="Login", location="main"):
    """Call authenticator.login() safely across versions."""
    sig = inspect.signature(authenticator.login)
    params = sig.parameters
    kwargs = {}
    if "form_name" in params:
        kwargs["form_name"] = form_name
    if "location" in params:
        kwargs["location"] = location
    # If neither param is present, just call with no args
    return authenticator.login(**kwargs)

def logout_compat(authenticator, button_label="Logout", location="sidebar"):
    sig = inspect.signature(authenticator.logout)
    params = sig.parameters
    kwargs = {}
    if "button_name" in params:
        kwargs["button_name"] = button_label
    if "location" in params:
        kwargs["location"] = location
    return authenticator.logout(**kwargs)

# --- load secrets (your TOML looks correct) ---
credentials = to_plain_dict(st.secrets["credentials"])
cookie = to_plain_dict(st.secrets["cookie"])

# --- build authenticator ---
authenticator = Authenticate(
    credentials=credentials,
    cookie_name=cookie["name"],
    key=cookie["key"],
    cookie_expiry_days=int(cookie["expiry_days"]),
)

# --- login (version-agnostic) ---
name, authentication_status, username = login_compat(authenticator, form_name="Login", location="main")

if authentication_status:
    st.sidebar.success(f"Welcome {name} 👋")
    logout_compat(authenticator, "Logout", "sidebar")
    st.title("Secure Streamlit Dashboard")
    st.write("This page is protected!")
elif authentication_status is False:
    st.error("Username or password incorrect")
else:
    st.warning("Please log in to continue.")
