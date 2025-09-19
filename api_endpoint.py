from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
import csv
import os
from test_1 import main_1 # Import the main function from test_1.py

# ---------------------
# Logging Configuration
# ---------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# ---------------------
# FastAPI App
# ---------------------
app = FastAPI()

CONVERSATIONS_CSV = "conversations.csv"
PROCESSED_IDS_FILE = "processed_message_ids.txt"


def phone_exists_in_csv(phone_number: str) -> bool:
    """
    Check if the phone number exists in the CSV.
    """
    if not os.path.exists(CONVERSATIONS_CSV):
        logger.warning(f"CSV file {CONVERSATIONS_CSV} not found.")
        return False

    with open(CONVERSATIONS_CSV, newline='', encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row and row[0] == phone_number:  # first column is phone number
                return True
    return False


def is_message_processed(message_id: str) -> bool:
    """
    Check if the message ID has already been processed.
    """
    if not message_id:
        return False
    if not os.path.exists(PROCESSED_IDS_FILE):
        return False
    with open(PROCESSED_IDS_FILE, "r", encoding="utf-8") as f:
        processed_ids = set(line.strip() for line in f)
    return message_id in processed_ids


def mark_message_processed(message_id: str):
    """
    Mark a message as processed by adding its ID to the processed IDs file.
    """
    if not message_id:
        return
    with open(PROCESSED_IDS_FILE, "a", encoding="utf-8") as f:
        f.write(message_id + "\n")


@app.post("/hello")
async def handle_whatsapp_webhook(request: Request):
    try:
        data = await request.json()
        phone_number = data.get("waId")
        message_id = data.get("id")  # Use a unique message ID from the payload
        logger.info(f"Received request for phone number: {phone_number}, message_id: {message_id}")

        if not phone_number:
            logger.warning("❌ No 'waId' found in the request payload. Returning a 400 error.")
            return JSONResponse(content={"error": "Missing phone number (waId)"}, status_code=400)

        if not message_id:
            logger.warning("❌ No 'id' found in the request payload. Returning a 400 error.")
            return JSONResponse(content={"error": "Missing message id"}, status_code=400)

        # Check for duplicate message
        if is_message_processed(message_id):
            logger.info(f"⚠️ Message {message_id} already processed. Skipping.")
            return JSONResponse(content={"status": "Duplicate message, already processed."}, status_code=200)

        # Check if phone exists in CSV
        if phone_exists_in_csv(phone_number):
            logger.info(f"✅ Phone number {phone_number} exists in conversations.csv. Forwarding to test_1.py")
            main_1(phone_number)
            mark_message_processed(message_id)
            return JSONResponse(content={"status": "Forwarded to test_1.py"}, status_code=200)
        else:
            logger.error(f"❌ Phone number {phone_number} not found in conversations.csv.")
            return JSONResponse(
                content={"error": f"Phone number {phone_number} not found in conversations.csv"},
                status_code=404
            )

    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        return JSONResponse(content={"error": "An internal server error occurred"}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
