import requests
import json

url = "http://localhost:8000/api/v1/auth/register"
data = {
    "email": "admin@test.com",
    "password": "admin123",
    "full_name": "Admin User",
    "role": "admin"
}

try:
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("\n✅ SUCCESS!")
        print(f"Access Token: {response.json().get('access_token', 'N/A')[:50]}...")
    else:
        print(f"\n❌ FAILED with status {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")