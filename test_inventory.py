import requests
import json


print("=" * 50)
print("TESTING INVENTORY MODULE")
print("=" * 50)

print("\n1. LOGIN...")
login = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"email": "admin@test.com", "password": "admin123"}
)

if login.status_code != 200:
    print(f"❌ Login failed: {login.text}")
    exit()

token = login.json()["access_token"]
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
print("✅ Login successful")


print("\n2. CREATE CATEGORY...")
category_data = {
    "name": "Electronics",
    "description": "Electronic products"
}
response = requests.post(
    "http://localhost:8000/api/v1/inventory/categories",
    json=category_data,
    headers=headers
)
print(f"Status: {response.status_code}")
if response.status_code == 201:
    category = response.json()
    print(f"✅ Category created: {category['name']} (ID: {category['id']})")
else:
    print(f"❌ Failed: {response.text}")


print("\n3. CREATE PRODUCT...")
product_data = {
    "sku": "LAPTOP001",
    "name": "Gaming Laptop",
    "description": "High performance gaming laptop",
    "category_id": 1,
    "unit_price": 15000000,
    "cost_price": 12000000,
    "current_stock": 50,
    "min_stock_level": 5,
    "reorder_level": 10
}
response = requests.post(
    "http://localhost:8000/api/v1/inventory/products",
    json=product_data,
    headers=headers
)
print(f"Status: {response.status_code}")
if response.status_code == 201:
    product = response.json()
    print(f"✅ Product created: {product['name']} (ID: {product['id']})")
    product_id = product['id']
else:
    print(f"❌ Failed: {response.text}")
    product_id = 1


print("\n4. GET PRODUCT BY ID...")
response = requests.get(
    f"http://localhost:8000/api/v1/inventory/products/{product_id}",
    headers=headers
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    product = response.json()
    print(f"✅ Product found: {product['name']} - Stock: {product['current_stock']}")
else:
    print(f"❌ Failed: {response.text}")


print("\n5. LIST PRODUCTS...")
response = requests.get(
    "http://localhost:8000/api/v1/inventory/products?skip=0&limit=10",
    headers=headers
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"✅ Total products: {data['total']}")
    for p in data['items'][:3]:
        print(f"   - {p['name']}: {p['current_stock']} pcs (Rp {p['unit_price']:,.0f})")
else:
    print(f"❌ Failed: {response.text}")


print("\n6. RECORD STOCK MOVEMENT (IN)...")
movement_data = {
    "product_id": product_id,
    "quantity": 10,
    "movement_type": "in",
    "notes": "Restock from supplier"
}
response = requests.post(
    "http://localhost:8000/api/v1/inventory/stock/movement",
    json=movement_data,
    headers=headers
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    movement = response.json()
    print(f"✅ Stock added: +{movement['quantity']} to {movement['product_name']}")
else:
    print(f"❌ Failed: {response.text}")


print("\n7. RECORD STOCK MOVEMENT (OUT)...")
movement_data = {
    "product_id": product_id,
    "quantity": 5,
    "movement_type": "out",
    "notes": "Sold to customer"
}
response = requests.post(
    "http://localhost:8000/api/v1/inventory/stock/movement",
    json=movement_data,
    headers=headers
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    movement = response.json()
    print(f"✅ Stock deducted: -{movement['quantity']} from {movement['product_name']}")
else:
    print(f"❌ Failed: {response.text}")


print("\n8. LIST STOCK MOVEMENTS...")
response = requests.get(
    f"http://localhost:8000/api/v1/inventory/stock/movements?product_id={product_id}&limit=10",
    headers=headers
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"✅ Total movements: {data['total']}")
    for m in data['items'][:3]:
        print(f"   - {m['movement_type']}: {m['quantity']} pcs - {m.get('notes', 'No notes')}")
else:
    print(f"❌ Failed: {response.text}")


print("\n9. UPDATE PRODUCT...")
update_data = {
    "unit_price": 16500000,
    "min_stock_level": 10
}
response = requests.put(
    f"http://localhost:8000/api/v1/inventory/products/{product_id}",
    json=update_data,
    headers=headers
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    product = response.json()
    print(f"✅ Product updated: New price Rp {product['unit_price']:,.0f}")
else:
    print(f"❌ Failed: {response.text}")


print("\n10. LIST CATEGORIES...")
response = requests.get(
    "http://localhost:8000/api/v1/inventory/categories",
    headers=headers
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"✅ Total categories: {data['total']}")
    for c in data['items']:
        print(f"   - {c['name']}: {c['description']}")
else:
    print(f"❌ Failed: {response.text}")


print("\n11. GET LOW STOCK ALERTS...")
response = requests.get(
    "http://localhost:8000/api/v1/inventory/alerts",
    headers=headers
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    alerts = response.json()
    print(f"✅ Total alerts: {len(alerts)}")
    for a in alerts:
        print(f"   - {a['product_name']}: Stock {a['current_stock']} < Reorder {a['reorder_level']}")
else:
    print(f"❌ Failed: {response.text}")

print("\n" + "=" * 50)
print("INVENTORY TEST COMPLETE!")
print("=" * 50)