import streamlit as st
import streamlit_authenticator as stauth

credentials = st.secrets["credentials"]
cookie = st.secrets["cookie"]

authenticator = stauth.Authenticate(
    credentials,
    cookie['name'],
    cookie['key'],
    cookie['expiry_days']
)

try:
    authenticator.login()
except Exception as e:
    st.error(e)
