#!/usr/bin/env python3
"""
Comprehensive script to fix all remaining \1 character issues in Scout CLI project.
"""

import os
import re
from pathlib import Path

def fix_backslash_one_issues(project_root: str):
    """Fix all \1 character issues across all Python files."""
    project_path = Path(project_root)
    fixed_files = []
    
    # Find all Python files
    python_files = list(project_path.rglob("*.py"))
    
    # Exclude venv and other build directories
    exclude_patterns = {'.venv/', '/venv/', '/env/', '/__pycache__/', '/build/', '/dist/'}
    python_files = [f for f in python_files if not any(pattern in str(f) for pattern in exclude_patterns)]
    
    print(f"Found {len(python_files)} Python files to check")
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Check if file contains \1 characters
            if '\\1' in content:
                print(f"\nFixing {file_path.relative_to(project_path)}...")
                
                # Fix various \1 patterns
                # Pattern 1: class ClassName( -> class ClassName(
                content = re.sub(r'\\1([A-Z][a-zA-Z_]*)\(', r'class \1(', content)
                
                # Pattern 2: \1ClassName: -> class ClassName:
                content = re.sub(r'\\1([A-Z][a-zA-Z_]*):$', r'class \1:', content, flags=re.MULTILINE)
                
                # Pattern 3: standalone \1 lines (likely dataclass decorators or blank lines)
                content = re.sub(r'^\s*\\1\s*$', '', content, flags=re.MULTILINE)
                
                # Pattern 4: \1 at start of line followed by lowercase (method/function names)
                content = re.sub(r'^\\1([a-z_][a-zA-Z0-9_]*)', r'    def \1', content, flags=re.MULTILINE)
                
                # Clean up multiple blank lines
                content = re.sub(r'\n\n\n+', '\n\n', content)
                
                # Ensure proper indentation for class bodies
                lines = content.split('\n')
                fixed_lines = []
                in_class = False
                class_indent = 0
                
                for i, line in enumerate(lines):
                    if line.strip().startswith('class ') and line.strip().endswith(':'):
                        in_class = True
                        class_indent = len(line) - len(line.lstrip())
                        fixed_lines.append(line)
                    elif in_class and line.strip() and not line.startswith(' '):
                        # This might be the start of a new class or function
                        if line.strip().startswith('class ') or line.strip().startswith('def ') or line.strip().startswith('@'):
                            in_class = False
                            fixed_lines.append(line)
                        else:
                            # This line should probably be indented
                            fixed_lines.append(' ' * (class_indent + 4) + line.strip())
                    else:
                        fixed_lines.append(line)
                
                content = '\n'.join(fixed_lines)
                
                # Write back if changes were made
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    fixed_files.append(str(file_path))
                    print(f"  ✅ Fixed \\1 issues in {file_path.name}")
                else:
                    print(f"  ⏭️  No \\1 issues found to fix in {file_path.name}")
        
        except Exception as e:
            print(f"  ❌ Error processing {file_path}: {e}")
    
    print(f"\n📊 Summary: Fixed \\1 issues in {len(fixed_files)} files")
    return fixed_files

def main():
    project_root = "/Users/morningstar/Desktop/untitled folder"
    fix_backslash_one_issues(project_root)

if __name__ == "__main__":
    main()
