import streamlit as st
from functions import *

# Streamlit app title
st.title("URL Input App")

# URL input field
url_input = st.text_input("Enter a URL", "")

# Submit button
if st.button("Submit"):
    # Call function to handle the input
    run_all()