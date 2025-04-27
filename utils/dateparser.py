from datetime import datetime, timedelta

def get_month_range(year: int, month: int):
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end = datetime(year, month + 1, 1) - timedelta(days=1)
    return start, end

def get_previous_month_range():
    today = datetime.today()
    first = today.replace(day=1)
    last_month = first - timedelta(days=1)
    start = last_month.replace(day=1)
    end = last_month.replace(day=last_month.day)
    return start, end

def parse_played_date(played_str, target_year, target_month):
    today = datetime.today()
    if played_str == "Today":
        return today, (today.year == target_year and today.month == target_month)
    elif played_str == "Yesterday":
        dt = today - timedelta(days=1)
        return dt, (dt.year == target_year and dt.month == target_month)
    elif played_str == "Last week":
        dt = today - timedelta(days=7)
        return dt, (dt.year == target_year and dt.month == target_month)
    # Try full month and year (e.g., 'February 2025')
    try:
        dt = datetime.strptime(played_str, "%B %Y")
        return dt, (dt.year == target_year and dt.month == target_month)
    except Exception:
        pass
    # Try abbreviated month, day, year (e.g., 'Mar 15, 2025')
    try:
        dt = datetime.strptime(played_str, "%b %d, %Y")
        return dt, (dt.year == target_year and dt.month == target_month)
    except Exception:
        return None, False 