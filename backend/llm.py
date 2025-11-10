import re
import json
import streamlit as st
import requests
from backend.config import GEMINI_API_KEY, GEMINI_API_URL

EXTRACTION_PROMPT = """
आप एक डेटा एक्सट्रैक्शन सहायक हैं। 
नीचे दिए गए अनस्ट्रक्चर्ड टेक्स्ट से निम्नलिखित जानकारी निकालें:

IMPORTANT: You must respond with ONLY valid JSON, no extra text before or after.

**CRITICAL INSTRUCTIONS:**
1. **Name**: Extract in BOTH Hindi and English. If only one language is present, transliterate to the other.
2. **Address**: Extract in BOTH Hindi and English. If only one language is present, transliterate to the other.
3. **Ward/Area**: Extract locality/ward information (e.g., "नए वार्ड", "वार्ड 5", "पुराना वार्ड")
4. **Date**: Format as DD/MM/YYYY (e.g., 15/03/2024). If year is missing, use current year 2025.
5. **Mobile**: Keep as numbers only, no formatting
6. **Amount**: Extract only the numeric value (e.g., if "5000 रुपये" then just "5000")
7. **Interest**: Extract percentage or amount (e.g., "5%" or "250")
8. **Guarantee**: Extract guarantee period and CONVERT TO MONTHS. Examples:
   - "1 साल" / "1 year" → "12"
   - "6 महीने" / "6 months" → "6"
   - "30 दिन" / "30 days" → "1"
   - "2 साल" / "2 years" → "24"
   If not mentioned, write "Not mentioned"
9. **Relationship/Reference**: Extract relationship information (e.g., "पत्नि प्रर्मिला देवी", "पिता राम लाल", "Wife: Pramila Devi")

Format exactly like this:
{
  "date": "DD/MM/YYYY or Not mentioned",
  "nameHindi": "हिंदी नाम or Not mentioned",
  "nameEnglish": "English Name or Not mentioned",
  "addressHindi": "हिंदी पता or Not mentioned",
  "addressEnglish": "English Address or Not mentioned",
  "wardArea": "locality/ward info or Not mentioned",
  "mobile": "10-digit number or Not mentioned",
  "pageNumber": "value or Not mentioned",
  "amount": "numeric value only or Not mentioned",
  "interest": "value or Not mentioned",
  "guarantee": "number of months or Not mentioned",
  "relationship": "relationship/reference person or Not mentioned"
}

अगर कोई जानकारी नहीं दी गई है तो "Not mentioned" लिखें।
सिर्फ JSON आउटपुट दें, किसी अतिरिक्त टेक्स्ट के बिना।
"""

def extract_json_from_text(text: str) -> dict:
    if not text or not text.strip():
        return None
    
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    
    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        return None

def call_gemini(prompt: str, context: str = "") -> dict:
    if not GEMINI_API_KEY:
        st.error("⚠️ Gemini API key not found!")
        return None

    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }

    payload = {
        "contents": [{"parts": [{"text": f"{prompt}\n\n## Input:\n{context}"}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 1024}
    }

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload, timeout=90)
        response.raise_for_status()
        result = response.json()
        
        if "candidates" in result and result["candidates"]:
            raw_text = result["candidates"][0]["content"]["parts"][0]["text"]
            extracted_data = extract_json_from_text(raw_text)
            
            if extracted_data:
                from backend.utils import validate_and_format_date
                if 'date' in extracted_data:
                    extracted_data['date'] = validate_and_format_date(extracted_data['date'])
                
                return extracted_data
            else:
                st.error("⚠️ Could not parse JSON from Gemini response.")
                st.code(raw_text)
                return None
        else:
            st.error("❌ Gemini API did not return any data.")
            return None
            
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None

def call_gemini_simple(prompt: str) -> str:
    if not GEMINI_API_KEY:
        return None
    
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 512}
    }
    
    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if "candidates" in result and result["candidates"]:
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            text = re.sub(r'```json\s*', '', text)
            text = re.sub(r'```\s*', '', text)
            return text.strip()
        return None
    except:
        return None