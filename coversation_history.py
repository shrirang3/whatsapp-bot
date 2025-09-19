import requests
import json
from datetime import datetime
from typing import Dict, List
import csv
import os

#API used: Get Messages by whatsapp number

# --------------------------
# WATI CONFIG
# --------------------------
API_BASE = "https://live-mt-server.wati.io/200128/api/v1"
HEADERS = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJhMTc3MzU3Mi01ODFiLTQ4MzQtOWJiOS1mYWM2NjRkYzNiMjAiLCJ1bmlxdWVfbmFtZSI6ImVrYWdhckB2YWhhbi5jbyIsIm5hbWVpZCI6ImVrYWdhckB2YWhhbi5jbyIsImVtYWlsIjoiZWthZ2FyQHZhaGFuLmNvIiwiYXV0aF90aW1lIjoiMTAvMDUvMjAyMyAwNzozNjo1NyIsImRiX25hbWUiOiJtdC1wcm9kLVRlbmFudHMiLCJ0ZW5hbnRfaWQiOiIyMDAxMjgiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL3JvbGUiOiJBRE1JTklTVFJBVE9SIiwiZXhwIjoyNTM0MDIzMDA4MDAsImlzcyI6IkNsYXJlX0FJIiwiYXVkIjoiQ2xhcmVfQUkifQ.ud5AYN5Kf5Xm17WX8Krr1Z3qJo0waJu75cY-o3N2EuU"
}

# --------------------------
# HELPER FUNCTIONS
# --------------------------
def get_conversation(phone_number: str) -> dict:
    """Fetch messages for a phone number"""
    url = f"{API_BASE}/getMessages/{phone_number}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()

def bot_sent_text(response_json: dict) -> bool:
    """Check if bot sent at least one text message (including broadcast messages)"""
    messages = response_json.get("messages", {}).get("items", [])
    for msg in messages:
        # Check for regular bot messages
        if (
            msg.get("eventType") == "message"
            and msg.get("owner") is True
            and msg.get("type") == "text"
        ):
            return True
        
        # Check for broadcast messages (these are also bot messages)
        if msg.get("eventType") == "broadcastMessage":
            return True
    
    return False

def format_conversation_json(phone_number: str, response_json: dict) -> dict:
    """Format conversation data into a simple JSON: respondent + response (only texts)"""
    messages = response_json.get("messages", {}).get("items", [])
    
    conversation_data = {
        "phone_number": phone_number,
        "export_timestamp": datetime.now().isoformat(),
        "messages": []
    }
    
    for msg in messages:
        # Case 1: Regular text message
        if msg.get("eventType") == "message" and msg.get("type") == "text":
            is_bot = msg.get("owner", False)
            sender = "assistant" if is_bot else "user"
            text = msg.get("text")
            
            if text:  # store only if there's actual text
                conversation_data["messages"].append({
                    "role": sender,
                    "content": text
                })
        
        # Case 2: Broadcast messages (bot only, with text)
        elif msg.get("eventType") == "broadcastMessage":
            text = msg.get("finalText")
            if text:
                conversation_data["messages"].append({
                    "role": "assistant",
                    "content": text
                })
    
    return conversation_data


def save_conversation_json(phone_number: str, conversation_data: dict, filename: str = None):
    """Save conversation data to JSON file"""
    if filename is None:
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{phone_number}_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(conversation_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Conversation saved to: {filename}")
    return filename

def remove_timestamps(conversation):
    """
    Remove 'timestamp' keys from all message dicts in the conversation.
    Handles both list of dicts and dicts with a 'messages' key.
    """
    if isinstance(conversation, list):
        return [{k: v for k, v in msg.items() if k != "timestamp"} for msg in conversation]
    elif isinstance(conversation, dict) and "messages" in conversation:
        conversation_copy = conversation.copy()
        conversation_copy["messages"] = [
            {k: v for k, v in msg.items() if k != "timestamp"}
            for msg in conversation["messages"]
        ]
        return conversation_copy
    return conversation

def update_conversation(phone_number, latest_conversation):
    """
    Update the messages field for the given phone number in conversations.csv
    with the latest conversation JSON (as a string), excluding timestamps.
    Only the latest conversation is stored. If the phone number does not exist, do nothing.
    """
    csv_file = "conversations.csv"
    updated = False
    rows = []
    # Remove timestamps before storing
    filtered_conversation = remove_timestamps(latest_conversation)
    # Read all rows
    if os.path.exists(csv_file):
        with open(csv_file, newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("phone_number") == str(phone_number):
                    row["messages"] = json.dumps(filtered_conversation, ensure_ascii=False)
                    updated = True
                rows.append(row)
    # Write back only if updated
    if updated:
        with open(csv_file, "w", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["phone_number", "messages"])
            writer.writeheader()
            writer.writerows(rows)
    return updated

def save_conversation(phone_number, conversation):
    """
    Save or update the conversation for a phone number in conversations.csv.
    If the number exists, replace its conversation. If not, add a new row.
    """
    csv_file = "conversations.csv"
    fieldnames = ["phone_number", "conversation"]
    rows = []
    found = False
    # Read all rows if file exists
    if os.path.exists(csv_file):
        with open(csv_file, newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("phone_number") == str(phone_number):
                    row["conversation"] = json.dumps(conversation, ensure_ascii=False)
                    found = True
                rows.append(row)
    # If not found, add new row
    if not found:
        rows.append({"phone_number": str(phone_number), "conversation": json.dumps(conversation, ensure_ascii=False)})
    # Write all rows back
    with open(csv_file, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return True

# --------------------------
# MAIN FUNCTIONS
# --------------------------
def process_number(phone_number: str, save_filename: str = None):
    try:
        data = get_conversation(phone_number)
        
        if bot_sent_text(data):
            print(f"✅ Bot sent text to {phone_number}, generating conversation JSON")
            conversation_json = format_conversation_json(phone_number, data)
            saved_file = save_conversation_json(phone_number, conversation_json, save_filename)
            update_conversation(phone_number, conversation_json['messages'])
            # Print summary
            print(f"📊 Summary:")
            print(f"   Total messages stored: {len(conversation_json['messages'])}")
            
            return conversation_json, saved_file
        else:
            print(f"❌ Bot has NOT sent text to {phone_number}, ignoring")
            return None, None
            
    except requests.RequestException as e:
        print(f"❌ Error fetching conversation for {phone_number}: {e}")
        return None, None
    except Exception as e:
        print(f"❌ Unexpected error processing {phone_number}: {e}")
        return None, None


def process_multiple_numbers(phone_numbers: List[str], batch_filename: str = None):
    """Process multiple phone numbers and optionally save to a single batch file"""
    all_conversations = {}
    successful_exports = []
    
    for phone_number in phone_numbers:
        print(f"\n🔄 Processing {phone_number}...")
        conversation_data, saved_file = process_number(phone_number)
        
        if conversation_data:
            all_conversations[phone_number] = conversation_data
            successful_exports.append(phone_number)
    
    # Optionally save all conversations in a single batch file
    if batch_filename and all_conversations:
        batch_data = {
            "export_timestamp": datetime.now().isoformat(),
            "total_numbers_processed": len(phone_numbers),
            "successful_exports": len(successful_exports),
            "conversations": all_conversations
        }
        
        with open(batch_filename, 'w', encoding='utf-8') as f:
            json.dump(batch_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Batch file saved: {batch_filename}")
        print(f"📊 Batch Summary: {len(successful_exports)}/{len(phone_numbers)} conversations exported")
    
    return all_conversations

# --------------------------
# EXAMPLE USAGE
# --------------------------
if __name__ == "__main__":
    # Single number processing
    process_number("919673399332")