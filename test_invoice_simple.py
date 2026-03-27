import requests

print("🔐 Logging in...")
login = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"email": "admin@test.com", "password": "admin123"}
)

if login.status_code != 200:
    print(f"❌ Login failed: {login.text}")
    exit()

token = login.json()["access_token"]
print(f"✅ Got token")


headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
invoice_data = {
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "items": [
        {"description": "Laptop", "quantity": 1, "unit_price": 10000000}
    ]
}

print("\n📝 Creating invoice...")
response = requests.post(
    "http://localhost:8000/api/v1/invoices/",
    json=invoice_data,
    headers=headers
)

print(f"Status: {response.status_code}")

if response.status_code == 201:
    print("✅ Invoice created successfully!")
    data = response.json()
    print(f"Invoice ID: {data['id']}")
    print(f"Invoice Number: {data['invoice_number']}")
    print(f"Customer: {data['customer_name']}")
    print(f"Total: {data['total']}")
    print(f"Status: {data['status']}")
else:
    print(f"❌ Failed: {response.text}")