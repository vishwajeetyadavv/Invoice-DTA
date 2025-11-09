import streamlit as st
from streamlit_authenticator import Authenticate


cookie = to_plain(st.secrets["cookie"])
credentials = to_plain(st.secrets["credentials"])
print(cookie)
