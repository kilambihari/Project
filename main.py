import os
import streamlit as st
import google.generativeai as genai
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import LLMResult
from pydantic import PrivateAttr
from typing import List, Optional, Any
import time
import base64
import pickle

# -------------------
# Streamlit Config
# -------------------
st.set_page_config(page_title="☁️ AI Marketing Generator", layout="centered")

# -------------------
# Load Gemini API Key
# -------------------
API_KEY = st.secrets.get("GEMINI_API_KEY")
if not API_KEY:
    st.error("Set your GEMINI_API_KEY in Streamlit secrets.")
    st.stop()

# -------------------
# Background Setup
# -------------------
def get_base64_bg(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

background_path = "pexels-freestockpro-31391838.jpg"  # Ensure this exists
bg_base64 = get_base64_bg(background_path)

st.markdown(f"""
<style>
html, body, [data-testid="stApp"] {{
    background-image: url("data:image/jpg;base64,{bg_base64}");
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
    background-position: center;
    color: #f3f3f3;
    font-family: 'Segoe UI', sans-serif;
}}
.title-container {{
    background: rgba(0, 0, 0, 0.75);
    padding: 25px 30px;
    border-radius: 15px;
    max-width: 900px;
    margin: 30px auto 10px auto;
    text-align: center;
}}
.title-container h1 {{
    color: #ffffff;
    font-size: 3.2rem;
    font-weight: 900;
    margin-bottom: 10px;
}}
.subtitle {{
    color: #eee;
    font-size: 1.3rem;
    margin-bottom: 20px;
}}
.output-box {{
    background-color: rgba(0, 0, 0, 0.6);
    padding: 20px;
    border-radius: 10px;
    margin-top: 15px;
    color: #fff;
    font-size: 1.25rem;
    line-height: 1.6;
}}
</style>
""", unsafe_allow_html=True)

# -------------------
# Typewriter Effect
# -------------------
def type_writer_effect(text, speed=0.02):
    output = ""
    placeholder = st.empty()
    for char in text:
        output += char
        placeholder.markdown(f"<div class='typing'>{output}</div>", unsafe_allow_html=True)
        time.sleep(speed)

# -------------------
# Gemini Wrapper
# -------------------
class GeminiLLM(LLM):
    model_name: str = "gemini-1.5-flash"
    _model: Any = PrivateAttr()

    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        super().__init__()
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model_name=model_name)

    @property
    def _llm_type(self) -> str:
        return "google-gemini"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        response = self._model.generate_content(prompt)
        return response.text.strip()

    def _generate(self, prompts: List[str], stop: Optional[List[str]] = None, run_manager: Optional[Any] = None) -> LLMResult:
        generations = [[{"text": self._call(prompt, stop)}] for prompt in prompts]
        return LLMResult(generations=generations)

# -------------------
# Cache Setup
# -------------------
CACHE_FILE = "generation_cache.pkl"
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "rb") as f:
        cache = pickle.load(f)
else:
    cache = {}

# -------------------
# Login Credentials
# -------------------
USER_CREDENTIALS = {
    "kilambihari@gmail.com": "password123",
    "user@example.com": "welcome"
}

# -------------------
# Login Page
# -------------------
def login_page():
    st.markdown("## 🔐 Login to Continue")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if email in USER_CREDENTIALS and USER_CREDENTIALS[email] == password:
            st.session_state.logged_in = True
        else:
            st.error("Invalid email or password")

# -------------------
# Main App
# -------------------
def show_marketing_app():
    st.markdown("""
    <div class="title-container">
        <h1>☁️ AI Marketing Idea Generator</h1>
        <p class="subtitle">Catchy <b>slogans</b>, <b>ad copies</b> and <b>bold campaign ideas</b>. AI Marketing, Simplified.</p>
    </div>
    """, unsafe_allow_html=True)

    task_type = st.selectbox("What do you want to generate?", ["Slogan", "Ad Copy", "Campaign Idea"])
    user_input = st.text_input("Describe your product or brand:", "e.g. eco-friendly cotton clothing").strip()

    prompt_templates = {
        "Slogan": "Create a catchy marketing slogan for: {product}",
        "Ad Copy": "Write a persuasive ad copy for: {product}",
        "Campaign Idea": "Come up with a creative marketing campaign for: {product}"
    }

    if user_input:
        if st.button("🚀 Generate"):
            key = (task_type, user_input)
            if key in cache:
                result = cache[key]
                st.success("Loaded from cache!")
            else:
                with st.spinner("Thinking..."):
                    try:
                        llm = GeminiLLM(api_key=API_KEY)
                        prompt = PromptTemplate.from_template(prompt_templates[task_type])
                        chain = LLMChain(llm=llm, prompt=prompt)
                        result = chain.run(product=user_input)
                        cache[key] = result
                        with open(CACHE_FILE, "wb") as f:
                            pickle.dump(cache, f)
                    except Exception as e:
                        st.error(f"Something went wrong: {e}")
                        return
            st.markdown("### 🎯 Generated Output")
            st.markdown(f'<div class="output-box">{result}</div>', unsafe_allow_html=True)

# -------------------
# Page Control
# -------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    show_marketing_app()
else:
    login_page()

