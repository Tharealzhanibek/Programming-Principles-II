import sys
from datetime import datetime, timedelta

def utc_midnight(line: str) -> datetime:
    date_part, tz_part = line.strip().split(' UTC')
    dt = datetime.strptime(date_part, "%Y-%m-%d")

    sign = 1 if tz_part[0] == '+' else -1
    hh, mm = map(int, tz_part[1:].split(':'))
    offset = timedelta(hours=hh, minutes=mm)

    return dt - sign * offset

a = utc_midnight(sys.stdin.readline())
b = utc_midnight(sys.stdin.readline())

diff_days = abs((a - b).total_seconds()) // 86400
print(int(diff_days))