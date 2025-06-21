# Contributing to Scout CLI

Thank you for your interest in contributing to Scout CLI! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of security concepts

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/scout.git
   cd scout
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

4. **Run Tests**
   ```bash
   pytest tests/ -v
   ```

## 🔧 Development Guidelines

### Code Style

- **PEP 8**: Follow Python PEP 8 style guidelines
- **Black**: Use Black for code formatting
- **Type Hints**: Include type hints where appropriate
- **Docstrings**: Write comprehensive docstrings

### Code Quality Tools

```bash
# Format code
black scout/

# Lint code
flake8 scout/

# Type checking
mypy scout/

# Security scanning
bandit -r scout/
```

### Testing

- **Unit Tests**: Write unit tests for all new functionality
- **Integration Tests**: Add integration tests for complex workflows
- **Coverage**: Maintain minimum 80% test coverage
- **Performance**: Include performance tests for critical paths

### Security Considerations

- **Input Validation**: Validate all user inputs
- **Secure Defaults**: Use secure defaults
- **Error Handling**: Don't expose sensitive information in errors
- **Dependencies**: Keep dependencies updated

## 📋 Contribution Types

### Bug Reports

Use the bug report template and include:

- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version)
- Error logs or screenshots

### Feature Requests

Use the feature request template and include:

- Clear description of the feature
- Use case and motivation
- Proposed implementation approach
- Any breaking changes

### Security Vulnerabilities

**DO NOT** open public issues for security vulnerabilities. See [SECURITY.md](SECURITY.md) for reporting instructions.

## 🔄 Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Write clean, documented code
- Add comprehensive tests
- Update documentation if needed

### 3. Test Changes

```bash
# Run all tests
pytest tests/ -v

# Run security checks
scout webscan https://httpbin.org/html

# Test CLI functionality
scout --help
```

### 4. Commit Changes

Use conventional commit format:

```bash
git commit -m "feat: add new vulnerability check for XXE"
git commit -m "fix: resolve issue with SSL certificate validation"
git commit -m "docs: update API documentation"
```

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Create a pull request with:
- Clear title and description
- Link to related issues
- Screenshots/examples if applicable

## 🧩 Adding New Features

### New Security Checks

1. **Create Check Module**
   ```python
   # scout/checks/my_new_check.py
   def check_my_vulnerability(url, response):
       """Check for specific vulnerability."""
       # Implementation here
       return findings
   ```

2. **Add to WebScan**
   ```python
   # scout/commands/webscan.py
   from scout.checks.my_new_check import check_my_vulnerability
   
   # Add to run_all_checks function
   ```

3. **Add Tests**
   ```python
   # tests/test_my_new_check.py
   def test_my_vulnerability_check():
       # Test implementation
   ```

### New Commands

1. **Create Command Module**
   ```python
   # scout/commands/my_command.py
   import click
   
   def register(cli):
       @cli.command()
       @click.option('--option', help='Command option')
       def my_command(option):
           """My new command description."""
           # Implementation here
   ```

2. **Add Documentation**
   - Update README.md
   - Add to help system
   - Include usage examples

### New Compliance Frameworks

1. **Add Framework to Enum**
   ```python
   # scout/compliance.py
   class ComplianceFramework(Enum):
       MY_FRAMEWORK = "my_framework"
   ```

2. **Add Rules**
   ```python
   # Add rules in _load_compliance_rules method
   ```

3. **Update Documentation**

## 📚 Documentation

### Code Documentation

- **Modules**: Include module-level docstrings
- **Functions**: Document parameters, return values, exceptions
- **Classes**: Document purpose, attributes, methods
- **Examples**: Include usage examples

### User Documentation

- **README**: Keep README.md updated
- **Help System**: Update scout/commands/help.py
- **Examples**: Add practical examples

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── performance/    # Performance tests
└── fixtures/       # Test data
```

### Writing Tests

```python
import pytest
from unittest.mock import Mock, patch

class TestMyFeature:
    def test_normal_case(self):
        """Test normal operation."""
        # Arrange
        # Act
        # Assert
    
    def test_error_case(self):
        """Test error handling."""
        # Test error conditions
    
    @patch('requests.get')
    def test_with_mock(self, mock_get):
        """Test with mocked dependencies."""
        # Mock setup and test
```

### Test Categories

Use pytest markers:

```python
@pytest.mark.unit
def test_unit_functionality():
    pass

@pytest.mark.integration
def test_integration_workflow():
    pass

@pytest.mark.slow
def test_performance_heavy():
    pass
```

## 🔍 Code Review Process

### Review Checklist

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Documentation updated
- [ ] No security vulnerabilities
- [ ] Performance impact considered
- [ ] Breaking changes documented

### Review Timeline

- **Initial Review**: Within 48 hours
- **Follow-up**: Within 24 hours of updates
- **Approval**: At least one maintainer approval required

## 🏆 Recognition

Contributors are recognized through:

- **Contributors List**: Listed in README.md
- **Changelog**: Credited in release notes
- **Hall of Fame**: Special recognition for significant contributions

## 📞 Getting Help

- **Discord**: Join our Discord server
- **GitHub Discussions**: Ask questions in discussions
- **Email**: Contact maintainers directly

## 📋 Development Roadmap

### Near Term (Next Release)
- Enhanced vulnerability detection
- Additional compliance frameworks
- Performance improvements
- Better error handling

### Medium Term
- GraphQL API
- Web interface
- Plugin marketplace
- Cloud integration

### Long Term
- Machine learning integration
- Advanced threat intelligence
- Enterprise features
- Multi-language support

## 🎯 Best Practices

### Security
- Never commit secrets or API keys
- Validate all inputs
- Use secure coding practices
- Regular dependency updates

### Performance
- Profile performance-critical code
- Use appropriate data structures
- Minimize network calls
- Cache when appropriate

### Maintainability
- Write clear, readable code
- Use descriptive variable names
- Keep functions focused
- Minimize dependencies

Thank you for contributing to Scout CLI! 🛡️
