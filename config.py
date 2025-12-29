"""
Bot-Hosting.net Configuration
Host: fi3.bot-hosting.net
Port: 22182
Server: https://control.bot-hosting.net/server/f3786e69
"""

import os

HOST = os.environ.get('HOST', 'fi3.bot-hosting')
PORT = int(os.environ.get('PORT', 22182))

SERVER_URL = f"http://{HOST}:{PORT}"

STREAMLIT_CONFIG = {
    'server.port': PORT,
    'server.address': '0.0.0.0',
    'server.headless': True,
    'browser.serverAddress': HOST,
    'browser.serverPort': PORT
}
