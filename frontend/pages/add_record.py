import streamlit as st
from backend.llm import call_gemini, EXTRACTION_PROMPT
from backend.sheets import append_record_to_sheet
from backend.utils import DEFAULT_FIELDS, validate_and_format_date

@st.fragment
def extraction_section():
    """Fragment for text extraction to avoid full reruns"""
    text_input = st.text_area(
        "📝 Paste record text here:", 
        height=200, 
        placeholder="हिंदी या English में डेटा पेस्ट करें...",
        key="text_input_area"
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        extract_btn = st.button("🔍 Extract Details", use_container_width=True, type="primary")
    
    if extract_btn and text_input.strip():
        with st.spinner("Extracting details ..."):
            extracted_data = call_gemini(EXTRACTION_PROMPT, text_input)
        
        if extracted_data:
            for field in DEFAULT_FIELDS:
                if field not in extracted_data:
                    extracted_data[field] = "NA"
            
            st.session_state["record_data"] = extracted_data
            st.success("✅ Extraction complete! Review and edit below.")
            st.rerun()
    elif extract_btn:
        st.warning("⚠️ Please paste some text before clicking Extract.")

def render():
    st.title("💰 Add New Loan Record")
    st.write("📊 Records are saved with bilingual support (Hindi + English)")
    
    # Show success message if it exists
    if "save_success" in st.session_state and st.session_state["save_success"]:
        st.success("✅ Record saved successfully !")
        st.info("🔄 You can now add another record")
        del st.session_state["save_success"]
    
    # Extraction section as fragment
    extraction_section()
    
    # Edit form
    if "record_data" in st.session_state:
        st.divider()
        st.subheader("✏️ Review and Edit Extracted Data")
        
        with st.form("edit_record_form", clear_on_submit=False):
            record = st.session_state["record_data"]
            
            # Date
            date_value = record.get('date', 'NA')
            date = st.text_input("📅 Date (DD/MM/YYYY)", date_value, help="Format: 15/03/2024")
            
            st.markdown("##### 👤 Name (both languages)")
            col1, col2 = st.columns(2)
            with col1:
                nameHindi = st.text_input("Name (Hindi)", record.get('nameHindi', 'NA'))
            with col2:
                nameEnglish = st.text_input("Name (English)", record.get('nameEnglish', 'NA'))
            
            st.markdown("##### 📍 Address (both languages)")
            col1, col2, col3 = st.columns(3)
            with col1:
                addressHindi = st.text_area("Address (Hindi)", record.get('addressHindi', 'NA'), height=100)
            with col2:
                addressEnglish = st.text_area("Address (English)", record.get('addressEnglish', 'NA'), height=100)
            with col3:
                wardArea = st.text_input("Ward/Area\n(वार्ड/क्षेत्र)", record.get('wardArea', 'NA'))
            
            st.markdown("##### 💰 Loan Details")
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                mobile = st.text_input("📱 Mobile", record.get('mobile', 'NA'))
            with col2:
                dairyNumber = st.text_input("Dairy", record.get('Dairy', 'd2'))
            with col3:
                pageNumber = st.text_input("📄 Page", record.get('pageNumber', 'NA'))
            with col4:
                amount = st.text_input("💰 Amount", record.get('amount', 'NA'))
            with col5:
                interest = st.text_input("📈 Interest", record.get('interest', 'NA'))
            
            st.markdown("##### 📝 Additional Context")
            col1, col2 = st.columns(2)
            with col1:
                guarantee = st.text_input("🔒 Guarantee (Months)", record.get('guarantee', 'NA'), help="e.g., 12 for 1 year")
            with col2:
                relationship = st.text_input("👥 Relationship/Reference", record.get('relationship', 'NA'), help="e.g., पत्नि प्रर्मिला देवी")
            
            # Form buttons
            col1, col2 = st.columns([3, 1])
            with col1:
                submit = st.form_submit_button("💾 Save to Google Sheets", type="primary", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("🔄 Clear", use_container_width=True)
            
            if submit:
                edited = {
                    'date': date, 'nameHindi': nameHindi, 'nameEnglish': nameEnglish,
                    'addressHindi': addressHindi, 'addressEnglish': addressEnglish,
                    'wardArea': wardArea, 'mobile': mobile, 'dairyNumber': dairyNumber,
                    'pageNumber': pageNumber, 'amount': amount, 'interest': interest,
                    'guarantee': guarantee, 'relationship': relationship
                }
                
                # Validate and format date
                if edited['date'] != "NA":
                    formatted_date = validate_and_format_date(edited['date'])
                    if formatted_date != edited['date']:
                        st.warning(f"⚠️ Date reformatted to: {formatted_date}")
                        edited['date'] = formatted_date
                
                with st.spinner("Saving to Google Sheets..."):
                    success = append_record_to_sheet(edited)
                
                if success:
                    st.session_state["save_success"] = True
                    del st.session_state["record_data"]
                    if "text_input_area" in st.session_state:
                        del st.session_state["text_input_area"]
                    st.rerun()
                else:
                    st.error("❌ Failed to save record. Please try again.")
            
            if cancel:
                del st.session_state["record_data"]
                st.rerun()