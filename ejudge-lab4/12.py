import sys
import json

a = json.loads(sys.stdin.readline())
b = json.loads(sys.stdin.readline())

missing = object()
diffs = []

def to_json(v):
    return json.dumps(v, separators=(',', ':'))

def dfs(path, x, y):
    if isinstance(x, dict) and isinstance(y, dict):
        keys = sorted(set(x.keys()) | set(y.keys()))
        for k in keys:
            nx = x.get(k, missing)
            ny = y.get(k, missing)
            new_path = f"{path}.{k}" if path else k
            dfs(new_path, nx, ny)
        return

    if x is missing:
        diffs.append(f"{path} : <missing> -> {to_json(y)}")
        return
    if y is missing:
        diffs.append(f"{path} : {to_json(x)} -> <missing>")
        return

    if x != y:
        diffs.append(f"{path} : {to_json(x)} -> {to_json(y)}")

dfs("", a, b)

if diffs:
    print("\n".join(sorted(diffs)))
else:
    print("No differences")