
#!/usr/bin/env python3
import requests
import time

BASE_URL = "http://localhost:5000"

# Test critical pages first
CRITICAL_PAGES = [
    "/",
    "/index", 
    "/main_dashboard",
    "/company_login",
    "/employee_login",
    "/demo",
    "/demo_access",
    "/inventory_hub",
    "/inbound_hub", 
    "/outbound_hub"
]

def test_pages():
    print("🧪 Testing Critical Pages...")
    print("=" * 40)
    
    # Check if server is running
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"✅ Server is accessible at {BASE_URL}")
    except:
        print(f"❌ Server not accessible at {BASE_URL}")
        return
    
    working = 0
    total = len(CRITICAL_PAGES)
    
    for page in CRITICAL_PAGES:
        try:
            response = requests.get(f"{BASE_URL}{page}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {page}")
                working += 1
            else:
                print(f"❌ {page} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {page} - Error: {str(e)}")
    
    print(f"\n📊 Results: {working}/{total} pages working ({working/total*100:.1f}%)")

if __name__ == "__main__":
    test_pages()
    test_pages()
