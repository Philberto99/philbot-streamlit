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
        }
        h1 {
            font-family: 'Orbitron', sans-serif;
            color: #00aced;
        }
        .response-box {
            background-color: #003366;
            color: white;
            padding: 1em;
            border-radius: 8px;
            max-height: 500px;
            overflow-y: auto;
            white-space: pre-wrap;
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

# 🧠 Input box
query = st.text_input("Ask PhilBot")

# 📦 Session state to store cumulative responses
if "response_log" not in st.session_state:
    st.session_state.response_log = ""

if query:
    if SERPAPI_KEY:
        params = {
            "q": query,
            "api_key": SERPAPI_KEY,
            "engine": "google",
        }

        response = requests.get("https://serpapi.com/search", params=params)
        data = response.json()

        if "organic_results" in data:
            new_response = f"**You asked:** {query}\n\n"
            new_response += "### Top Search Results:\n"
            for result in data["organic_results"][:3]:
                new_response += f"- [{result['title']}]({result['link']})\n"
            new_response += "\nPhilBot is ready for your next question 🔍\n\n"
        else:
            new_response = f"**You asked:** {query}\n\nNo results found or API limit reached.\n\n"
    else:
        new_response = f"**You asked:** {query}\n\nAPI key not found. Please set SERPAPI_KEY in secrets or .env.\n\n"

    # Append to response log
    st.session_state.response_log += new_response

# 🖋️ Display cumulative responses
if st.session_state.response_log:
    st.markdown('<div class="response-box">', unsafe_allow_html=True)
    st.markdown(st.session_state.response_log, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

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
st.markdown('<div class="footer">Development version 1.004</div>', unsafe_allow_html=True)