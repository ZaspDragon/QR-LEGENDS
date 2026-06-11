
#!/usr/bin/env python3
"""Test critical imports"""

try:
    import flask
    print("✅ Flask imported successfully")
except ImportError as e:
    print(f"❌ Flask import failed: {e}")

try:
    import qrcode
    print("✅ QRCode imported successfully") 
except ImportError as e:
    print(f"❌ QRCode import failed: {e}")

try:
    from PIL import Image
    print("✅ PIL imported successfully")
except ImportError as e:
    print(f"❌ PIL import failed: {e}")

try:
    import requests
    print("✅ Requests imported successfully")
except ImportError as e:
    print(f"❌ Requests import failed: {e}")

print("Import test completed successfully!") test completed")
