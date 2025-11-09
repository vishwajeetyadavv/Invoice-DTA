import streamlit as st
import streamlit_authenticator as stauth
from collections.abc import Mapping

st.set_page_config(page_title="Auth Demo", page_icon="🔐")

# --- Make st.secrets mutable (deep copy) ---
def to_plain(obj):
    if isinstance(obj, Mapping):
        return {k: to_plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_plain(x) for x in obj]
    return obj

raw_credentials = to_plain(st.secrets["credentials"])
cookie = to_plain(st.secrets["cookie"])

# --- Normalize users to the structure expected by streamlit-authenticator ---
# Required per user: email, name, password
def normalize_credentials(creds):
    users = creds.get("usernames", {})
    cleaned = {}
    for username, data in users.items():
        # build a 'name' if missing
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

# --- Init authenticator (credentials must be MUTABLE dicts) ---
authenticator = stauth.Authenticate(
    credentials,
    cookie["name"],
    cookie["key"],
    cookie["expiry_days"],
)

# --- UI ---
st.title("🔐 Login")
name, auth_status, username = authenticator.login("Login", location="main")

if auth_status:
    st.success(f"Welcome, {name}!")
    st.write(f"Username: `{username}`")
    authenticator.logout("Logout", "sidebar")
elif auth_status is False:
    st.error("Username or password is incorrect.")
else:
    st.info("Please log in to continue.")
