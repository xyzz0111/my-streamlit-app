import re
import random
import string
from datetime import datetime

def generate_record_id(name: str, date: str) -> str:
    name_clean = re.sub(r'[^a-zA-Z0-9\u0900-\u097F]', '', name.split()[0] if name and name != "Not mentioned" else "Unknown")[:10]
    date_clean = date.replace('/', '').replace('-', '')[:8] if date and date != "Not mentioned" else datetime.now().strftime('%d%m%Y')
    unique_id = ''.join(random.choices(string.digits, k=4))
    return f"{name_clean}_{date_clean}_{unique_id}"

def get_current_timestamp() -> str:
    return datetime.now().strftime('%d/%m/%Y %H:%M:%S')

def validate_and_format_date(date_str: str) -> str:
    if not date_str or date_str == "Not mentioned":
        return "Not mentioned"
    
    date_patterns = [
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{2})',
        r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, date_str)
        if match:
            try:
                groups = match.groups()
                if len(groups[2]) == 2:
                    year = f"20{groups[2]}"
                    day, month = groups[0], groups[1]
                elif len(groups[0]) == 4:
                    year, month, day = groups[0], groups[1], groups[2]
                else:
                    day, month, year = groups[0], groups[1], groups[2]
                
                datetime(int(year), int(month), int(day))
                return f"{int(day):02d}/{int(month):02d}/{year}"
            except:
                pass
    
    return date_str

DEFAULT_FIELDS = {
    "date": "NA",
    "nameHindi": "NA",
    "nameEnglish": "NA",
    "addressHindi": "NA",
    "addressEnglish": "NA",
    "wardArea": "NA",
    "mobile": "NA",
    'dairyNumber': 'd2',
    "pageNumber": "NA",
    "amount": "NA",
    "interest": "NA",
    "guarantee": "NA",
    "relationship": "NA"
}