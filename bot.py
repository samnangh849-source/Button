import re
import logging
from urllib.parse import quote
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

# --- Configuration ---
# Replace with your actual Telegram Bot Token
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"

# Option 1: URL for the Flask server (recommended)
# Ensure the server.py is running.
BASE_URL = "http://127.0.0.1:5000/print"

# Option 2: Path to the standalone HTML file (no server needed)
# Uncomment the line below and update the path to the correct location on your computer.
# IMPORTANT: The path must be absolute.
# For Windows: "file:///C:/Users/YourUser/path/to/project/standalone_label.html"
# For macOS/Linux: "file:///home/user/path/to/project/standalone_label.html"
# BASE_URL = "file:///C:/path/to/your/project/standalone_label.html"

# --- End Configuration ---


# Set up basic logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def parse_order_text(text: str) -> dict:
    """
    Parses the order text using regular expressions to extract key details.

    Args:
        text: The full text of the Telegram message.

    Returns:
        A dictionary containing the extracted data or None if parsing fails.
    """
    patterns = {
        'name': r"👤 អតិថិជន:\s*(.*?)\s*\n",
        'phone': r"📞 លេខទូរស័ព្ទ:\s*(.*?)\s*\n",
        'total': r"សរុបចុងក្រោយ:\s*\$(.*?)\s*\n",
        'payment': r"🟥\s*(.*?)\s*\n",
    }

    data = {}
    # Find all matches
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            data[key] = match.group(1).strip()
        else:
            # If any pattern fails, we consider the message invalid
            logger.warning(f"Pattern for '{key}' not found in message.")
            return None
    
    logger.info(f"Successfully parsed data: {data}")
    return data

def handle_order_message(update: Update, context: CallbackContext) -> None:
    """
    Handles incoming text messages, parses them, and replies with a print button.
    """
    message_text = update.message.text
    logger.info("Received message. Attempting to parse...")

    # The bot will only process messages containing this specific Khmer header
    if "👤 អតិថិជន:" not in message_text:
        logger.info("Message does not contain the trigger phrase. Ignoring.")
        return

    order_data = parse_order_text(message_text)

    if order_data:
        # URL-encode the data to ensure it's safe for the query string
        name_encoded = quote(order_data.get('name', ''))
        phone_encoded = quote(order_data.get('phone', ''))
        total_encoded = quote(order_data.get('total', ''))
        payment_encoded = quote(order_data.get('payment', ''))

        # Construct the final URL with query parameters
        print_url = (
            f"{BASE_URL}?name={name_encoded}&phone={phone_encoded}"
            f"&total={total_encoded}&payment={payment_encoded}"
        )

        logger.info(f"Generated Print URL: {print_url}")

        # Create the inline button
        keyboard = [
            [InlineKeyboardButton("🖨️ បោះពុម្ព Label", url=print_url)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Reply to the message with the button
        update.message.reply_text(
            "✅ Order details parsed. Click the button below to print the label:",
            reply_markup=reply_markup,
            quote=True # Reply directly to the order message
        )
    else:
        logger.warning("Failed to parse message. No action taken.")

def main() -> None:
    """Start the bot."""
    updater = Updater(TELEGRAM_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register the handler for non-command text messages
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_order_message))

    # Start the Bot
    updater.start_polling()
    logger.info("Telegram Bot has started successfully.")

    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
