
#!/usr/bin/env python3
"""
Enhanced JavaScript Syntax Fixer for QR Legends
Fixes template literal issues, missing braces, and other syntax errors
"""

import os
import re
import json

def fix_template_literal_issues(content):
    """Fix template literal syntax issues"""
    
    # Fix semicolons inside template literals
    # Pattern: ${variable;} -> ${variable}
    content = re.sub(r'\$\{([^}]*?);([^}]*?)\}', r'${\1\2}', content)
    
    # Fix missing closing braces in template literals
    # Find incomplete template expressions at end of lines
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Check for incomplete template expressions
        if '${' in line:
            # Count opening and closing braces
            open_count = line.count('${')
            close_count = line.count('}')
            
            # If we have more opens than closes, try to fix
            if open_count > close_count:
                missing_braces = open_count - close_count
                # Add missing closing braces before semicolons or end of line
                if line.rstrip().endswith(';'):
                    line = line.rstrip()[:-1] + '}' * missing_braces + ';'
                else:
                    line = line.rstrip() + '}' * missing_braces
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_function_calls(content):
    """Fix function call syntax issues"""
    
    # Fix onclick handlers with syntax issues
    content = re.sub(r'onclick="([^"]*?)\(([^)]*?);([^)]*?)\)"', r'onclick="\1(\2\3)"', content)
    
    # Fix function parameter syntax
    content = re.sub(r'(\w+)\(([^)]*?);([^)]*?)\)', r'\1(\2\3)', content)
    
    return content

def fix_missing_functions(content):
    """Add missing function definitions"""
    
    missing_functions = []
    
    # Check for common missing functions
    if 'toggleTheme' in content and 'function toggleTheme' not in content:
        missing_functions.append('''
function toggleTheme() {
    const body = document.body;
    const isDark = body.classList.contains('dark-theme');
    
    if (isDark) {
        body.classList.remove('dark-theme');
        localStorage.setItem('theme', 'light');
    } else {
        body.classList.add('dark-theme');
        localStorage.setItem('theme', 'dark');
    }
}''')
    
    if 'showNotification' in content and 'function showNotification' not in content:
        missing_functions.append('''
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px;
        border-radius: 8px;
        color: white;
        z-index: 10000;
        background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8'};
    `;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}''')
    
    # Add missing functions before closing </script> tag
    if missing_functions and '</script>' in content:
        functions_code = '\n'.join(missing_functions)
        content = content.replace('</script>', f'{functions_code}\n</script>')
    
    return content

def fix_json_syntax(content):
    """Fix JSON syntax issues in JavaScript objects"""
    
    # Fix trailing semicolons in object properties
    content = re.sub(r'(\w+):\s*([^,}]*?);([,}])', r'\1: \2\3', content)
    
    # Fix semicolons in object literals
    content = re.sub(r'{\s*([^}]*?);([^}]*?)\s*}', r'{\1\2}', content)
    
    return content

def fix_html_file(filepath):
    """Fix JavaScript syntax issues in HTML file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all fixes
        content = fix_template_literal_issues(content)
        content = fix_function_calls(content)
        content = fix_json_syntax(content)
        content = fix_missing_functions(content)
        
        # Additional specific fixes
        # Fix common syntax patterns
        content = re.sub(r'\.classList\.add\(([^)]*?);\)', r'.classList.add(\1)', content)
        content = re.sub(r'\.innerHTML\s*=\s*`([^`]*?);([^`]*?)`', r'.innerHTML = `\1\2`', content)
        
        # Fix fetch calls
        content = re.sub(r"'Content-Type':\s*'application/json';", r"'Content-Type': 'application/json'", content)
        
        # Save if changes were made
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")
        return False

def fix_js_file(filepath):
    """Fix JavaScript syntax issues in .js files"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply fixes
        content = fix_template_literal_issues(content)
        content = fix_function_calls(content)
        content = fix_json_syntax(content)
        
        # Fix specific JavaScript issues
        content = re.sub(r'headers:\s*{\s*([^}]*?);\s*}', r'headers: {\1}', content)
        content = re.sub(r'body:\s*JSON\.stringify\({\s*([^}]*?);\s*}\)', r'body: JSON.stringify({\1})', content)
        
        # Save if changes were made
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
            
        return False
        
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")
        return False

def main():
    """Fix JavaScript syntax issues across all files"""
    print("🔧 Enhanced JavaScript syntax fixer starting...")
    
    static_dir = 'static'
    if not os.path.exists(static_dir):
        print(f"❌ Static directory not found: {static_dir}")
        return
    
    fixed_files = []
    
    # Process HTML files
    for filename in os.listdir(static_dir):
        if filename.endswith('.html'):
            filepath = os.path.join(static_dir, filename)
            if fix_html_file(filepath):
                fixed_files.append(filename)
                print(f"✅ Fixed: {filename}")
            else:
                print(f"✓ OK: {filename}")
    
    # Process JavaScript files
    js_files = []
    for root, dirs, files in os.walk(static_dir):
        for file in files:
            if file.endswith('.js'):
                js_files.append(os.path.join(root, file))
    
    print(f"📁 Found {len(js_files)} JavaScript files")
    
    for js_file in js_files:
        if fix_js_file(js_file):
            fixed_files.append(os.path.basename(js_file))
            print(f"✅ Fixed: {os.path.basename(js_file)}")
        else:
            print(f"✓ OK: {os.path.basename(js_file)}")
    
    print(f"✅ JavaScript syntax fix complete!")
    if fixed_files:
        print(f"Fixed {len(fixed_files)} files: {', '.join(fixed_files)}")
    else:
        print("No syntax issues found to fix.")

if __name__ == "__main__":
    main()
