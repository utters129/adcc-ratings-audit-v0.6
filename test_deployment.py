#!/usr/bin/env python3
"""
Test deployed Railway application
"""
import requests
import sys
from urllib.parse import urljoin

def test_deployment(base_url):
    """Test the deployed application endpoints"""
    print(f"🧪 Testing deployment at: {base_url}")
    print()
    
    # Test health endpoint
    try:
        health_url = urljoin(base_url, "/health")
        response = requests.get(health_url, timeout=10)
        if response.status_code == 200:
            print("✅ Health check: PASSED")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check: FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Health check: ERROR - {e}")
    
    print()
    
    # Test main page
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print("✅ Main page: PASSED")
        else:
            print(f"❌ Main page: FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Main page: ERROR - {e}")
    
    print()
    
    # Test API endpoints
    api_endpoints = [
        "/api/events",
        "/api/athletes", 
        "/api/leaderboards"
    ]
    
    for endpoint in api_endpoints:
        try:
            api_url = urljoin(base_url, endpoint)
            response = requests.get(api_url, timeout=10)
            if response.status_code in [200, 401, 403]:  # 401/403 are expected for unauthenticated requests
                print(f"✅ API {endpoint}: PASSED (Status: {response.status_code})")
            else:
                print(f"❌ API {endpoint}: FAILED (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ API {endpoint}: ERROR - {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_deployment.py <your-railway-url>")
        print("Example: python test_deployment.py https://your-app.railway.app")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    test_deployment(base_url) 