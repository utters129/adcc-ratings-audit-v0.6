#!/usr/bin/env python3
"""
Test static file debug endpoint
"""
import requests
import json

def test_static_debug():
    base_url = "https://web-production-fffa07.up.railway.app"
    
    print("🔍 Testing Static File Debug")
    print("=" * 50)
    
    try:
        response = requests.get(f"{base_url}/debug/static", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Debug endpoint successful!")
            print(f"Static Directory: {data.get('static_dir')}")
            print(f"Static Directory Exists: {data.get('static_dir_exists')}")
            print(f"Static URL: {data.get('static_url')}")
            print(f"Static Files Found: {len(data.get('static_files', []))}")
            
            for file in data.get('static_files', []):
                print(f"  - {file}")
                
        else:
            print(f"❌ Debug endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Debug endpoint error: {e}")
    
    print("\n" + "=" * 50)
    print("🧪 Testing Static File Access")
    
    # Test direct access to static files
    static_files = [
        "/static/js/main.js",
        "/static/css/style.css"
    ]
    
    for file_path in static_files:
        try:
            response = requests.get(f"{base_url}{file_path}", timeout=10)
            print(f"{file_path}: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✅ File accessible ({len(response.content)} bytes)")
            else:
                print(f"  ❌ File not accessible")
        except Exception as e:
            print(f"{file_path}: ERROR - {e}")

if __name__ == "__main__":
    test_static_debug() 