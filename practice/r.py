import re

log_data = """
[2026-03-10] INFO - User john.doe@example.com logged in successfully.
[2026-03-12] ERROR - Failed login attempt by admin_user1@tech-corp.org!
[2026-03-14] WARNING - Guest account guest@web.net accessed a restricted page.
"""

my_pattern = r"\[(\d{4}-\d{2}-\d{2})\].*?([A-Z]+).*?([\w.-]+@[\w.-]+)"

statuses = re.findall(my_pattern, log_data)
print(statuses)