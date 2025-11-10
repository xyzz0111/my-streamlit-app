import streamlit as st
import pandas as pd
from backend.sheets import read_all_records

def render():
    st.title("📚 Last 10 Records")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    records = read_all_records()
    
    if records:
        if len(records) > 1:
            last_10 = records[-10:] if len(records) > 10 else records[1:]
            df = pd.DataFrame(last_10, columns=records[0])
            st.dataframe(df, use_container_width=True, height=600)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Last 10 as CSV",
                data=csv,
                file_name="last_10_loan_records.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            st.info(f"📊 Showing: {len(df)} record(s) | Total in database: {len(records)-1}")
        else:
            st.info("📝 No records found. Add your first record!")
    else:
        st.warning("⚠️ Could not load records. Check your Google Sheets configuration.")