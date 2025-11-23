from datetime import datetime
from .sheets import read_all_records

def calculate_interest(amount, interest_rate, start_date, current_date=None):
    """
    Calculate interest based on monthly rate and time elapsed
    
    Args:
        amount: Principal loan amount
        interest_rate: Monthly interest rate (default 3%)
        start_date: Loan disbursement date
        current_date: Date to calculate interest until (default: today)
    
    Returns:
        dict with calculated values
    """
    if current_date is None:
        current_date = datetime.now()
    
    # Convert string dates to datetime if needed
    if isinstance(start_date, str):
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            # Try other date formats
            try:
                start_date = datetime.strptime(start_date, "%d/%m/%Y")
            except ValueError:
                return None
    
    if isinstance(current_date, str):
        try:
            current_date = datetime.strptime(current_date, "%Y-%m-%d")
        except ValueError:
            current_date = datetime.now()
    
    # Calculate months elapsed
    months_elapsed = (current_date.year - start_date.year) * 12 + (current_date.month - start_date.month)
    
    # Add partial month based on days
    days_in_current_month = (current_date.day - start_date.day) / 30
    total_months = months_elapsed + max(0, days_in_current_month)
    
    # Calculate interest
    total_interest = amount * (interest_rate / 100) * total_months
    total_amount = amount + total_interest
    
    return {
        "principal": amount,
        "interest_rate": interest_rate,
        "months_elapsed": round(total_months, 2),
        "interest_accrued": round(total_interest, 2),
        "total_amount": round(total_amount, 2),
        "is_doubled": total_interest >= (2 * amount)
    }


def get_records_with_interest_analysis(default_interest_rate=3.0):
    """
    Get all records from Google Sheets with calculated interest
    
    Args:
        default_interest_rate: Interest rate to use when field is NA/empty (default 3%)
    
    Returns:
        list of records with interest calculations
    """
    rows = read_all_records()
    
    if not rows or len(rows) < 2:
        return []
    
    # Get headers from first row
    headers = rows[0]
    analyzed_records = []
    
    # Process data rows (skip header)
    for row in rows[1:]:
        # Pad row with empty strings if needed
        while len(row) < len(headers):
            row.append('')
        
        # Create record dictionary
        record = {}
        for i, header in enumerate(headers):
            record[header] = row[i] if i < len(row) else ''
        
        # Skip if no date or amount
        if not record.get('date') or not record.get('amount'):
            continue
        
        try:
            # Parse amount
            amount_str = str(record['amount']).replace(',', '').strip()
            if not amount_str:
                continue
            amount = float(amount_str)
            
            # Get interest rate (use default if NA or empty)
            interest_str = str(record.get('interest', '')).strip()
            if not interest_str or interest_str.upper() == 'NA' or interest_str == '':
                interest_rate = default_interest_rate
            else:
                interest_rate = float(interest_str.replace('%', '').strip())
            
            # Parse loan date
            loan_date = record['date']
            
            # Calculate interest
            calc = calculate_interest(amount, interest_rate, loan_date)
            
            if calc:
                # Add calculations to record
                record['calculated_interest'] = calc['interest_accrued']
                record['total_due'] = calc['total_amount']
                record['months_elapsed'] = calc['months_elapsed']
                record['is_interest_doubled'] = calc['is_doubled']
                record['interest_exceeds_principal'] = calc['interest_accrued'] > amount
                record['amount'] = amount  # Store parsed amount
                record['interest'] = interest_rate  # Store parsed interest rate
                
                analyzed_records.append(record)
        except (ValueError, KeyError, TypeError) as e:
            # Skip invalid records
            continue
    
    return analyzed_records


def get_defaulters_by_interest_ratio():
    """
    Get records where interest >= principal amount
    
    Returns:
        list of defaulter records sorted by interest ratio (highest first)
    """
    all_records = get_records_with_interest_analysis()
    
    defaulters = [r for r in all_records if r.get('interest_exceeds_principal', False)]
    
    # Sort by interest ratio (descending)
    defaulters.sort(key=lambda x: x['calculated_interest'] / x['amount'], reverse=True)
    
    return defaulters


def get_records_by_interest_threshold_custom(threshold_percentage, default_interest_rate=3.0):
    """
    Get records where interest exceeds a custom threshold percentage of principal
    
    Args:
        threshold_percentage: Interest threshold as % of principal (e.g., 50, 100, 200)
        default_interest_rate: Interest rate to use when field is NA/empty (default 3%)
    
    Returns:
        list of records exceeding threshold
    """
    all_records = get_records_with_interest_analysis(default_interest_rate)
    
    filtered = []
    for record in all_records:
        interest_ratio = (record['calculated_interest'] / record['amount']) * 100
        
        if interest_ratio >= threshold_percentage:
            record['interest_ratio_percentage'] = round(interest_ratio, 2)
            filtered.append(record)
    
    # Sort by interest ratio (descending)
    filtered.sort(key=lambda x: x['interest_ratio_percentage'], reverse=True)
    
    return filtered


def get_doubled_interest_alerts():
    """
    Get critical alerts where interest has become 2x the principal amount
    
    Returns:
        list of critical defaulter records
    """
    all_records = get_records_with_interest_analysis()
    
    critical = [r for r in all_records if r.get('is_interest_doubled', False)]
    
    # Sort by total amount due (descending)
    critical.sort(key=lambda x: x['total_due'], reverse=True)
    
    return critical