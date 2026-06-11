
#!/usr/bin/env python3
"""
Quick Button Functionality Test
Tests specific button actions and JavaScript functionality
"""

import requests
import json
import os

BASE_URL = "http://localhost:5000"

def test_button_functionality():
    """Test specific button functionality and JavaScript features"""
    print("🔘 Testing Button Functionality")
    print("=" * 40)
    
    # Test main dashboard buttons
    dashboard_buttons = [
        ("Inbound", "/inbound_hub"),
        ("Outbound", "/outbound_hub"), 
        ("Inventory", "/inventory_hub"),
        ("Exceptions", "/exceptions_hub"),
        ("Tools", "/tools_hub"),
        ("Admin", "/admin_hub"),
        ("Reports", "/reports_hub"),
        ("Help", "/help_hub")
    ]
    
    print("Testing Main Dashboard Buttons:")
    for button_name, route in dashboard_buttons:
        try:
            response = requests.get(f"{BASE_URL}{route}", timeout=5)
            status = "✅" if response.status_code == 200 else f"❌ ({response.status_code})"
            print(f"  {button_name}: {status}")
        except:
            print(f"  {button_name}: ❌ (Connection Error)")
    
    # Test authentication buttons
    print("\nTesting Authentication:")
    auth_routes = [
        ("Company Login", "/company_login"),
        ("Employee Login", "/employee_login"),
        ("Demo Access", "/demo_access"),
        ("Reset Password", "/reset_password")
    ]
    
    for button_name, route in auth_routes:
        try:
            response = requests.get(f"{BASE_URL}{route}", timeout=5)
            status = "✅" if response.status_code == 200 else f"❌ ({response.status_code})"
            print(f"  {button_name}: {status}")
        except:
            print(f"  {button_name}: ❌ (Connection Error)")
    
    # Test API endpoints that buttons might call
    print("\nTesting API Endpoints:")
    api_endpoints = [
        ("Analytics API", "/api/analytics"),
        ("Scan Logs", "/api/scan-logs"),
        ("Inventory Items", "/api/inventory/items"),
        ("System Health", "/api/system-health")
    ]
    
    for api_name, endpoint in api_endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            status = "✅" if response.status_code == 200 else f"❌ ({response.status_code})"
            print(f"  {api_name}: {status}")
        except:
            print(f"  {api_name}: ❌ (Connection Error)")
    
    # Check for critical static files
    print("\nChecking Critical Static Files:")
    critical_files = [
        "qr_camera_scanner.js",
        "universal_dashboard_button.js", 
        "floating_chat_widget.js",
        "employee_messaging_widget.js",
        "qr_validation.js"
    ]
    
    for file in critical_files:
        file_path = f"static/{file}"
        if os.path.exists(file_path):
            print(f"  {file}: ✅")
        else:
            print(f"  {file}: ❌ (Not Found)")
    
    print("\n🎯 Quick Button Test Complete!")

if __name__ == "__main__":
    test_button_functionality()  {file}: ❌ (Missing)")

if __name__ == "__main__":
    test_button_functionality()
