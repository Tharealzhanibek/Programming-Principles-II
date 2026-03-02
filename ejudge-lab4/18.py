x1, y1 = map(float, input().split())
x2, y2 = map(float, input().split())

t = y1 / (y1 + y2)
px = x1 + (x2 - x1) * t
py = 0.0

print(f"{px:.10f} {py:.10f}")