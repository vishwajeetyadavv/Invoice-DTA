import streamlit as st
import streamlit_authenticator as stauth
from collections.abc import Mapping
import inspect

st.set_page_config(page_title="Auth Demo", page_icon="🔐")

def to_plain(o):
    if isinstance(o, Mapping): return {k: to_plain(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [to_plain(x) for x in o]
    return o

# Load & normalize secrets
raw_credentials = to_plain(st.secrets["credentials"])
cookie = to_plain(st.secrets["cookie"])

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

# ---- Call .login() compatibly across versions ----
login_sig = inspect.signature(authenticator.login)
params = login_sig.parameters

if "form_name" in params:
    # Older API: login(form_name, location="main")
    name, auth_status, username = authenticator.login("Login", location="main")
else:
    # Newer API: login(location="main")  (form_name removed/changed)
    # Some releases also accept a `key` to avoid widget clashes.
    name, auth_status, username = authenticator.login(location="main", key="login_form")

# ---- Post-login UI ----
if auth_status:
    st.success(f"Welcome, {name}!")
    st.write(f"Username: `{username}`")
    authenticator.logout("Logout", "sidebar")
elif auth_status is False:
    st.error("Username or password is incorrect.")
else:
    st.info("Please log in to continue.")
