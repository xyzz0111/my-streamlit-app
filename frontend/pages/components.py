import streamlit as st
from backend.sheets import update_loan_status

@st.fragment
def close_loan_fragment(row_number: int, record_id: str):
    st.markdown("---")
    st.markdown("### 🔴 Close Loan")
    
    @st.dialog("Confirm Loan Closure")
    def confirm_close_dialog():
        st.warning(f"⚠️ Are you sure you want to close this loan?")
        st.info(f"**Loan ID:** {record_id}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, Close Loan", type="primary", use_container_width=True):
                with st.spinner("Closing loan..."):
                    success = update_loan_status(row_number, "Closed")
                
                if success:
                    st.success("✅ Loan closed successfully!")
                    if 'current_search_results' in st.session_state:
                        del st.session_state['current_search_results']
                    st.rerun()
                else:
                    st.error("❌ Failed to close loan. Please try again.")
        
        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                st.rerun()
    
    if st.button("🔴 Close This Loan", key=f"close_{row_number}", type="secondary", use_container_width=True):
        confirm_close_dialog()

def display_record(result: dict, idx: int):
    name_display = f"{result.get('nameHindi', 'N/A')} / {result.get('nameEnglish', 'N/A')}"
    record_id = result.get('recordId', 'N/A')
    loan_status = result.get('loanStatus', 'Active')
    row_number = result['row_number']
    
    status_color = "🟢" if loan_status == "Active" else "🔴"
    
    with st.expander(f"📄 Record {idx}: {name_display} (ID: {record_id}) {status_color}", expanded=False):
        
        st.markdown("### 🔖 Record Information")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**🆔 Record ID:**\n{record_id}")
        with col2:
            st.info(f"**📅 Date:**\n{result.get('date', 'N/A')}")
        with col3:
            st.info(f"**📊 Status:**\n{status_color} {loan_status}")
        
        st.markdown("---")
        st.markdown("### 📋 Record Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**👤 Name (Hindi):** {result.get('nameHindi', 'N/A')}")
            st.write(f"**👤 Name (English):** {result.get('nameEnglish', 'N/A')}")
            st.write(f"**📍 Address (Hindi):** {result.get('addressHindi', 'N/A')}")
            st.write(f"**📍 Address (English):** {result.get('addressEnglish', 'N/A')}")
            st.write(f"**🏘️ Ward/Area:** {result.get('wardArea', 'N/A')}")
            st.write(f"**👥 Relationship:** {result.get('relationship', 'N/A')}")

        with col2:
            st.write(f"**📱 Mobile:** {result.get('mobile', 'N/A')}")
            st.write(f"**📄 Dairy Number:** {result.get('dairyNumber', 'N/A')}")
            st.write(f"**📄 Page Number:** {result.get('pageNumber', 'N/A')}")
            st.write(f"**💰 Amount:** {result.get('amount', 'N/A')}")
            st.write(f"**📈 Interest:** {result.get('interest', 'N/A')}")
            st.write(f"**🔒 Guarantee (Months):** {result.get('guarantee', 'N/A')}")
        
        if loan_status == "Active":
            close_loan_fragment(row_number, record_id)