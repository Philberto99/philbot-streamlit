import streamlit as st
import requests
import os
from datetime import datetime
from openai import AzureOpenAI

# 🔐 Load API keys
SERPAPI_KEY = st.secrets.get("SERPAPI_KEY", os.getenv("SERPAPI_KEY"))
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
WEATHER_API_KEY = st.secrets.get("WEATHER_API_KEY", os.getenv("WEATHER_API_KEY"))

# 🔧 Azure OpenAI client
client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

# 🎨 CSS styling
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

input {
    border: 2px solid #dddddd !important;
    transition: border-color 0.3s ease;
}
input:focus {
    border: 2px solid yellow !important;
}

.scroll-box {
    max-height: 70vh;
    overflow-y: auto;
    border: 2px solid #444;
    padding: 16px;
    border-radius: 12px;
    background-color: #001a33;
    margin-bottom: 1em;
}

.response {
    background-color: transparent;
    color: #f8f8f2;
    padding: 0.75em 0.5em;
    border-bottom: 1px solid rgba(255,255,255,0.12);
    white-space: pre-wrap;
    font-size: 1.05em;
    line-height: 1.7em;
}
.response:last-child {
    border-bottom: none;
}

.response .label {
    color: #87cefa;
    font-weight: 600;
    display: block;
    margin-bottom: 0.35em;
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

# 📦 Session state
if "response_log" not in st.session_state:
    st.session_state.response_log = []
if "should_rerun" not in st.session_state:
    st.session_state.should_rerun = False
if "input_version" not in st.session_state:
    st.session_state.input_version = 0
if "token_log" not in st.session_state:
    st.session_state.token_log = []

# 🧠 Input box with dynamic key
input_key = f"query_input_{st.session_state.input_version}"
user_input = st.text_input("Query", placeholder="Ask PhilBot…", key=input_key, label_visibility="collapsed")

# 🧠 Clear query after rerun
if st.session_state.should_rerun:
    st.session_state.should_rerun = False
    query = ""
else:
    query = user_input.strip()

# 🧠 Override matchers
def is_time_override(q):
    q = q.lower()
    return any(phrase in q for phrase in [
        "#what time is it", "#what's the time", "#what is my time",
        "#tell me the time", "#current time", "#time now"
    ])

def is_weather_override(q):
    q = q.lower()
    return any(phrase in q for phrase in [
        "#what is my weather like", "#what's the weather", "#weather now",
        "#current weather", "#how's the weather", "#weather in my area"
    ])

def is_cost_today(q):
    return q.lower().strip() in ["#what is today's cost", "#today's cost", "#cost today"]

def is_cost_total(q):
    return q.lower().strip() in ["#what is the total cost", "#total cost", "#how many tokens used"]

# ⏱️ Override: time
def get_current_time():
    now = datetime.now()
    return now.strftime("🕒 Current system time: %A, %d %B %Y — %H:%M:%S")

# 🌍 Override: IP-based weather
def get_ip_location():
    try:
        response = requests.get("http://ip-api.com/json/")
        data = response.json()
        return data.get("city", "your location"), data.get("lat"), data.get("lon")
    except:
        return None, None, None

def get_weather(lat, lon, city="your location"):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={WEATHER_API_KEY}"
        response = requests.get(url)
        data = response.json()
        if "main" in data and "weather" in data:
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            return f"🌦️ Weather in {city}: {temp}°C, {desc}"
        else:
            return "Weather data not available at the moment."
    except Exception as e:
        return f"Weather API failed: {str(e)}"

# 🧠 Response logic
if query:
    new_response = ""
    used_serpapi = False

    if is_time_override(query):
        new_response = f"**You asked:** {query}\n\n{get_current_time()}\n\n"

    elif is_weather_override(query):
        city, lat, lon = get_ip_location()
        if lat and lon:
            weather = get_weather(lat, lon, city)
            new_response = f"**You asked:** {query}\n\n{weather}\n\n"
        else:
            new_response = f"**You asked:** {query}\n\n🌍 Location not available. Please try again later.\n\n"

    elif is_cost_today(query):
        today = datetime.now().date()
        today_tokens = sum(
            entry["tokens"]
            for entry in st.session_state.token_log
            if datetime.fromisoformat(entry["timestamp"]).date() == today
        )
        cost = today_tokens / 1000 * 0.01
        new_response = f"**You asked:** {query}\n\nPhilBot says: Today's cost is {today_tokens} tokens, approximately ${cost:.4f}\n\n"

    elif is_cost_total(query):
        total_tokens = sum(entry["tokens"] for entry in st.session_state.token_log)
        cost = total_tokens / 1000 * 0.01
        new_response = f"**You asked:** {query}\n\nPhilBot says: Total cost is {total_tokens} tokens, approximately ${cost:.4f}\n\n"

    else:
        if AZURE_OPENAI_KEY and AZURE_OPENAI_DEPLOYMENT:
            try:
                messages = [{"role": "system", "content": "You are PhilAIbot, a semantic assistant built by Phil."}]
                for entry in st.session_state.response_log[:5]:
                    messages.append({"role": "assistant", "content": entry})
                messages.append({"role": "user", "content": query})

                completion = client.chat.completions.create(
                    model=AZURE_OPENAI_DEPLOYMENT,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500
                )
                gpt_response = completion.choices[0].message.content

                if hasattr(completion, "usage") and completion.usage:
                    tokens_used = completion.usage.total_tokens
                    st.session_state.token_log.append({
                        "query": query,
                        "tokens": tokens_used,
                        "timestamp": datetime.now().isoformat()
                    })

                new_response = f"**You asked:** {query}\n\nPhilBot says: {gpt_response}\n\n"
            except Exception as e:
                new_response = f"**You asked:** {query}\n\nPhilBot says: GPT-4o failed: {str(e)}\n\n"

        # Fallback SERPAPI (kept identical in spirit to v28/v29)
        if not new_response and SERPAPI_KEY:
            used_serpapi = True
            fallback_query = query
            params = {
                "q": fallback_query,
                "api_key": SERPAPI_KEY,
                "engine": "google",
            }
            response = requests.get("https://serpapi.com/search", params=params)
            data = response.json()
            if "organic_results" in data:
                fallback_response = f"**You asked:** {fallback_query}\n\nPhilBot says (via SERPAPI):\n\n"
                for result in data["organic_results"][:3]:
                    fallback_response += f"- [{result['title']}]({result['link']})\n"
                new_response = fallback_response
            else:
                new_response = f"**You asked:** {fallback_query}\n\nPhilBot says: No results found or API limit reached.\n\n"

    # Update state and rerun
    st.session_state.response_log.insert(0, new_response)
    st.session_state.used_serpapi = used_serpapi
    st.session_state.input_version += 1
    st.session_state.should_rerun = True
    st.rerun()

# 🖋️ Display responses in a single expanding, scrollable container (latest first)
entries_html = ["<div class='scroll-box'>"]
for entry in st.session_state.response_log:
    # Wrap each entry neatly; label for readability
    entries_html.append(f"<div class='response'><span class='label'>PhilBot says:</span>{entry}</div>")
entries_html.append("</div>")
st.markdown("".join(entries_html), unsafe_allow_html=True)

# 📊 Show SerpAPI usage only if fallback was used
if st.session_state.get("used_serpapi", False) and SERPAPI_KEY:
    usage_response = requests.get("https://serpapi.com/account", params={"api_key": SERPAPI_KEY})
    if usage_response.status_code == 200:
        usage_data = usage_response.json()
        searches_left = usage_data.get("plan_searches_left", "N/A")
        st.markdown(f"<div class='searches-left'>🔢 Searches left this month: {searches_left}</div>", unsafe_allow_html=True)

# 🧾 Footer (version 1.030)
st.markdown('<div class="footer">Development version 1.030b 🍀</div>', unsafe_allow_html=True)