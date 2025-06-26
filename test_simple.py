import requests

# Test the wizard with a simple question
url = "http://localhost:8000/ask"
data = {"question": "What tables exist?"}

print("Testing wizard endpoint...")
try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        print("Success!")
        print(f"Response: {response.json()}")
    else:
        print("Error!")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"Connection error: {e}")
