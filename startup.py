
#!/usr/bin/env python3
"""Startup validation and preparation script"""

import os
import sys
import json
import subprocess

def check_requirements():
    """Check if all required packages are installed"""
    print("📦 Checking requirements...")
    try:
        import flask
        import qrcode
        import requests
        from PIL import Image
        print("✅ All required packages are available")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("🔧 Installing requirements...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Requirements installed")
            return True
        except Exception as install_error:
            print(f"❌ Failed to install requirements: {install_error}")
            return False

def create_data_directory():
    """Create data directory if it doesn't exist"""
    print("📁 Setting up data directory...")
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"✅ Created {data_dir} directory")
    else:
        print(f"✅ {data_dir} directory exists")

def validate_static_files():
    """Check for critical static files"""
    print("📄 Validating static files...")
    critical_files = [
        'static/index.html',
        'static/main_dashboard.html',
        'static/company_login.html',
        'static/employee_login.html'
    ]
    
    missing_files = []
    for file_path in critical_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"⚠️ Missing files: {missing_files}")
    else:
        print("✅ All critical files present")

def main():
    """Run startup validation"""
    print("🚀 QR Legends Startup Validation")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        print("❌ Startup failed: Missing requirements")
        return False
    
    # Setup data
    create_data_directory()
    
    # Validate files
    validate_static_files()
    
    print("=" * 40)
    print("✅ Startup validation complete!")
    print("🔗 Ready to start main.py")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
