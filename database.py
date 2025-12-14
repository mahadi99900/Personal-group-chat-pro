# --- database.py (JSON ভিত্তিক স্টোরেজ) ---
import json
import os
from datetime import datetime
from config import STATIC_FOLDER, JSON_DATA_FILE_NAME, UPLOAD_FOLDER_NAME

# ডেটা এবং আপলোড ফোল্ডারের সঠিক পথ তৈরি
DATA_FILE_PATH = os.path.join(STATIC_FOLDER, JSON_DATA_FILE_NAME)
UPLOAD_FOLDER = os.path.join(STATIC_FOLDER, UPLOAD_FOLDER_NAME)

def load_messages():
    """Loads all messages from the JSON file."""
    if not os.path.exists(DATA_FILE_PATH):
        return []
    try:
        with open(DATA_FILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # যদি ফাইলটি খালি বা Corrupted হয়, তবে খালি লিস্ট রিটার্ন করবে
        return []

def save_messages(messages):
    """Saves the current list of messages to the JSON file."""
    # ফোল্ডার আছে কিনা নিশ্চিত করা
    if not os.path.exists(STATIC_FOLDER):
        os.makedirs(STATIC_FOLDER)
        
    try:
        with open(DATA_FILE_PATH, 'w', encoding='utf-8') as f:
            # ensure_ascii=False যোগ করা হয়েছে যাতে বাংলা অক্ষর ঠিকমতো সেভ হয়
            json.dump(messages, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving data to JSON file: {e}")
        return False

def get_new_message_id(messages):
    """Generates a new unique message ID based on the last message."""
    if not messages:
        return 1
    # আইডি হিসেবে সর্বশেষ মেসেজের আইডি থেকে 1 যোগ করা হচ্ছে
    return messages[-1].get('id', 0) + 1

def find_message(msg_id, messages=None):
    """Finds a message by its ID."""
    if messages is None:
        messages = load_messages()
    return next((msg for msg in messages if msg.get('id') == msg_id), None)

def add_message(username, content=None, image_path=None, reply_to_id=None, reactions=None):
    """Creates a new message and adds it to the JSON file."""
    messages = load_messages()
    new_id = get_new_message_id(messages)
    timestamp = datetime.now().strftime('%H:%M')
    
    # রিপ্লাই মেসেজের তথ্য বের করা
    reply_user = None
    reply_content = None
    if reply_to_id:
        replied_msg = find_message(reply_to_id, messages)
        if replied_msg:
            reply_user = replied_msg.get('user')
            reply_content = replied_msg.get('message')
            if not reply_content and replied_msg.get('image_path'):
                reply_content = "Image attached"
            elif not reply_content:
                reply_content = "(No content)"

    new_message = {
        'id': new_id,
        'user': username,
        'message': content,
        'time': timestamp,
        'image_path': image_path,
        'reactions': reactions or {},
        'reply_to_id': reply_to_id,
        'reply_to_user': reply_user,
        'reply_to_content': reply_content
    }
    
    messages.append(new_message)
    save_messages(messages)
    return new_message

def update_messages(messages):
    """Saves the entire list of messages after modification."""
    save_messages(messages)

def init_db(app=None):
    """Initializes the required folders and the JSON file."""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    # Ensures chat_data.json exists with empty list
    if not os.path.exists(DATA_FILE_PATH):
        save_messages([])
    
    print("JSON Storage and Upload folder initialized successfully.")
    return True
