# ☁️ AI Marketing Generator

An interactive AI-powered Streamlit app that generates **slogans**, **ad copies**, and **marketing campaign ideas** using **Google Gemini** via LangChain. It includes **user authentication** via **email/password** and **Google Sign-In (OAuth2)** using **Firebase**.

---

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

