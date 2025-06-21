#!/usr/bin/env python3
"""
Final linting check and cleanup script.
"""

import subprocess
import sys
from pathlib import Path


def check_syntax_errors():
    """Check for Python syntax errors across the project."""
    project_root = Path("/Users/morningstar/Desktop/untitled folder")
    python_files = []
    
    # Find all Python files, excluding venv
    for py_file in project_root.rglob("*.py"):
        if '.venv' not in str(py_file) and '__pycache__' not in str(py_file):
            python_files.append(py_file)
    
    print(f"Checking syntax in {len(python_files)} Python files...")
    
    syntax_errors = []
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to compile the file
            compile(content, str(file_path), 'exec')
            
        except SyntaxError as e:
            syntax_errors.append((file_path, e))
            print(f"❌ Syntax error in {file_path.relative_to(project_root)}: {e}")
        except Exception as e:
            print(f"⚠️  Warning in {file_path.relative_to(project_root)}: {e}")
    
    if not syntax_errors:
        print("✅ No syntax errors found!")
    else:
        print(f"\n❌ Found {len(syntax_errors)} files with syntax errors")
    
    return syntax_errors

def fix_remaining_issues():
    """Fix any remaining common issues."""
    project_root = Path("/Users/morningstar/Desktop/untitled folder")
    
    # List of files to check based on the Problems panel
    problem_files = [
        "scout/ai_engine.py",
        "scout/blockchain_security.py", 
        "scout/realtime_monitor.py",
        "scout/compliance.py",
        "scout/voice_assistant.py",
        "scout/vulnerability_db.py",
        "scout/reporting.py"
    ]
    
    for file_rel_path in problem_files:
        file_path = project_root / file_rel_path
        if file_path.exists():
            print(f"\nChecking {file_rel_path}...")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                fixes_made = 0
                
                # Check for remaining \1 issues
                if '\\1' in content:
                    print(f"  Still has \\1 characters - fixing...")
                    # More aggressive fix
                    lines = content.split('\n')
                    fixed_lines = []
                    
                    for line in lines:
                        if '\\1' in line:
                            # Remove standalone \1 lines
                            if line.strip() == '\\1':
                                continue
                            # Fix class declarations
                            line = line.replace('\\1', 'class ')
                            fixes_made += 1
                        fixed_lines.append(line)
                    
                    content = '\n'.join(fixed_lines)
                
                # Fix common spacing issues
                content = content.replace(' - ', '-')
                content = content.replace('"""AI - ', '"""AI-')
                content = content.replace('"""Advanced ', '"""Advanced ')
                
                # Clean up extra whitespace
                content = '\n'.join(line.rstrip() for line in content.split('\n'))
                
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"  ✅ Fixed {fixes_made} additional issues")
                else:
                    print(f"  ✅ No additional issues found")
                    
            except Exception as e:
                print(f"  ❌ Error processing {file_path}: {e}")

def main():
    """Main function."""
    print("🔍 Running final linting check and cleanup...")
    
    # Fix remaining issues first
    fix_remaining_issues()
    
    # Check for syntax errors
    syntax_errors = check_syntax_errors()
    
    if syntax_errors:
        print(f"\n⚠️  {len(syntax_errors)} files still have syntax errors.")
        print("These may need manual review.")
    else:
        print("\n🎉 All syntax errors have been resolved!")
    
    print("\n📊 Final cleanup completed!")


if __name__ == "__main__":
    main()
