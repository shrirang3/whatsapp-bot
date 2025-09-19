import csv
import os
import logging
import conversation_handler_api as handler
from coversation_history import process_number

# Configure a basic logger for the script
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

CONVERSATIONS_CSV = "conversations.csv"

def initialize_csv():
    """Create the CSV file with headers if it doesn't exist."""
    if not os.path.exists(CONVERSATIONS_CSV):
        logger.info(f"CSV file '{CONVERSATIONS_CSV}' not found. Creating a new one.")
        with open(CONVERSATIONS_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["phone_number", "messages"])
            writer.writeheader()
    else:
        logger.info(f"CSV file '{CONVERSATIONS_CSV}' already exists.")

# Initialize the CSV file
initialize_csv()

def main_1(phone_number):
    test_phone_number = phone_number  # Replace with a real number for testing
    logger.info(f"Manual test: Processing phone number {test_phone_number}")

    # Step 1: Fetch conversation history
    conversation_json, _ = process_number(test_phone_number)
    logger.info(f"Conversation history: {conversation_json}")

    if conversation_json:
        # Step 2: Send to LLM API and get the response
        chat_response = handler.send_conversation(conversation_json, phone_number=test_phone_number)
        logger.info(f"Chat response: {chat_response}")

        # Step 3: Extract the bot's reply
        bot_reply = chat_response.get("message")
        logger.info(f"Bot reply: {bot_reply}")
        if bot_reply:
            # Step 4: Forward the LLM's reply back to WhatsApp
            wati_response = handler.send_wati_message_alternative(test_phone_number, bot_reply)
            logger.info(f"WATI response: {wati_response}")
        else:
            logger.error("LLM response message is empty. Cannot send a reply.")
    else:
        logger.info("No conversation history found. Nothing to do.")

if __name__ == "__main__":
    main_1("918307008102")  # Replace with a real number for testing
