# --- app.py (SocketIO ভিত্তিক চূড়ান্ত সংস্করণ) ---
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, flash, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
# FIX: SocketIO, emit, join_room আমদানি করা হয়েছে
from database import load_messages, add_message, update_messages, init_db, UPLOAD_FOLDER, find_message
from config import SECRET_KEY, SITE_PASSWORD, UPLOAD_FOLDER_NAME
import os
import json
import base64 
from datetime import datetime
import eventlet # SocketIO এর জন্য এটি দরকার

# --- App এবং SocketIO ইনিশিয়ালাইজেশন ---
app = Flask(__name__, static_folder='static')
app.config.from_pyfile('config.py') 
app.secret_key = SECRET_KEY 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# FIX: SocketIO পুনরুদ্ধার করা হয়েছে
socketio = SocketIO(app, async_mode='eventlet', allow_upgrades=False) 
CHAT_ROOM = 'general_chat' # চ্যাটরুমের নাম

# --- Authentication Function (অপরিবর্তিত) ---
def is_logged_in():
    return session.get('logged_in')

# --- HTTP Routes (অপরিবর্তিত, শুধুমাত্র /chat রুটে messages লোড) ---

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        username = request.form.get('username').strip() 

        if not username:
            flash('Please enter a username.')
            return render_template('login.html')

        if password == SITE_PASSWORD:
            session['logged_in'] = True
            session['username'] = username.capitalize()
            return redirect(url_for('chat'))
        else:
            flash('Incorrect password.')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    # FIX: ডিসকানেক্ট ইভেন্ট সঠিকভাবে হ্যান্ডেল করার জন্য session ক্লিয়ার করা
    session.clear()
    return redirect(url_for('login'))

@app.route('/chat')
def chat():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    # FIX: SocketIO ব্যবহারের জন্য initial messages লোড করা
    messages = load_messages()
        
    return render_template('chat.html', 
                           username=session.get('username'),
                           messages=messages, # messages এখন JSON Dict list
                           current_user=session.get('username'))

@app.route(f'/{UPLOAD_FOLDER_NAME}/<filename>')
def uploaded_file(filename):
    if not is_logged_in():
        return '', 401
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ----------------- SocketIO Event Handlers -----------------

@socketio.on('connect')
def handle_connect():
    user = session.get('username')
    if user:
        join_room(CHAT_ROOM) # ব্যবহারকারীকে চ্যাটরুমে যোগ করা
        
        # FIX: ইউজার জয়েন নোটিফিকেশন তৈরি
        join_msg = {
            'id': -1, # বিশেষ আইডি যাতে এটি সেভ না হয়
            'user': 'System',
            'message': f'{user} has joined the room.',
            'time': datetime.now().strftime('%H:%M'),
            'system_notification': True # ক্লায়েন্টে রেন্ডার করার জন্য ফ্ল্যাগ
        }
        # শুধুমাত্র অন্যদের কাছে নোটিফিকেশন ব্রডকাস্ট করা
        emit('user_joined', join_msg, room=CHAT_ROOM, include_self=False) 
        print(f'{user} connected and joined room: {CHAT_ROOM}')
    else:
        # যদি লগইন না করা থাকে, তাহলে সকেট ডিসকানেক্ট করা
        return False

@socketio.on('disconnect')
def handle_disconnect():
    user = session.get('username')
    if user:
        leave_room(CHAT_ROOM)
        # FIX: ইউজার ডিসকানেক্ট নোটিফিকেশন তৈরি (ঐচ্ছিক)
        disconnect_msg = {
            'id': -2, 
            'user': 'System',
            'message': f'{user} has left the room.',
            'time': datetime.now().strftime('%H:%M'),
            'system_notification': True
        }
        emit('user_left', disconnect_msg, room=CHAT_ROOM, include_self=False) 
        print(f'{user} disconnected from room: {CHAT_ROOM}')

@socketio.on('send_message')
def handle_send_message(data):
    if not is_logged_in(): return

    user = session.get('username')
    content = data.get('message', '').strip()
    reply_to_id = data.get('reply_to_id') 

    if content:
        try:
            reply_msg_id = int(reply_to_id) if reply_to_id else None
        except (ValueError, TypeError):
            reply_msg_id = None
        
        # FIX: JSON ফাংশন ব্যবহার করে মেসেজ যোগ করা
        new_msg = add_message(username=user, content=content, reply_to_id=reply_msg_id)
        
        # নতুন মেসেজ ব্রডকাস্ট করা হচ্ছে
        emit('new_message', new_msg, room=CHAT_ROOM)

@socketio.on('upload_file')
def handle_upload_file(data):
    # ... (আগের upload_file লজিক অপরিবর্তিত) ...
    if not is_logged_in(): return
    try:
        file_data = data['file_data']
        caption = data.get('caption', '') 
        reply_to_id = data.get('reply_to_id')
        
        if ',' in file_data:
            header, encoded = file_data.split(',', 1)
        else: 
            encoded = file_data
            header = ''

        file_extension = '.png'
        if 'image/jpeg' in header or 'jpeg' in header: file_extension = '.jpg'
        elif 'image/png' in header or 'png' in header: file_extension = '.png'
        elif 'image/gif' in header or 'gif' in header: file_extension = '.gif' 

        file_bytes = base64.b64decode(encoded)
        file_name = f"{session.get('username', 'user')}_{int(datetime.now().timestamp())}_{os.urandom(4).hex()}{file_extension}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)

        with open(file_path, 'wb') as f: f.write(file_bytes)

        user = session.get('username')
        try:
            reply_msg_id = int(reply_to_id) if reply_to_id else None
        except (ValueError, TypeError):
            reply_msg_id = None
        
        new_msg = add_message(username=user, content=caption, image_path=file_name, reply_to_id=reply_msg_id)
            
        emit('new_message', new_msg, room=CHAT_ROOM)
    except Exception as e:
        print(f"Error handling file upload: {e}") 

@socketio.on('typing')
def handle_typing(data):
    """FIX: টাইপিং স্ট্যাটাস ব্রডকাস্ট করা"""
    if not is_logged_in(): return
    user = session.get('username')
    # Sender ছাড়া রুমে উপস্থিত সবার কাছে স্ট্যাটাস পাঠানো 
    emit('typing_status', {'user': user, 'is_typing': data['is_typing']}, room=CHAT_ROOM, include_self=False)

@socketio.on('react')
def handle_react(data):
    # ... (আগের reaction লজিক অপরিবর্তিত - database.py/load_messages ব্যবহার করবে) ...
    if not is_logged_in(): return
    
    user = session.get('username')
    msg_id = data.get('msg_id')
    reaction_type = data.get('reaction_type') 
    
    messages = load_messages()
    message = find_message(msg_id, messages)
    
    if message:
        reactions_data = message.get('reactions', {})
            
        user_reacted = False
        current_reaction_type = None

        for r_type, reaction_info in reactions_data.items():
            if user in reaction_info.get('users', []):
                user_reacted = True
                current_reaction_type = r_type
                break
        
        if user_reacted:
            if current_reaction_type == reaction_type:
                reactions_data[reaction_type]['count'] -= 1
                reactions_data[reaction_type]['users'].remove(user)
                if reactions_data[reaction_type]['count'] <= 0:
                    del reactions_data[reaction_type] 
            else:
                if current_reaction_type in reactions_data:
                    reactions_data[current_reaction_type]['count'] -= 1
                    if user in reactions_data[current_reaction_type]['users']:
                        reactions_data[current_reaction_type]['users'].remove(user)
                    if reactions_data[current_reaction_type]['count'] <= 0:
                        del reactions_data[current_reaction_type] 
                
                if reaction_type not in reactions_data:
                    reactions_data[reaction_type] = {'count': 0, 'users': []}
                
                reactions_data[reaction_type]['count'] += 1
                reactions_data[reaction_type]['users'].append(user)
        
        else:
            if reaction_type not in reactions_data:
                reactions_data[reaction_type] = {'count': 0, 'users': []}
                
            reactions_data[reaction_type]['count'] += 1
            reactions_data[reaction_type]['users'].append(user)
            
        message['reactions'] = reactions_data
        update_messages(messages) 

        simple_reactions = {r_type: data['count'] for r_type, data in reactions_data.items() if data.get('count', 0) > 0}
        
        # SocketIO এর মাধ্যমে সবার কাছে আপডেট পাঠানো
        emit('reaction_update', {'msg_id': msg_id, 'reactions': simple_reactions}, room=CHAT_ROOM)


# --- Running App ---
if __name__ == '__main__':
    init_db() 
    print("Starting SocketIO Server with JSON Storage...")
    # SocketIO দিয়ে সার্ভার রান করা হচ্ছে
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
