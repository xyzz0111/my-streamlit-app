import streamlit as st
import requests
from backend.config import GEMINI_API_KEY, GEMINI_EMBEDDING_URL

def get_embedding(text: str) -> list:
    if not GEMINI_API_KEY or not text.strip():
        return None
    
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }
    
    payload = {
        "content": {
            "parts": [{"text": text}]
        }
    }
    
    try:
        response = requests.post(GEMINI_EMBEDDING_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if "embedding" in result:
            return result["embedding"]["values"]
        return None
    except Exception as e:
        st.warning(f"Embedding error: {e}")
        return None