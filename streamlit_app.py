import streamlit as st

st.set_page_config(page_title="PhilBot 🦞", layout="centered")
st.title("PhilBot 🔍🦞")

query = st.text_input("Ask me anything")

if query:
    st.markdown("### Echoing your query with semantic clarity...")
    st.write(f"You asked: {query}")