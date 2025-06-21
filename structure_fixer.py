#!/usr/bin/env python3
"""
Comprehensive indentation and structure fixer for Scout CLI project.
"""

import ast
import os
import re
from pathlib import Path


def fix_file_structure(file_path: Path) -> bool:
    """Fix indentation and structure issues in a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Basic fixes
        # Fix shebang line
        if content.startswith('#!/usr / bin / env'):
            content = content.replace('#!/usr / bin / env', '#!/usr/bin/env')

        lines = content.split('\n')
        fixed_lines = []

        i = 0
        while i < len(lines):
            line = lines[i]

            # Skip empty lines
            if not line.strip():
                fixed_lines.append(line)
                i += 1
                continue

            # Fix function definitions that were corrupted
            if line.strip().startswith('"""') and not line.strip().endswith('"""'):
                # This might be a docstring that got separated from its function
                if i > 0 and fixed_lines and not fixed_lines[-1].strip():
                    # Look for patterns that suggest this should be a function
                    docstring_content = line.strip()[3:]

                    if any(word in docstring_content.lower() for word in [
                        'demonstrate', 'show', 'test', 'run', 'execute', 'main'
                    ]):
                        # Create a function name from the docstring
                        func_name = docstring_content.lower()
                        func_name = re.sub(r'[^a-z0-9_\s]', '', func_name)
                        func_name = '_'.join(func_name.split()[:3])
                        if not func_name:
                            func_name = 'main_function'

                        fixed_lines.append(f'def {func_name}():')
                        fixed_lines.append(f'    """{docstring_content}"""')

                        # Skip ahead to find the end of the docstring
                        i += 1
                        while i < len(lines) and not lines[i].strip().endswith('"""'):
                            fixed_lines.append('    ' + lines[i])
                            i += 1
                        if i < len(lines):
                            fixed_lines.append('    ' + lines[i])
                        i += 1
                        continue

            # Fix lines that should be indented (are part of a function body)
            if line and not line.startswith(' ') and not line.startswith('#'):
                # Check if this line should be indented
                if (line.strip().startswith('print(') or
                    line.strip().startswith('return') or
                    line.strip().startswith('if ') or
                    line.strip().startswith('for ') or
                    line.strip().startswith('while ') or
                    line.strip().startswith('try:') or
                    line.strip().startswith('except') or
                    ('"' in line and not line.strip().startswith('"""'))):

                    # This should probably be indented
                    if fixed_lines and not any(fixed_lines[-j].strip().startswith(('def ', 'class ', 'if __name__'))
                                              for j in range(1, min(5, len(fixed_lines) + 1))):
                        line = '    ' + line

            # Fix class declarations 
            if line.strip().startswith('class ') and ':' not in line:
                line = line + ':'

            # Fix def declarations
            if line.strip().startswith('def ') and ':' not in line:
                line = line + ':'

            fixed_lines.append(line)
            i += 1

        content = '\n'.join(fixed_lines)

        # Fix common patterns
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)  # Multiple blank lines

        # Ensure proper main function structure
        if 'if __name__ == "__main__":' in content and 'def main(' not in content:
            # Add a main function if it's missing
            main_call_match = re.search(r'if __name__ == "__main__":\s*\n\s*(\w+)\(\)', content)
            if main_call_match:
                func_name = main_call_match.group(1)
                if f'def {func_name}(' not in content:
                    # Create the missing function
                    insert_pos = content.find('if __name__ == "__main__":')
                    new_func = f'\n\ndef {func_name}():\n    """Main function."""\n    pass\n\n'
                    content = content[:insert_pos] + new_func + content[insert_pos:]

        # Write back if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False


def fix_all_python_files():
    """Fix all Python files in the project."""
    project_root = Path("/Users/morningstar/Desktop/untitled folder")

    # Find all Python files
    python_files = []
    for py_file in project_root.rglob("*.py"):
        if '.venv' not in str(py_file) and '__pycache__' not in str(py_file):
            python_files.append(py_file)

    print(f"Fixing structure in {len(python_files)} Python files...")

    fixed_count = 0
    for file_path in python_files:
        if fix_file_structure(file_path):
            fixed_count += 1
            print(f"  ✅ Fixed {file_path.relative_to(project_root)}")
        else:
            print(f"  ⏭️  {file_path.relative_to(project_root)} - no changes needed")

    print(f"\n📊 Fixed structure in {fixed_count} files")


def validate_syntax():
    """Validate Python syntax in all files."""
    project_root = Path("/Users/morningstar/Desktop/untitled folder")

    python_files = []
    for py_file in project_root.rglob("*.py"):
        if '.venv' not in str(py_file) and '__pycache__' not in str(py_file):
            python_files.append(py_file)

    syntax_errors = []
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            compile(content, str(file_path), 'exec')
        except SyntaxError:
            syntax_errors.append(file_path)

    if syntax_errors:
        print(f"\n❌ {len(syntax_errors)} files still have syntax errors:")
        for file_path in syntax_errors[:10]:  # Show first 10
            print(f"  - {file_path.relative_to(project_root)}")
        if len(syntax_errors) > 10:
            print(f"  ... and {len(syntax_errors) - 10} more")
    else:
        print("\n✅ All files have valid Python syntax!")

    return len(syntax_errors)


def main():
    """Main function."""
    print("🔧 Starting comprehensive structure fix...")

    fix_all_python_files()

    error_count = validate_syntax()

    if error_count == 0:
        print("\n🎉 All syntax errors have been resolved!")
    else:
        print(f"\n⚠️  {error_count} files may need manual review")

    print("\n📊 Structure fix completed!")


if __name__ == "__main__":
    main()
