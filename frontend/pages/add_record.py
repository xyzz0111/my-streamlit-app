import streamlit as st
from backend.llm import call_gemini, EXTRACTION_PROMPT
from backend.sheets import append_record_to_sheet
from backend.utils import DEFAULT_FIELDS, validate_and_format_date

def render():
    st.title("💰 Add New Loan Record")
    st.write("📊 Records are saved with bilingual support (Hindi + English)")
    
    text_input = st.text_area("📝 Paste record text here:", height=200, placeholder="हिंदी या English में डेटा पेस्ट करें...")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        extract_btn = st.button("🔍 Extract Details", use_container_width=True, type="primary")
    
    if extract_btn:
        if text_input.strip():
            with st.spinner("Extracting details with Gemini AI..."):
                extracted_data = call_gemini(EXTRACTION_PROMPT, text_input)
            
            if extracted_data:
                for field in DEFAULT_FIELDS:
                    if field not in extracted_data:
                        extracted_data[field] = "Not mentioned"
                
                st.session_state["record_data"] = extracted_data
                st.success("✅ Extraction complete! Review and edit below.")
        else:
            st.warning("⚠️ Please paste some text before clicking Extract.")
    
    if "record_data" in st.session_state:
        st.subheader("✏️ Review and Edit Extracted Data")
        record = st.session_state["record_data"]
        
        edited = {}
        
        col1, col2 = st.columns(2)
        with col1:
            date_value = record.get('date', 'Not mentioned')
            edited['date'] = st.text_input("📅 Date (DD/MM/YYYY)", date_value, help="Format: 15/03/2024")
        
        st.markdown("---")
        st.subheader("👤 Name (both languages)")
        col1, col2 = st.columns(2)
        with col1:
            edited['nameHindi'] = st.text_input("Name (Hindi)", record.get('nameHindi', 'Not mentioned'))
        with col2:
            edited['nameEnglish'] = st.text_input("Name (English)", record.get('nameEnglish', 'Not mentioned'))
        
        st.markdown("---")
        st.subheader("📍 Address (both languages)")
        col1, col2, col3 = st.columns(3)
        with col1:
            edited['addressHindi'] = st.text_area("Address (Hindi)", record.get('addressHindi', 'Not mentioned'), height=100)
        with col2:
            edited['addressEnglish'] = st.text_area("Address (English)", record.get('addressEnglish', 'Not mentioned'), height=100)
        with col3:
            edited['wardArea'] = st.text_input("Ward/Area\n(वार्ड/क्षेत्र)", record.get('wardArea', 'Not mentioned'))
        
        st.markdown("---")
        st.subheader("💰 Loan Details")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            edited['mobile'] = st.text_input("📱 Mobile", record.get('mobile', 'Not mentioned'))
        with col2:
            edited['pageNumber'] = st.text_input("📄 Page Number", record.get('pageNumber', 'Not mentioned'))
        with col3:
            edited['amount'] = st.text_input("💰 Amount", record.get('amount', 'Not mentioned'))
        with col4:
            edited['interest'] = st.text_input("📈 Interest", record.get('interest', 'Not mentioned'))
        
        st.markdown("---")
        st.subheader("📝 Additional Context")
        col1, col2 = st.columns(2)
        with col1:
            edited['guarantee'] = st.text_input("🔒 Guarantee (Months)", record.get('guarantee', 'Not mentioned'), help="Guarantee period in months (e.g., 12 for 1 year)")
        with col2:
            edited['relationship'] = st.text_input("👥 Relationship/Reference", record.get('relationship', 'Not mentioned'), help="e.g., पत्नि प्रर्मिला देवी, पिता राम लाल")
        
        st.markdown("---")
        
        if st.button("💾 Save to Google Sheets", type="primary", use_container_width=True):
            if edited['date'] != "Not mentioned":
                formatted_date = validate_and_format_date(edited['date'])
                if formatted_date != edited['date']:
                    st.warning(f"⚠️ Date reformatted to: {formatted_date}")
                    edited['date'] = formatted_date
            
            with st.spinner("Saving to Google Sheets..."):
                success = append_record_to_sheet(edited)
                
                if success:
                    st.success("✅ Record saved successfully!")
                    
                    if st.button("➕ Add Another Record"):
                        del st.session_state["record_data"]
                        st.rerun()