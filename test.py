# # conversation_history.py

# import requests
# import json
# import pandas as pd
# import os
# from datetime import datetime
# from coversation_history import process_number   # <-- import your first file

# # -------------------------
# # CONFIG
# # -------------------------
# CHAT_API_URL = "https://239104f95ea8.ngrok-free.app/chat"   # Your RAG bot API
# WATI_API_BASE = "https://live-mt-server.wati.io/200128/api/v1"   # Your WATI base
# WATI_TOKEN = "ey"  # Make sure this is your complete token
# CSV_FILE_PATH = "conversations.csv"  # Path to save conversations


# CHAT_HEADERS = {
#     "Content-Type": "application/json"
# }
# WATI_HEADERS = {
#     "Authorization": f"Bearer {WATI_TOKEN}",
#     "Content-Type": "application/json"
# }

# def send_conversation(conversation_json, phone_number=None):
#     """
#     Send conversation JSON to /chat endpoint.
#     """
#     if not conversation_json or "messages" not in conversation_json:
#         raise ValueError("Invalid conversation_json format")

#     payload = {"messages": []}

#     if phone_number:
#         payload["phone_number"] = str(phone_number)

#     for msg in conversation_json["messages"]:
#         role = msg.get("role", "").lower()
#         if role not in ["user", "assistant"]:
#             continue

#         payload["messages"].append({
#             "role": role,
#             "content": msg.get("content", ""),
#             "timestamp": msg.get("timestamp")  # optional
#         })

#     print("📤 Sending payload to /chat API:")
#     print(json.dumps(payload, indent=2, ensure_ascii=False))

#     try:
#         response = requests.post(CHAT_API_URL, headers=CHAT_HEADERS, json=payload, timeout=30)
#         response.raise_for_status()
#         return response.json()
#     except requests.RequestException as e:
#         print(f"❌ Error sending conversation: {e}")
#         return {"success": False, "error": str(e)}



# def messages_to_conversation_string(messages):
#     """
#     Convert list of messages to a readable conversation string
#     """
#     conversation_parts = []
#     for msg in messages:
#         role = msg.get("role", "").title()
#         content = msg.get("content", "").strip()
#         if content:
#             conversation_parts.append(f"{role}: {content}")
    
#     return "\n".join(conversation_parts)


# def conversation_string_to_messages(conversation_str):
#     """
#     Convert conversation string back to messages list
#     """
#     if not conversation_str:
#         return []
    
#     messages = []
#     lines = conversation_str.strip().split('\n')
    
#     for line in lines:
#         if ':' in line:
#             role_part, content_part = line.split(':', 1)
#             role = role_part.strip().lower()
#             content = content_part.strip()
#             if role in ['user', 'assistant'] and content:
#                 messages.append({"role": role, "content": content})
    
#     return messages


# def find_common_messages(existing_messages, new_messages):
#     """
#     Find common messages between existing and new conversations
#     Returns: (common_count, new_messages_only)
#     """
#     if not existing_messages or not new_messages:
#         return 0, new_messages
    
#     # Find the longest common sequence from the beginning
#     common_count = 0
#     min_length = min(len(existing_messages), len(new_messages))
    
#     for i in range(min_length):
#         existing_msg = existing_messages[i]
#         new_msg = new_messages[i]
        
#         if (existing_msg.get("role") == new_msg.get("role") and 
#             existing_msg.get("content") == new_msg.get("content")):
#             common_count += 1
#         else:
#             break
    
#     # Return only the new messages that aren't in common
#     new_messages_only = new_messages[common_count:]
#     return common_count, new_messages_only


# def save_conversation_to_csv(phone_number, conversation_json):
#     """
#     Save conversation to CSV, handling updates efficiently
#     """
#     try:
#         # Create CSV file if it doesn't exist
#         if not os.path.exists(CSV_FILE_PATH):
#             df = pd.DataFrame(columns=['phone_number', 'conversation', 'last_updated'])
#             df.to_csv(CSV_FILE_PATH, index=False)
#             print(f"📄 Created new CSV file: {CSV_FILE_PATH}")
        
#         # Read existing CSV
#         df = pd.read_csv(CSV_FILE_PATH)
        
#         # Extract messages from new conversation
#         new_messages = conversation_json.get("messages", [])
#         if not new_messages:
#             print("❌ No messages found in conversation_json")
#             return
        
#         # Check if phone number already exists
#         existing_row = df[df['phone_number'] == phone_number]
        
#         if not existing_row.empty:
#             # Phone number exists, need to merge conversations
#             print(f"📱 Found existing conversation for {phone_number}")
            
#             existing_conversation = existing_row.iloc[0]['conversation']
#             existing_messages = conversation_string_to_messages(existing_conversation)
            
#             # Find common messages and get only new ones
#             common_count, new_messages_only = find_common_messages(existing_messages, new_messages)
            
#             print(f"🔄 Common messages: {common_count}")
#             print(f"➕ New messages to add: {len(new_messages_only)}")
            
#             if new_messages_only:
#                 # Combine existing and new messages
#                 combined_messages = existing_messages + new_messages_only
#                 combined_conversation = messages_to_conversation_string(combined_messages)
                
#                 # Update the existing row
#                 df.loc[df['phone_number'] == phone_number, 'conversation'] = combined_conversation
#                 df.loc[df['phone_number'] == phone_number, 'last_updated'] = datetime.now().isoformat()
                
#                 print(f"✅ Updated conversation for {phone_number}")
#                 print(f"📝 Added {len(new_messages_only)} new messages")
#             else:
#                 print(f"ℹ️ No new messages to add for {phone_number}")
#         else:
#             # New phone number, add entire conversation
#             print(f"📱 Adding new conversation for {phone_number}")
            
#             conversation_str = messages_to_conversation_string(new_messages)
#             new_row = pd.DataFrame([{
#                 'phone_number': phone_number,
#                 'conversation': conversation_str,
#                 'last_updated': datetime.now().isoformat()
#             }])
            
#             df = pd.concat([df, new_row], ignore_index=True)
#             print(f"✅ Added new conversation with {len(new_messages)} messages")
        
#         # Save updated CSV
#         df.to_csv(CSV_FILE_PATH, index=False)
#         print(f"💾 Saved to {CSV_FILE_PATH}")
        
#         # Print summary
#         total_rows = len(df)
#         print(f"📊 Total conversations in CSV: {total_rows}")
        
#         return True
        
#     except Exception as e:
#         print(f"❌ Error saving conversation to CSV: {e}")
#         return False


# def load_conversation_from_csv(phone_number):
#     """
#     Load conversation for a specific phone number from CSV
#     """
#     try:
#         if not os.path.exists(CSV_FILE_PATH):
#             print(f"📄 CSV file {CSV_FILE_PATH} doesn't exist")
#             return None
        
#         df = pd.read_csv(CSV_FILE_PATH)
#         existing_row = df[df['phone_number'] == phone_number]
        
#         if not existing_row.empty:
#             conversation_str = existing_row.iloc[0]['conversation']
#             last_updated = existing_row.iloc[0]['last_updated']
#             messages = conversation_string_to_messages(conversation_str)
            
#             print(f"📱 Loaded conversation for {phone_number}")
#             print(f"🕐 Last updated: {last_updated}")
#             print(f"💬 Messages count: {len(messages)}")
            
#             return {
#                 "phone_number": phone_number,
#                 "messages": messages,
#                 "last_updated": last_updated
#             }
#         else:
#             print(f"📱 No conversation found for {phone_number}")
#             return None
            
#     except Exception as e:
#         print(f"❌ Error loading conversation from CSV: {e}")
#         return None
#     """
#     Send conversation JSON to /chat endpoint.
#     """
#     if not conversation_json or "messages" not in conversation_json:
#         raise ValueError("Invalid conversation_json format")

#     payload = {"messages": []}

#     if phone_number:
#         payload["phone_number"] = str(phone_number)

#     for msg in conversation_json["messages"]:
#         role = msg.get("role", "").lower()
#         if role not in ["user", "assistant"]:
#             continue

#         payload["messages"].append({
#             "role": role,
#             "content": msg.get("content", ""),
#             "timestamp": msg.get("timestamp")  # optional
#         })

#     print("📤 Sending payload to /chat API:")
#     print(json.dumps(payload, indent=2, ensure_ascii=False))

#     try:
#         response = requests.post(CHAT_API_URL, headers=CHAT_HEADERS, json=payload, timeout=30)
#         response.raise_for_status()
#         return response.json()
#     except requests.RequestException as e:
#         print(f"❌ Error sending conversation: {e}")
#         return {"success": False, "error": str(e)}


# def send_wati_message(phone_number: str, message: str):
#     """
#     Send a WhatsApp message to the user via WATI.
#     """
#     # Clean and validate the message
#     message = str(message).strip()
#     if not message:
#         print("❌ Message is empty after cleaning")
#         return {"result": False, "error": "Message is empty"}
    
#     print(f"📤 Message length: {len(message)}")
#     print(f"📤 Message repr: {repr(message)}")
    
#     # Remove emojis to test if they're causing issues
#     message_no_emoji = ''.join(char for char in message if ord(char) < 127)
#     print(f"📤 Message without emojis: {repr(message_no_emoji)}")
    
#     url = f"{WATI_API_BASE}/sendSessionMessage/{phone_number}"
    
#     # Try different payload formats that WATI might accept
#     payloads_to_try = [
#         {"messageText": message},
#         {"messageText": message_no_emoji},  # Try without emojis
#         {"message": message},
#         {"text": message},
#         {"messageText": message, "messageType": "text"},
#         {"messageText": message, "format": "text"}
#     ]
    
#     print(f"📤 Sending WhatsApp message to {phone_number}")
#     print(f"📤 URL: {url}")
#     print(f"📤 Headers: {WATI_HEADERS}")

#     for i, payload in enumerate(payloads_to_try):
#         print(f"\n📤 Trying payload format {i+1}: {json.dumps(payload, ensure_ascii=False)}")
        
#         try:
#             response = requests.post(url, headers=WATI_HEADERS, json=payload, timeout=30)
#             print(f"📤 Response status: {response.status_code}")
#             print(f"📤 Response headers: {dict(response.headers)}")
#             print(f"📤 Response text: {response.text}")
            
#             if response.status_code == 200:
#                 try:
#                     response_json = response.json()
#                     print(f"📤 Parsed JSON: {response_json}")
#                     if response_json.get("result", False):
#                         print(f"✅ Success with payload format {i+1}")
#                         return response_json
#                     else:
#                         print(f"❌ Failed with payload format {i+1}: {response_json}")
#                 except json.JSONDecodeError:
#                     print(f"❌ Could not parse JSON response: {response.text}")
#             else:
#                 print(f"❌ HTTP error {response.status_code} with payload format {i+1}")
                
#         except requests.RequestException as e:
#             print(f"❌ Request error with payload format {i+1}: {e}")
    
#     return {"result": False, "error": "All payload formats failed"}


# def send_wati_message_alternative(phone_number: str, message: str):
#     """
#     Alternative method using form data instead of JSON
#     """
#     message = str(message).strip()
#     if not message:
#         return {"result": False, "error": "Message is empty"}
    
#     url = f"{WATI_API_BASE}/sendSessionMessage/{phone_number}"
    
#     # Try with form data
#     headers_form = {
#         "Authorization": f"Bearer {WATI_TOKEN}"
#     }
    
#     data = {"messageText": message}
    
#     print(f"📤 Trying form data approach")
#     print(f"📤 Data: {data}")
#     print(f"📤 Headers: {headers_form}")
    
#     try:
#         response = requests.post(url, headers=headers_form, data=data, timeout=30)
#         print(f"📤 Form response status: {response.status_code}")
#         print(f"📤 Form response text: {response.text}")
        
#         if response.status_code == 200:
#             return response.json()
#         else:
#             return {"result": False, "error": f"HTTP {response.status_code}: {response.text}"}
            
#     except Exception as e:
#         print(f"❌ Form data error: {e}")
#         return {"result": False, "error": str(e)}


# if __name__ == "__main__":
#     phone_number = "919550822097"

#     # Step 1: Fetch conversation history
#     conversation_json, _ = process_number(phone_number)

#     if conversation_json:
#         # Step 1.5: Save conversation to CSV (with smart merging)
#         print("\n" + "="*50)
#         print("💾 SAVING CONVERSATION TO CSV")
#         print("="*50)
#         save_success = save_conversation_to_csv(phone_number, conversation_json)
        
#         if save_success:
#             print("✅ Conversation saved successfully")
#         else:
#             print("❌ Failed to save conversation")
        
#         # Optional: Load and display saved conversation
#         print("\n" + "="*50)
#         print("📖 LOADING SAVED CONVERSATION")
#         print("="*50)
#         saved_conversation = load_conversation_from_csv(phone_number)
#         if saved_conversation:
#             print("📝 Saved conversation preview:")
#             for i, msg in enumerate(saved_conversation["messages"][-3:]):  # Show last 3 messages
#                 print(f"  {i+1}. {msg['role'].title()}: {msg['content'][:100]}...")
        
#         # Step 2: Send to /chat API
#         print("\n" + "="*50)
#         print("🤖 SENDING TO CHAT API")
#         print("="*50)
#         chat_response = send_conversation(conversation_json, phone_number=phone_number)
#         print("✅ Chat API Response:")
#         print(json.dumps(chat_response, indent=2, ensure_ascii=False))

#         # Step 3: Extract bot message and forward to WhatsApp
#         if chat_response.get("success"):
#             bot_reply = chat_response.get("message", "Thank you for contacting us.")
            
#             print(f"🔍 Bot reply to send: {repr(bot_reply)}")
#             print(f"🔍 Bot reply length: {len(bot_reply)}")
#             print(f"🔍 Phone number: {phone_number}")
            
#             print("\n" + "="*50)
#             print("📱 SENDING WHATSAPP MESSAGE")
#             print("="*50)
            
#             # Try primary method
#             wati_response = send_wati_message(phone_number, bot_reply)
#             print("✅ WATI API Response (JSON):")
#             print(json.dumps(wati_response, indent=2, ensure_ascii=False))
            
#             # If JSON method fails, try form data method
#             if not wati_response.get("result", False):  # Changed from "success" to "result"
#                 print("\n🔄 Trying alternative form data method...")
#                 wati_response_alt = send_wati_message_alternative(phone_number, bot_reply)
#                 print("✅ WATI API Response (Form):")
#                 print(json.dumps(wati_response_alt, indent=2, ensure_ascii=False))
#         else:
#             print("❌ Chat API did not return success, not sending WhatsApp message")
#     else:
#         print("❌ No conversation data found")


# conversation_history.py

import requests
import json
from coversation_history import process_number   # <-- import your first file
import time
import re

# -------------------------
# CONFIG
# -------------------------
CHAT_API_URL = "https://8795a39e8611.ngrok-free.app/chat"   # Your RAG bot API
WATI_API_BASE = "https://live-mt-server.wati.io/200128/api/v1"   # Your WATI base
WATI_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJhMTc3MzU3Mi01ODFiLTQ4MzQtOWJiOS1mYWM2NjRkYzNiMjAiLCJ1bmlxdWVfbmFtZSI6ImVrYWdhckB2YWhhbi5jbyIsIm5hbWVpZCI6ImVrYWdhckB2YWhhbi5jbyIsImVtYWlsIjoiZWthZ2FyQHZhaGFuLmNvIiwiYXV0aF90aW1lIjoiMTAvMDUvMjAyMyAwNzozNjo1NyIsImRiX25hbWUiOiJtdC1wcm9kLVRlbmFudHMiLCJ0ZW5hbnRfaWQiOiIyMDAxMjgiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL3JvbGUiOiJBRE1JTklTVFJBVE9SIiwiZXhwIjoyNTM0MDIzMDA4MDAsImlzcyI6IkNsYXJlX0FJIiwiYXVkIjoiQ2xhcmVfQUkifQ.ud5AYN5Kf5Xm17WX8Krr1Z3qJo0waJu75cY-o3N2EuU"
  # Make sure this is your complete token


CHAT_HEADERS = {
    "Content-Type": "application/json"
}
WATI_HEADERS = {
    "Authorization": f"Bearer {WATI_TOKEN}",
    "Content-Type": "application/json"
}

def send_conversation(conversation_json, phone_number=None):
    """
    MODIFIED FUNCTION
    Finds the first "Congratulations!" assistant template message
    and sends only the messages that came BEFORE it.
    """
    if not conversation_json or "messages" not in conversation_json:
        raise ValueError("Invalid conversation_json format")

    all_messages = conversation_json.get("messages", [])

    # --- REFINED LOGIC START ---
    target_content_snippet = "Congratulations! Aap *Swiggy Instamart Delivery Partner* job ke liye shortlist hue hain."
    
    template_index = -1
    # Search from TOP to bottom: stop at the FIRST matching template
    for i, msg in enumerate(all_messages):
        role = msg.get("role", "").lower()
        content = msg.get("content", "")
        
        if role == "assistant" and target_content_snippet in content:
            template_index = i
            break  # stop at the first template block
    
    # Slice the list to get only messages BEFORE the template
    if template_index != -1:
        messages_to_send = all_messages[:template_index]
        print(f"✅ Found template message at index {template_index}. Sending {len(messages_to_send)} message(s) that came BEFORE it.")
    else:
        # Fallback: If the template is not found, send the whole history
        messages_to_send = all_messages
        print("⚠️ Template message not found. Sending full conversation history as a fallback.")
    # --- REFINED LOGIC END ---

    if not messages_to_send:
        print("✅ No messages found before the template. Nothing to send.")
        return {"success": False, "message": "No messages to process."}

    # Build the payload with the filtered messages
    payload = {"messages": []}
    if phone_number:
        payload["phone_number"] = str(phone_number)

    for msg in messages_to_send:
        role = msg.get("role", "").lower()
        if role not in ["user", "assistant"]:
            continue

        payload["messages"].append({
            "role": role,
            "content": msg.get("content", ""),
            "timestamp": msg.get("timestamp")
        })

    print(f"📤 Sending payload with {len(payload['messages'])} message(s) to /chat API:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    try:
        response = requests.post(CHAT_API_URL, headers=CHAT_HEADERS, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ Error sending conversation: {e}")
        return {"success": False, "error": str(e)}



def split_message_into_chunks(message: str, max_sentences: int = 2):
    """
    Split message into chunks of 1–2 sentences each.
    """
    # Split into sentences using regex for ., !, ?
    sentences = re.split(r'(?<=[.!?])\s+', message.strip())
    chunks = []

    # Group sentences into chunks of max_sentences
    for i in range(0, len(sentences), max_sentences):
        chunk = " ".join(sentences[i:i+max_sentences]).strip()
        if chunk:
            chunks.append(chunk)
    
    return chunks


def send_wati_message_alternative(phone_number: str, message: str, delay_seconds: int = 1):
    """
    Alternative method using form data instead of JSON
    Splits message into smaller chunks and sends sequentially.
    """
    message = str(message).strip()
    if not message:
        return {"result": False, "error": "Message is empty"}
    
    url = f"{WATI_API_BASE}/sendSessionMessage/{phone_number}"
    headers_form = {"Authorization": f"Bearer {WATI_TOKEN}"}

    # Split into smaller chunks
    chunks = split_message_into_chunks(message)
    results = []

    for idx, chunk in enumerate(chunks, start=1):
        data = {"messageText": chunk}
        print(f"📤 Sending part {idx}/{len(chunks)}: {chunk}")

        try:
            response = requests.post(url, headers=headers_form, data=data, timeout=30)
            print(f"📤 Status: {response.status_code}, Response: {response.text}")
            
            if response.status_code == 200:
                results.append(response.json())
            else:
                results.append({"result": False, "error": f"HTTP {response.status_code}: {response.text}"})
            
        except Exception as e:
            print(f"❌ Error sending part {idx}: {e}")
            results.append({"result": False, "error": str(e)})

        # Add a delay between messages (to avoid rate limiting)
        time.sleep(delay_seconds)

    return results



if __name__ == "__main__":
    phone_number = "919550822097"

    # Step 1: Fetch conversation history
    conversation_json, _ = process_number(phone_number)

    if conversation_json:
        # Step 2: Send to /chat API
        chat_response = send_conversation(conversation_json, phone_number=phone_number)
        print("✅ Chat API Response:")
        print(json.dumps(chat_response, indent=2, ensure_ascii=False))

        # Step 3: Extract bot message and forward to WhatsApp
        if chat_response.get("success"):
            bot_reply = chat_response.get("message", "Thank you for contacting us.")
            
            if isinstance(bot_reply, dict):
                bot_reply = bot_reply.get("content", "Thank you for contacting us.")

            print(f"🔍 Bot reply to send: {repr(bot_reply)}")
            print(f"🔍 Bot reply length: {len(bot_reply)}")
            print(f"🔍 Phone number: {phone_number}")


            print("\n🔄 Trying alternative form data method...")
            wati_response_alt = send_wati_message_alternative(phone_number, bot_reply)
            print("✅ WATI API Response (Form):")
            print(json.dumps(wati_response_alt, indent=2, ensure_ascii=False))
        else:
            print("❌ Chat API did not return success or no new messages found, not sending WhatsApp message.")
    else:
        print("❌ No conversation data found")