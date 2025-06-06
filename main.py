import os
import streamlit as st
import google.generativeai as genai
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import LLMResult
from pydantic import PrivateAttr
from typing import List, Optional, Any
import base64
import pickle
import hashlib

# --- Page Config ---
st.set_page_config(page_title="☁️ AI Marketing Generator", layout="centered")

# --- Constants ---
API_KEY = st.secrets.get("GEMINI_API_KEY", "")
USERS_FILE = "users.pkl"
CACHE_FILE = "generation_cache.pkl"
BACKGROUND_IMAGE = "background_image.jpg"

# --- Load Users ---
if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "rb") as f:
        users = pickle.load(f)
else:
    users = {
        "hari@gmail.com": {"password": hashlib.sha256("admin123".encode()).hexdigest()}
    }

def save_users():
    with open(USERS_FILE, "wb") as f:
        pickle.dump(users, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- Gemini Wrapper ---
class GeminiLLM(LLM):
    model_name: str = "models/gemini-1.5-flash"
    _model: Any = PrivateAttr()

    def __init__(self, api_key: str, model_name: str = "models/gemini-1.5-flash"):
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

# --- Background Styling ---
def get_base64_bg(path):
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

bg_base64 = get_base64_bg(BACKGROUND_IMAGE)

st.markdown(f"""
<style>
html, body, [data-testid="stApp"] {{
    background-image: url("data:image/jpg;base64,{bg_base64}");
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
    background-position: center;
    font-family: 'Segoe UI', sans-serif;
}}
h1, h2, h3, .stTextInput label, .stSelectbox label {{
    color: white !important;
    text-shadow: 1px 1px 3px black;
}}
input, textarea, select {{
    background-color: rgba(255, 255, 255, 0.97) !important;
    color: black !important;
    border-radius: 5px !important;
    padding: 10px;
    font-size: 16px;
}}
input:focus, textarea:focus, select:focus {{
    outline: 2px solid #ffa94d !important;
    box-shadow: 0 0 5px #ffa94d !important;
}}
.stSelectbox div[role="combobox"] {{
    border-radius: 5px;
    border: none !important;
    background-color: rgba(0, 0, 0, 0.6) !important;
}}
.stSelectbox div[role="combobox"] > div:first-child {{
    color: white !important;
    font-weight: 600;
    padding: 8px;
}}
.stButton>button {{
    background-color: #ffa94d;
    color: black;
    border-radius: 10px;
    font-weight: bold;
    padding: 8px 16px;
    transition: 0.2s ease-in-out;
}}
.stButton>button:hover {{
    background-color: #ff922b;
}}
.title-container {{
    text-align: center;
    margin-bottom: 30px;
    background-color: rgba(0, 0, 0, 0.5);
    padding: 20px;
    border-radius: 15px;
}}
.title-container h1 {{
    font-size: 40px;
    margin-bottom: 10px;
    color: white;
    text-shadow: 2px 2px 5px rgba(0,0,0,0.8);
}}
.title-container .subtitle {{
    font-size: 18px;
    color: #f1f1f1;
    text-shadow: 1px 1px 4px rgba(0,0,0,0.7);
}}
.output-box {{
    background: rgba(0, 0, 0, 0.6);
    padding: 15px;
    border-radius: 10px;
    font-size: 18px;
    margin-top: 15px;
    color: #ffffff;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.6);
}}
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="title-container">
    <h1>☁️ AI Marketing Idea Generator</h1>
    <p class="subtitle">Catchy <b>slogans</b>, <b>ad copies</b>, and <b>bold campaign ideas</b>. AI Marketing, Simplified.</p>
</div>
""", unsafe_allow_html=True)

# --- Session State Init ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.page = "login"
    st.session_state.email = ""
    st.session_state.show_history = False

# --- Auth Pages ---
def login_page():
    st.subheader("🔐 Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        if email in users and users[email]["password"] == hash_password(password):
            st.session_state.logged_in = True
            st.session_state.email = email
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid email or password.")
    if st.button("Go to Signup"):
        st.session_state.page = "signup"
        st.rerun()

def signup_page():
    st.subheader("📝 Signup")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")
    if st.button("Signup"):
        if email in users:
            st.error("User already exists.")
        else:
            users[email] = {"password": hash_password(password)}
            save_users()
            st.success("Signup successful! Please log in.")
            st.session_state.page = "login"
            st.rerun()

    if st.button("Go to Login"):
        st.session_state.page = "login"
        st.rerun()

def logout():
    st.session_state.logged_in = False
    st.session_state.email = ""
    st.rerun()

# --- Login Flow ---
if not st.session_state.logged_in:
    if st.session_state.page == "login":
        login_page()
    else:
        signup_page()
    st.stop()

# --- Sidebar ---
st.sidebar.success(f"Logged in as {st.session_state.email}")
if st.sidebar.button("Logout"):
    logout()

if st.sidebar.button("📜 Show History" if not st.session_state.show_history else "📜 Hide History"):
    st.session_state.show_history = not st.session_state.show_history

if st.sidebar.button("🗑️ Delete History"):
    email = st.session_state.email
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "rb") as f:
            cache = pickle.load(f)
        keys_to_delete = [key for key in cache if key[0] == email]
        for key in keys_to_delete:
            del cache[key]
        with open(CACHE_FILE, "wb") as f:
            pickle.dump(cache, f)
    st.sidebar.success("Your generation history has been cleared!")

# --- Load or Init Cache ---
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "rb") as f:
        cache = pickle.load(f)
else:
    cache = {}

# --- Prompt ---
task_type = st.selectbox("Select what you want to generate:", ["-- Select --", "Slogan", "Ad Copy", "Campaign Idea"])
user_input = st.text_input("Describe your product or brand:", "e.g. 'A new eco-friendly recycled cotton clothing'").strip()

prompt_templates = {
    "Slogan": "Create a catchy marketing slogan for: {product}",
    "Ad Copy": "Write a persuasive ad copy for: {product}",
    "Campaign Idea": "Come up with a creative marketing campaign for: {product}"
}

generate_clicked = st.button("🚀 Generate")

# --- Generate Output ---
if user_input and task_type != "-- Select --" and generate_clicked:
    key = (st.session_state.email, task_type, user_input)
    if key in cache:
        result = cache[key]
        st.success("Loaded from cache!")
    else:
        try:
            with st.spinner("Generating..."):
                llm = GeminiLLM(api_key=API_KEY)
                prompt = PromptTemplate.from_template(prompt_templates[task_type])
                chain = LLMChain(llm=llm, prompt=prompt)
                result = chain.run(product=user_input)
                cache[key] = result
                with open(CACHE_FILE, "wb") as f:
                    pickle.dump(cache, f)
        except Exception as e:
            st.error(f"Error: {e}")
            result = None

    if result:
        st.markdown("🎯 Generated Output")
        st.markdown(f'<div class="output-box">{result}</div>', unsafe_allow_html=True)

# --- Show History (Main Area) ---
if st.session_state.show_history:
    user_email = st.session_state.email
    history_items = [(k, v) for k, v in cache.items() if k[0] == user_email]
    
    if history_items:
        st.subheader("📜 Your Generation History")
        for (email, task, desc), output in reversed(history_items):
            with st.expander(f"📝 {task} for: {desc}"):
                st.markdown(f'<div class="output-box">{output}</div>', unsafe_allow_html=True)
    else:
        st.info("No history found.")

# --- Default Info ---
if not user_input:
    st.info("Please describe your product or brand to start generating.")
