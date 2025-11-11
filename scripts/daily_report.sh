#!/bin/bash
# ZenMarket AI - Daily Report Automation Script
# This script runs the daily report generation and optionally sends it via Telegram

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}ZenMarket AI - Daily Report Generator${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root
cd "$PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}Error: Virtual environment not found!${NC}"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Please copy .env.example to .env and configure your API keys"
    exit 1
fi

# Run the report generation
echo -e "${GREEN}Generating daily report...${NC}"
python -m src.main --log-level INFO

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Report generated successfully!${NC}"

    # Find the most recent PDF report
    LATEST_PDF=$(ls -t reports/*.pdf 2>/dev/null | head -n 1)

    if [ -n "$LATEST_PDF" ]; then
        echo -e "${BLUE}Latest report: $LATEST_PDF${NC}"

        # Ask if user wants to send via Telegram (only in interactive mode)
        if [ -t 0 ]; then
            read -p "Send report via Telegram? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                echo -e "${GREEN}Sending via Telegram...${NC}"
                python scripts/telegram_sender.py "$LATEST_PDF"
            fi
        else
            # Non-interactive mode: check environment variable
            if [ "$SEND_TELEGRAM" = "true" ]; then
                echo -e "${GREEN}Sending via Telegram...${NC}"
                python scripts/telegram_sender.py "$LATEST_PDF"
            fi
        fi
    fi

    # Optional: Commit to git (uncomment if desired)
    # echo -e "${GREEN}Committing report to git...${NC}"
    # git add reports/
    # git commit -m "Daily report: $(date +%Y-%m-%d)" || true
    # git push || true

    echo ""
    echo -e "${GREEN}✓ Daily report workflow completed!${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}✗ Report generation failed!${NC}"
    exit 1
fi
