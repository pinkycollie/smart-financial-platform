# Contributing to MBTQ Smart Financial Platform

Thank you for your interest in contributing to the MBTQ Smart Financial Platform! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)
- [Community](#community)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, especially members of the Deaf and Hard of Hearing (DHH) community. We pledge to make participation in our project a harassment-free experience for everyone.

### Our Standards

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members
- Ensure accessibility in all communications

## Getting Started

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 15 or higher
- Git
- Docker (optional, for containerized development)

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/smart-financial-platform.git
   cd smart-financial-platform
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e .
   pip install -r requirements-dev.txt  # If available
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database**
   ```bash
   python scripts/migrate.py
   python scripts/seed.py
   ```

6. **Run the application**
   ```bash
   python main.py
   ```

### Using Docker

```bash
docker-compose up -d
```

## Development Workflow

### Branching Strategy

- `main`: Production-ready code
- `develop`: Integration branch for features
- `staging`: Pre-production testing
- `feature/*`: New features
- `bugfix/*`: Bug fixes
- `hotfix/*`: Critical production fixes

### Workflow Steps

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following our coding standards
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Run tests
   python -m unittest discover tests
   
   # Run linters
   flake8 .
   black --check .
   pylint services/ api/
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: Add new feature description"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request**

## Coding Standards

### Python Style Guide

We follow **PEP 8** with some modifications:

- **Line length**: Maximum 127 characters
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Single quotes for strings (unless double quotes improve readability)
- **Docstrings**: Google-style docstrings for all public modules, classes, and functions

### Code Formatting

We use **Black** for automatic code formatting:

```bash
black .
```

### Linting

We use **Flake8** and **Pylint** for code quality:

```bash
flake8 .
pylint services/ api/
```

### Type Hints

Use type hints for function signatures:

```python
def calculate_refund(income: float, deductions: float) -> float:
    """Calculate tax refund amount."""
    return income - deductions
```

### Naming Conventions

- **Functions/Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_CASE`
- **Private members**: `_leading_underscore`

### Comments

- Write clear, concise comments
- Explain *why*, not *what* (code should be self-documenting)
- Use docstrings for public APIs
- Keep comments up-to-date

### Example Code Structure

```python
"""
Module for DHH-specific tax deduction calculations.

This module provides functionality for calculating tax deductions
specific to Deaf and Hard of Hearing individuals.
"""

from decimal import Decimal
from typing import List, Dict, Any


class DHHDeductionCalculator:
    """Calculate DHH-specific tax deductions."""
    
    def calculate_interpreter_fees(self, fees: List[Dict[str, Any]]) -> Decimal:
        """
        Calculate total deductible interpreter fees.
        
        Args:
            fees: List of fee dictionaries containing amount and purpose
            
        Returns:
            Total deductible amount as Decimal
            
        Example:
            >>> calculator = DHHDeductionCalculator()
            >>> fees = [{'amount': 500.00, 'purpose': 'work_related'}]
            >>> calculator.calculate_interpreter_fees(fees)
            Decimal('500.00')
        """
        total = Decimal('0.00')
        for fee in fees:
            if fee.get('purpose') == 'work_related':
                total += Decimal(str(fee['amount']))
        return total
```

## Testing Guidelines

### Test Structure

- **Unit tests**: Test individual functions/methods
- **Integration tests**: Test component interactions
- **API tests**: Test endpoint functionality

### Writing Tests

Use Python's `unittest` framework:

```python
import unittest
from services.tax.dhh_deductions import DHHDeductionCalculator


class TestDHHDeductionCalculator(unittest.TestCase):
    """Test DHH deduction calculator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = DHHDeductionCalculator()
    
    def test_calculate_interpreter_fees(self):
        """Test interpreter fee calculation."""
        fees = [{'amount': 500.00, 'purpose': 'work_related'}]
        result = self.calculator.calculate_interpreter_fees(fees)
        self.assertEqual(result, Decimal('500.00'))
```

### Running Tests

```bash
# All tests
python -m unittest discover tests

# Specific test file
python -m unittest tests/test_dhh_services.py

# With coverage
pytest --cov=services --cov=api --cov-report=html
```

### Test Coverage

- Aim for 80%+ code coverage
- All new features must include tests
- Critical paths require 100% coverage

## Pull Request Process

### Before Submitting

1. ✅ All tests pass
2. ✅ Code follows style guidelines
3. ✅ Documentation is updated
4. ✅ Commit messages are clear
5. ✅ No merge conflicts

### PR Title Format

Use conventional commits format:

- `feat: Add new feature`
- `fix: Fix bug in calculator`
- `docs: Update API documentation`
- `test: Add tests for DHH services`
- `refactor: Improve code structure`
- `chore: Update dependencies`

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass
- [ ] No new warnings
```

### Review Process

1. Automated checks must pass (CI/CD)
2. At least one maintainer approval required
3. All review comments must be addressed
4. Squash and merge (usually)

## Reporting Issues

### Bug Reports

Include:
- Clear title and description
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Screenshots (if applicable)

### Feature Requests

Include:
- Clear title and description
- Use case and motivation
- Proposed solution
- Alternatives considered

### Security Issues

**DO NOT** open public issues for security vulnerabilities.

Email: security@mbtquniverse.com

## DHH-Specific Guidelines

### Accessibility Considerations

- All UI changes must maintain WCAG 2.1 AA compliance
- Video content must include captions
- Audio alerts must have visual alternatives
- Test with screen readers when applicable

### ASL Content

- ASL videos should be clear and well-lit
- Signing space should be fully visible
- Background should provide good contrast
- Include written transcripts

### Communication Preferences

- Respect DHH communication preferences
- Provide multiple communication options
- Test with DHH community members when possible

## Community

### Getting Help

- **Issues**: GitHub Issues for bugs and features
- **Discussions**: GitHub Discussions for questions
- **Email**: support@mbtquniverse.com
- **ASL Support**: [Book an appointment](https://support.mbtquniverse.com/asl)

### Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project README

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to making financial services more accessible for the DHH community! 🤟
