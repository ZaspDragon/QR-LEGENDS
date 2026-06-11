
#!/usr/bin/env python3
"""
Syntax Check Script
"""

import ast
import os
import sys

def check_python_syntax(filepath):
    """Check Python file for syntax errors"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error in {filepath}: {e}"
    except Exception as e:
        return False, f"Error reading {filepath}: {e}"

def main():
    python_files = [
        'main.py',
        'backup_service.py', 
        'company_integrations.py',
        'company_website_integration.py'
    ]
    
    errors_found = []
    
    for file in python_files:
        if os.path.exists(file):
            valid, error = check_python_syntax(file)
            if not valid:
                errors_found.append(error)
                print(f"❌ {error}")
            else:
                print(f"✅ {file} - OK")
        else:
            print(f"⚠️  {file} - File not found")
    
    if errors_found:
        print(f"\n❌ Found {len(errors_found)} syntax errors")
        return 1
    else:
        print(f"\n✅ All Python files passed syntax check")
        return 0

if __name__ == '__main__':
    sys.exit(main())
