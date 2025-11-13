import streamlit as st
import requests
import os

# 🔐 Load API key from secrets (cloud) or .env (local)
if "SERPAPI_KEY" in st.secrets:
    SERPAPI_KEY = st.secrets["SERPAPI_KEY"]
else:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        SERPAPI_KEY = os.getenv("SERPAPI_KEY")
    except ImportError:
        SERPAPI_KEY = None

# 🦞 UI setup
st.set_page_config(page_title="PhilBot 🦞", layout="centered")
st.title("PhilBot 🔍🦞")

query = st.text_input("Ask me anything")

if query:
    st.markdown("### Echoing your query with semantic clarity...")
    st.write(f"You asked: {query}")

    if SERPAPI_KEY:
        params = {
            "q": query,
            "api_key": SERPAPI_KEY,
            "engine": "google",
        }

        response = requests.get("https://serpapi.com/search", params=params)
        data = response.json()

        if "organic_results" in data:
            st.markdown("### Top Search Results:")
            for result in data["organic_results"][:3]:
                st.markdown(f"- [{result['title']}]({result['link']})")
        else:
            st.warning("No results found or API limit reached.")
    else:
        st.error("API key not found. Please set SERPAPI_KEY in secrets or .env.")

# 🔍 Perform SerpAPI search
params = {
    "api_key": SERPAPI_KEY,
    "engine": "google",
    "q": query
}

response = requests.get("https://serpapi.com/search", params=params)
results = response.json()

if "organic_results" in results:
    st.markdown("### Top Search Results:")
    for result in results["organic_results"][:3]:
        st.markdown(f"- [{result['title']}]({result['link']})")
else:
    st.warning("No results found or API limit reached.")

# 🔐 Handle missing API key
if not SERPAPI_KEY:
    st.error("API key not found. Please set SERPAPI_KEY in secrets or .env.")

# 📊 Check SerpAPI usage
usage_response = requests.get(
    "https://serpapi.com/account",
    params={"api_key": SERPAPI_KEY}
)

if usage_response.status_code == 200:
    usage_data = usage_response.json()
    searches_left = usage_data.get("searches_left", "N/A")
    st.markdown(f"🔍 Searches left this month: **{searches_left}**")
else:
    st.warning("Could not retrieve usage info from SerpAPI.")