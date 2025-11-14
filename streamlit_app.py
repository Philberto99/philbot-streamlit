import streamlit as st
import requests
import os
import openai

# 🔐 Load API keys from secrets or .env
if "SERPAPI_KEY" in st.secrets:
    SERPAPI_KEY = st.secrets["SERPAPI_KEY"]
else:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        SERPAPI_KEY = os.getenv("SERPAPI_KEY")
    except ImportError:
        SERPAPI_KEY = None

AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")

# 🔧 Configure Azure OpenAI
openai.api_type = "azure"
openai.api_base = "https://philbot251114instance.cognitiveservices.azure.com/"
openai.api_version = "2025-01-01-preview"
openai.api_key = AZURE_OPENAI_KEY

# 🎨 Aggressive CSS styling
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500&display=swap');
        html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"] {
            background-color: #001f3f !important;
        }
        h1 {
            font-family: 'Orbitron', sans-serif;
            color: #f5f5dc !important;
        }
        label[for="Ask PhilBot"] {
            color: #f8f8f2 !important;
            font-weight: bold !important;
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
        }
        .stTextInput input, .stTextArea textarea {
            border: none !important;
            background-color: #001f3f !important;
            color: #ffffff !important;
        }
        .stTextInput > div > div {
            background-color: transparent !important;
            box-shadow: none !important;
        }
        .response-box {
            background-color: transparent !important;
            color: #f8f8f2 !important;
            padding: 1em;
            border-radius: 8px;
            max-height: 500px;
            overflow-y: auto;
            white-space: pre-wrap;
            font-size: 1.1em;
            line-height: 1.7em;
        }
        .searches-left {
            color: #ffff00 !important;
            font-weight: bold;
            font-size: 1.1em;
            margin-top: 1em;
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
query = st.text_input("Ask PhilBot", label_visibility="visible")
use_gpt = st.checkbox("Use GPT-4o instead of SerpAPI", value=True)

# 📦 Session state to store cumulative responses
if "response_log" not in st.session_state:
    st.session_state.response_log = ""

if query:
    if use_gpt and AZURE_OPENAI_KEY:
        try:
            completion = openai.ChatCompletion.create(
                deployment_id="Philbot-gpt-4o",
                messages=[
                    {"role": "system", "content": "You are PhilAIbot, a semantic assistant built by Phil."},
                    {"role": "user", "content": query}
                ],
                temperature=0.7,
                max_tokens=500
            )
            gpt_response = completion.choices[0].message.content
            new_response = f"**You asked:** {query}\n\n{gpt_response}\n\nPhilBot is ready for your next question 🔍\n\n"
        except Exception as e:
            new_response = f"**You asked:** {query}\n\nError from GPT-4o: {str(e)}\n\n"
    elif SERPAPI_KEY:
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
        new_response = f"**You asked:** {query}\n\nNo valid API key found for GPT-4o or SerpAPI.\n\n"

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
        st.markdown(f"<div class='searches-left'>🔢 Searches left this month: {searches_left}</div>", unsafe_allow_html=True)
    else:
        st.warning("Could not retrieve usage info from SerpAPI.")

# 🧾 Footer version tag
st.markdown('<div class="footer">Development version 1.008</div>', unsafe_allow_html=True)