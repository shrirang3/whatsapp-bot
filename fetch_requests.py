import requests
import csv
import os

# -------------------
# CONFIG
# -------------------
API_ENDPOINT = "https://797ff10d6e5b.ngrok-free.app/hello"  # Source of incoming data
CONVERSATIONS_CSV = "conversations.csv"
WEBHOOK_API = "http://127.0.0.1:8001/webhook"  # Your FastAPI webhook handler


# -------------------
# HELPERS
# -------------------
def is_phone_in_conversations(phone_number: str) -> bool:
    """Check if phone_number exists in conversations.csv"""
    if not os.path.exists(CONVERSATIONS_CSV):
        return False

    with open(CONVERSATIONS_CSV, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row.get("phone_number") == str(phone_number):  # match column name from your CSV
                return True
    return False


def call_webhook(data: dict):
    """Send data to your webhook API"""
    try:
        response = requests.post(WEBHOOK_API, json=data, timeout=15)
        print(f"➡️ Webhook call: {response.status_code} {response.text}")
        return response.status_code, response.text
    except Exception as e:
        print(f"❌ Error calling webhook: {e}")
        return None, str(e)


def process_request(request_data: dict):
    """Main processing pipeline - Only process type:text requests"""
    print(f"🔔 Received request: {request_data}")
    
    # ONLY process requests that have type: "text" - skip everything else
    if request_data.get("type") != "text":
        print(f"⚠️ Request type is '{request_data.get('type')}', not 'text'. Skipping.")
        return
    
    # Extract phone number and message from WhatsApp format
    phone_number = request_data.get("waId")
    
    # Handle different text field formats
    text_field = request_data.get("text", "")
    if isinstance(text_field, dict):
        message_text = text_field.get("body", "")
    else:
        message_text = str(text_field)
    
    # Check if we have required data
    if not phone_number:
        print("⚠️ No phone number (waId) found in request. Skipping.")
        return
    
    if not message_text:
        print("⚠️ No message text found in request. Skipping.")
        return
    
    # Check if phone number exists in CSV
    if is_phone_in_conversations(phone_number):
        print(f"✅ Found {phone_number} in CSV. Calling webhook...")
        return call_webhook({
            "phone_number": phone_number,
            "message": message_text,
            "messageId": request_data.get("messageId"),
            "timestamp": request_data.get("timestamp"),
            "original_data": request_data
        })
    else:
        print(f"⚠️ Phone number {phone_number} not in conversations.csv, skipping.")


# -------------------
# SIMULATION / POLLING
# -------------------
if __name__ == "__main__":
    try:
        # This assumes API_ENDPOINT returns JSON (a message object or list of messages)
        response = requests.post(API_ENDPOINT, timeout=15)
        if response.status_code == 200:
            data = response.json()

            # Handle single or multiple messages
            if isinstance(data, list):
                for req in data:
                    process_request(req)
            elif isinstance(data, dict):
                process_request(data)
            else:
                print("⚠️ Unexpected response format:", data)

        else:
            print(f"❌ Failed to fetch from API_ENDPOINT: {response.status_code} {response.text}")

    except Exception as e:
        print(f"❌ Error fetching data: {e}")