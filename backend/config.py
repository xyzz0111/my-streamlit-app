import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
GEMINI_EMBEDDING_URL = "https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent"
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")


# Add these lines to your config.py file:

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = st.secrets.get("SPREADSHEET_ID") or os.getenv("SPREADSHEET_ID")

# Ensure USERS is always a dictionary, never None
USERS = st.secrets.get("USERS") or os.getenv("USERS")

SECRET_KEY =  st.secrets.get("SECRET_KEY") or os.environ.get("SECRET_KEY")

# If USERS is still None or empty, provide a default empty dict
if USERS is None:
    USERS = {}
    st.warning("⚠️ USERS not configured. Please set up user credentials in Streamlit secrets or environment variables.")

# If USERS is a string (from environment variable), try to parse it
if isinstance(USERS, str):
    try:
        import json
        USERS = json.loads(USERS)
    except json.JSONDecodeError:
        st.error("❌ Invalid USERS format. Expected JSON dictionary.")
        USERS = {}