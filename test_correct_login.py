#!/usr/bin/env python3
"""
Test login with correct credentials
"""
import requests
import json

def test_correct_login():
    base_url = "https://web-production-fffa07.up.railway.app"
    
    print("🔐 Testing Correct Login Credentials")
    print("=" * 50)
    
    # Test admin login
    print("\n🧪 Testing Admin Login:")
    print("Username: admin")
    print("Password: admin123")
    
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", json=login_data, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Admin login successful!")
            response_data = response.json()
            print(f"Access Token: {response_data.get('access_token', 'N/A')[:50]}...")
            print(f"Token Type: {response_data.get('token_type', 'N/A')}")
        else:
            print("❌ Admin login failed!")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Admin login error: {e}")
    
    # Test developer login
    print("\n🧪 Testing Developer Login:")
    print("Username: developer")
    print("Password: dev123")
    
    login_data = {
        "username": "developer",
        "password": "dev123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", json=login_data, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Developer login successful!")
            response_data = response.json()
            print(f"Access Token: {response_data.get('access_token', 'N/A')[:50]}...")
            print(f"Token Type: {response_data.get('token_type', 'N/A')}")
        else:
            print("❌ Developer login failed!")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Developer login error: {e}")

if __name__ == "__main__":
    test_correct_login() 