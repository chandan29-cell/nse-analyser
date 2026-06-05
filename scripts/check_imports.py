import importlib

modules = ["pandas", "numpy", "pytest", "yfinance", "requests", "python_dotenv"]
status = {}
for m in modules:
    try:
        importlib.import_module(m)
        status[m] = "OK"
    except Exception as e:
        status[m] = f"MISSING: {e}"

for k, v in status.items():
    print(f"{k}: {v}")
