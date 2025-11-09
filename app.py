import streamlit as st
from streamlit_authenticator import Authenticate

def to_plain_recursive(d):
    """
    Recursively converts a Streamlit Secrets object (or any dict-like object)
    into a plain Python dictionary.
    
    Args:
        d: A dict-like object (e.g., dict, streamlit.runtime.secrets.Secrets)
    
    Returns:
        A plain Python dictionary.
    """
    # Check if it's dict-like (works for dict and st.secrets proxy objects)
    # by checking for the 'keys' attribute.
    if hasattr(d, 'keys'):
        # Iterate over keys and apply recursively
        return {k: to_plain_recursive(d[k]) for k in d.keys()}
    
    # Base case: not a dict-like object, return the value as-is
    return d

# --- Main App ---
try:
    # Get credentials from secrets and convert them to plain dicts
    credentials = to_plain_recursive(st.secrets["credentials"])
    cookie = to_plain_recursive(st.secrets["cookie"])

    # --- Configuration Checks ---
    # Ensure cookie config is valid before proceeding
    if not all(k in cookie for k in ["name", "key", "expiry_days"]):
        st.error("Cookie configuration is incomplete in secrets.toml. Missing 'name', 'key', or 'expiry_days'.")
        st.stop()
        
    # Ensure credentials config is valid
    if "usernames" not in credentials:
        st.error("Credentials configuration is missing '[credentials.usernames]' section in secrets.toml.")
        st.stop()

    # --- Authenticator Init ---
    authenticator = Authenticate(
        credentials=credentials,
        cookie_name=cookie["name"],
        cookie_key=cookie["key"], # This is the correct parameter for v0.3.2
        cookie_expiry_days=int(cookie["expiry_days"]),
    )

    # --- Login Logic ---
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

except KeyError as e:
    st.error(f"Error: Missing key {e} in secrets.toml. Please check your configuration.")
except Exception as e:
    st.error(f"An error occurred during authentication setup: {e}")
    st.info("""
    Please ensure your `secrets.toml` file is correctly formatted.
    """)

# Optional: quick diagnostics in the footer
import streamlit_authenticator as stauth
st.caption(f"streamlit-authenticator: {getattr(stauth, '__version__', 'unknown')}")
st.caption(f"secrets keys: {list(st.secrets.keys())}")
