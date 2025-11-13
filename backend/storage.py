"""
Storage Module - Google Sheets Data Access Layer
Provides unified interface for loading records from Google Sheets
"""

import streamlit as st
from .sheets import read_all_records

def load_records():
    """
    Load all loan records from Google Sheets
    Returns: list of rows (list of lists) including header
    """
    try:
        records = read_all_records()
        
        if not records:
            st.warning("⚠️ No records found in Google Sheets")
            return []
        
        # Ensure we have at least the header row
        if len(records) < 1:
            return []
        
        return records
    
    except Exception as e:
        st.error(f"❌ Error loading records: {e}")
        return []

def get_record_count():
    """
    Get total number of records (excluding header)
    Returns: int
    """
    records = load_records()
    if not records or len(records) <= 1:
        return 0
    return len(records) - 1

def get_active_records():
    """
    Get only active loan records
    Returns: list of rows (including header)
    """
    records = load_records()
    if not records or len(records) <= 1:
        return []
    
    # Keep header
    active_records = [records[0]]
    
    # Filter active records
    for row in records[1:]:
        if len(row) >= 15:
            status = row[14] if len(row) > 14 else 'Active'
            if status == 'Active':
                active_records.append(row)
    
    return active_records

def get_closed_records():
    """
    Get only closed loan records
    Returns: list of rows (including header)
    """
    records = load_records()
    if not records or len(records) <= 1:
        return []
    
    # Keep header
    closed_records = [records[0]]
    
    # Filter closed records
    for row in records[1:]:
        if len(row) >= 15:
            status = row[14] if len(row) > 14 else 'Active'
            if status == 'Closed':
                closed_records.append(row)
    
    return closed_records

def search_records(query: str, search_field: str = 'all'):
    """
    Search records by field
    Args:
        query: search term
        search_field: field to search in ('all', 'name', 'ward', 'mobile', 'recordId')
    Returns: list of matching rows (including header)
    """
    records = load_records()
    if not records or len(records) <= 1:
        return []
    
    query = query.lower().strip()
    if not query:
        return records
    
    # Keep header
    results = [records[0]]
    
    for row in records[1:]:
        if len(row) < 4:
            continue
        
        match = False
        
        if search_field == 'all':
            # Search in all text fields
            row_text = ' '.join(str(cell).lower() for cell in row)
            match = query in row_text
        
        elif search_field == 'name':
            # Search in both Hindi and English names
            name_hindi = row[2].lower() if len(row) > 2 else ''
            name_english = row[3].lower() if len(row) > 3 else ''
            match = query in name_hindi or query in name_english
        
        elif search_field == 'ward':
            # Search in ward/area
            ward = row[6].lower() if len(row) > 6 else ''
            match = query in ward
        
        elif search_field == 'mobile':
            # Search in mobile number
            mobile = row[7] if len(row) > 7 else ''
            match = query in str(mobile)
        
        elif search_field == 'recordId':
            # Search by record ID
            record_id = row[0].lower() if len(row) > 0 else ''
            match = query in record_id
        
        if match:
            results.append(row)
    
    return results

def get_recent_records(limit: int = 10):
    """
    Get most recent records
    Args:
        limit: number of records to return
    Returns: list of rows (including header)
    """
    records = load_records()
    if not records or len(records) <= 1:
        return []
    
    # Keep header and last N records
    if len(records) - 1 <= limit:
        return records
    
    return [records[0]] + records[-(limit):]

def validate_record_structure(record):
    """
    Validate that a record has the minimum required fields
    Args:
        record: single row (list)
    Returns: bool
    """
    if not record or len(record) < 11:
        return False
    
    # Check essential fields are not empty
    required_indices = [0, 1, 3, 10]  # recordId, date, name, amount
    for idx in required_indices:
        if idx >= len(record) or not str(record[idx]).strip():
            return False
    
    return True

def get_statistics():
    """
    Get quick statistics from records
    Returns: dict with basic stats
    """
    records = load_records()
    if not records or len(records) <= 1:
        return {
            'total': 0,
            'active': 0,
            'closed': 0,
            'has_data': False
        }
    
    total = len(records) - 1
    active = 0
    closed = 0
    
    for row in records[1:]:
        if len(row) >= 15:
            status = row[14] if len(row) > 14 else 'Active'
            if status == 'Active':
                active += 1
            else:
                closed += 1
    
    return {
        'total': total,
        'active': active,
        'closed': closed,
        'has_data': True
    }

def refresh_cache():
    """
    Force refresh of cached data
    This can be called when records are updated
    """
    # Clear any Streamlit cache if needed
    if hasattr(st, 'cache_data'):
        st.cache_data.clear()
    elif hasattr(st, 'legacy_caching'):
        st.legacy_caching.clear_cache()