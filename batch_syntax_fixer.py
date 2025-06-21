#!/usr/bin/env python3
"""
Comprehensive batch fixer for remaining syntax errors in Scout CLI project.
"""

import ast
import re
from pathlib import Path
from typing import List, Tuple


class BatchSyntaxFixer:
    """Batch fixer for common syntax error patterns."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.fixed_files = []
        
    def fix_common_patterns(self, content: str) -> str:
        """Fix common syntax error patterns."""
        lines = content.split('\n')
        fixed_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Pattern 1: Docstring without function definition
            if (line.strip().startswith('"""') and 
                not line.strip().endswith('"""') and
                i > 0 and 
                not any(lines[j].strip().startswith(('def ', 'class ')) 
                       for j in range(max(0, i-3), i))):
                
                # Create a function from the docstring
                docstring = line.strip()[3:]
                if i + 1 < len(lines) and lines[i + 1].strip().endswith('"""'):
                    docstring += " " + lines[i + 1].strip()[:-3]
                    i += 1
                
                # Generate function name
                func_name = self._generate_function_name(docstring)
                fixed_lines.append(f'def {func_name}():')
                fixed_lines.append(f'    """{docstring}"""')
                
                # Skip to next non-indented line or add pass
                found_body = False
                while i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if next_line.strip() and not next_line.startswith(' '):
                        break
                    if next_line.strip():
                        found_body = True
                        fixed_lines.append('    ' + next_line.strip())
                    else:
                        fixed_lines.append(next_line)
                    i += 1
                
                if not found_body:
                    fixed_lines.append('    pass')
                    
            # Pattern 2: Standalone indented lines (should be part of function)
            elif (line and 
                  line.startswith('    ') and 
                  not line.strip().startswith('#') and
                  i > 0 and 
                  not any(lines[j].strip().startswith(('def ', 'class ', 'if ', 'for ', 'while ', 'try:', 'with '))
                         for j in range(max(0, i-5), i))):
                
                # This might need a function wrapper
                if not fixed_lines or not any('def ' in line for line in fixed_lines[-5:]):
                    fixed_lines.append('def main_function():')
                    fixed_lines.append('    """Main function."""')
                
                fixed_lines.append(line)
                
            # Pattern 3: Fix constants that are indented incorrectly
            elif (line.strip() and 
                  line.startswith('    ') and 
                  '=' in line and 
                  line.strip().isupper().replace('_', '').replace('=', '').replace(' ', '').isalpha()):
                
                # This is probably a constant that shouldn't be indented
                fixed_lines.append(line.lstrip())
                
            else:
                fixed_lines.append(line)
                
            i += 1
        
        return '\n'.join(fixed_lines)
    
    def _generate_function_name(self, docstring: str) -> str:
        """Generate a function name from a docstring."""
        # Extract meaningful words
        words = re.findall(r'\b[a-z]+\b', docstring.lower())
        
        # Common action words first
        action_words = ['demo', 'show', 'test', 'run', 'execute', 'display', 'print']
        func_parts = []
        
        for word in action_words:
            if word in words:
                func_parts.append(word)
                break
        
        # Add other meaningful words
        for word in words:
            if (word not in func_parts and 
                len(word) > 3 and 
                word not in ['the', 'and', 'for', 'with', 'this', 'that']):
                func_parts.append(word)
                if len(func_parts) >= 3:
                    break
        
        if not func_parts:
            return 'main_function'
        
        return '_'.join(func_parts)
    
    def fix_file(self, file_path: Path) -> bool:
        """Fix a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply common pattern fixes
            content = self.fix_common_patterns(content)
            
            # Additional specific fixes
            content = self._fix_specific_issues(content)
            
            # Validate syntax
            try:
                compile(content, str(file_path), 'exec')
                syntax_valid = True
            except SyntaxError:
                syntax_valid = False
            
            # Write back only if we improved things
            if content != original_content:
                if syntax_valid:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    return True
                else:
                    # Try a simpler fix
                    content = self._simple_fix(original_content)
                    try:
                        compile(content, str(file_path), 'exec')
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        return True
                    except SyntaxError:
                        pass
            
            return False
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False
    
    def _fix_specific_issues(self, content: str) -> str:
        """Fix specific known issues."""
        # Fix spacing in strings and URLs
        content = content.replace(' - ', '-')
        content = content.replace('utf - 8', 'utf-8')
        content = content.replace('/ ', '/')
        content = content.replace(' / ', '/')
        
        # Fix common indentation issues
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Fix def/class lines missing colons
            if (line.strip().startswith(('def ', 'class ')) and 
                not line.strip().endswith(':') and
                '(' in line and ')' in line):
                line = line.rstrip() + ':'
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _simple_fix(self, content: str) -> str:
        """Apply simple fixes as a fallback."""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Skip obviously broken lines
            if line.strip().startswith('"""') and 'def ' not in line:
                # Convert to a simple comment
                fixed_lines.append('# ' + line.strip()[3:].strip('"'))
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def run(self) -> int:
        """Run the batch fixer on all Python files."""
        python_files = []
        for py_file in self.project_root.rglob("*.py"):
            if '.venv' not in str(py_file) and '__pycache__' not in str(py_file):
                python_files.append(py_file)
        
        print(f"🔧 Batch fixing {len(python_files)} Python files...")
        
        fixed_count = 0
        for file_path in python_files:
            if self.fix_file(file_path):
                fixed_count += 1
                rel_path = file_path.relative_to(self.project_root)
                print(f"  ✅ Fixed {rel_path}")
        
        print(f"\n📊 Batch fixed {fixed_count} files")
        return fixed_count


def main():
    """Main function."""
    project_root = "/Users/morningstar/Desktop/untitled folder"
    fixer = BatchSyntaxFixer(project_root)
    fixed_count = fixer.run()
    
    if fixed_count > 0:
        print(f"\n🎉 Successfully fixed {fixed_count} files!")
    else:
        print("\n⚠️  No files were fixed")


if __name__ == "__main__":
    main()
