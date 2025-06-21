#!/usr/bin/env python3
"""
Scout CLI Auto - Formatter and Linter Fix Script
Automatically fixes common style and import issues across the project.
"""

import os
import re
import sys
from pathlib import Path

    """
    Fix common linting issues in a Python file."""
    print(f"Fixing {file_path}...")

    try:
        with open(file_path, 'r', encoding='utf - 8') as f:
            content = f.read()

        original_content = content

        # Fix 1: Remove unused imports (common ones)
        unused_imports = [
            r'import base64\n',
            r'import json\n(?!.*json\.)',
            r'            r'            r'            r'import aiohttp\n(?!.*aiohttp\.)',
        ]

        for pattern in unused_imports:
            content = re.sub(pattern, '', content, flags=re.MULTILINE)

        # Fix 2: Add proper spacing between classes
        content = re.sub(r'\n(class [A - Z])', r'\n\n\n\\1', content)
        content = re.sub(r'\n(@dataclass)', r'\n\n\\1', content)
        content = re.sub(r'\n(def [a - z_]+.*?:)\n', r'\n\\1\n', content)

        # Fix 3: Break long lines in common patterns
        # Long logger warnings
        content = re.sub(
            r'logger\.warning\("([^"]{60,})"\)',
            lambda m: f'logger.warning(\n            "{m.group(1)}"\n        )',
            content
        )

        # Fix 4: Remove trailing whitespace
        content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)

        # Fix 5: Fix multiple consecutive blank lines
        content = re.sub(r'\n{4,}', '\n\n\n', content)

        # Fix 6: Normalize imports
        content = re.sub(
            r'from typing import ([A - Za - z, ]+)',
            lambda m: f'from typing import {", ".join(sorted(m.group(1).split(", ")))}',
            content
        )

        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf - 8') as f:
                f.write(content)
            print(f"  ✅ Fixed {file_path}")
            return True
        else:
            print(f"  ⚪ No changes needed for {file_path}")
            return False

    except Exception as e:
        print(f"  ❌ Error fixing {file_path}: {e}")
        return False

    """Fix common YAML linting issues."""
    print(f"Fixing YAML {file_path}...")

    try:
        with open(file_path, 'r', encoding='utf - 8') as f:
            content = f.read()

        original_content = content

        # Fix trailing whitespace
        content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)

        # Fix indentation issues (basic)
        lines = content.split('\n')
        fixed_lines = []

        for line in lines:
            # Convert tabs to spaces
            line = line.replace('\t', '  ')
            fixed_lines.append(line)

        content = '\n'.join(fixed_lines)

        if content != original_content:
            with open(file_path, 'w', encoding='utf - 8') as f:
                f.write(content)
            print(f"  ✅ Fixed {file_path}")
            return True
        else:
            print(f"  ⚪ No changes needed for {file_path}")
            return False

    except Exception as e:
        print(f"  ❌ Error fixing {file_path}: {e}")
        return False

    """Main auto - fix function."""
    print("🔧 Scout CLI Auto - Formatter Starting...")
    print("=" * 50)

    project_root = Path(__file__).parent

    # Find Python files
    python_files = list(project_root.rglob("*.py"))
    yaml_files = list(project_root.rglob("*.yml")) + list(project_root.rglob("*.yaml"))

    fixed_count = 0
    total_count = 0

    # Fix Python files
    print(f"\n📄 Processing {len(python_files)} Python files...")
    for py_file in python_files:
        if fix_python_file(py_file):
            fixed_count += 1
        total_count += 1

    # Fix YAML files
    print(f"\n📄 Processing {len(yaml_files)} YAML files...")
    for yaml_file in yaml_files:
        if fix_yaml_file(yaml_file):
            fixed_count += 1
        total_count += 1

    print("\n" + "=" * 50)
    print(f"🎉 Auto - fix complete!")
    print(f"📊 Fixed {fixed_count} out of {total_count} files")
    print("💡 Run your linter again to check remaining issues")

    

def main():
    """Main function."""
    pass

if __name__ == "__main__":
    main()
