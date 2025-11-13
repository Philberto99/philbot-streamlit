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

# 🖌️ Custom CSS for dark blue background and input styling
st.markdown("""
    <style>
        body {
            background-color: #001f3f;
            color: white;
        }
        .stTextInput > div > div > input {
            background-color: #003366;
            color: white;
        }
        .arrow-icon {
            font-size: 1.5em;
            margin-left: 10px;
            vertical-align: middle;
        }
        footer {
            text-align: center;
            font-size: 0.9em;
            color: #ccc;
            margin-top: 2em;
        }
    </style>
""", unsafe_allow_html=True)

# 🦞 UI setup
st.set_page_config(page_title="PhilBot 🦞", layout="centered")
st.title("PhilBot 🔍🦞")

# 🧠 Input box with dynamic arrow icon
query = st.text_input("Ask PhilBot", key="query_input")

if query:
    st.markdown("### Echoing your query with semantic clarity...")
    st.write(f"You asked: {query}")
    st.markdown('<span class="arrow-icon">➡️</span>', unsafe_allow_html=True)

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

# 📊 Check SerpAPI usage
if SERPAPI_KEY:
    usage_response = requests.get(
        "https://serpapi.com/account",
        params={"api_key": SERPAPI_KEY}
    )

    if usage_response.status_code == 200:
        usage_data = usage_response.json()
        searches_left = usage_data.get("plan_searches_left", "N/A")
        st.markdown(f"🔍 Searches left this month: **{searches_left}**")
    else:
        st.warning("Could not retrieve usage info from SerpAPI.")

# 🧾 Footer version tag
st.markdown("<footer>Development version 1.001</footer>", unsafe_allow_html=True)