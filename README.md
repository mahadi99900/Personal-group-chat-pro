‎💬 Termux-Royal Chat Web Pro
‎
‎A modern, lightweight, real-time private web chat application built with Flask + Flask-SocketIO, optimized for mobile users and local network deployment (especially Android + Termux / Hotspot setups).
‎
‎This project focuses on simplicity, speed, and smooth real-time interaction on low-resource devices while still offering rich chat features like replies, reactions, typing indicators, and image sharing.
‎
‎
‎---
‎
‎✨ Features
‎
‎🚀 Real-time Messaging using Socket.IO
‎
‎📱 Mobile-Optimized UI (Dark Mode, touch-friendly, swipe gestures)
‎
‎💾 Persistent Storage using local JSON (chat history survives restart)
‎
‎💬 Message Replies (reply to specific messages)
‎
‎👉 Swipe-to-Reply (mobile-friendly gesture)
‎
‎❤️ Live Reactions (long-press / double-tap to react)
‎
‎✍️ Typing Indicator (see who is typing in real time)
‎
‎🖼 Image Sharing (upload & preview images in chat)
‎
‎🔔 System Notifications (join / leave alerts)
‎
‎🔐 Room Protection using a shared password
‎
‎
‎
‎---
‎
‎🧠 Designed For
‎
‎Android users running Termux
‎
‎Local network chatting via Hotspot / Wi-Fi
‎
‎Lightweight private group chat without cloud dependency
‎
‎Learning Flask + Socket.IO in a practical project
‎
‎
‎
‎---
‎
‎🚀 Installation & Setup
‎
‎📦 Prerequisites
‎
‎Python 3.9+
‎
‎Termux (optional, for Android users)
‎
‎
‎📚 Required Libraries
‎
‎pip install Flask Flask-SocketIO eventlet
‎
‎> Why eventlet?
‎Socket.IO requires an async worker. eventlet provides fast and lightweight async support.
‎
‎
‎
‎
‎---
‎
‎▶️ Run the Server
‎
‎git clone YOUR_REPOSITORY_URL
‎cd chating_web_pro
‎python app.py
‎
‎The server will start at:
‎
‎http://0.0.0.0:5000
‎
‎Access it from any device on the same network:
‎
‎http://YOUR-IP:5000
‎
‎Example:
‎
‎http://192.168.43.1:5000
‎
‎
‎---
‎
‎⚙️ Configuration
‎
‎Edit config.py:
‎
‎SECRET_KEY → Flask security key
‎
‎SITE_PASSWORD → Chat room password
‎
‎
‎
‎---
‎
‎⚠️ Known Issues & Future Updates
‎
‎🐞 Reaction Persistence Bug
‎Reactions on old messages loaded from JSON may not register correctly after restart.
‎
‎📡 Presence Stability
‎On unstable mobile networks, Socket.IO may show false disconnects.
‎
‎⚠️ Eventlet Deprecation Warning
‎Future update may migrate to a newer async framework.
‎
‎
‎> These issues do not affect core messaging and will be improved in future releases.
‎
‎
‎
‎
‎---
‎
‎🤝 Contribution
‎
‎Contributions are welcome!
‎
‎Report bugs
‎
‎Suggest features
‎
‎Submit pull requests
‎
‎
‎
‎---
‎
‎👤 Author
‎
‎Mahdi bin Iqbal
‎Python Developer | Web Enthusiast
‎
‎
‎
