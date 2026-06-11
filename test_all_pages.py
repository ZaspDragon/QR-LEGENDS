
#!/usr/bin/env python3
"""
Comprehensive Page Testing Script for QR Legends
Tests all routes, buttons, and page functionality
"""

import requests
import json
import os
from urllib.parse import urljoin
import time

# Base URL for testing (adjust if needed)
BASE_URL = "http://localhost:5000"

# List of all routes to test based on main.py
ROUTES_TO_TEST = [
    # Main pages
    "/",
    "/index",
    "/main_dashboard",
    "/company_login",
    "/employee_login",
    "/demo",
    "/demo_access",
    
    # Hub pages
    "/inbound_hub",
    "/outbound_hub", 
    "/inventory_hub",
    "/exceptions_hub",
    "/tools_hub",
    "/admin_hub",
    "/reports_hub",
    "/help_hub",
    "/erp_hub",
    
    # Core functionality pages
    "/receiving",
    "/putaway", 
    "/quality_check",
    "/order_picking",
    "/packing",
    "/shipping",
    "/returns",
    "/transfers",
    "/cross_docking",
    "/container_management",
    "/delivery_management",
    "/yard_management",
    
    # Inventory management
    "/company_inventory",
    "/inventory",
    "/inventory_analysis",
    "/inventory_valuation",
    
    # Tools and scanners
    "/qr_generator",
    "/slot_qr_generator", 
    "/warehouse_video_scanner",
    "/ai_item_finder",
    "/phone_measurement",
    "/printer_wms_setup",
    "/voice_picking",
    "/mobile_scanner",
    "/label_printing",
    "/rf_handheld",
    "/camera_test",
    
    # Administration
    "/admin_dashboard",
    "/user_management",
    "/company_employee_management",
    "/backup_management",
    "/super_admin",
    "/system_config",
    "/user_roles",
    "/data_maintenance",
    "/license_management",
    
    # ERP and SalesPad
    "/erp_dashboard",
    "/erp_configuration",
    "/erp_customers",
    "/erp_suppliers", 
    "/erp_items",
    "/erp_supplier_performance",
    "/erp_wms_sync",
    "/purchase_orders",
    "/purchase_analytics",
    "/salespad_dashboard",
    "/salespad_configuration",
    "/quotes_pricing",
    "/order_management",
    "/customer_portal",
    "/payment_processing",
    
    # Reports and analytics
    "/analytics_dashboard",
    "/financial_reports",
    "/operational_kpis",
    "/exception_reports",
    "/labor_management",
    "/cost_tracking",
    
    # Integrations
    "/integration_management",
    "/company_integrations",
    "/website_integration_setup",
    
    # Support and help
    "/customer_support",
    "/it_support_request",
    "/problem_solving",
    "/company_training",
    "/onboarding",
    
    # Billing and subscription
    "/billing_dashboard",
    "/billing_notification_panel",
    "/subscription_suspended",
    
    # Other utilities
    "/contact",
    "/profile_page",
    "/notification_center",
    "/messaging_system",
    "/department_group_chat",
    "/employee_messaging",
    "/delivery_qr_generator",
    "/dropoff_location_generator",
    "/driver_dropoff",
    "/admin_freight",
    "/admin_tracking",
    "/two_factor_setup",
    "/reset_password",
    "/access_denied",
    "/app_installer",
    "/code_download",
    "/email_test",
    "/stripe_test",
    "/task_interleaving",
]

# API endpoints to test
API_ROUTES_TO_TEST = [
    "/api/analytics",
    "/api/scan-logs", 
    "/api/inventory/items",
    "/api/labels",
    "/api/auth/profile",
    "/api/system-health",
    "/api/route-status",
]

def test_route(route):
    """Test a single route and return results"""
    try:
        url = urljoin(BASE_URL, route)
        response = requests.get(url, timeout=10)
        
        result = {
            'route': route,
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'content_length': len(response.content),
            'content_type': response.headers.get('content-type', 'unknown'),
            'error': None
        }
        
        # Check for common issues in HTML content
        if response.status_code == 200 and 'text/html' in result['content_type']:
            content = response.text.lower()
            if 'error' in content or 'not found' in content:
                result['warning'] = "Page contains error text"
            if len(content) < 100:
                result['warning'] = "Page content suspiciously short"
                
        return result
        
    except requests.exceptions.RequestException as e:
        return {
            'route': route,
            'status_code': None,
            'success': False,
            'content_length': 0,
            'content_type': 'error',
            'error': str(e)
        }

def test_api_route(route):
    """Test an API route specifically"""
    try:
        url = urljoin(BASE_URL, route)
        response = requests.get(url, timeout=10)
        
        result = {
            'route': route,
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'content_type': response.headers.get('content-type', 'unknown'),
            'error': None
        }
        
        # Try to parse JSON for API routes
        if response.status_code == 200:
            try:
                json_data = response.json()
                result['json_valid'] = True
                result['data_keys'] = list(json_data.keys()) if isinstance(json_data, dict) else 'array'
            except:
                result['json_valid'] = False
                
        return result
        
    except requests.exceptions.RequestException as e:
        return {
            'route': route,
            'status_code': None,
            'success': False,
            'content_type': 'error',
            'error': str(e)
        }

def check_static_files():
    """Check if static files exist"""
    static_files = []
    static_dir = "static"
    
    if os.path.exists(static_dir):
        for file in os.listdir(static_dir):
            if file.endswith('.html'):
                static_files.append(file)
    
    return static_files

def run_comprehensive_test():
    """Run comprehensive test of all pages and functionality"""
    print("🧪 Starting Comprehensive QR Legends Page Testing")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"✅ Server is running at {BASE_URL}")
    except:
        print(f"❌ Server is not accessible at {BASE_URL}")
        print("Please make sure the Flask app is running with: python main.py")
        return
    
    # Test all HTML routes
    print(f"\n📄 Testing {len(ROUTES_TO_TEST)} HTML Routes...")
    html_results = []
    
    for i, route in enumerate(ROUTES_TO_TEST):
        print(f"Testing {i+1}/{len(ROUTES_TO_TEST)}: {route}", end="")
        result = test_route(route)
        html_results.append(result)
        
        if result['success']:
            print(" ✅")
        else:
            print(f" ❌ ({result.get('status_code', 'ERROR')})")
        
        time.sleep(0.1)  # Small delay to avoid overwhelming server
    
    # Test API routes
    print(f"\n🔌 Testing {len(API_ROUTES_TO_TEST)} API Routes...")
    api_results = []
    
    for route in API_ROUTES_TO_TEST:
        print(f"Testing API: {route}", end="")
        result = test_api_route(route)
        api_results.append(result)
        
        if result['success']:
            print(" ✅")
        else:
            print(f" ❌ ({result.get('status_code', 'ERROR')})")
    
    # Check static files
    print(f"\n📁 Checking Static Files...")
    static_files = check_static_files()
    print(f"Found {len(static_files)} HTML files in static directory")
    
    # Generate summary report
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY REPORT")
    print("=" * 60)
    
    # HTML Routes Summary
    successful_html = sum(1 for r in html_results if r['success'])
    failed_html = len(html_results) - successful_html
    
    print(f"\n📄 HTML Routes: {successful_html}/{len(html_results)} successful")
    if failed_html > 0:
        print("❌ Failed HTML Routes:")
        for result in html_results:
            if not result['success']:
                print(f"   {result['route']} - {result.get('status_code', 'ERROR')}: {result.get('error', 'Unknown error')}")
    
    # API Routes Summary  
    successful_api = sum(1 for r in api_results if r['success'])
    failed_api = len(api_results) - successful_api
    
    print(f"\n🔌 API Routes: {successful_api}/{len(api_results)} successful")
    if failed_api > 0:
        print("❌ Failed API Routes:")
        for result in api_results:
            if not result['success']:
                print(f"   {result['route']} - {result.get('status_code', 'ERROR')}: {result.get('error', 'Unknown error')}")
    
    # Routes with warnings
    warnings = [r for r in html_results if r.get('warning')]
    if warnings:
        print(f"\n⚠️  Routes with warnings:")
        for result in warnings:
            print(f"   {result['route']} - {result['warning']}")
    
    # Missing static files check
    missing_files = []
    for route in ROUTES_TO_TEST:
        expected_file = route.lstrip('/') + '.html'
        if expected_file not in static_files and route not in ['/', '/index']:
            missing_files.append(expected_file)
    
    if missing_files:
        print(f"\n📁 Potentially Missing Static Files:")
        for file in missing_files[:10]:  # Show first 10
            print(f"   {file}")
        if len(missing_files) > 10:
            print(f"   ... and {len(missing_files) - 10} more")
    
    # Overall score
    total_routes = len(html_results) + len(api_results)
    total_successful = successful_html + successful_api
    success_rate = (total_successful / total_routes) * 100
    
    print(f"\n🏆 Overall Success Rate: {success_rate:.1f}% ({total_successful}/{total_routes})")
    
    if success_rate >= 90:
        print("🎉 Excellent! Most pages are working correctly.")
    elif success_rate >= 75:
        print("👍 Good! Most pages are working, but some need attention.")
    else:
        print("⚠️  Many pages need attention. Check the failed routes above.")
    
    # Save detailed results
    detailed_results = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'base_url': BASE_URL,
        'html_routes': html_results,
        'api_routes': api_results,
        'static_files': static_files,
        'summary': {
            'total_routes': total_routes,
            'successful_routes': total_successful,
            'success_rate': success_rate,
            'html_success': successful_html,
            'api_success': successful_api
        }
    }
    
    with open('test_results.json', 'w') as f:
        json.dump(detailed_results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to test_results.json")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    run_comprehensive_test()
