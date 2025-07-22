from datetime import datetime

def get_today_date_str():
    return datetime.now().strftime("%Y-%m-%d")
