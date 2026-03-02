import math

R = float(input())
x1, y1 = map(float, input().split())
x2, y2 = map(float, input().split())

ax, ay = x1, y1
bx, by = x2, y2

dx, dy = bx - ax, by - ay
dist_AB = math.hypot(dx, dy)

ABx, ABy = bx - ax, by - ay

OCx, OCy = ax, ay

t = -(OCx * ABx + OCy * ABy) / (ABx**2 + ABy**2)
t = max(0, min(1, t))
closest_x = ax + t * ABx
closest_y = ay + t * ABy
dist_to_center = math.hypot(closest_x, closest_y)

if dist_to_center >= R - 1e-12:
    print(f"{dist_AB:.10f}")
else:
    len_A = math.sqrt(ax**2 + ay**2 - R**2)
    len_B = math.sqrt(bx**2 + by**2 - R**2)
    
    dot = ax * bx + ay * by
    cos_theta = dot / (math.hypot(ax, ay) * math.hypot(bx, by))
    cos_theta = max(-1.0, min(1.0, cos_theta))
    theta = math.acos(cos_theta)
    
    alpha = math.acos(R / math.hypot(ax, ay))
    beta = math.acos(R / math.hypot(bx, by))
    arc_angle = theta - alpha - beta
    arc_length = R * arc_angle
    
    total_length = len_A + len_B + arc_length
    print(f"{total_length:.10f}")