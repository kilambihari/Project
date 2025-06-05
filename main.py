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

# --- Streamlit page config ---
st.set_page_config(page_title="☁️ AI Marketing Generator", layout="centered")

# --- Load API key from secrets ---
API_KEY = st.secrets.get("GEMINI_API_KEY")
if not API_KEY:
    st.error("If API key is not found, Set your GEMINI_API_KEY in Streamlit secrets.")
    st.stop()

# --- Helper to embed background image ---
def get_base64_bg(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

background_path = "pexels-freestockpro-31391838.jpg"  # Ensure this file exists in your directory
bg_base64 = get_base64_bg(background_path)

# --- Custom CSS Styling ---
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
    box-shadow: 0 0 15px rgba(0,0,0,0.8);
    text-align: center;
}}

.title-container h1 {{
    color: #ffffff;
    font-size: 3.2rem;
    font-weight: 900;
    margin-bottom: 10px;
    text-shadow: 2px 2px 8px rgba(0,0,0,0.9);
}}

.subtitle {{
    color: #eee;
    font-size: 1.3rem;
    margin-bottom: 20px;
    font-weight: 500;
    text-shadow: 1px 1px 6px rgba(0,0,0,0.8);
}}

.stSelectbox label {{
    color: #eee !important;
    font-weight: bold;
}}

div[data-baseweb="select"] > div {{
    background-color: rgba(20, 20, 20, 0.7) !important;
    color: white !important;
    border-radius: 10px;
}}

div[data-baseweb="select"] > div:hover {{
    background-color: rgba(40, 40, 40, 0.9) !important;
}}

.stTextInput input {{
    background-color: rgba(30, 30, 30, 0.8) !important;
    color: white !important;
    border: none !important;
    padding: 0.75rem;
    font-size: 1rem;
    border-radius: 10px !important;
}}

.stTextInput label {{
    color: white !important;
    font-weight: 600;
    font-size: 1rem;
}}

button[kind="secondary"], button[kind="primary"] {{
    font-size: 1rem;
    font-weight: bold;
    background: linear-gradient(135deg, #4a00e0, #8e2de2);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 10px 24px;
    cursor: pointer;
    transition: all 0.4s ease;
    box-shadow: 0 4px 14px rgba(0,0,0,0.4);
}}

button[kind="secondary"]:hover, button[kind="primary"]:hover {{
    transform: scale(1.05);
    box-shadow: 0 6px 18px rgba(0,0,0,0.5);
    filter: brightness(1.1);
}}

.output-box {{
    background-color: rgba(0, 0, 0, 0.6);
    padding: 20px;
    border-radius: 10px;
    margin-top: 15px;
    color: #fff;
    font-size: 1.25rem;
    line-height: 1.6;
    backdrop-filter: blur(6px);
    border: 1px solid rgba(255,255,255,0.2);
    text-shadow: 1px 1px 5px rgba(0,0,0,0.9);
}}

.typing {{
    color: #fff;
    font-size: 1.2rem;
    line-height: 1.5;
    text-shadow: 1px 1px 5px rgba(0,0,0,0.8);
}}
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="title-container">
    <h1>☁️ AI Marketing Idea Generator</h1>
    <p class="subtitle">Catchy <b>slogans</b>, <b>ad copies</b> and <b> Bold campaign ideas. AI Marketing, Simplified.</b></p>
</div>
""", unsafe_allow_html=True)

# --- Gemini LLM Wrapper for LangChain ---
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

# --- Typewriter Effect ---
def type_writer_effect(text, speed=0.02):
    output = ""
    placeholder = st.empty()
    for char in text:
        output += char
        placeholder.markdown(f"<div class='typing'>{output}</div>", unsafe_allow_html=True)
        time.sleep(speed)

# --- Caching ---
CACHE_FILE = "generation_cache.pkl"
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "rb") as f:
        cache = pickle.load(f)
else:
    cache = {}

# --- Main App Logic ---
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
