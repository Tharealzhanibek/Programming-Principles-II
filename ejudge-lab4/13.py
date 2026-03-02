import sys
import json
import re

data = json.loads(sys.stdin.readline())
q = int(sys.stdin.readline())

pattern = re.compile(r'\[(\d+)\]')

not_found = object()

def resolve(obj, query):
    cur = obj

    parts = query.split('.')
    for part in parts:
        key_end = part.find('[')

        if key_end == -1:
            key = part
            rest = ''
        else:
            key = part[:key_end]
            rest = part[key_end:]

        if key:
            if not isinstance(cur, dict) or key not in cur:
                return not_found
            cur = cur[key]

        for idx_str in pattern.findall(rest):
            idx = int(idx_str)
            if not isinstance(cur, list) or idx >= len(cur):
                return not_found
            cur = cur[idx]

    return cur


for i in range(q):
    query = sys.stdin.readline().strip()
    result = resolve(data, query)

    if result is not_found:
        print("NOT_FOUND")
    else:
        print(json.dumps(result, separators=(',', ':')))