import requests

base_url = "http://127.0.0.1:10000"
session = requests.Session()

def run_tests():
    print("1. Logging in as Admin (Mohit)...")
    res = session.post(f"{base_url}/", data={"role": "Admin", "username": "Mohit", "password": "Mohit123"})
    if "Welcome, Admin" in res.text or res.status_code == 200:
        print(" -> Login successful! ")
    else:
        print(" -> Login failed.")

    print("\n2. Accessing Library Dashboard...")
    res = session.get(f"{base_url}/library")
    if res.status_code == 200:
        if "Library Management" in res.text:
            print(" -> Dashboard loaded successfully.")
        else:
            print(" -> Page loaded but missing expected content.")
    else:
        print(f" -> Error: Status {res.status_code}")

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"Test script failed: {e}")
