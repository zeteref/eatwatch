from datetime import datetime

def today_at(hour):
    now = datetime.now()
    hour, minute = [int(x) for x in  hour.split(':')]

    ret = datetime(now.year, now.month, now.day, hour, minute)
    return ret
