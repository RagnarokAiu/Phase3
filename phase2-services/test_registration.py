import requests
import json

url = "http://127.0.0.1:8001/register"
payload = {
    "username": "debug_student_final",
    "email": "debug_final@test.com",
    "password": "password123",
    "role": "student"
}
headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
