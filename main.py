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
import hashlib

# --- Streamlit page config ---
st.set_page_config(page_title="☁️ AI Marketing Generator", layout="centered")

# --- Load API key from secrets ---
API_KEY = st.secrets.get("GEMINI_API_KEY")
if not API_KEY:
    st.error("If API key is not found, Set your GEMINI_API_KEY in Streamlit secrets.")
    st.stop()

# --- Authentication System ---
USERS_FILE = "users.pkl"

if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "rb") as f:
        users = pickle.load(f)
else:
    users = {}

def save_users():
    with open(USERS_FILE, "wb") as f:
        pickle.dump(users, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_page():
    st.title("🔐 Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if email in users and users[email]["password"] == hash_password(password):
            st.session_state.logged_in = True
            st.session_state.email = email
            st.success("Login successful!")
            
        else:
            st.error("Invalid email or password.")
    if st.button("Go to Signup"):
        st.session_state.page = "signup"
        

def signup_page():
    st.title("📝 Signup")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Signup"):
        if email in users:
            st.error("User already exists.")
        else:
            users[email] = {"password": hash_password(password)}
            save_users()
            st.success("Signup successful! Please log in.")
            st.session_state.page = "login"
            st.experimental_rerun()
    if st.button("Go to Login"):
        st.session_state.page = "login"
        st.experimental_rerun()

def logout():
    st.session_state.logged_in = False
    st.session_state.email = ""
    st.experimental_rerun()

def admin_dashboard():
    st.subheader("👑 Admin Dashboard")
    st.info("Welcome, admin! You can view user stats here.")
    st.write(users)

# --- App Entry ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.page = "login"

if not st.session_state.logged_in:
    if st.session_state.page == "login":
        login_page()
    else:
        signup_page()
    st.stop()

# --- Show logout and admin dashboard ---
st.sidebar.success(f"Logged in as {st.session_state.email}")
if st.sidebar.button("Logout"):
    logout()
if st.session_state.email == "admin@example.com":
    admin_dashboard()

# --- Background & Styling ---
def get_base64_bg(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

background_path = "pexels-freestockpro-31391838.jpg"
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
/* rest of CSS unchanged */
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="title-container">
    <h1>☁️ AI Marketing Idea Generator</h1>
    <p class="subtitle">Catchy <b>slogans</b>, <b>ad copies</b> and <b> Bold campaign ideas. AI Marketing, Simplified.</b></p>
</div>
""", unsafe_allow_html=True)

class GeminiLLM(LLM):
    model_name: str = "gemini-1.5-flash"
    _model: Any = PrivateAttr()

    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        super().__init__()
        genai.configure(api_key=api_key)
        self.model_name = model_name
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

def type_writer_effect(text, speed=0.02):
    output = ""
    placeholder = st.empty()
    for char in text:
        output += char
        placeholder.markdown(f"<div class='typing'>{output}</div>", unsafe_allow_html=True)
        time.sleep(speed)

CACHE_FILE = "generation_cache.pkl"
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "rb") as f:
        cache = pickle.load(f)
else:
    cache = {}

# --- Generator ---
task_type = st.selectbox(" Select what you want to generate:", ["Slogan", "Ad Copy", "Campaign Idea"])
user_input = st.text_input(" Describe your product or brand:", "e.g. 'A new eco-friendly recycled cotton clothing'").strip()

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
                    result = None

        if result:
            st.markdown(" 🎯 Generated Output")
            st.markdown(f'<div class="output-box">{result}</div>', unsafe_allow_html=True)
else:
    st.info("Fill in the product/brand description to begin.")
