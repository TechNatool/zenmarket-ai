#!/usr/bin/env python3
"""
Telegram Bot Sender for ZenMarket AI
Sends daily reports via Telegram bot.
"""

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv


def send_telegram_document(bot_token: str, chat_id: str, file_path: Path, caption: str = None) -> bool:
    """
    Send a document via Telegram bot.

    Args:
        bot_token: Telegram bot token
        chat_id: Telegram chat ID
        file_path: Path to file to send
        caption: Optional caption for the document

    Returns:
        True if successful, False otherwise
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"

    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return False

    try:
        with open(file_path, 'rb') as f:
            files = {'document': f}
            data = {
                'chat_id': chat_id,
                'caption': caption or f"ZenMarket AI Report - {file_path.stem}",
                'parse_mode': 'Markdown'
            }

            print(f"Sending {file_path.name} to Telegram...")
            response = requests.post(url, files=files, data=data, timeout=30)

            if response.status_code == 200:
                print("✓ Document sent successfully!")
                return True
            else:
                print(f"✗ Failed to send document: {response.status_code}")
                print(f"Response: {response.text}")
                return False

    except Exception as e:
        print(f"✗ Error sending document: {e}")
        return False


def send_telegram_message(bot_token: str, chat_id: str, message: str) -> bool:
    """
    Send a text message via Telegram bot.

    Args:
        bot_token: Telegram bot token
        chat_id: Telegram chat ID
        message: Message text

    Returns:
        True if successful, False otherwise
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    try:
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }

        response = requests.post(url, data=data, timeout=10)

        if response.status_code == 200:
            return True
        else:
            print(f"Failed to send message: {response.status_code}")
            return False

    except Exception as e:
        print(f"Error sending message: {e}")
        return False


def main():
    """Main function."""
    # Load environment variables
    load_dotenv()

    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        print("Error: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set in .env file")
        print("\nTo set up Telegram notifications:")
        print("1. Create a bot via @BotFather on Telegram")
        print("2. Get your chat ID from @userinfobot")
        print("3. Add these to your .env file:")
        print("   TELEGRAM_BOT_TOKEN=your_bot_token")
        print("   TELEGRAM_CHAT_ID=your_chat_id")
        sys.exit(1)

    # Get file path from command line or find latest PDF
    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
    else:
        # Find latest PDF in reports directory
        reports_dir = Path(__file__).parent.parent / "reports"
        pdf_files = list(reports_dir.glob("*.pdf"))

        if not pdf_files:
            print("Error: No PDF reports found")
            sys.exit(1)

        # Sort by modification time and get latest
        file_path = max(pdf_files, key=lambda p: p.stat().st_mtime)

    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    print(f"Sending report: {file_path.name}")

    # Send greeting message
    from datetime import datetime
    date_str = datetime.now().strftime("%Y-%m-%d")
    greeting = f"📊 *ZenMarket AI - Daily Financial Brief*\n📅 {date_str}\n\n🤖 Your automated market intelligence report is ready!"

    send_telegram_message(bot_token, chat_id, greeting)

    # Send the document
    success = send_telegram_document(
        bot_token,
        chat_id,
        file_path,
        caption=f"📈 Daily Market Report - {date_str}"
    )

    if success:
        print("\n✓ Report sent successfully via Telegram!")
        sys.exit(0)
    else:
        print("\n✗ Failed to send report via Telegram")
        sys.exit(1)


if __name__ == "__main__":
    main()
