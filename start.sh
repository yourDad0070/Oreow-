#!/bin/bash
# Bot-Hosting.net Startup Script
# Server: https://control.bot-hosting.net/server/f3786e69
# Host: fi3.bot-hosting.net
# Port: 22182

echo "Starting FB E2EE Application..."
echo "Host: fi3.hosting.net"
echo "Port: 22182"

# Install dependencies if needed
pip install -r requirements.txt --quiet

# Create data directory for JSON database
mkdir -p data

# Start Streamlit on port 22182
streamlit run streamlit_app.py --server.port 22182 --server.address 0.0.0.0 --server.headless true
