# Contributing to ZenMarket AI

Thank you for your interest in contributing to ZenMarket AI! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Convention](#commit-convention)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/zenmarket-ai.git
   cd zenmarket-ai
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/TechNatool/zenmarket-ai.git
   ```

## Development Setup

### Prerequisites

- Python 3.11 or 3.12
- pip and virtualenv
- Git

### Installation

1. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install development dependencies**:
   ```bash
   make setup
   # Or manually:
   pip install -e ".[dev]"
   ```

3. **Install pre-commit hooks**:
   ```bash
   make install-hooks
   # Or manually:
   pre-commit install
   ```

4. **Verify installation**:
   ```bash
   make version
   make test
   ```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes

- Write clean, readable code
- Follow the code standards (see below)
- Add or update tests
- Update documentation as needed

### 3. Run Quality Checks

```bash
# Format code
make fmt

# Run all checks (recommended before commit)
make precommit

# Or run individual checks:
make lint       # Linting
make type       # Type checking
make test       # Tests
make docstrings # Docstring coverage
make audit      # Security audit
```

### 4. Commit Your Changes

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```bash
git commit -m "feat: add new position sizing method"
git commit -m "fix: correct ATR calculation in risk manager"
git commit -m "docs: update installation instructions"
```

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Code Standards

### Python Style

- **Line length**: 100 characters
- **Formatter**: Black
- **Import sorting**: isort (black profile)
- **Linter**: Ruff
- **Type hints**: Required for public APIs

### Code Quality Rules

1. **Type Hints**: All public functions must have type hints
   ```python
   def calculate_position_size(
       equity: Decimal,
       risk_percent: float,
       entry_price: Decimal
   ) -> Decimal:
       ...
   ```

2. **Docstrings**: All public modules, classes, and functions must have docstrings (Google style)
   ```python
   def function_name(param1: str, param2: int) -> bool:
       """Short description.

       Longer description if needed.

       Args:
           param1: Description of param1.
           param2: Description of param2.

       Returns:
           Description of return value.

       Raises:
           ValueError: If param1 is invalid.
       """
       ...
   ```

3. **Error Handling**: Use specific exceptions, not bare `except:`
   ```python
   try:
       value = risky_operation()
   except ValueError as e:
       logger.error(f"Invalid value: {e}")
       raise
   ```

4. **Logging**: Use structured logging
   ```python
   logger.info("Order placed: %s", order_id)
   logger.error("Failed to fetch price for %s: %s", symbol, error)
   ```

5. **Constants**: Use UPPER_CASE for constants
   ```python
   MAX_POSITION_SIZE = 0.20
   DEFAULT_RISK_PERCENT = 0.01
   ```

## Testing Guidelines

### Test Organization

- Unit tests in `tests/` mirror `src/` structure
- Integration tests marked with `@pytest.mark.integration`
- Network tests marked with `@pytest.mark.network`

### Writing Tests

1. **Test Naming**: Use descriptive names
   ```python
   def test_position_sizer_returns_zero_when_risk_is_zero():
       ...

   def test_risk_manager_rejects_oversized_position():
       ...
   ```

2. **Test Structure**: Follow Arrange-Act-Assert pattern
   ```python
   def test_example():
       # Arrange
       broker = BrokerSimulator(initial_cash=Decimal('100000'))
       broker.connect()

       # Act
       order = broker.place_order(...)

       # Assert
       assert order.status == OrderStatus.FILLED
   ```

3. **Fixtures**: Use pytest fixtures for common setup
   ```python
   @pytest.fixture
   def broker():
       broker = BrokerSimulator(initial_cash=Decimal('100000'))
       broker.connect()
       return broker
   ```

4. **Mocking**: Mock external dependencies (yfinance, APIs)
   ```python
   @pytest.fixture(autouse=True)
   def mock_yfinance(monkeypatch):
       def mock_download(*args, **kwargs):
           return pd.DataFrame(...)  # Mock data
       monkeypatch.setattr("yfinance.download", mock_download)
   ```

### Test Coverage

- Aim for **≥90% coverage**
- Critical modules (position sizing, risk management) should have **≥95%**
- Use property-based tests (hypothesis) for complex logic

### Running Tests

```bash
# All tests
make test

# Fast (parallel)
make test-fast

# Unit tests only
make test-unit

# Integration tests only
make test-integration

# With coverage report
make cov
```

## Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only changes
- `style`: Code style changes (formatting, missing semi-colons, etc.)
- `refactor`: Code refactoring (no functional changes)
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks (dependencies, build, etc.)
- `ci`: CI/CD changes

### Examples

```bash
feat: add Kelly criterion position sizing
fix: correct stop loss calculation in execution engine
docs: add backtest runner usage examples
test: add property-based tests for risk manager
refactor: extract price fetching into separate module
chore: update dependencies to latest versions
```

### Scope (Optional)

```bash
feat(backtest): add equity curve visualization
fix(risk): correct daily drawdown calculation
docs(api): update execution engine documentation
```

## Pull Request Process

### Before Submitting

1. ✅ All tests pass (`make test`)
2. ✅ Code is formatted (`make fmt`)
3. ✅ Linting passes (`make lint`)
4. ✅ Type checking passes (`make type`)
5. ✅ Documentation is updated
6. ✅ CHANGELOG.md is updated (if applicable)

### PR Description Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## How Has This Been Tested?
Describe the tests you ran to verify your changes.

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published
```

### Review Process

1. **Automated Checks**: CI must pass before review
2. **Code Review**: At least one maintainer approval required
3. **Testing**: New features must include tests
4. **Documentation**: Public APIs must be documented

### After Approval

- Maintainers will merge your PR
- Your contribution will be included in the next release
- You'll be added to the contributors list

## Questions?

- 📧 Email: contact@technatool.com
- 🐛 Issues: [GitHub Issues](https://github.com/TechNatool/zenmarket-ai/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/TechNatool/zenmarket-ai/discussions)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
