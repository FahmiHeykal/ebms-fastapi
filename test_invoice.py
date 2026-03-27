import requests
import json

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzc0NjAwNzkzLCJ0eXBlIjoiYWNjZXNzIn0.J4wo84bZaUFOSYPzZdEsR-5rJT0xK05WQwRYQNOw0So"  # Ganti dengan token baru

login_response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"email": "admin@test.com", "password": "admin123"}
)

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    print(f"✅ Got token: {token[:50]}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    invoice_data = {
        "customer_name": "John Doe",
        "items": [
            {
                "description": "Laptop",
                "quantity": 1,
                "unit_price": 10000000
            }
        ]
    }
    
    print("\n📝 Creating invoice...")
    response = requests.post(
        "http://localhost:8000/api/v1/invoices/",
        json=invoice_data,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200 or response.status_code == 201:
        print("\n✅ Invoice created!")
        print(json.dumps(response.json(), indent=2))
    else:
        print("\n❌ Failed")
else:
    print("Login failed:", login_response.text)