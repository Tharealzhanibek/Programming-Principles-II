import json

s = input()

d = json.loads(s)

customers = d["customers"]

for customer in customers:
    total_cnt = 0

    for order in customer["orders"]:
        total_cnt += order["price"]

    if total_cnt >= 100:
        customer["is_vip"] = True
    else:
        customer["is_vip"] = False

new_s = json.dumps(d)
print(new_s)