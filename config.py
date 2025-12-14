# --- config.py ---

import os
# প্রজেক্টের রুট ডিরেক্টরি
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = 'YOUR_SUPER_SECRET_KEY_HERE' 
SITE_PASSWORD = "u"  

# JSON Data file Configuration
# FIX: JSON ফাইলটি static ফোল্ডারের ভেতরে রাখা হলো
STATIC_FOLDER = os.path.join(BASE_DIR, 'static')
JSON_DATA_FILE_NAME = 'chat_data.json'
UPLOAD_FOLDER_NAME = 'uploads' # static/uploads

