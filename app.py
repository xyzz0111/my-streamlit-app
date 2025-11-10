import streamlit as st
from frontend.pages import add_record, search_records, last_records
from backend.auth import check_password

st.set_page_config(page_title="💰 KuberX", layout="wide")

if not check_password():
    st.stop()

st.sidebar.success(f"👤 Logged in as: **{st.session_state['logged_in_user']}**")

if st.sidebar.button("🚪 Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

st.sidebar.markdown("---")

page = st.sidebar.radio("📋 Navigation", ["🔍 Search Records", "➕ Add Record", "📚 Last 10 Records"])

if page == "➕ Add Record":
    add_record.render()
elif page == "🔍 Search Records":
    search_records.render()
elif page == "📚 Last 10 Records":
    last_records.render()

st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ About KuberX")
st.sidebar.markdown("Loan record management system with bilingual support")