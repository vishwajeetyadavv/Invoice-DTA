import streamlit as st
import streamlit_authenticator as stauth
from collections.abc import Mapping
import inspect
from main_function import getDetails
st.set_page_config(page_title="Auth Demo", page_icon="🔐")

# --- Deep-copy st.secrets to plain, mutable dicts ---
def to_plain(o):
    if isinstance(o, Mapping): return {k: to_plain(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [to_plain(x) for x in o]
    return o

raw_credentials = to_plain(st.secrets["credentials"])
cookie = to_plain(st.secrets["cookie"])

# Normalize to the schema expected by streamlit-authenticator
def normalize_credentials(creds):
    users = creds.get("usernames", {})
    cleaned = {}
    for username, data in users.items():
        full_name = data.get("name") or " ".join(
            [x for x in [data.get("first_name"), data.get("second_name")] if x]
        ).strip() or username
        cleaned[username] = {
            "email": data.get("email", ""),
            "name": full_name,
            "password": data.get("password", ""),
        }
    return {"usernames": cleaned}

credentials = normalize_credentials(raw_credentials)

authenticator = stauth.Authenticate(
    credentials,
    cookie["name"],
    cookie["key"],
    cookie["expiry_days"],
)

st.title("🔐 Login")

# --- Version-flexible login call + return normalization ---
def call_login_compat(auth):
    """Call stauth.Authenticate.login across versions and normalize the return."""
    sig = inspect.signature(auth.login)
    params = list(sig.parameters.keys())

    # Try safest pattern first: no args
    try:
        res = auth.login()
    except TypeError:
        res = None

    # If that failed or returned None, try with positional only
    if res is None:
        try:
            # Many versions treat the 1st positional arg as form name or location
            res = auth.login("Login")
        except TypeError:
            res = None

    # If still None, try explicit kwarg for location
    if res is None:
        try:
            res = auth.login(location="main")
        except TypeError:
            res = None

    # If still None, try ("Login", location="main")
    if res is None:
        try:
            res = auth.login("Login", location="main")
        except TypeError:
            res = None

    # Normalize return into (name, auth_status, username)
    name = auth_status = username = None
    if isinstance(res, tuple) and len(res) == 3:
        name, auth_status, username = res
    elif isinstance(res, dict):
        # Some versions returned a dict
        name = res.get("name")
        auth_status = res.get("authentication_status")
        username = res.get("username")

    return name, auth_status, username

name, auth_status, username = call_login_compat(authenticator)

# --- Post-login UI ---
if auth_status:
    # st.success(f"Welcome, {name}!")
    # st.write(f"Username: `{username}`")
    api_key = st.secrets["api_keys"]["openrouter"]
    getDetails(api_key)
    authenticator.logout("Logout", "sidebar")
elif auth_status is False:
    st.error("Username or password is incorrect.")
else:
    st.info("Please log in to continue.")
