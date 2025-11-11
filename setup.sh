#!/bin/bash
# ZenMarket AI - Automated Setup Script
# This script sets up the complete environment for ZenMarket AI

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   ZenMarket AI - Setup Script         ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo ""

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
    echo -e "${RED}Error: Python 3.11+ required, found $PYTHON_VERSION${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION detected${NC}"
echo ""

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
if [ -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment already exists, skipping...${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi
echo ""

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip --quiet
echo -e "${GREEN}✓ pip upgraded${NC}"
echo ""

# Install dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
echo -e "${BLUE}This may take a few minutes...${NC}"
pip install -r requirements.txt --quiet

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
else
    echo -e "${RED}✗ Failed to install dependencies${NC}"
    exit 1
fi
echo ""

# Create .env file if not exists
echo -e "${YELLOW}Setting up configuration...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file from template${NC}"
    echo -e "${YELLOW}⚠ Please edit .env and add your API keys${NC}"
else
    echo -e "${BLUE}ℹ .env file already exists${NC}"
fi
echo ""

# Create necessary directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p reports data/logs data/cache
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Make scripts executable
echo -e "${YELLOW}Making scripts executable...${NC}"
chmod +x scripts/daily_report.sh
chmod +x scripts/telegram_sender.py
chmod +x src/main.py
echo -e "${GREEN}✓ Scripts are now executable${NC}"
echo ""

# Display next steps
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Setup completed successfully! ✓      ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo ""
echo -e "1. ${YELLOW}Configure your API keys:${NC}"
echo -e "   ${BLUE}nano .env${NC}"
echo ""
echo -e "2. ${YELLOW}Add the following API keys:${NC}"
echo -e "   - NEWSAPI_KEY (get from https://newsapi.org/)"
echo -e "   - OPENAI_API_KEY (get from https://platform.openai.com/)"
echo -e "   - Or ANTHROPIC_API_KEY (get from https://console.anthropic.com/)"
echo ""
echo -e "3. ${YELLOW}Test your installation:${NC}"
echo -e "   ${BLUE}source venv/bin/activate${NC}"
echo -e "   ${BLUE}python -m src.main --no-ai --format markdown${NC}"
echo ""
echo -e "4. ${YELLOW}Generate your first report:${NC}"
echo -e "   ${BLUE}./scripts/daily_report.sh${NC}"
echo ""
echo -e "5. ${YELLOW}Set up automation (optional):${NC}"
echo -e "   ${BLUE}crontab -e${NC}"
echo -e "   Add: ${BLUE}0 7 * * 1-5 cd $(pwd) && ./scripts/daily_report.sh${NC}"
echo ""
echo -e "${GREEN}For more information, see README.md and docs/INSTALLATION.md${NC}"
echo ""
echo -e "${BLUE}Happy trading! 📊${NC}"
