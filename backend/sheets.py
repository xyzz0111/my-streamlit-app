import os
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from backend.config import SCOPES, SPREADSHEET_ID

def get_sheets_service():
    try:
        if "gcp_service_account" in st.secrets:
            creds = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=SCOPES
            )
            service = build('sheets', 'v4', credentials=creds)
            return service.spreadsheets()
        
        elif os.path.exists("service-account.json"):
            creds = service_account.Credentials.from_service_account_file(
                "service-account.json",
                scopes=SCOPES
            )
            service = build('sheets', 'v4', credentials=creds)
            return service.spreadsheets()
        
        else:
            st.error("⚠️ No Google Sheets credentials found!")
            return None
        
    except Exception as e:
        st.error(f"❌ Error connecting to Google Sheets: {e}")
        return None

def read_all_records():
    sheet = get_sheets_service()
    if not sheet or not SPREADSHEET_ID:
        return []
    
    try:
        result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='Sheet1!A:O'
        ).execute()
        rows = result.get('values', [])
        return rows
    except Exception as e:
        st.error(f"❌ Error reading from Google Sheets: {e}")
        return []

def append_record_to_sheet(record_data: dict):
    sheet = get_sheets_service()
    if not sheet or not SPREADSHEET_ID:
        st.error("⚠️ Google Sheets not configured properly.")
        return False
    
    try:
        from backend.utils import generate_record_id
        
        existing = read_all_records()
        
        record_id = generate_record_id(
            record_data.get('nameEnglish', record_data.get('nameHindi', 'Unknown')),
            record_data.get('date', '')
        )
        
        if not existing:
            headers = [[
                'recordId',
                'date', 
                'nameHindi', 'nameEnglish',
                'addressHindi', 'addressEnglish',
                'wardArea',
                'mobile', 
                'dairyNumber',
                'pageNumber', 
                'amount',
                'interest',
                'guarantee',
                'relationship',
                'loanStatus'
            ]]
            sheet.values().update(
                spreadsheetId=SPREADSHEET_ID,
                range='Sheet1!A1',
                valueInputOption='RAW',
                body={'values': headers}
            ).execute()
        
        row = [[
            record_id,
            record_data.get('date', ''),
            record_data.get('nameHindi', ''),
            record_data.get('nameEnglish', ''),
            record_data.get('addressHindi', ''),
            record_data.get('addressEnglish', ''),
            record_data.get('wardArea', ''),
            record_data.get('mobile', ''),
            record_data.get('dairyNumber',''),
            record_data.get('pageNumber', ''),
            record_data.get('amount', ''),
            record_data.get('interest', ''),
            record_data.get('guarantee', ''),
            record_data.get('relationship', ''),
            'Active'
        ]]
        
        sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range='Sheet1!A:O',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': row}
        ).execute()
        
        return True
    except Exception as e:
        st.error(f"❌ Error writing to Google Sheets: {e}")
        return False

def update_loan_status(row_number: int, new_status: str):
    sheet = get_sheets_service()
    if not sheet or not SPREADSHEET_ID:
        st.error("⚠️ Google Sheets not configured properly.")
        return False
    
    try:
        result = sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f'Sheet1!O{row_number}',
            valueInputOption='RAW',
            body={'values': [[new_status]]}
        ).execute()
        
        if result.get('updatedCells', 0) > 0:
            return True
        else:
            return False
        
    except Exception as e:
        st.error(f"❌ Error updating Google Sheets: {e}")
        return False