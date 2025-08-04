#!/usr/bin/env python3
"""
Test login functionality for ADCC Analysis Engine
"""
import requests
import json
import sys

def test_login(base_url, username, password):
    """Test login with provided credentials"""
    print(f"🧪 Testing login at: {base_url}")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print()
    
    # Test login endpoint
    login_url = f"{base_url}/api/auth/login"
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(login_url, json=login_data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            try:
                response_data = response.json()
                print(f"Response: {json.dumps(response_data, indent=2)}")
            except:
                print(f"Response text: {response.text}")
        else:
            print("❌ Login failed!")
            try:
                error_data = response.json()
                print(f"Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error text: {response.text}")
                
    except Exception as e:
        print(f"❌ Login request failed: {e}")

def test_auth_endpoints(base_url):
    """Test authentication-related endpoints"""
    print(f"\n🔍 Testing auth endpoints at: {base_url}")
    
    endpoints = [
        "/api/auth/login",
        "/api/auth/logout", 
        "/api/auth/verify"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=5)
            print(f"✅ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

if __name__ == "__main__":
    base_url = "https://web-production-fffa07.up.railway.app"
    
    print("🔐 ADCC Analysis Engine Login Test")
    print("=" * 50)
    
    # Test auth endpoints
    test_auth_endpoints(base_url)
    
    print("\n" + "=" * 50)
    print("📝 Login Test Instructions:")
    print("1. Try logging in with: admin / admin")
    print("2. Try logging in with: developer / developer") 
    print("3. Check browser console for JavaScript errors")
    print("4. Check Railway logs for backend errors")
    print()
    
    # Test with common admin credentials
    test_login(base_url, "admin", "admin")
    print()
    test_login(base_url, "developer", "developer") 