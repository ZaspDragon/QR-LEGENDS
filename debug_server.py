
#!/usr/bin/env python3
import sys
import os
import subprocess

print("🔍 QR Legends Server Diagnostics")
print("-" * 40)

# Check Python version
print(f"Python version: {sys.version}")

# Check if main.py exists
if os.path.exists('main.py'):
    print("✅ main.py found")
else:
    print("❌ main.py not found")

# Check for common dependencies
try:
    import flask
    print(f"✅ Flask version: {flask.__version__}")
except ImportError:
    print("❌ Flask not installed")

try:
    import qrcode
    print("✅ QRCode library available")
except ImportError:
    print("❌ QRCode library missing")

# Check if port 5000 is in use
try:
    result = subprocess.run(['lsof', '-i', ':5000'], capture_output=True, text=True)
    if result.returncode == 0:
        print("⚠️  Port 5000 is in use:")
        print(result.stdout)
    else:
        print("✅ Port 5000 is available")
except Exception as e:
    print(f"❓ Could not check port status: {e}")

# Check data directory
if os.path.exists('data'):
    print("✅ Data directory exists")
    data_files = os.listdir('data')
    print(f"   Contains {len(data_files)} files")
else:
    print("❌ Data directory missing")

# Check static directory  
if os.path.exists('static'):
    print("✅ Static directory exists")
else:
    print("❌ Static directory missing")

print("\n🔧 To fix issues:")
print("1. Run: pip install -r requirements.txt")
print("2. Kill any processes on port 5000")
print("3. Check main.py for syntax errors")
print("4. Ensure all data files exist")
