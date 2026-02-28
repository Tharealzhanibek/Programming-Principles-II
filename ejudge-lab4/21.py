import importlib

n = int(input())

for _ in range(n):
    module_path, attr_name = input().split()
    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        print("MODULE_NOT_FOUND")
        continue
    
    if not hasattr(module, attr_name):
        print("ATTRIBUTE_NOT_FOUND")
    else:
        attr = getattr(module, attr_name)
        if callable(attr):
            print("CALLABLE")
        else:
            print("VALUE")