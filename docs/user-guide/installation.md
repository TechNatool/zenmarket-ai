# Installation Guide

This guide walks you through installing ZenMarket AI on your system.

---

## System Requirements

### Minimum Requirements
- **Python**: 3.11 or 3.12
- **RAM**: 4GB (8GB recommended)
- **Disk Space**: 1GB for dependencies
- **OS**: Linux, macOS, or Windows

### Recommended Requirements
- **Python**: 3.12
- **RAM**: 8GB+
- **Disk Space**: 5GB (for data and logs)
- **OS**: Linux or macOS

---

## Installation Methods

### Method 1: Quick Install (Recommended)

```bash
# Clone repository
git clone https://github.com/TechNatool/zenmarket-ai.git
cd zenmarket-ai

# Install with pip
pip install -e ".[dev]"

# Verify installation
python -m src.cli --help
```

### Method 2: Using uv (Faster)

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/TechNatool/zenmarket-ai.git
cd zenmarket-ai

uv pip install -e ".[dev]"
```

### Method 3: Virtual Environment (Isolated)

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install
pip install -e ".[dev]"
```

---

## Dependency Installation

### Core Dependencies

Automatically installed with the package:

- **Data & Analysis**:
  - pandas (data manipulation)
  - numpy (numerical computing)
  - yfinance (market data)
  
- **AI & NLP**:
  - openai (GPT-4 API)
  - anthropic (Claude API)
  
- **Visualization**:
  - matplotlib (charts)
  - seaborn (statistical plots)
  
- **Other**:
  - pydantic (data validation)
  - feedparser (RSS parsing)

### Development Dependencies

```bash
# Testing
pytest pytest-cov pytest-xdist pytest-timeout pytest-mock

# Code Quality
black isort ruff mypy

# Documentation
mkdocs mkdocs-material mkdocstrings
```

---

## API Keys Setup

### Required API Keys

You need **at least one** AI provider:

1. **OpenAI** (Recommended)
   - Sign up: https://platform.openai.com/
   - Generate API key
   - Cost: ~$0.002 per 1K tokens

2. **Anthropic** (Alternative)
   - Sign up: https://www.anthropic.com/
   - Generate API key
   - Cost: ~$0.015 per 1K tokens

### Configure API Keys

Create `.env` file:

```bash
# Copy template
cp .env.example .env

# Edit with your keys
nano .env  # or use your favorite editor
```

Add your keys:

```bash
# AI Providers (choose at least one)
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional: News API
NEWSAPI_KEY=your-news-api-key

# Optional: Broker credentials
IBKR_HOST=127.0.0.1
IBKR_PORT=7497
```

!!! warning "Security"
    Never commit `.env` to version control.
    The `.gitignore` file already excludes it.

---

## Verification

### 1. Check Installation

```bash
python -m src.cli --version
```

Expected output:
```
ZenMarket AI v1.0.0
```

### 2. Run Tests

```bash
pytest
```

Expected: All tests pass

### 3. Quick Test

```bash
python -m src.cli brief --symbols AAPL
```

Should generate a brief for Apple stock.

---

## Platform-Specific Instructions

### Linux (Ubuntu/Debian)

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv python3-pip

# Install ZenMarket AI
git clone https://github.com/TechNatool/zenmarket-ai.git
cd zenmarket-ai
python3.11 -m pip install -e ".[dev]"
```

### macOS

```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11
brew install python@3.11

# Install ZenMarket AI
git clone https://github.com/TechNatool/zenmarket-ai.git
cd zenmarket-ai
python3.11 -m pip install -e ".[dev]"
```

### Windows

```powershell
# Install Python 3.11 from python.org

# Clone repository
git clone https://github.com/TechNatool/zenmarket-ai.git
cd zenmarket-ai

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install
pip install -e ".[dev]"
```

---

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'src'`

**Solution**: Install in editable mode

```bash
pip install -e .
```

### Issue: `ImportError: No module named 'yfinance'`

**Solution**: Install dependencies

```bash
pip install -r requirements.txt
```

### Issue: Permission denied

**Solution**: Use user install

```bash
pip install --user -e ".[dev]"
```

### Issue: SSL Certificate Error

**Solution**: Update certificates

```bash
# macOS
/Applications/Python\ 3.11/Install\ Certificates.command

# Linux
sudo apt-get install ca-certificates
```

---

## Updating

### Update to Latest Version

```bash
cd zenmarket-ai
git pull origin main
pip install -e ".[dev]" --upgrade
```

### Update Dependencies Only

```bash
pip install --upgrade -r requirements.txt
```

---

## Uninstallation

```bash
pip uninstall zenmarket-ai
```

To completely remove:

```bash
rm -rf zenmarket-ai  # Remove directory
rm -rf ~/.zenmarket  # Remove config (if any)
```

---

## Next Steps

After installation:

1. [Configure the system](configuration.md)
2. [Learn CLI commands](cli.md)
3. [Try examples](examples.md)

---

## Getting Help

If you encounter issues:

- 📖 Check [FAQ](../faq.md)
- 🐛 Report bugs on [GitHub Issues](https://github.com/TechNatool/zenmarket-ai/issues)
- 💬 Ask questions in [Discussions](https://github.com/TechNatool/zenmarket-ai/discussions)
