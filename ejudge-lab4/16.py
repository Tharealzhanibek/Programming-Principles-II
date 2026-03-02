from datetime import datetime, timedelta

def to_utc_seconds(line):
    date_part, time_part, offset_part = line.split()

    dt = datetime.strptime(date_part + " " + time_part, "%Y-%m-%d %H:%M:%S")

    sign = 1 if offset_part[3] == '+' else -1
    off_h, off_m = map(int, offset_part[4:].split(':'))

    offset = timedelta(hours=off_h, minutes=off_m)

    if sign == 1:
        dt -= offset
    else:
        dt += offset

    return int(dt.timestamp())

start = input().strip()
end = input().strip()

print(to_utc_seconds(end) - to_utc_seconds(start))