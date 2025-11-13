"""
Loan Management System - Analytics & Metrics Module
Provides business insights and growth metrics
"""

from datetime import datetime, timedelta
from collections import defaultdict
import calendar

def parse_date(date_str):
    """Parse date string to datetime object"""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except:
        try:
            return datetime.strptime(date_str, '%d/%m/%Y')
        except:
            return None

def parse_amount(amount_str):
    """Convert amount string to float"""
    try:
        return float(str(amount_str).replace(',', '').strip())
    except:
        return 0.0

def calculate_basic_metrics(records):
    """
    Calculate basic loan metrics
    Returns: dict with key metrics
    """
    if not records or len(records) <= 1:
        return {
            'total_loans': 0,
            'active_loans': 0,
            'closed_loans': 0,
            'total_amount_disbursed': 0,
            'active_amount': 0,
            'avg_loan_amount': 0,
            'total_interest_expected': 0
        }
    
    total_loans = len(records) - 1  # Exclude header
    active_loans = 0
    closed_loans = 0
    total_amount = 0.0
    active_amount = 0.0
    total_interest = 0.0
    
    for row in records[1:]:  # Skip header
        if len(row) < 15:
            continue
        
        status = row[14] if len(row) > 14 else 'Active'
        amount = parse_amount(row[10]) if len(row) > 10 else 0
        interest = parse_amount(row[11]) if len(row) > 11 else 0
        
        total_amount += amount
        total_interest += interest
        
        if status == 'Active':
            active_loans += 1
            active_amount += amount
        else:
            closed_loans += 1
    
    avg_amount = total_amount / total_loans if total_loans > 0 else 0
    
    return {
        'total_loans': total_loans,
        'active_loans': active_loans,
        'closed_loans': closed_loans,
        'total_amount_disbursed': round(total_amount, 2),
        'active_amount': round(active_amount, 2),
        'avg_loan_amount': round(avg_amount, 2),
        'total_interest_expected': round(total_interest, 2),
        'closure_rate': round((closed_loans / total_loans * 100), 2) if total_loans > 0 else 0
    }

def get_monthly_disbursement_data(records):
    """
    Get monthly loan disbursement data for trends
    Returns: list of dicts with month and amount
    """
    if not records or len(records) <= 1:
        return []
    
    monthly_data = defaultdict(lambda: {'count': 0, 'amount': 0.0})
    
    for row in records[1:]:
        if len(row) < 11:
            continue
        
        date_str = row[1]
        amount = parse_amount(row[10]) if len(row) > 10 else 0
        
        dt = parse_date(date_str)
        if dt:
            month_key = dt.strftime('%Y-%m')
            month_label = dt.strftime('%b %Y')
            monthly_data[month_key]['month'] = month_label
            monthly_data[month_key]['count'] += 1
            monthly_data[month_key]['amount'] += amount
    
    result = []
    for key in sorted(monthly_data.keys()):
        result.append({
            'month': monthly_data[key]['month'],
            'count': monthly_data[key]['count'],
            'amount': round(monthly_data[key]['amount'], 2)
        })
    
    return result

def get_ward_wise_distribution(records):
    """
    Get loan distribution by ward/area
    Returns: list of dicts with ward and metrics
    """
    if not records or len(records) <= 1:
        return []
    
    ward_data = defaultdict(lambda: {'count': 0, 'amount': 0.0, 'active': 0})
    
    for row in records[1:]:
        if len(row) < 11:
            continue
        
        ward = row[6] if len(row) > 6 else 'Unknown'
        amount = parse_amount(row[10]) if len(row) > 10 else 0
        status = row[14] if len(row) > 14 else 'Active'
        
        if ward.strip():
            ward_data[ward]['count'] += 1
            ward_data[ward]['amount'] += amount
            if status == 'Active':
                ward_data[ward]['active'] += 1
    
    result = []
    for ward, data in ward_data.items():
        result.append({
            'ward': ward,
            'total_loans': data['count'],
            'active_loans': data['active'],
            'total_amount': round(data['amount'], 2)
        })
    
    result.sort(key=lambda x: x['total_amount'], reverse=True)
    return result

def get_loan_amount_ranges(records):
    """
    Categorize loans by amount ranges
    Returns: list of dicts with range and count
    """
    if not records or len(records) <= 1:
        return []
    
    ranges = {
        '0-10K': (0, 10000),
        '10K-25K': (10000, 25000),
        '25K-50K': (25000, 50000),
        '50K-1L': (50000, 100000),
        '1L+': (100000, float('inf'))
    }
    
    range_data = defaultdict(int)
    
    for row in records[1:]:
        if len(row) < 11:
            continue
        
        amount = parse_amount(row[10]) if len(row) > 10 else 0
        
        for range_name, (min_val, max_val) in ranges.items():
            if min_val <= amount < max_val:
                range_data[range_name] += 1
                break
    
    result = []
    for range_name in ['0-10K', '10K-25K', '25K-50K', '50K-1L', '1L+']:
        result.append({
            'range': range_name,
            'count': range_data[range_name]
        })
    
    return result

def get_recent_activity(records, days=30):
    """
    Get loans disbursed in recent days
    Returns: list of recent loan dicts
    """
    if not records or len(records) <= 1:
        return []
    
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_loans = []
    
    for row in records[1:]:
        if len(row) < 11:
            continue
        
        date_str = row[1]
        dt = parse_date(date_str)
        
        if dt and dt >= cutoff_date:
            recent_loans.append({
                'date': date_str,
                'name': row[3] if len(row) > 3 else '',
                'amount': parse_amount(row[10]) if len(row) > 10 else 0,
                'ward': row[6] if len(row) > 6 else ''
            })
    
    recent_loans.sort(key=lambda x: x['date'], reverse=True)
    return recent_loans

def get_top_borrowers(records, limit=10):
    """
    Get top borrowers by total loan amount
    Returns: list of top borrower dicts
    """
    if not records or len(records) <= 1:
        return []
    
    borrower_data = defaultdict(lambda: {'loans': 0, 'amount': 0.0, 'active': 0})
    
    for row in records[1:]:
        if len(row) < 11:
            continue
        
        name = row[3] if len(row) > 3 else 'Unknown'
        amount = parse_amount(row[10]) if len(row) > 10 else 0
        status = row[14] if len(row) > 14 else 'Active'
        
        if name.strip():
            borrower_data[name]['loans'] += 1
            borrower_data[name]['amount'] += amount
            if status == 'Active':
                borrower_data[name]['active'] += 1
    
    result = []
    for name, data in borrower_data.items():
        result.append({
            'name': name,
            'total_loans': data['loans'],
            'total_amount': round(data['amount'], 2),
            'active_loans': data['active']
        })
    
    result.sort(key=lambda x: x['total_amount'], reverse=True)
    return result[:limit]

def get_interest_analysis(records):
    """
    Analyze interest rates and expected returns
    Returns: dict with interest metrics
    """
    if not records or len(records) <= 1:
        return {
            'total_interest_expected': 0,
            'avg_interest_rate': 0,
            'interest_by_status': {}
        }
    
    total_principal = 0.0
    total_interest = 0.0
    active_interest = 0.0
    closed_interest = 0.0
    count = 0
    
    for row in records[1:]:
        if len(row) < 12:
            continue
        
        amount = parse_amount(row[10]) if len(row) > 10 else 0
        interest = parse_amount(row[11]) if len(row) > 11 else 0
        status = row[14] if len(row) > 14 else 'Active'
        
        total_principal += amount
        total_interest += interest
        count += 1
        
        if status == 'Active':
            active_interest += interest
        else:
            closed_interest += interest
    
    avg_rate = (total_interest / total_principal * 100) if total_principal > 0 else 0
    
    return {
        'total_interest_expected': round(total_interest, 2),
        'avg_interest_rate': round(avg_rate, 2),
        'active_interest': round(active_interest, 2),
        'closed_interest': round(closed_interest, 2),
        'interest_by_status': {
            'Active': round(active_interest, 2),
            'Closed': round(closed_interest, 2)
        }
    }

def get_growth_metrics(records):
    """
    Calculate month-over-month growth metrics
    Returns: dict with growth percentages
    """
    monthly_data = get_monthly_disbursement_data(records)
    
    if len(monthly_data) < 2:
        return {
            'mom_growth_count': 0,
            'mom_growth_amount': 0,
            'trend': 'stable'
        }
    
    current = monthly_data[-1]
    previous = monthly_data[-2]
    
    count_growth = ((current['count'] - previous['count']) / previous['count'] * 100) if previous['count'] > 0 else 0
    amount_growth = ((current['amount'] - previous['amount']) / previous['amount'] * 100) if previous['amount'] > 0 else 0
    
    trend = 'growing' if amount_growth > 5 else 'declining' if amount_growth < -5 else 'stable'
    
    return {
        'mom_growth_count': round(count_growth, 2),
        'mom_growth_amount': round(amount_growth, 2),
        'trend': trend,
        'current_month': current['month'],
        'previous_month': previous['month']
    }

def get_yearly_summary(records):
    """
    Get year-wise loan summary
    Returns: list of dicts with year, count, amount, active stats
    """
    if not records or len(records) <= 1:
        return []
    
    yearly_data = defaultdict(lambda: {'total_count': 0, 'total_amount': 0.0, 'active_count': 0, 'active_amount': 0.0})
    
    for row in records[1:]:
        if len(row) < 11:
            continue
        
        date_str = row[1]
        amount = parse_amount(row[10]) if len(row) > 10 else 0
        status = row[14] if len(row) > 14 else 'Active'
        
        dt = parse_date(date_str)
        if dt:
            year = str(dt.year)
            yearly_data[year]['total_count'] += 1
            yearly_data[year]['total_amount'] += amount
            
            if status == 'Active':
                yearly_data[year]['active_count'] += 1
                yearly_data[year]['active_amount'] += amount
    
    result = []
    for year in sorted(yearly_data.keys()):
        data = yearly_data[year]
        result.append({
            'year': year,
            'total_loans': data['total_count'],
            'total_amount': round(data['total_amount'], 2),
            'active_loans': data['active_count'],
            'active_amount': round(data['active_amount'], 2)
        })
    
    return result

def generate_dashboard_data(records):
    """
    Generate complete dashboard data
    Returns: dict with all metrics and chart data
    """
    return {
        'basic_metrics': calculate_basic_metrics(records),
        'monthly_trend': get_monthly_disbursement_data(records),
        'yearly_summary': get_yearly_summary(records),
        'ward_distribution': get_ward_wise_distribution(records),
        'loan_ranges': get_loan_amount_ranges(records),
        'recent_activity': get_recent_activity(records, days=30),
        'top_borrowers': get_top_borrowers(records, limit=10),
        'interest_analysis': get_interest_analysis(records),
        'growth_metrics': get_growth_metrics(records)
    }

