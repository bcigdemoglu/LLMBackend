import requests
import json

# Test the wizard with a more complex question
url = "http://localhost:8000/ask"
data = {"question": "Show me all customers and how many orders each has placed"}

print("Testing wizard with complex query...")
try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("Success!")
        result = response.json()
        print(f"Question: {result['question']}")
        print(f"Answer:\n{result['answer']}")
    else:
        print("Error!")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"Connection error: {e}")