import math

R = float(input())
x1, y1 = map(float, input().split())
x2, y2 = map(float, input().split())

dx = x2 - x1
dy = y2 - y1

a = dx*dx + dy*dy
b = 2*(dx*x1 + dy*y1)
c = x1*x1 + y1*y1 - R*R

discr = b*b - 4*a*c

if discr < 0:
    length_inside = 0.0
else:
    sqrt_disc = math.sqrt(discr)
    t1 = (-b - sqrt_disc)/(2*a)
    t2 = (-b + sqrt_disc)/(2*a)
    
    t1 = max(0, min(1, t1))
    t2 = max(0, min(1, t2))
    
    length_inside = abs(t2 - t1) * math.sqrt(a)

print(f"{length_inside:.10f}")