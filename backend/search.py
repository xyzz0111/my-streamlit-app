import json
import streamlit as st
import numpy as np
from backend.embeddings import get_embedding
from backend.llm import call_gemini_simple

# try:
#     from sklearn.metrics.pairwise import cosine_similarity
#     SKLEARN_AVAILABLE = True
# except ImportError:
#     SKLEARN_AVAILABLE = False
def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b.T) / (np.linalg.norm(a, axis=1)[:, np.newaxis] * np.linalg.norm(b, axis=1))

def basic_search(records: list, query: str) -> list:
    if not records or len(records) < 2:
        return []
    
    query_lower = query.lower().strip()
    results = []
    
    headers = records[0]
    for i, row in enumerate(records[1:], start=2):
        if len(row) < len(headers):
            row.extend([''] * (len(headers) - len(row)))
        
        record_dict = dict(zip(headers, row))
        record_dict['row_number'] = i
        
        loan_status = record_dict.get('loanStatus', 'Active')
        if loan_status == 'Closed':
            continue
        
        searchable_text = " ".join([
            record_dict.get('recordId', ''),
            record_dict.get('nameHindi', ''),
            record_dict.get('nameEnglish', ''),
            record_dict.get('addressHindi', ''),
            record_dict.get('addressEnglish', ''),
            record_dict.get('wardArea', ''),
            record_dict.get('mobile', ''),
            record_dict.get('relationship', '')
        ]).lower()
        
        if query_lower in searchable_text:
            results.append(record_dict)
    
    return results

def semantic_search(records: list, query: str, top_k: int = 5) -> list:
    if not records or len(records) < 2:
        return []
    
    with st.spinner("Processing..."):
        query_embedding = get_embedding(query)
        
        if not query_embedding:
            st.warning("Could not compute query embedding")
            return []
        
        headers = records[0]
        similarities = []
        
        for i, row in enumerate(records[1:], start=2):
            if len(row) < len(headers):
                row.extend([''] * (len(headers) - len(row)))
            
            record_dict = dict(zip(headers, row))
            record_dict['row_number'] = i
            
            loan_status = record_dict.get('loanStatus', 'Active')
            if loan_status == 'Closed':
                continue
            
            record_text = " ".join([
                record_dict.get('recordId', ''),
                record_dict.get('nameHindi', ''),
                record_dict.get('nameEnglish', ''),
                record_dict.get('addressHindi', ''),
                record_dict.get('addressEnglish', ''),
                record_dict.get('wardArea', ''),
                record_dict.get('mobile', ''),
                record_dict.get('date', ''),
                record_dict.get('amount', ''),
                record_dict.get('relationship', '')
            ])
            
            record_embedding = get_embedding(record_text)
            
            if record_embedding:
                similarity = cosine_similarity(
                    [query_embedding],
                    [record_embedding]
                )[0][0]
                
                similarities.append({
                    'record': record_dict,
                    'similarity': similarity
                })
        
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        results = [item['record'] for item in similarities[:top_k]]
        
        return results

def ai_deep_search(records: list, query: str, batch_size: int = 20) -> list:
    if not records or len(records) < 2:
        return []
    
    headers = records[0]
    all_records = []
    
    for i, row in enumerate(records[1:], start=2):
        if len(row) < len(headers):
            row.extend([''] * (len(headers) - len(row)))
        record_dict = dict(zip(headers, row))
        record_dict['row_number'] = i
        
        loan_status = record_dict.get('loanStatus', 'Active')
        if loan_status == 'Closed':
            continue
        
        all_records.append(record_dict)
    
    if not all_records:
        return []
    
    best_matches = []
    total_batches = (len(all_records) + batch_size - 1) // batch_size
    
    progress_bar = st.progress(0)
    
    for batch_idx in range(0, len(all_records), batch_size):
        batch = all_records[batch_idx:batch_idx + batch_size]
        
        batch_text = "\n\n".join([
            f"Record {r['row_number']}: ID: {r.get('recordId', '')}, Name: {r.get('nameHindi', '')} / {r.get('nameEnglish', '')}, Address: {r.get('addressHindi', '')} / {r.get('addressEnglish', '')}, Ward: {r.get('wardArea', '')}, Mobile: {r.get('mobile', '')}, Amount: {r.get('amount', '')}, Relationship: {r.get('relationship', '')}"
            for r in batch
        ])
        
        prompt = f"""You are a search expert. Find the most relevant records that match this query: "{query}"

Records to search:
{batch_text}

Return ONLY a JSON array of row numbers that are relevant, ordered by relevance.
Format: {{"matches": [row_number1, row_number2, ...]}}

If no good matches, return: {{"matches": []}}"""

        result = call_gemini_simple(prompt)
        
        if result:
            try:
                matches = json.loads(result).get('matches', [])
                for row_num in matches:
                    matching_record = next((r for r in batch if r['row_number'] == row_num), None)
                    if matching_record:
                        best_matches.append(matching_record)
            except:
                pass
        
        progress_bar.progress(min(1.0, (batch_idx + batch_size) / len(all_records)))
    
    progress_bar.empty()
    
    return best_matches[:10]