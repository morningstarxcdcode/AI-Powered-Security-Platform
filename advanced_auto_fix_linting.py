#!/usr/bin/env python3
"""
Advanced linting auto - fix script for Scout CLI project.
Fixes common Python linting issues systematically.
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple

class LintingAutoFixer:
    """
    Advanced auto - fixer for Python linting issues."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.fixed_files = []
        self.failed_fixes = []
        self.stats = {
            'files_processed': 0,
            'files_fixed': 0,
            'errors_fixed': 0,
            'warnings_fixed': 0
        }

    def find_python_files(self) -> List[Path]:
        """
    Find all Python files in the project."""
        python_files = []

        # Exclude patterns
        exclude_patterns = {
            '/.venv/', '/venv/', '/env/', '/.env/',
            '/__pycache__/', '/build/', '/dist/',
            '/.git/', '/.pytest_cache/', '/.mypy_cache/',
            '/node_modules/', '/.tox/'
        }

        for py_file in self.project_root.rglob("*.py"):
            # Check if file should be excluded
            if any(pattern in str(py_file) for pattern in exclude_patterns):
                continue
            python_files.append(py_file)

        return python_files

    def fix_syntax_errors(self, content: str) -> Tuple[str, int]:
        """Fix critical syntax errors."""
        fixes_made = 0
        original_content = content

        # Fix the \1 character issue that corrupted class declarations
        if '\\1' in content:
            # Replace \1 followed by a capital letter (likely class names)
            content = re.sub(r'\\1([A - Z][a - zA - Z_]*)\(', r'class \1(', content)
            if content != original_content:
                fixes_made += content.count('class ') - original_content.count('class ')
                print(f"    Fixed \\1 class declaration syntax errors")

        # Fix other common syntax issues
        patterns = [
            # Fix missing colons after class / function definitions
            (r'^(\s*)(class\s+\w+(?:\([^)]*\))?)\s*$', r'\1\2:'),
            (r'^(\s*)(def\s+\w+\([^)]*\))\s*$', r'\1\2:'),

            # Fix malformed docstrings
            (r'"""([^"]*?)"""([^"\n])', r'"""\1"""\n\2'),

            # Fix missing spaces around operators
            (r'([a-zA-Z0-9_)])(==|!=|<=|>=|<|>)([a-zA-Z0-9_(])', r'\1 \2 \3'),
            (r'([a-zA-Z0-9_)])(\+|\-|\*|/|%)([a-zA-Z0-9_(])', r'\1 \2 \3'),

            # Fix missing spaces after commas
            (r',([a - zA - Z0 - 9_"\'[{])', r', \1'),
        ]

        for pattern, replacement in patterns:
            new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            if new_content != content:
                fixes_made += 1
                content = new_content

        return content, fixes_made

    def fix_imports(self, content: str) -> Tuple[str, int]:
        """Fix import - related issues."""
        lines = content.split('\n')
        fixed_lines = []
        fixes_made = 0

        for line in lines:
            original_line = line

            # Fix unused imports (remove if clearly unused)
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                # Don't remove imports that might be used dynamically
                if any(pattern in line for pattern in ['__future__', 'typing', 'dataclasses']):
                    fixed_lines.append(line)
                    continue

            # Fix import formatting
            if 'import' in line and ', ' in line:
                # Sort imports within the same line
                if line.strip().startswith('from '):
                    match = re.match(r'(\s * from\s+\S+\s + import\s+)(.+)', line)
                    if match:
                        prefix, imports = match.groups()
                        import_list = [imp.strip() for imp in imports.split(', ')]
                        import_list.sort()
                        line = prefix + ', '.join(import_list)
                        if line != original_line:
                            fixes_made += 1

            fixed_lines.append(line)

        return '\n'.join(fixed_lines), fixes_made

    def fix_formatting(self, content: str) -> Tuple[str, int]:
        """
    Fix formatting issues."""
        fixes_made = 0
        original_content = content

        # Fix line length issues (basic)
        lines = content.split('\n')
        fixed_lines = []

        for line in lines:
            # Skip if line is already reasonable length or is a comment/docstring
            if len(line) <= 100 or line.strip().startswith('#') or '"""' in line:
                fixed_lines.append(line)
                continue

            # Try to break long lines at logical points
            if len(line) > 100 and (',' in line or ' and ' in line or ' or ' in line):
                # Very basic line breaking for function calls
                if '(' in line and ')' in line and line.count('(') == line.count(')'):
                    # Break at commas if it's a function call
                    indent = len(line) - len(line.lstrip())
                    if line.strip().endswith(', '):
                        fixed_lines.append(line)
                        continue

                    # Simple comma breaking
                    parts = line.split(', ')
                    if len(parts) > 2:
                        fixed_lines.append(parts[0] + ', ')
                        for part in parts[1:-1]:
                            fixed_lines.append(' ' * (indent + 4) + part.strip() + ', ')
                        if parts[-1].strip():
                            fixed_lines.append(' ' * (indent + 4) + parts[-1].strip())
                        fixes_made += 1
                        continue

            fixed_lines.append(line)

        content = '\n'.join(fixed_lines)

        # Fix trailing whitespace
        content = re.sub(r' +$', '', content, flags=re.MULTILINE)
        if content != original_content:
            fixes_made += 1

        # Fix multiple blank lines
        content = re.sub(r'\n\n\n+', '\n\n', content)

        # Ensure file ends with newline
        if content and not content.endswith('\n'):
            content += '\n'
            fixes_made += 1

        return content, fixes_made

    def fix_code_quality(self, content: str) -> Tuple[str, int]:
        """Fix code quality issues."""
        fixes_made = 0

        # Fix common code patterns
        patterns = [
            # Fix comparison to None
            (r'(\w+)\s*==\s * None', r'\1 is None'),
            (r'(\w+)\s*!=\s * None', r'\1 is not None'),

            # Fix comparison to True / False
            (r'(\w+)\s*==\s * True', r'\1'),
            (r'(\w+)\s*==\s * False', r'not \1'),
            (r'(\w+)\s*!=\s * True', r'not \1'),
            (r'(\w+)\s*!=\s * False', r'\1'),

            # Fix empty string checks
            (r"(\w+)\s*==\s*['\"][\'\"]", r'not \1'),
            (r"(\w+)\s*!=\s*['\"][\'\"]", r'\1'),
        ]

        for pattern, replacement in patterns:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                fixes_made += 1
                content = new_content

        return content, fixes_made

    def fix_file(self, file_path: Path) -> bool:
        """Fix linting issues in a single file."""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf - 8') as f:
                content = f.read()

            original_content = content
            total_fixes = 0

            # Apply fixes in order of importance
            content, syntax_fixes = self.fix_syntax_errors(content)
            total_fixes += syntax_fixes

            content, import_fixes = self.fix_imports(content)
            total_fixes += import_fixes

            content, format_fixes = self.fix_formatting(content)
            total_fixes += format_fixes

            content, quality_fixes = self.fix_code_quality(content)
            total_fixes += quality_fixes

            # Only write if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf - 8') as f:
                    f.write(content)

                self.fixed_files.append(str(file_path))
                self.stats['files_fixed'] += 1
                self.stats['errors_fixed'] += total_fixes
                print(f"  ✅ Fixed {total_fixes} issues in {file_path.name}")
                return True
            else:
                print(f"  ⏭️  No fixes needed for {file_path.name}")
                return False

        except Exception as e:
            self.failed_fixes.append((str(file_path), str(e)))
            print(f"  ❌ Failed to fix {file_path.name}: {e}")
            return False

    def run(self):
        """Run the auto - fixer on all Python files."""
        print("🔧 Starting advanced linting auto - fix...")

        python_files = self.find_python_files()
        print(f"📁 Found {len(python_files)} Python files to process")

        for file_path in python_files:
            print(f"\n🔍 Processing: {file_path.relative_to(self.project_root)}")
            self.stats['files_processed'] += 1
            self.fix_file(file_path)

        # Print summary
        print(f"\n📊 Auto - fix Summary:")
        print(f"   Files processed: {self.stats['files_processed']}")
        print(f"   Files fixed: {self.stats['files_fixed']}")
        print(f"   Total fixes applied: {self.stats['errors_fixed']}")

        if self.failed_fixes:
            print(f"\n❌ Failed to fix {len(self.failed_fixes)} files:")
            for file_path, error in self.failed_fixes:
                print(f"   - {file_path}: {error}")

        print(f"\n✅ Auto - fix completed!")

def main():
    """Main function."""
    project_root = "/Users / morningstar / Desktop / untitled folder"
    fixer = LintingAutoFixer(project_root)
    fixer.run()

    if __name__ == "__main__":
    main()
