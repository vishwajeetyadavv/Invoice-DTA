import streamlit as st
from streamlit_authenticator import Authenticate


cookie = st.secrets["cookie"]
credentials = st.secrets["credentials"]
print(cookie)
