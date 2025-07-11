# ☁️ AI Marketing Generator

An interactive AI-powered Streamlit app that generates **slogans**, **ad copies**, and **marketing campaign ideas** using **Google Gemini** via LangChain. It includes **user authentication** via **email/password** and **Google Sign-In (OAuth2)** using **Firebase**.

---

## 🚀 Live Demo

Click below to try the app:

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://project-eamay5pxacuhxuvqhe6xtf.streamlit.app/)

Or open directly:  
👉 https://project-eamay5pxacuhxuvqhe6xtf.streamlit.app/


## ✨ Features

- 🔐 **User Authentication**
  - Email/Password login and signup
  - Google Sign-In via Firebase OAuth
- 🤖 **Marketing Idea Generation**
  - Catchy Slogans
  - Persuasive Ad Copies
  - Creative Campaign Ideas
- ⚡ **Gemini API Integration**
  - Uses `google-generativeai` through a custom LangChain wrapper
- 💾 **Session and Cache Handling**
  - Pickle-based caching to avoid redundant LLM calls
- 🎨 **Custom Background and UI Styling**
  - Background image and custom CSS
- 👤 **Admin/Default User Setup**
  - Comes with default admin credentials

---

## 📁 Project Structure
├── main.py # Main Streamlit application
├── users.pkl # Stores registered users securely (hashed)
├── generation_cache.pkl # Caches generation results for reuse
├── pexels-freestockpro.jpg # Background image
├── README.md # This file
├── requirements.txt # Python dependencies
└── .streamlit/
└── secrets.toml # Stores API keys and Firebase config


---

## 🔧 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/kilambihari/project.git
cd project

5. Default Admin Credentials
To log in as admin:

Email: hari@gmail.com

Password: admin123

You can also sign up as a new user.

💡 Usage
Log in or Sign up.

Choose the type of content: Slogan, Ad Copy, or Campaign Idea.

Describe your brand or product.

Click "🚀 Generate" to get results powered by Google Gemini AI.

Results are cached and styled beautifully on the interface.

🔐 Authentication Notes

Email/Password credentials are stored as SHA256 hashes.

User login states are stored via st.session_state.

🛡️ Security
Passwords are hashed before saving to disk.

Pickled files are not encrypted; for production use, consider a proper DB and secure backend.

Use HTTPS and proper OAuth2 flows in deployed settings.

📜 License
This project is open-source and available under the MIT License.

✍️ Author
Built by Harivadan Kilambi




