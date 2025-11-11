# Installation Guide

Complete installation instructions for ZenMarket AI.

## System Requirements

- **Operating System**: Linux, macOS, or Windows
- **Python**: 3.11 or higher
- **Memory**: Minimum 2GB RAM (4GB recommended)
- **Storage**: 500MB for dependencies + space for reports
- **Internet**: Stable connection for API calls

## Platform-Specific Instructions

### Linux (Ubuntu/Debian)

```bash
# Update system
sudo apt-get update

# Install Python 3.11+ if not already installed
sudo apt-get install python3.11 python3.11-venv python3-pip

# Install system dependencies for PDF generation
sudo apt-get install libcairo2-dev libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

# Clone repository
git clone https://github.com/TechNatool/zenmarket-ai.git
cd zenmarket-ai

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit with your API keys
```

### macOS

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11+
brew install python@3.11

# Install system dependencies for PDF generation
brew install cairo pango gdk-pixbuf libffi

# Clone repository
git clone https://github.com/TechNatool/zenmarket-ai.git
cd zenmarket-ai

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # or: open -e .env
```

### Windows

```powershell
# Install Python 3.11+ from python.org if not already installed
# Download from: https://www.python.org/downloads/

# Install GTK for PDF generation
# Download GTK runtime from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
# Or use: choco install gtk-runtime (if using Chocolatey)

# Clone repository
git clone https://github.com/TechNatool/zenmarket-ai.git
cd zenmarket-ai

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Configure environment
copy .env.example .env
notepad .env  # Edit with your API keys
```

## Getting API Keys

### NewsAPI (Required)

1. Go to [https://newsapi.org/](https://newsapi.org/)
2. Click "Get API Key"
3. Sign up for free account
4. Copy your API key
5. Add to `.env`: `NEWSAPI_KEY=your_key_here`

### OpenAI (Required for AI features)

1. Go to [https://platform.openai.com/](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new API key
5. Add to `.env`: `OPENAI_API_KEY=your_key_here`

### Anthropic Claude (Alternative to OpenAI)

1. Go to [https://console.anthropic.com/](https://console.anthropic.com/)
2. Create an account
3. Generate an API key
4. Add to `.env`: `ANTHROPIC_API_KEY=your_key_here`
5. Set: `AI_PROVIDER=anthropic`

### Telegram Bot (Optional)

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow instructions
3. Copy your bot token
4. Search for [@userinfobot](https://t.me/userinfobot)
5. Send `/start` to get your chat ID
6. Add to `.env`:
   ```
   TELEGRAM_BOT_TOKEN=your_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here
   ```

## Verification

Test your installation:

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Run a test report (without AI to save costs)
python -m src.main --no-ai --format markdown

# Check if report was generated
ls reports/
```

You should see a `.md` file in the `reports/` directory.

## Troubleshooting

### Import Errors

```bash
# Make sure virtual environment is activated
which python  # Should show path inside venv/

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### PDF Generation Issues

If PDF generation fails, you can still use HTML and Markdown:

```bash
python -m src.main --format markdown html
```

To fix PDF support:

**Linux:**
```bash
sudo apt-get install libcairo2-dev libpango1.0-dev
pip install --upgrade weasyprint
```

**macOS:**
```bash
brew install cairo pango
pip install --upgrade weasyprint
```

**Windows:**
- Install GTK runtime: [Download here](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer)

### API Connection Issues

```bash
# Test API connectivity
python -c "import requests; print(requests.get('https://newsapi.org').status_code)"

# Check your API keys
cat .env | grep API_KEY
```

## Next Steps

- Read [USAGE.md](USAGE.md) for detailed usage instructions
- Configure automation: [AUTOMATION.md](AUTOMATION.md)
- Review [API.md](API.md) for API documentation
