import requests

email = "admin@test.com"
password = "admin123"

print(f"Login with: {email}")

response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"email": email, "password": password}
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    data = response.json()
    print(f"\n✅ LOGIN SUCCESS!")
    print(f"Access Token: {data['access_token'][:50]}...")
    print(f"Token Type: {data['token_type']}")
    print(f"Expires in: {data['expires_in']} seconds")
    
    headers = {"Authorization": f"Bearer {data['access_token']}"}
    user_response = requests.get(
        "http://localhost:8000/api/v1/users/me",
        headers=headers
    )
    print(f"\nGet Current User: {user_response.status_code}")
    if user_response.status_code == 200:
        print(user_response.json())