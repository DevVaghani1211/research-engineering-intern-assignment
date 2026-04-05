from dateutil.parser import parse, ParserError
import datetime

def parse_date_robust(date_val):
    """
    Robustly parse date strings or timestamps.
    Returns a datetime object or None if invalid.
    """
    if date_val is None:
        return None
        
    # Handle numeric timestamps
    if isinstance(date_val, (int, float)):
        try:
            return datetime.datetime.fromtimestamp(date_val, tz=datetime.timezone.utc)
        except (ValueError, OSError):
            return None
            
    # Handle strings
    if isinstance(date_val, str):
        try:
            # First try numeric string if it looks like a timestamp
            if date_val.replace('.', '', 1).isdigit():
                return datetime.datetime.fromtimestamp(float(date_val), tz=datetime.timezone.utc)
            return parse(date_val)
        except (ParserError, ValueError, TypeError):
            return None
            
    return None

def clean_text(text):
    """
    Safely clean and trim text.
    """
    if not isinstance(text, str):
        return ""
    return text.strip()
