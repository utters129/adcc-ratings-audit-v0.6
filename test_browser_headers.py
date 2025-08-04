#!/usr/bin/env python3
"""
Test HTTP headers to identify why static files are blocked in browser
"""
import requests

def test_headers():
    base_url = "https://web-production-fffa07.up.railway.app"
    
    print("🔍 Testing HTTP Headers")
    print("=" * 50)
    
    # Test main page headers
    print("\n📄 Main Page Headers:")
    try:
        response = requests.get(base_url, timeout=10)
        print(f"Status: {response.status_code}")
        print("Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test static file headers
    print("\n📁 Static File Headers:")
    static_files = [
        "/static/js/main.js",
        "/static/css/style.css"
    ]
    
    for file_path in static_files:
        print(f"\n{file_path}:")
        try:
            response = requests.get(f"{base_url}{file_path}", timeout=10)
            print(f"  Status: {response.status_code}")
            print(f"  Content-Type: {response.headers.get('content-type', 'Not set')}")
            print(f"  Content-Length: {response.headers.get('content-length', 'Not set')}")
            print(f"  Cache-Control: {response.headers.get('cache-control', 'Not set')}")
            print(f"  Access-Control-Allow-Origin: {response.headers.get('access-control-allow-origin', 'Not set')}")
            
            # Check for security headers
            security_headers = [
                'content-security-policy',
                'x-frame-options',
                'x-content-type-options',
                'x-xss-protection'
            ]
            
            for header in security_headers:
                value = response.headers.get(header)
                if value:
                    print(f"  {header}: {value}")
                    
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    test_headers() 