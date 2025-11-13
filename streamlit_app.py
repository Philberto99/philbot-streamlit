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

# 🎨 Custom styling
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500&display=swap');

        html, body {
            background-color: #001f3f;
            color: white;
        }
        h1 {
            font-family: 'Orbitron', sans-serif;
            color: #00aced;
        }
        .stTextArea textarea {
            background-color: #ffffff;
            color: black;
            height: 300px !important;
            overflow-y: auto;
        }
        .footer {
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

# 🧠 Input box with expandable response area
query = st.text_input("Ask PhilBot")

response_text = ""

if query and SERPAPI_KEY:
    params = {
        "q": query,
        "api_key": SERPAPI_KEY,
        "engine": "google",
    }

    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()

    if "organic_results" in data:
        response_text += f"**You asked:** {query}\n\n"
        response_text += "### Top Search Results:\n"
        for result in data["organic_results"][:3]:
            response_text += f"- [{result['title']}]({result['link']})\n"
        response_text += "\nPhilBot is ready for your next question 🔍"
    else:
        response_text = "No results found or API limit reached."
elif query and not SERPAPI_KEY:
    response_text = "API key not found. Please set SERPAPI_KEY in secrets or .env."

# 🖋️ Display response inside a scrollable text area
if response_text:
    st.text_area("PhilBot's Response", value=response_text, height=300)

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
st.markdown('<div class="footer">Development version 1.003</div>', unsafe_allow_html=True)