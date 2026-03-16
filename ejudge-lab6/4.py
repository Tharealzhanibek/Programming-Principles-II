n = int(input())
arr1 = list(map(int, input().split()))
arr2 = list(map(int, input().split()))

dot_product = sum(x * y for x, y in zip(arr1, arr2))
print(dot_product)