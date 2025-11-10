import streamlit as st
from backend.sheets import read_all_records
from backend.search import basic_search, semantic_search, ai_deep_search
from .components import display_record

def render():
    st.title("🔍 Smart Record Search")
    st.write("🟢 Searching Active Records Only")
    
    search_query = st.text_input("🔎 Enter search query:", placeholder="e.g., राज कुमार, Raj Kumar, 9876543210, पटना")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        basic_search_btn = st.button("⚡ Quick Search (Fast)", use_container_width=True)
    with col2:
        semantic_search_btn = st.button("🧠 Smart Search (AI)", use_container_width=True)
    with col3:
        deep_search_btn = st.button("🔬 Deep Search (Thorough)", use_container_width=True)
    
    if basic_search_btn or semantic_search_btn or deep_search_btn:
        keys_to_delete = [key for key in st.session_state.keys() if key.startswith('confirm_close_')]
        for key in keys_to_delete:
            del st.session_state[key]
        if 'current_search_results' in st.session_state:
            del st.session_state['current_search_results']
    
    if search_query.strip() and (basic_search_btn or semantic_search_btn or deep_search_btn):
        records = read_all_records()
        
        if not records or len(records) < 2:
            st.warning("⚠️ No records found in database.")
        else:
            results = []
            
            if basic_search_btn:
                with st.spinner("Processing..."):
                    results = basic_search(records, search_query)
                
            elif semantic_search_btn:
                results = semantic_search(records, search_query, top_k=5)
                
            elif deep_search_btn:
                with st.spinner("Processing..."):
                    results = ai_deep_search(records, search_query, batch_size=20)
            
            if results:
                st.success(f"✅ Found {len(results)} matching record(s)")
                st.session_state['current_search_results'] = results
                
                for idx, result in enumerate(results, 1):
                    display_record(result, idx)
                
                if basic_search_btn and len(results) < 3:
                    st.info("💡 Didn't find what you're looking for? Try **Smart Search** or **Deep Search** for better results.")
            else:
                st.warning("❌ No matching records found.")
                
                if basic_search_btn:
                    st.info("💡 Try using **Smart Search** or **Deep Search** for better results.")
                elif semantic_search_btn:
                    st.info("💡 Try **Deep Search** for a more thorough AI-powered search.")
    
    elif 'current_search_results' in st.session_state and st.session_state['current_search_results']:
        results = st.session_state['current_search_results']
        st.success(f"✅ Found {len(results)} matching record(s)")
        
        for idx, result in enumerate(results, 1):
            display_record(result, idx)