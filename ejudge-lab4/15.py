import sys
from datetime import datetime, timedelta, timezone

def prs_line(s):
    s = s.strip()
    date_part, tz_part = s.split()
    y, m, d = map(int, date_part.split("-"))
    sign = 1 if tz_part[3] == '+' else -1
    hh = int(tz_part[4:6])
    mm = int(tz_part[7:9])
    tz = timezone(sign * timedelta(hours=hh, minutes=mm))
    local_midnight = datetime(y, m, d, 0, 0, 0, tzinfo=tz)
    return y, m, d, tz, local_midnight.astimezone(timezone.utc)

def is_leap(y):
    return y % 400 == 0 or (y % 4 == 0 and y % 100 != 0)

def bday_utc(bm, bd, birth_tz, year):
    if bm == 2 and bd == 29 and not is_leap(year):
        bd = 28
    return datetime(year, bm, bd, 0, 0, 0, tzinfo=birth_tz).astimezone(timezone.utc)

lines = sys.stdin.read().strip().splitlines()
i, bm, bd, birth_tz, i = prs_line(lines[0])
cy, i, i, i, curr_utc = prs_line(lines[1])

cand = bday_utc(bm, bd, birth_tz, cy)
if cand < curr_utc:
    cand = bday_utc(bm, bd, birth_tz, cy + 1)

delta = int((cand - curr_utc).total_seconds())
if delta <= 0:
    print(0)
else:
    print((delta + 86400 - 1) // 86400)