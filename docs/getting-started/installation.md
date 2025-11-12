# Installation

## Requirements

- Python 3.11 or 3.12
- pip (latest version recommended)
- Git

## Installation Methods

### Development Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/TechNatool/zenmarket-ai.git
cd zenmarket-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### User Installation

```bash
# Install from source
pip install git+https://github.com/TechNatool/zenmarket-ai.git
```

## Verification

```bash
# Check installation
python -c "import src; print('Installation successful!')"

# Run tests
pytest

# Check version
python -m src.cli --version
```

## Next Steps

- [Configuration](configuration.md)
- [Quick Start](quickstart.md)
