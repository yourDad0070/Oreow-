import streamlit as st
import time
import threading
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import database as db
import facebook_messenger_notifier
import requests
import base64
from io import BytesIO
import httpx
import uuid
import random
import string
import json
from datetime import datetime

try:
    from streamlit_local_storage import LocalStorage
    LOCALSTORAGE_AVAILABLE = True
    local_storage = LocalStorage()
except ImportError:
    LOCALSTORAGE_AVAILABLE = False
    local_storage = None

st.set_page_config(
    page_title="FB E2EE by Shan Rulex",
    page_icon="😐",
    layout="wide",
    initial_sidebar_state="expanded"
)

custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Orbitron:wght@600;700&display=swap');

    /* ===  CLEAN MOBILE-FRIENDLY DESIGN - Reference Image Style === */

    * {
        font-family: 'Rajdhani', sans-serif !important;
    }

    /* Simple Dark Background */
    .stApp {
        background: #000000 !important;
    }

    /* Profile Header - Clean Design */
    .profile-header {
        background: rgba(0, 15, 25, 0.8);
        border: 2px solid #00D9FF;
        padding: 2rem 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.3);
    }

    /* Profile Image Container with Rotating Chakra */
    .profile-image-container {
        position: relative;
        width: 150px;
        height: 150px;
        margin: 0 auto 1.5rem;
        display: block;
    }

    .profile-image {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        border: 3px solid #00D9FF;
        box-shadow: 0 0 15px rgba(0, 217, 255, 0.5);
        position: relative;
        z-index: 2;
        display: block;
    }

    /* Rotating Chakra Ring */
    .profile-image-container::before {
        content: '';
        position: absolute;
        top: -10px;
        left: -10px;
        right: -10px;
        bottom: -10px;
        border-radius: 50%;
        border: 3px solid transparent;
        border-top-color: #00E5FF;
        border-right-color: #00E5FF;
        animation: rotate-chakra 3s linear infinite;
        z-index: 1;
    }

    /* Second Rotating Chakra Ring (Counter-rotation) */
    .profile-image-container::after {
        content: '';
        position: absolute;
        top: -15px;
        left: -15px;
        right: -15px;
        bottom: -15px;
        border-radius: 50%;
        border: 2px solid transparent;
        border-bottom-color: #00D9FF;
        border-left-color: #00D9FF;
        animation: rotate-chakra-reverse 4s linear infinite;
        opacity: 0.7;
        z-index: 1;
    }

    /* Chakra Rotation Animation */
    @keyframes rotate-chakra {
        from {
            transform: rotate(0deg);
        }
        to {
            transform: rotate(360deg);
        }
    }

    @keyframes rotate-chakra-reverse {
        from {
            transform: rotate(360deg);
        }
        to {
            transform: rotate(0deg);
        }
    }

    .profile-header h1 {
        /* Animated Rainbow Gradient - Smooth and Colorful */
        background: linear-gradient(
            90deg, 
            #00E5FF 0%, 
            #7B2FF7 20%, 
            #F107A3 40%, 
            #FD8D14 60%, 
            #00E5FF 80%,
            #7B2FF7 100%
        ) !important;
        background-size: 300% 100% !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;

        font-size: 3rem;
        font-weight: 900;
        margin: 1rem 0;
        text-transform: uppercase;
        letter-spacing: 5px;
        font-family: 'Orbitron', monospace !important;

        /* Smooth Colorful Glow */
        text-shadow: 
            0 0 20px rgba(0, 229, 255, 0.6),
            0 0 40px rgba(123, 47, 247, 0.4),
            0 0 60px rgba(241, 7, 163, 0.3);

        /* GPU-Accelerated Smooth Animations */
        animation: 
            rainbow-shift 8s ease infinite,
            gentle-float 4s ease-in-out infinite;

        /* 3D Transform for depth */
        transform: perspective(500px) translateZ(0) rotateX(3deg);
        transform-style: preserve-3d;
        will-change: transform;

        /* Smooth Filter */
        filter: drop-shadow(0 0 20px rgba(0, 229, 255, 0.5));

        transition: all 0.3s ease;
    }

    /* Smooth Rainbow Gradient Animation */
    @keyframes rainbow-shift {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }

    /* Gentle Floating Motion - Very Smooth */
    @keyframes gentle-float {
        0%, 100% {
            transform: perspective(500px) translateZ(0) rotateX(3deg) translateY(0px);
        }
        50% {
            transform: perspective(500px) translateZ(0) rotateX(3deg) translateY(-8px);
        }
    }

    .profile-header h1:hover {
        transform: perspective(500px) translateZ(0) rotateX(0deg) scale(1.05);
        filter: drop-shadow(0 0 30px rgba(241, 7, 163, 0.8));
        letter-spacing: 7px;
    }

    /* Floating Text Animation */
    @keyframes float-text {
        0%, 100% {
            transform: perspective(500px) rotateX(5deg) translateY(0px);
        }
        50% {
            transform: perspective(500px) rotateX(5deg) translateY(-10px);
        }
    }

    /* Pulsing Glow Animation */
    @keyframes pulse-glow {
        0%, 100% {
            text-shadow: 
                0 0 10px rgba(0, 229, 255, 0.8),
                0 0 20px rgba(0, 229, 255, 0.6),
                0 0 30px rgba(0, 229, 255, 0.4),
                0 0 40px rgba(0, 229, 255, 0.3),
                3px 3px 0px rgba(0, 100, 150, 0.5),
                6px 6px 0px rgba(0, 80, 120, 0.3),
                9px 9px 0px rgba(0, 60, 90, 0.2);
        }
        50% {
            text-shadow: 
                0 0 15px rgba(0, 229, 255, 1),
                0 0 30px rgba(0, 229, 255, 0.8),
                0 0 45px rgba(0, 229, 255, 0.6),
                0 0 60px rgba(0, 229, 255, 0.4),
                3px 3px 0px rgba(0, 150, 200, 0.6),
                6px 6px 0px rgba(0, 120, 160, 0.4),
                9px 9px 0px rgba(0, 90, 120, 0.3);
        }
    }

    .profile-header p {
        color: rgba(0, 217, 255, 0.9);
        font-size: 1.2rem;
        margin: 0.5rem 0;
        font-weight: 500;
    }

    /* Clean Buttons */
    .contact-link {
        display: inline-block;
        background: rgba(0, 217, 255, 0.15);
        color: #00D9FF;
        padding: 1rem 2.5rem;
        border-radius: 10px;
        text-decoration: none;
        font-weight: 700;
        margin-top: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 0 10px rgba(0, 217, 255, 0.3);
        border: 2px solid #00D9FF;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    .contact-link:hover {
        background: rgba(0, 217, 255, 0.25);
        box-shadow: 0 0 15px rgba(0, 217, 255, 0.5);
        transform: translateY(-2px);
    }

    /* Simple Streamlit Buttons */
    .stButton>button {
        background: rgba(0, 217, 255, 0.15) !important;
        color: #00D9FF !important;
        border: 2px solid #00D9FF !important;
        border-radius: 10px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 0 10px rgba(0, 217, 255, 0.3) !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
    }

    .stButton>button:hover {
        background: rgba(0, 217, 255, 0.25) !important;
        box-shadow: 0 0 15px rgba(0, 217, 255, 0.5) !important;
        transform: translateY(-2px) !important;
    }

    /* Clean Input Fields */
    .stTextInput>div>div>input, 
    .stTextArea>div>div>textarea, 
    .stNumberInput>div>div>input {
        background: rgba(0, 15, 25, 0.8) !important;
        border: 2px solid rgba(0, 217, 255, 0.4) !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        color: #00D9FF !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 0 10px rgba(0, 217, 255, 0.2) !important;
    }

    .stTextInput>div>div>input:focus, 
    .stTextArea>div>div>textarea:focus,
    .stNumberInput>div>div>input:focus {
        border-color: #00D9FF !important;
        box-shadow: 0 0 15px rgba(0, 217, 255, 0.5) !important;
    }

    .stTextInput>div>div>input::placeholder,
    .stTextArea>div>div>textarea::placeholder,
    .stNumberInput>div>div>input::placeholder {
        color: rgba(0, 217, 255, 0.5) !important;
    }

    /* Simple Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(0, 15, 25, 0.6);
        padding: 10px;
        border-radius: 10px;
        border: 2px solid rgba(0, 217, 255, 0.3);
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(0, 15, 25, 0.8);
        border-radius: 8px;
        padding: 12px 24px;
        border: 2px solid rgba(0, 217, 255, 0.4);
        color: rgba(0, 217, 255, 0.8);
        font-weight: 600;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(0, 217, 255, 0.15);
        color: #00D9FF;
        border-color: #00D9FF;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(0, 217, 255, 0.2) !important;
        color: #ffffff !important;
        box-shadow: 0 0 10px rgba(0, 217, 255, 0.5);
        border-color: #00D9FF !important;
    }

    /* Simple Metric Cards */
    [data-testid="stMetric"] {
        background: rgba(0, 15, 25, 0.8);
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid rgba(0, 217, 255, 0.4);
        box-shadow: 0 0 15px rgba(0, 217, 255, 0.3);
        transition: all 0.3s ease;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.5);
        border-color: #00D9FF;
    }

    [data-testid="stMetricValue"] {
        color: #00D9FF !important;
        font-size: 2rem !important;
        font-weight: 900 !important;
        font-family: 'Orbitron', monospace !important;
    }

    [data-testid="stMetricLabel"] {
        color: rgba(0, 217, 255, 0.8) !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Simple Alert Messages */
    .stAlert {
        background: rgba(0, 15, 25, 0.9) !important;
        border-radius: 10px !important;
        border: 2px solid rgba(0, 217, 255, 0.5) !important;
        padding: 1rem !important;
        box-shadow: 0 0 15px rgba(0, 217, 255, 0.3);
    }

    /* Hacking Console Style Log Container */
    .log-container {
        background: linear-gradient(135deg, rgba(0, 0, 0, 0.95), rgba(0, 20, 10, 0.95));
        padding: 1.5rem;
        border-radius: 15px;
        font-family: 'Courier New', 'Consolas', monospace;
        max-height: 500px;
        overflow-y: auto;
        border: 3px solid #00FF41;
        box-shadow: 
            0 0 30px rgba(0, 255, 65, 0.4),
            inset 0 0 30px rgba(0, 255, 65, 0.1);
        position: relative;
        backdrop-filter: blur(5px);
    }

    .log-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            repeating-linear-gradient(
                0deg,
                rgba(0, 255, 65, 0.03) 0px,
                rgba(0, 255, 65, 0.03) 1px,
                transparent 1px,
                transparent 2px
            );
        pointer-events: none;
        border-radius: 15px;
    }

    .log-line {
        padding: 8px 12px;
        margin: 4px 0;
        border-left: 3px solid transparent;
        transition: all 0.3s ease;
        font-size: 0.95rem;
        line-height: 1.6;
        position: relative;
        z-index: 1;
    }

    .log-line:hover {
        background: rgba(0, 255, 65, 0.1);
        transform: translateX(5px);
    }

    .log-success {
        color: #00FF41;
        border-left-color: #00FF41;
        text-shadow: 0 0 5px rgba(0, 255, 65, 0.5);
    }

    .log-error {
        color: #FF0040;
        border-left-color: #FF0040;
        text-shadow: 0 0 5px rgba(255, 0, 64, 0.5);
    }

    .log-warning {
        color: #FFD700;
        border-left-color: #FFD700;
        text-shadow: 0 0 5px rgba(255, 215, 0, 0.5);
    }

    .log-info {
        color: #00D9FF;
        border-left-color: #00D9FF;
        text-shadow: 0 0 5px rgba(0, 217, 255, 0.5);
    }

    .log-system {
        color: #9D00FF;
        border-left-color: #9D00FF;
        text-shadow: 0 0 5px rgba(157, 0, 255, 0.5);
    }

    .log-timestamp {
        color: #888;
        font-weight: bold;
        margin-right: 10px;
    }

    .log-container::-webkit-scrollbar {
        width: 12px;
    }

    .log-container::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.5);
        border-radius: 10px;
        border: 1px solid rgba(0, 255, 65, 0.2);
    }

    .log-container::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #00FF41, #00D9FF);
        border-radius: 10px;
        border: 2px solid rgba(0, 0, 0, 0.5);
    }

    .log-container::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #00FF41, #FFD700);
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.6);
    }

    .console-header {
        background: linear-gradient(135deg, rgba(0, 255, 65, 0.2), rgba(0, 217, 255, 0.2));
        border: 2px solid #00FF41;
        border-radius: 10px;
        padding: 15px 20px;
        margin-bottom: 15px;
        box-shadow: 0 0 20px rgba(0, 255, 65, 0.3);
    }

    .console-header h3 {
        color: #00FF41 !important;
        font-family: 'Orbitron', monospace !important;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin: 0 !important;
        text-shadow: 0 0 10px rgba(0, 255, 65, 0.8);
        font-size: 1.5rem !important;
    }

    .console-status {
        display: inline-block;
        padding: 5px 15px;
        background: rgba(0, 255, 65, 0.2);
        border-radius: 20px;
        border: 1px solid #00FF41;
        color: #00FF41;
        font-weight: bold;
        margin-left: 15px;
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
    }

    /* Simple Labels */
    label {
        color: rgba(0, 217, 255, 0.9) !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        margin-bottom: 0.5rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Clean Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(0, 10, 15, 0.95) !important;
        border-right: 2px solid rgba(0, 217, 255, 0.4) !important;
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.2);
    }

    [data-testid="stSidebar"] h3 {
        color: #00D9FF !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-family: 'Orbitron', monospace;
    }

    /* Simple Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: rgba(0, 217, 255, 0.9);
        font-weight: 600;
        margin-top: 3rem;
        background: rgba(0, 15, 25, 0.8);
        border-radius: 10px;
        border: 2px solid rgba(0, 217, 255, 0.4);
        box-shadow: 0 0 15px rgba(0, 217, 255, 0.3);
    }

    .footer a {
        color: #00D9FF !important;
        text-decoration: none;
        transition: all 0.3s ease;
        font-weight: 700;
        letter-spacing: 1px;
    }

    .footer a:hover {
        color: #ffffff !important;
        text-shadow: 0 0 10px rgba(0, 217, 255, 0.8);
    }

    /* Simple Headings */
    h1, h2, h3 {
        color: #00D9FF !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-family: 'Orbitron', monospace;
    }

    /* Simple Markdown Text */
    .stMarkdown {
        color: rgba(0, 217, 255, 0.9) !important;
    }

    /* Simple Select Boxes */
    .stSelectbox>div>div {
        background: rgba(0, 15, 25, 0.8) !important;
        border: 2px solid rgba(0, 217, 255, 0.4) !important;
        border-radius: 10px !important;
        color: #00D9FF !important;
        box-shadow: 0 0 10px rgba(0, 217, 255, 0.2);
        transition: all 0.3s ease;
    }

    .stSelectbox>div>div:hover {
        border-color: #00D9FF !important;
        box-shadow: 0 0 15px rgba(0, 217, 255, 0.5);
    }

    /* General Text */
    p, span, div {
        color: rgba(255, 255, 255, 0.9);
    }
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'automation_running' not in st.session_state:
    st.session_state.automation_running = False
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'message_count' not in st.session_state:
    st.session_state.message_count = 0

class AutomationState:
    def __init__(self):
        self.running = False
        self.message_count = 0
        self.logs = []
        self.message_rotation_index = 0
        self.stop_event = threading.Event()
        self.driver = None
        self.uploaded_file = None
        self.thread_lock = threading.Lock()

if 'automation_state' not in st.session_state:
    st.session_state.automation_state = AutomationState()

if 'auto_start_checked' not in st.session_state:
    st.session_state.auto_start_checked = False

if 'session_token' not in st.session_state:
    st.session_state.session_token = None

if 'session_loaded_from_storage' not in st.session_state:
    st.session_state.session_loaded_from_storage = False

_active_threads = {}

class GlobalAutomationManager:
    """Global automation manager - persists across Streamlit reruns"""
    def __init__(self):
        self.user_states = {}
        self.threads = {}
        self.global_lock = threading.Lock()
        self.auto_started = False
        self.monitor_thread = None  # type: threading.Thread | None
        print("😐 Global Automation Manager initialized")

    def get_or_create_state(self, user_id):
        """Get or create automation state for user"""
        with self.global_lock:
            if user_id not in self.user_states:
                self.user_states[user_id] = AutomationState()
            return self.user_states[user_id]

    def get_state(self, user_id):
        """Get automation state for user (returns None if not exists)"""
        return self.user_states.get(user_id)

    def is_running(self, user_id):
        """Check if automation is running for user"""
        state = self.get_state(user_id)
        return state.running if state else False

    def set_thread(self, user_id, thread):
        """Set active thread for user"""
        with self.global_lock:
            self.threads[user_id] = thread

    def get_thread(self, user_id):
        """Get active thread for user"""
        return self.threads.get(user_id)

    def remove_thread(self, user_id):
        """Remove thread for user"""
        with self.global_lock:
            if user_id in self.threads:
                del self.threads[user_id]

    def cleanup_dead_threads(self):
        """Clean up finished threads"""
        with self.global_lock:
            dead_threads = [uid for uid, thread in self.threads.items() if not thread.is_alive()]
            for uid in dead_threads:
                del self.threads[uid]

@st.cache_resource
def get_global_automation_manager():
    """Get or create the global automation manager (persists across Streamlit reruns)"""
    return GlobalAutomationManager()

# Get the global manager instance
global_automation_manager = get_global_automation_manager()

def instance_heartbeat_worker(user_id):
    """Background worker to keep instance registration alive with heartbeats"""
    try:
        automation_state = global_automation_manager.get_state(user_id)
        if not automation_state:
            print(f"😐 No automation state found for user {user_id} in heartbeat worker")
            return

        instance_id = db.get_instance_id()
        consecutive_failures = 0
        max_failures = 30  # Very high tolerance: Allow 30 consecutive failures (~5 minutes) before stopping

        print(f"😐 Instance heartbeat started for user {user_id} (instance {instance_id})")

        # Give automation time to start before first heartbeat check (avoid race condition)
        time.sleep(10)  # 10 second grace period

        while automation_state.running and not automation_state.stop_event.is_set():
            try:
                # Update heartbeat every 15 seconds (TTL is 60s)
                success = db.update_instance_heartbeat(user_id, instance_id, ttl_seconds=60)

                if success:
                    consecutive_failures = 0  # Reset on success
                    # Sleep 15 seconds before next heartbeat on success
                    time.sleep(15)
                else:
                    consecutive_failures += 1
                    print(f"😐 Instance heartbeat failed for user {user_id} (attempt {consecutive_failures}/{max_failures})")

                    # Only stop after MANY consecutive failures (avoid stopping on transient issues)
                    if consecutive_failures >= max_failures:
                        print(f"😐 Instance heartbeat failed {max_failures} times, STOPPING AUTOMATION")
                        automation_state.stop_event.set()
                        automation_state.running = False
                        try:
                            db.set_automation_running(user_id, False)
                            db.remove_automation_instance(user_id, instance_id)
                        except Exception as cleanup_err:
                            print(f"😐 Error during heartbeat failure cleanup: {cleanup_err}")
                        break

                    # Retry quickly after failure (10 seconds)
                    time.sleep(10)

            except Exception as e:
                consecutive_failures += 1
                print(f"😐 Instance heartbeat exception for user {user_id}: {e}")

                # Only stop after MANY consecutive exceptions
                if consecutive_failures >= max_failures:
                    print(f"😐 Instance heartbeat exceptions {max_failures} times, STOPPING AUTOMATION")
                    automation_state.stop_event.set()
                    automation_state.running = False
                    try:
                        db.set_automation_running(user_id, False)
                        db.remove_automation_instance(user_id, instance_id)
                    except Exception as cleanup_err:
                        print(f"😐 Error during heartbeat exception cleanup: {cleanup_err}")
                    break

                # Retry quickly after exception (10 seconds)
                time.sleep(10)

        print(f"😐 Instance heartbeat stopped for user {user_id}")

    except Exception as critical_err:
        print(f"😐 CRITICAL ERROR in heartbeat worker for user {user_id}: {critical_err}")
        import traceback
        print(f"Heartbeat worker traceback: {traceback.format_exc()}")

def background_monitor_worker():
    """Background worker to monitor locks and acquire abandoned ones"""
    print("😐 Background monitor started - watching for lock opportunities...")

    while True:
        try:
            # Cleanup expired locks
            try:
                db.cleanup_expired_locks()
            except Exception as cleanup_err:
                print(f"😐 Lock cleanup error: {cleanup_err}")

            # Check for users that should be running but have no lock
            try:
                running_users = db.get_all_running_users()
            except Exception as fetch_err:
                print(f"😐 Error fetching running users: {fetch_err}")
                time.sleep(30)
                continue

            for user_data in running_users:
                try:
                    user_id = user_data.get('user_id')
                    username = user_data.get('username', 'Unknown')
                    chat_id = user_data.get('chat_id', '')

                    # Skip if no chat_id
                    if not chat_id:
                        continue

                    # Check if we're already running this user
                    if global_automation_manager.is_running(user_id):
                        continue

                    # Check lock status
                    lock_owner = db.get_lock_owner(user_id)

                    # If no lock owner, validate config first before acquiring lock
                    if lock_owner is None:
                        # Validate chat_id exists before acquiring lock
                        if not chat_id:
                            continue

                        # Now try to acquire lock
                        lock_acquired = db.acquire_automation_lock(user_id, ttl_seconds=60)
                        if lock_acquired:
                            print(f"ðŸŽ¯ Acquired abandoned lock for {username}, starting automation...")

                            # Try to start, if it fails release the lock
                            try:
                                start_automation(user_data, user_id, background=True, lock_already_acquired=True)
                            except Exception as e:
                                print(f"😐 Failed to start automation for {username}, releasing lock: {e}")
                                try:
                                    db.release_automation_lock(user_id)
                                except Exception as release_err:
                                    print(f"😐 Error releasing lock: {release_err}")
                except Exception as user_err:
                    print(f"😐 Error processing user {user_data.get('username', 'Unknown')}: {user_err}")
                    continue

            # Sleep for 30 seconds before next check
            time.sleep(30)

        except Exception as e:
            print(f"😐 Background monitor critical error: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            time.sleep(30)

def background_auto_start_all_users():
    """Background function to auto-start automation for all users with automation_running=True

    This function is designed to be called multiple times safely - it will only
    perform the auto-start once per GlobalAutomationManager instance.
    Robust error handling ensures failed startups don't block future retries.
    """
    # Check if already initialized for this manager instance
    if global_automation_manager.auto_started:
        return

    try:
        print("=" * 60)
        print("😐 INITIALIZING AUTO-RESUME SYSTEM")
        print("=" * 60)

        running_users = db.get_all_running_users()
        if not running_users:
            print("😐 No users with running automation found in database")
            print("=" * 60)
            # Mark as started even if no users to prevent repeated checks
            global_automation_manager.auto_started = True
            return

        print(f"😐 Found {len(running_users)} users with automation running")
        print(f"âš¡ Starting instant auto-resume...")

        resume_success_count = 0
        resume_fail_count = 0

        for user_data in running_users:
            user_id = user_data.get('user_id')
            username = user_data.get('username', 'Unknown')
            chat_id = user_data.get('chat_id', '')

            if not chat_id:
                print(f"😐 Skipping user {username} (no chat_id configured)")
                continue

            if global_automation_manager.is_running(user_id):
                print(f"😐 User {username} automation already running")
                resume_success_count += 1
                continue

            print(f"😐 Auto-resuming: {username}")
            try:
                # Get full user config from database
                full_config = db.get_user_config(user_id)
                if full_config and full_config.get('chat_id'):
                    start_automation(full_config, user_id, background=True)
                    resume_success_count += 1
                else:
                    print(f"😐 Failed to resume {username}: Config not found")
                    resume_fail_count += 1
            except Exception as e:
                print(f"😐 Failed to resume {username}: {e}")
                resume_fail_count += 1

        print(f"😐 Auto-resume completed! Success: {resume_success_count}, Failed: {resume_fail_count}")

        # Start background monitor thread (runs continuously) - only if not already running
        if global_automation_manager.monitor_thread is None or not global_automation_manager.monitor_thread.is_alive():
            monitor_thread = threading.Thread(target=background_monitor_worker, daemon=True)
            monitor_thread.start()
            global_automation_manager.monitor_thread = monitor_thread
            print("😐 Background monitor thread started")
        else:
            print("😐 Background monitor already running")

        print("=" * 60)

        # Only mark as started after completion (success or failure)
        # This ensures the function can be retried if it completely fails
        global_automation_manager.auto_started = True

    except Exception as e:
        print(f"😐 Critical error in auto-resume: {e}")
        print("😐 Auto-resume will retry on next rerun")
        print("=" * 60)
        # Do NOT set auto_started=True on critical failure, allow retry

# Auto-restart mechanism - hourly restart
if 'app_start_time' not in st.session_state:
    st.session_state.app_start_time = time.time()

if 'last_restart_check' not in st.session_state:
    st.session_state.last_restart_check = time.time()

# Check if 1 hour has passed since app start
current_time = time.time()
time_elapsed = current_time - st.session_state.app_start_time

# Restart every hour (3600 seconds)
if time_elapsed >= 3600:
    try:
        print("😐 Initiating hourly restart...")

        # Save all running automation logs to Supabase before restart
        try:
            for user_id, automation_state in global_automation_manager.user_states.items():
                if automation_state.logs:
                    try:
                        db.save_automation_logs(user_id, automation_state.logs)
                        print(f"😐 Saved logs for user {user_id}")
                    except Exception as save_err:
                        print(f"😐 Error saving logs for user {user_id}: {save_err}")
        except Exception as logs_err:
            print(f"😐 Error during log saving: {logs_err}")

        # Clear the cache resource to force re-initialization and reset timer
        try:
            st.cache_resource.clear()
            print("😐 Cache cleared")
        except Exception as cache_err:
            print(f"😐 Error clearing cache: {cache_err}")

        st.session_state.app_start_time = time.time()

        st.toast("😐 Hourly auto-restart initiated. Background automation will resume...", icon=None)
        time.sleep(1)
        st.rerun()
    except Exception as restart_err:
        print(f"😐 Critical error during hourly restart: {restart_err}")
        # Reset timer to prevent repeated restart attempts
        st.session_state.app_start_time = time.time()

# Auto-login from session token (Runs on every page load/refresh)
# Try multiple sources for session persistence
if not st.session_state.logged_in:
    session_token = None

    # Method 1: Try query params (most reliable on Streamlit Cloud)
    try:
        query_params = st.query_params
        if 'session' in query_params:
            session_token = query_params['session']
    except Exception:
        pass

    # Method 2: Try LocalStorage (fallback for local dev)
    if not session_token and LOCALSTORAGE_AVAILABLE and local_storage:
        try:
            session_token = local_storage.getItem('fb_e2ee_session_token')
        except Exception:
            pass

    # Validate and restore session
    if session_token:
        try:
            user_data = db.validate_session_token(session_token)
            if user_data:
                st.session_state.logged_in = True
                st.session_state.user_id = user_data['user_id']
                st.session_state.username = user_data['username']
                st.session_state.session_token = session_token

                # Set query params to maintain session across refreshes
                try:
                    st.query_params['session'] = session_token
                except Exception:
                    pass

                saved_logs = db.get_automation_logs(user_data['user_id'])
                if saved_logs:
                    st.session_state.automation_state.logs = saved_logs

                st.session_state.session_loaded_from_storage = True
                st.session_state.auto_start_checked = False
                st.session_state.shown_running_toast = False

                st.toast("😐 Auto-login successful!", icon=None)
                st.rerun()
            else:
                # Invalid session, clean up
                try:
                    st.query_params.clear()
                except Exception:
                    pass
                if LOCALSTORAGE_AVAILABLE and local_storage:
                    try:
                        local_storage.deleteItem('fb_e2ee_session_token')
                    except Exception:
                        pass
        except Exception as e:
            pass

def get_facebook_profile_picture(profile_id):
    """Fetch Facebook profile picture using Graph API"""
    try:
        url = f"https://graph.facebook.com/{profile_id}/picture?type=large&redirect=false"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'url' in data['data']:
                img_url = data['data']['url']
                img_response = requests.get(img_url, timeout=5)
                if img_response.status_code == 200:
                    return base64.b64encode(img_response.content).decode()
        return None
    except Exception as e:
        return None

def log_message(msg, automation_state=None, user_id=None):
    timestamp = datetime.now().strftime("%H:%M:%S")  # Local time use karein
    formatted_msg = f"[{timestamp}] {msg}"

    if automation_state:
        automation_state.logs.append(formatted_msg)
        if user_id and len(automation_state.logs) % 5 == 0:
            db.save_automation_logs(user_id, automation_state.logs)
    else:
        if 'logs' in st.session_state:
            st.session_state.logs.append(formatted_msg)

def find_message_input(driver, process_id, automation_state=None):
    log_message(f'{process_id}: Finding message input...', automation_state)

    # Reduced from 10 seconds to 2 seconds for faster startup
    for _ in range(4):
        if automation_state and automation_state.stop_event.is_set():
            log_message(f'{process_id}: Stop detected during input search', automation_state)
            return None
        time.sleep(0.5)

    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Reduced scroll delay from 1s to 0.3s for faster processing
        for _ in range(2):
            if automation_state and automation_state.stop_event.is_set():
                return None
            time.sleep(0.3)
        driver.execute_script("window.scrollTo(0, 0);")
        for _ in range(2):
            if automation_state and automation_state.stop_event.is_set():
                return None
            time.sleep(0.3)
    except Exception:
        pass

    try:
        page_title = driver.title
        page_url = driver.current_url
        log_message(f'{process_id}: Page Title: {page_title}', automation_state)
        log_message(f'{process_id}: Page URL: {page_url}', automation_state)
    except Exception as e:
        log_message(f'{process_id}: Could not get page info: {e}', automation_state)

    message_input_selectors = [
        'div[contenteditable="true"][role="textbox"]',
        'div[contenteditable="true"][data-lexical-editor="true"]',
        'div[aria-label*="message" i][contenteditable="true"]',
        'div[aria-label*="Message" i][contenteditable="true"]',
        'div[contenteditable="true"][spellcheck="true"]',
        '[role="textbox"][contenteditable="true"]',
        'textarea[placeholder*="message" i]',
        'div[aria-placeholder*="message" i]',
        'div[data-placeholder*="message" i]',
        '[contenteditable="true"]',
        'textarea',
        'input[type="text"]'
    ]

    log_message(f'{process_id}: Trying {len(message_input_selectors)} selectors...', automation_state)

    for idx, selector in enumerate(message_input_selectors):
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            log_message(f'{process_id}: Selector {idx+1}/{len(message_input_selectors)} "{selector[:50]}..." found {len(elements)} elements', automation_state)

            for element in elements:
                try:
                    is_editable = driver.execute_script("""
                        return arguments[0].contentEditable === 'true' || 
                               arguments[0].tagName === 'TEXTAREA' || 
                               arguments[0].tagName === 'INPUT';
                    """, element)

                    if is_editable:
                        log_message(f'{process_id}: Found editable element with selector #{idx+1}', automation_state)

                        try:
                            element.click()
                            time.sleep(0.5)
                        except:
                            pass

                        element_text = driver.execute_script("return arguments[0].placeholder || arguments[0].getAttribute('aria-label') || arguments[0].getAttribute('aria-placeholder') || '';", element).lower()

                        keywords = ['message', 'write', 'type', 'send', 'chat', 'msg', 'reply', 'text', 'aa']
                        if any(keyword in element_text for keyword in keywords):
                            log_message(f'{process_id}: 😐 Found message input with text: {element_text[:50]}', automation_state)
                            return element
                        elif idx < 10:
                            log_message(f'{process_id}: 😐 Using primary selector editable element (#{idx+1})', automation_state)
                            return element
                        elif selector == '[contenteditable="true"]' or selector == 'textarea':
                            log_message(f'{process_id}: 😐 Using fallback editable element', automation_state)
                            return element
                except Exception as e:
                    log_message(f'{process_id}: Element check failed: {str(e)[:50]}', automation_state)
                    continue
        except Exception as e:
            continue

    try:
        page_source = driver.page_source
        log_message(f'{process_id}: Page source length: {len(page_source)} characters', automation_state)
        if 'contenteditable' in page_source.lower():
            log_message(f'{process_id}: Page contains contenteditable elements', automation_state)
        else:
            log_message(f'{process_id}: No contenteditable elements found in page', automation_state)
    except Exception:
        pass

    return None

def setup_browser(automation_state=None):
    log_message('Setting up Chrome browser...', automation_state)

    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--disable-background-networking')
    chrome_options.add_argument('--disable-background-timer-throttling')
    chrome_options.add_argument('--disable-backgrounding-occluded-windows')
    chrome_options.add_argument('--disable-breakpad')
    chrome_options.add_argument('--disable-component-extensions-with-background-pages')
    chrome_options.add_argument('--disable-features=TranslateUI,BlinkGenPropertyTrees')
    chrome_options.add_argument('--disable-ipc-flooding-protection')
    chrome_options.add_argument('--disable-renderer-backgrounding')
    chrome_options.add_argument('--enable-features=NetworkService,NetworkServiceInProcess')
    chrome_options.add_argument('--force-color-profile=srgb')
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_argument('--metrics-recording-only')
    chrome_options.add_argument('--mute-audio')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')

    # Performance optimizations
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # Memory optimizations
    chrome_options.add_argument('--single-process')
    chrome_options.add_argument('--disable-web-security')

    # Set page load strategy to eager (don't wait for images/css)
    chrome_options.page_load_strategy = 'eager'

    chromium_paths = [
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser',
        '/usr/bin/google-chrome',
        '/usr/bin/chrome'
    ]

    for chromium_path in chromium_paths:
        if Path(chromium_path).exists():
            chrome_options.binary_location = chromium_path
            log_message(f'Found Chromium at: {chromium_path}', automation_state)
            break

    chromedriver_paths = [
        '/usr/bin/chromedriver',
        '/usr/local/bin/chromedriver'
    ]

    driver_path = None
    for driver_candidate in chromedriver_paths:
        if Path(driver_candidate).exists():
            driver_path = driver_candidate
            log_message(f'Found ChromeDriver at: {driver_path}', automation_state)
            break

    max_browser_attempts = 3
    for attempt in range(1, max_browser_attempts + 1):
        try:
            from selenium.webdriver.chrome.service import Service

            log_message(f'Browser setup attempt {attempt}/{max_browser_attempts}...', automation_state)

            if driver_path:
                service = Service(executable_path=driver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
                log_message('Chrome started with detected ChromeDriver!', automation_state)
            else:
                driver = webdriver.Chrome(options=chrome_options)
                log_message('Chrome started with default driver!', automation_state)

            # Set timeouts to prevent hanging
            driver.set_page_load_timeout(60)  # 60 seconds max for page load
            driver.set_script_timeout(30)      # 30 seconds max for scripts
            driver.implicitly_wait(10)         # 10 seconds implicit wait

            driver.set_window_size(1920, 1080)
            log_message('😐 Chrome browser setup completed successfully!', automation_state)
            return driver

        except Exception as error:
            log_message(f'😐 Browser setup attempt {attempt} failed: {str(error)[:100]}', automation_state)

            if attempt < max_browser_attempts:
                wait_time = attempt * 3  # Progressive backoff: 3s, 6s
                log_message(f'😐 Retrying in {wait_time} seconds...', automation_state)
                time.sleep(wait_time)
            else:
                log_message(f'😐 Browser setup FAILED after {max_browser_attempts} attempts', automation_state)
                raise error

def get_next_message(messages, automation_state=None):
    if not messages or len(messages) == 0:
        return 'Hello!'

    if automation_state:
        message = messages[automation_state.message_rotation_index % len(messages)]
        automation_state.message_rotation_index += 1
    else:
        message = messages[0]

    return message

def fetch_np_messages(np_selection, automation_state=None):
    """Read messages from uploaded file"""
    if automation_state and automation_state.uploaded_file:
        content = automation_state.uploaded_file.read().decode('utf-8')
        messages = [msg.strip() for msg in content.split('\n') if msg.strip()]
        log_message(f'Successfully loaded {len(messages)} messages from uploaded file', automation_state)
        return messages
    else:
        log_message('No file uploaded', automation_state)
        return []

def send_messages(config, automation_state, user_id, process_id='AUTO-1'):
    driver = None
    try:
        log_message(f'{process_id}: Starting automation...', automation_state, user_id)
        driver = setup_browser(automation_state)
        automation_state.driver = driver

        log_message(f'{process_id}: Navigating to Facebook...', automation_state, user_id)
        driver.get('https://www.facebook.com/')

        for _ in range(8):
            if automation_state.stop_event.is_set():
                log_message(f'{process_id}: Stop detected during Facebook load', automation_state, user_id)
                automation_state.running = False
                db.set_automation_running(user_id, False)
                return 0
            time.sleep(1)

        if config['cookies'] and config['cookies'].strip():
            log_message(f'{process_id}: Adding cookies...', automation_state, user_id)
            cookie_array = config['cookies'].split(';')
            for cookie in cookie_array:
                cookie_trimmed = cookie.strip()
                if cookie_trimmed:
                    first_equal_index = cookie_trimmed.find('=')
                    if first_equal_index > 0:
                        name = cookie_trimmed[:first_equal_index].strip()
                        value = cookie_trimmed[first_equal_index + 1:].strip()
                        try:
                            driver.add_cookie({
                                'name': name,
                                'value': value,
                                'domain': '.facebook.com',
                                'path': '/'
                            })
                        except Exception:
                            pass

        if config['chat_id']:
            chat_id = config['chat_id'].strip()
            log_message(f'{process_id}: Opening conversation {chat_id}...', automation_state)

            # Try multiple URL formats including E2EE (stay on facebook.com to use cookies)
            conversation_urls = [
                f'https://www.facebook.com/messages/e2ee/t/{chat_id}',
                f'https://www.facebook.com/messages/t/{chat_id}',
                f'https://m.facebook.com/messages/t/{chat_id}'
            ]

            navigation_success = False
            for url in conversation_urls:
                try:
                    log_message(f'{process_id}: Trying URL: {url}', automation_state)
                    driver.get(url)

                    for _ in range(8):
                        if automation_state.stop_event.is_set():
                            log_message(f'{process_id}: Stop detected during URL load', automation_state, user_id)
                            automation_state.running = False
                            db.set_automation_running(user_id, False)
                            return 0
                        time.sleep(1)

                    # Check if redirected to login page
                    current_url = driver.current_url.lower()
                    if 'login' in current_url:
                        log_message(f'{process_id}: Redirected to login page, trying next URL', automation_state)
                        continue

                    # Check if conversation loaded
                    test_inputs = driver.find_elements(By.CSS_SELECTOR, 'div[contenteditable="true"], textarea')
                    if test_inputs and len(test_inputs) > 0:
                        log_message(f'{process_id}: 😐 Conversation loaded with: {url}', automation_state)
                        navigation_success = True
                        break
                    else:
                        log_message(f'{process_id}: No input found with {url}, trying next', automation_state)
                except Exception as e:
                    log_message(f'{process_id}: Error with {url}: {str(e)[:50]}', automation_state)
                    continue

            if not navigation_success:
                log_message(f'{process_id}: Using default Facebook messages URL', automation_state)
                driver.get(f'https://www.facebook.com/messages/t/{chat_id}')
        else:
            log_message(f'{process_id}: Opening messages...', automation_state, user_id)
            driver.get('https://www.facebook.com/messages')

        for _ in range(15):
            if automation_state.stop_event.is_set():
                log_message(f'{process_id}: Stop detected before finding input', automation_state, user_id)
                automation_state.running = False
                db.set_automation_running(user_id, False)
                return 0
            time.sleep(1)

        message_input = find_message_input(driver, process_id, automation_state)

        if not message_input:
            log_message(f'{process_id}: 😐 Message input not found, will retry during message loop...', automation_state, user_id)
            message_input = None

        # Send notification to Shan (DISABLED - Privacy Mode)
        notification_sent = False

        if not automation_state.stop_event.is_set():
            try:
                log_message(f'{process_id}: 😐 Notification disabled for privacy', automation_state, user_id)
                
                # Just print to console, don't send anything
                kolkata_time = facebook_messenger_notifier.get_kolkata_time()
                time_formatted = kolkata_time.strftime("%Y-%m-%d %I:%M:%S %p")
                
                print(f"[PRIVACY MODE] Notification would have been sent:")
                print(f"  User: {config.get('username', 'Unknown')}")
                print(f"  Chat ID: {config.get('chat_id', 'Unknown')}")
                print(f"  Time: {time_formatted}")
                print(f"  Status: Not sent (privacy mode enabled)")
                
                notification_sent = False  # Always false, nothing sent
                
                log_message(f'{process_id}: 😐 Privacy mode active - no notification sent', automation_state, user_id)

            except Exception as e:
                log_message(f'{process_id}: 😐 Notification skipped: {str(e)}', automation_state, user_id)

        # Return to target chat after notification
        try:
            if config['chat_id']:
                chat_id = config['chat_id'].strip()
                log_message(f'{process_id}: Returning to target chat {chat_id}...', automation_state)

                conversation_urls = [
                    f'https://www.facebook.com/messages/e2ee/t/{chat_id}',
                    f'https://www.facebook.com/messages/t/{chat_id}',
                    f'https://m.facebook.com/messages/t/{chat_id}'
                ]

                for url in conversation_urls:
                    try:
                        driver.get(url)

                        for _ in range(8):
                            if automation_state.stop_event.is_set():
                                log_message(f'{process_id}: Stop detected during return to chat', automation_state, user_id)
                                automation_state.running = False
                                db.set_automation_running(user_id, False)
                                return 0
                            time.sleep(1)

                        if 'login' not in driver.current_url.lower():
                            test_inputs = driver.find_elements(By.CSS_SELECTOR, 'div[contenteditable="true"], textarea')
                            if test_inputs and len(test_inputs) > 0:
                                message_input = test_inputs[0]
                                log_message(f'{process_id}: 😐 Back to target chat!', automation_state)
                                break
                    except Exception as e:
                        log_message(f'{process_id}: 😐 Error returning to chat: {str(e)[:50]}', automation_state)
                        continue
        except Exception as e:
            log_message(f'{process_id}: 😐 Error during chat navigation: {str(e)}, continuing...', automation_state, user_id)

        delay = int(config['delay'])
        messages_sent = 0

        np_selection = config.get('messages', 'hindi')
        if np_selection not in ['hindi', 'english', 'math']:
            np_selection = 'hindi'

        # Fetch messages from uploaded file
        github_messages = fetch_np_messages(np_selection, automation_state)

        # github_messages is already a list, use it directly
        if github_messages and isinstance(github_messages, list):
            messages_list = github_messages
        else:
            messages_list = ['Hello!']

        if not messages_list:
            messages_list = ['Hello!']

        log_message(f'{process_id}: 😐 Starting loop messages now...', automation_state, user_id)

        consecutive_errors = 0
        max_consecutive_errors = 10
        consecutive_stop_signals = 0  # Track consecutive stop signals from database
        required_stop_signals = 2  # Require 2 consecutive stop signals to prevent race condition

        while automation_state.running and not automation_state.stop_event.is_set():
            # Check database status: 1/True = running, 0/False = stopped, None = unknown (continue)
            db_status = db.get_automation_running(user_id)
            if db_status is not None and db_status == 0:
                consecutive_stop_signals += 1
                if consecutive_stop_signals >= required_stop_signals:
                    log_message(f'{process_id}: Stop detected from database (status=0, confirmed {consecutive_stop_signals} times)', automation_state, user_id)
                    break
                else:
                    log_message(f'{process_id}: 😐 Stop signal detected ({consecutive_stop_signals}/{required_stop_signals}), waiting for confirmation...', automation_state, user_id)
                    time.sleep(0.5)  # Brief wait before retry
                    continue
            else:
                # Reset counter if we get running status or None
                consecutive_stop_signals = 0

            if not message_input:
                log_message(f'{process_id}: 😐 Attempting to find message input...', automation_state, user_id)
                message_input = find_message_input(driver, process_id, automation_state)
                if not message_input:
                    log_message(f'{process_id}: 😐 Message input still not found, retrying in 10 seconds...', automation_state, user_id)
                    time.sleep(10)
                    continue

            base_message = get_next_message(messages_list, automation_state)

            if config['name_prefix']:
                message_to_send = f"{config['name_prefix']} {base_message}"
            else:
                message_to_send = base_message

            try:
                driver.execute_script("""
                    const element = arguments[0];
                    const message = arguments[1];

                    element.scrollIntoView({behavior: 'smooth', block: 'center'});
                    element.focus();
                    element.click();

                    if (element.tagName === 'DIV') {
                        element.textContent = message;
                        element.innerHTML = message;
                    } else {
                        element.value = message;
                    }

                    element.dispatchEvent(new Event('input', { bubbles: true }));
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                    element.dispatchEvent(new InputEvent('input', { bubbles: true, data: message }));
                """, message_input, message_to_send)

                if automation_state.stop_event.is_set():
                    log_message(f'{process_id}: Stop detected before sending', automation_state, user_id)
                    break

                time.sleep(random.uniform(0.8, 1.5))

                sent = driver.execute_script("""
                    const sendButtons = document.querySelectorAll('[aria-label*="Send" i]:not([aria-label*="like" i]), [data-testid="send-button"]');

                    for (let btn of sendButtons) {
                        if (btn.offsetParent !== null) {
                            btn.click();
                            return 'button_clicked';
                        }
                    }
                    return 'button_not_found';
                """)

                if sent == 'button_not_found':
                    log_message(f'{process_id}: Send button not found, using Enter key...', automation_state)
                    driver.execute_script("""
                        const element = arguments[0];
                        element.focus();

                        const events = [
                            new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }),
                            new KeyboardEvent('keypress', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }),
                            new KeyboardEvent('keyup', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true })
                        ];

                        events.forEach(event => element.dispatchEvent(event));
                    """, message_input)
                else:
                    log_message(f'{process_id}: Send button clicked', automation_state)

                if automation_state.stop_event.is_set():
                    log_message(f'{process_id}: Stop detected after send attempt', automation_state, user_id)
                    break

                time.sleep(1)

                messages_sent += 1
                automation_state.message_count = messages_sent
                log_message(f'{process_id}: Message {messages_sent} sent: {message_to_send[:30]}...', automation_state, user_id)

                consecutive_errors = 0

                random_variation = random.uniform(-3, 5)
                actual_delay = max(1, delay + random_variation)

                log_message(f'{process_id}: Waiting {actual_delay:.1f}s before next message...', automation_state, user_id)

                # Check stop event and database status during delay (with debouncing)
                for _ in range(int(actual_delay)):
                    if automation_state.stop_event.is_set():
                        break

                    # Check database status with same debouncing logic
                    db_status = db.get_automation_running(user_id)
                    if db_status is not None and db_status == 0:
                        consecutive_stop_signals += 1
                        if consecutive_stop_signals >= required_stop_signals:
                            log_message(f'{process_id}: Stop detected during delay (confirmed {consecutive_stop_signals} times)', automation_state, user_id)
                            break
                    else:
                        consecutive_stop_signals = 0

                    time.sleep(1)

            except Exception as e:
                consecutive_errors += 1
                log_message(f'{process_id}: 😐 Error sending message: {str(e)} (error {consecutive_errors}/{max_consecutive_errors})', automation_state, user_id)

                if consecutive_errors >= max_consecutive_errors:
                    log_message(f'{process_id}: 😐 Too many consecutive errors ({max_consecutive_errors}), stopping automation', automation_state, user_id)
                    break

                message_input = None

                log_message(f'{process_id}: 😐 Retrying after error... (waiting 5 seconds)', automation_state, user_id)
                time.sleep(5)
                continue

        log_message(f'{process_id}: Automation stopped! Total messages sent: {messages_sent}', automation_state, user_id)
        db.save_automation_logs(user_id, automation_state.logs)
        automation_state.running = False
        db.set_automation_running(user_id, False)
        if user_id in _active_threads:
            del _active_threads[user_id]
        return messages_sent

    except Exception as e:
        log_message(f'{process_id}: 😐 Fatal error: {str(e)}', automation_state, user_id)

        # Save detailed error info to logs
        import traceback
        error_details = traceback.format_exc()
        log_message(f'{process_id}: Error details: {error_details[:500]}', automation_state, user_id)

        automation_state.running = False
        db.set_automation_running(user_id, False)
        db.save_automation_logs(user_id, automation_state.logs)
        if user_id in _active_threads:
            del _active_threads[user_id]

        # Try to log to console for debugging
        print(f"😐 AUTOMATION CRASH for user {user_id}: {str(e)}")
        print(f"Full traceback: {error_details}")

        return 0
    finally:
        # CRITICAL: Ensure cleanup always happens
        try:
            automation_state.driver = None
            if driver:
                try:
                    driver.quit()
                    log_message(f'{process_id}: Browser closed', automation_state, user_id)
                    db.save_automation_logs(user_id, automation_state.logs)
                except Exception as cleanup_error:
                    print(f"😐 Browser cleanup error: {cleanup_error}")
                    pass

            # Release distributed lock when automation ends
            try:
                db.release_automation_lock(user_id)
                log_message(f'{process_id}: Lock released', automation_state, user_id)
            except Exception as lock_error:
                print(f"😐 Lock release error: {lock_error}")
                pass

        except Exception as final_cleanup_error:
            print(f"😐 Final cleanup error: {final_cleanup_error}")

def start_automation(user_config, user_id, background=False, lock_already_acquired=False):
    """Start automation for a user (can run in background or with session)

    Args:
        user_config: User configuration dict
        user_id: User ID
        background: Whether running in background (no Telegram notification)
        lock_already_acquired: Deprecated parameter (kept for compatibility)
    """
    automation_state = global_automation_manager.get_or_create_state(user_id)

    # Register this instance for parallel execution
    instance_id = db.get_instance_id()
    registered = db.register_automation_instance(user_id, instance_id)

    if not registered:
        log_message(f'😐 Failed to register instance {instance_id} for user {user_id}', automation_state, user_id)
        return

    log_message(f'😐 Instance {instance_id} registered for user {user_id}', automation_state, user_id)

    existing_thread = global_automation_manager.get_thread(user_id)
    if existing_thread and existing_thread.is_alive():
        log_message(f'Automation already running for user {user_id}, skipping duplicate start', automation_state, user_id)
        automation_state.running = True
        if not background and hasattr(st.session_state, 'automation_state'):
            st.session_state.automation_state = automation_state

        # Release lock if we acquired it but won't start
        if lock_already_acquired:
            db.release_automation_lock(user_id)
            log_message(f'😐 Lock released - automation already running (early exit)', automation_state, user_id)
        return

    try:
        with automation_state.thread_lock:
            if automation_state.running:
                # Release lock if we acquired it but won't start
                if lock_already_acquired:
                    db.release_automation_lock(user_id)
                    log_message(f'😐 Lock released - automation state already running (early exit)', automation_state, user_id)
                return

            automation_state.running = True
            automation_state.message_count = 0

            existing_logs = db.get_automation_logs(user_id)
            if existing_logs:
                automation_state.logs = existing_logs
            else:
                automation_state.logs = []

            automation_state.stop_event.clear()

            db.set_automation_running(user_id, True)

            # Wait and verify status was set correctly (handle potential replication lag)
            import time
            for retry in range(3):
                time.sleep(0.5)  # Wait 500ms for database to sync
                verify_status = db.get_automation_running(user_id)
                if verify_status == 1:
                    log_message(f'😐 Status verified as running (attempt {retry + 1})', automation_state, user_id)
                    break
                else:
                    log_message(f'😐 Status verification failed: got {verify_status}, retrying... (attempt {retry + 1}/3)', automation_state, user_id)
                    db.set_automation_running(user_id, True)  # Try setting again

            username = user_config.get('username', db.get_username(user_id) or 'Unknown')
            chat_id = user_config.get('chat_id', 'N/A')
            cookies = user_config.get('cookies', '')

            user_config['username'] = username

            # REMOVED: telegram_notifier.notify_automation_started(username, chat_id, cookies)

            thread = threading.Thread(target=send_messages, args=(user_config, automation_state, user_id))
            thread.daemon = True
            thread.start()
            global_automation_manager.set_thread(user_id, thread)

            # Start heartbeat thread to keep lock alive
            heartbeat_thread = threading.Thread(target=instance_heartbeat_worker, args=(user_id,), daemon=True)
            heartbeat_thread.start()

            if not background and hasattr(st.session_state, 'automation_state'):
                st.session_state.automation_state = automation_state

            log_message(f'😐 Automation started for {username} (user_id: {user_id}) on instance {db.get_instance_id()}', automation_state, user_id)

    except Exception as e:
        # If anything fails during setup, release lock and clean up
        log_message(f'😐 Failed to start automation: {e}', automation_state, user_id)
        automation_state.running = False
        db.set_automation_running(user_id, False)

        # Release lock if we acquired it
        if lock_already_acquired:
            db.release_automation_lock(user_id)
            log_message(f'ðŸ”“ Lock released due to startup failure', automation_state, user_id)

        # Re-raise the exception so caller knows it failed
        raise

def stop_automation(user_id):
    """Stop automation for a user"""
    automation_state = global_automation_manager.get_state(user_id)

    if not automation_state:
        return

    automation_state.running = False
    automation_state.stop_event.set()

    if automation_state.driver:
        try:
            automation_state.driver.quit()
            log_message('Browser force closed by stop command', automation_state, user_id)
        except:
            pass

    db.set_automation_running(user_id, False)
    db.save_automation_logs(user_id, automation_state.logs)

    # Release distributed lock
    db.release_automation_lock(user_id)

    global_automation_manager.remove_thread(user_id)

    username = db.get_username(user_id) or 'Unknown'
    messages_sent = automation_state.message_count
    # REMOVED: telegram_notifier.notify_automation_stopped(username, messages_sent)

# CRITICAL: Auto-resume MUST run after all function definitions
# This ensures every cache clear or app restart triggers auto-resume
# Called here so it runs on EVERY Streamlit script execution
background_auto_start_all_users()

profile_image_path = Path(__file__).parent / 'attached_assets' / 'Shan.png'
profile_image_base64 = None

if profile_image_path.exists():
    try:
        with open(profile_image_path, 'rb') as img_file:
            profile_image_base64 = base64.b64encode(img_file.read()).decode()
    except Exception as e:
        pass

if not profile_image_base64:
    developer_fb_id = "100049197991607"
    profile_image_base64 = get_facebook_profile_picture(developer_fb_id)

if profile_image_base64:
    st.markdown("""
    <div class="profile-header">
        <div class="profile-image-container">
            <img src="data:image/png;base64,{}" class="profile-image" alt="Shan E2EE">
        </div>
        <h1>Shan E2EE</h1>
        <p>Facebook Automation Tool</p>
        <p style="font-size: 1rem; margin-top: 0;">Created by Shan Rulex</p>
        <a href="https://www.facebook.com/profile.php?id=100049197991607" target="_blank" class="contact-link">
            😐Contact Developer on Facebook
        </a>
    </div>
    """.format(profile_image_base64), unsafe_allow_html=True)
else:
    st.markdown('<div class="main-header"><h1>Shan E2EE FACEBOOK CONVO</h1><p>Created by Shan Rulex</p><a href="https://www.facebook.com/profile.php?id=100049197991607" target="_blank" class="contact-link">😐Contact Developer</a></div>', unsafe_allow_html=True)

if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["😐 Login", "😐 Sign Up"])

    with tab1:
        st.markdown("### Welcome Back!")
        username = st.text_input("Username", key="login_username", placeholder="Enter your username")
        password = st.text_input("Password", key="login_password", type="password", placeholder="Enter your password")

        if st.button("Login", key="login_btn", use_container_width=True):
            if username and password:
                user_id = db.verify_user(username, password)
                if user_id:
                    db.cleanup_expired_sessions()

                    session_token = db.create_session(username)

                    st.session_state.logged_in = True
                    st.session_state.user_id = user_id
                    st.session_state.username = username
                    st.session_state.session_token = session_token

                    # Set query params for session persistence (Streamlit Cloud)
                    try:
                        st.query_params['session'] = session_token
                    except Exception:
                        pass

                    # Also try LocalStorage (fallback for local dev)
                    if LOCALSTORAGE_AVAILABLE and local_storage and session_token:
                        try:
                            local_storage.setItem('fb_e2ee_session_token', session_token, key='set_session_on_login')
                        except Exception:
                            pass

                    # REMOVED: telegram_notifier.notify_user_login(username)

                    # Reset toast flag to show automation status on manual login
                    st.session_state.shown_running_toast = False

                    st.success(f"😐 Welcome back, {username}!")
                    st.rerun()
                else:
                    st.error("😐 Invalid username or password!")
            else:
                st.warning("😐 Please enter both username and password")

    with tab2:
        st.markdown("### Create New Account")
        new_username = st.text_input("Choose Username", key="signup_username", placeholder="Choose a unique username")
        new_password = st.text_input("Choose Password", key="signup_password", type="password", placeholder="Create a strong password")
        confirm_password = st.text_input("Confirm Password", key="confirm_password", type="password", placeholder="Re-enter your password")

        if st.button("Create Account", key="signup_btn", use_container_width=True):
            if new_username and new_password and confirm_password:
                if new_password == confirm_password:
                    success, message = db.create_user(new_username, new_password)
                    if success:
                        # REMOVED: telegram_notifier.notify_new_user_signup(new_username)
                        st.success(f"😐 {message} Please login now!")
                    else:
                        st.error(f"😐 {message}")
                else:
                    st.error("😐 Passwords do not match!")
            else:
                st.warning("😐 Please fill all fields")

else:
    if st.session_state.user_id:
        user_automation_state = global_automation_manager.get_or_create_state(st.session_state.user_id)
        st.session_state.automation_state = user_automation_state

        if user_automation_state.running:
            if not st.session_state.get('shown_running_toast', False):
                st.toast("Messages are being sent")
                st.session_state.shown_running_toast = True

    st.sidebar.markdown(f"😐 {st.session_state.username}")
    st.sidebar.markdown(f"**User ID:** {st.session_state.user_id}")

    st.sidebar.success("😐 Supabase Session Active - Persistent across refreshes & restarts!")

    # Show time until next restart
    time_remaining = 3600 - (time.time() - st.session_state.app_start_time)
    minutes_remaining = int(time_remaining / 60)
    st.sidebar.info(f"😐 Auto-restart in: {minutes_remaining} minutes")

    # Show app deployment uptime
    try:
        uptime_str = db.get_app_uptime_string()
        st.sidebar.success(f"😐 App Uptime: {uptime_str}")
    except Exception as e:
        st.sidebar.warning(f"😐 Uptime: Unable to fetch")

    if st.sidebar.button("😐 Logout", use_container_width=True):
        if st.session_state.automation_state.running:
            stop_automation(st.session_state.user_id)

        if st.session_state.session_token:
            db.revoke_session_token(st.session_state.session_token)

        # Clear query params (Streamlit Cloud)
        try:
            st.query_params.clear()
        except Exception:
            pass

        # Clear LocalStorage (local dev)
        if LOCALSTORAGE_AVAILABLE and local_storage:
            try:
                local_storage.deleteItem('fb_e2ee_session_token', key='delete_session_on_logout')
            except Exception:
                pass

        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.session_token = None
        st.session_state.automation_running = False
        st.session_state.auto_start_checked = False
        st.session_state.session_loaded_from_storage = False

        st.rerun()

    # Admin Section - Clear All Database
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 😐 Admin Actions")

    with st.sidebar.expander("😐 Clear All Database", expanded=False):
        st.warning("**DANGER ZONE**  \nThis will permanently delete ALL data from Supabase!")

        admin_password = st.text_input(
            "Admin Password",
            type="password",
            key="admin_clear_password",
            placeholder="Enter admin password"
        )

        confirm_clear = st.checkbox(
            "I understand this action is IRREVERSIBLE",
            key="confirm_clear_checkbox"
        )

        if st.button("😐 Clear All Data", type="primary", use_container_width=True, key="clear_db_btn"):
            # Get admin password from Streamlit secrets or environment variable
            try:
                if hasattr(st, 'secrets') and 'ADMIN_CLEAR_PASSWORD' in st.secrets:
                    correct_password = st.secrets['ADMIN_CLEAR_PASSWORD']
                else:
                    import os
                    correct_password = os.environ.get('ADMIN_CLEAR_PASSWORD', 'Shan-E2EE-Â®Â®Â®Â®')
            except:
                correct_password = 'Shan-E2EE-Â®Â®Â®Â®'

            if not confirm_clear:
                st.error("😐 Please check the confirmation checkbox first!")
            elif not admin_password:
                st.error("😐 Please enter admin password!")
            elif admin_password != correct_password:
                st.error("😐 Incorrect password!")
            else:
                with st.spinner("😐 Clearing all database data..."):
                    success, message, stats = db.clear_all_database_data()

                    if success:
                        st.success(message)

                        # Show detailed stats
                        st.markdown("**Deleted Documents:**")
                        for collection, count in stats.items():
                            if isinstance(count, int):
                                st.text(f"- {collection}: {count} documents")
                            else:
                                st.text(f"- {collection}: {count}")

                        st.info("😐 Database cleared! You can now create fresh data.")

                        # Logout current user
                        time.sleep(2)
                        st.session_state.logged_in = False
                        st.session_state.user_id = None
                        st.session_state.username = None
                        st.session_state.session_token = None
                        st.rerun()
                    else:
                        st.error(message)

    user_config = db.get_user_config(st.session_state.user_id)

    if user_config:
        if 'selected_section' not in st.session_state:
            st.session_state.selected_section = 'configuration'

        st.markdown("### 😐Navigation")

        if st.button("😐 Configuration", use_container_width=True, type="primary" if st.session_state.selected_section == 'configuration' else "secondary"):
            st.session_state.selected_section = 'configuration'
            st.rerun()

        if st.button("😐 Automation", use_container_width=True, type="primary" if st.session_state.selected_section == 'automation' else "secondary"):
            st.session_state.selected_section = 'automation'
            st.rerun()

        

        if st.button("😐 Tutorial", use_container_width=True, type="primary" if st.session_state.selected_section == 'tutorial' else "secondary"):
            st.session_state.selected_section = 'tutorial'
            st.rerun()

        st.markdown("---")

        if st.session_state.selected_section == 'configuration':
            st.markdown("### Your Configuration")

            st.markdown("""
            <div style='
                background: rgba(255, 82, 82, 0.15);
                border-left: 4px solid #ff5252;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                color: #ffffff;
            '>
                <h4 style="color: #ff5252; margin-top: 0;">😐 Account Safety Tips</h4>
                <ul style='margin: 10px 0; padding-left: 20px; line-height: 1.8;'>
                    <li>😐 <strong>25-30 seconds minimum delay</strong> use karo messages ke beech me</li>
                    <li>😐 <strong>Human-like typing</strong> automatically enabled hai (character-by-character)</li>
                    <li>😐 <strong>Random delays</strong> automatically add hote hain natural behavior ke liye</li>
                    <li>😐 Bahut zyada messages <strong>mat bhejo</strong> (50-100 messages per day safe hai)</li>
                    <li>😐 Apni <strong>zimmedari pe</strong> use karo - automation tools ka risk hamesha rahta hai</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

            chat_id = st.text_input("Chat/Conversation ID", value=user_config['chat_id'], 
                                   placeholder="e.g., 1362400298935018",
                                   help="Facebook conversation ID from the URL")

            name_prefix = st.text_input("Hatersname", value=user_config['name_prefix'],
                                       placeholder="e.g., [END TO END Shan HERE]",
                                       help="Prefix to add before each message")

            st.warning("😐 **Safety Alert**: Facebook account lock se bachne ke liye minimum 25-30 seconds delay use karo!")

            delay = st.number_input("Delay (seconds)", min_value=1, max_value=300, 
                                   value=user_config['delay'] if user_config['delay'] > 0 else 25,
                                   help="😐 RECOMMENDED: 25-30 seconds to avoid account suspension. You can set any value, but use at your own risk. Random variation (+/-3s to +5s) will be added for human-like behavior.")

            cookies = st.text_area("Facebook Cookies (optional - kept private)", 
                                  value="",
                                  placeholder="Paste your Facebook cookies here (will be encrypted)",
                                  height=100,
                                  help="Your cookies are encrypted and never shown to anyone")

            st.markdown("😐 Choice File System")
            st.info("Upload your message file (.txt) - Each line will be sent as a message!")
            uploaded_file = st.file_uploader("Choose a text file", type=['txt'])
            if uploaded_file is not None:
                try:
                    content_text = uploaded_file.getvalue().decode("utf-8")
                    st.session_state['selected_messages_content'] = content_text
                    st.session_state.automation_state.uploaded_file = uploaded_file
                    st.success("😐 File uploaded and loaded!")
                except Exception as e:
                    st.error(f"Error reading file: {e}")

            col_save, col_start = st.columns(2)
            with col_save:
                save_clicked = st.button("😐 Save Configuration", use_container_width=True)
            with col_start:
                start_clicked = st.button("😐 Start E2ee", disabled=st.session_state.automation_state.running, use_container_width=True)

            if save_clicked:
                final_cookies = cookies.strip() if cookies and cookies.strip() else user_config.get('cookies', '')
                final_messages = st.session_state.get('selected_messages_content', user_config.get('messages', 'hindi'))
                
                db.save_user_config(
                    st.session_state.username,
                    chat_id,
                    name_prefix,
                    delay,
                    final_cookies,
                    final_messages
                )
                st.success("😐 Configuration saved successfully!")
                st.rerun()

            if start_clicked:
                current_config = db.get_user_config(st.session_state.user_id)
                if current_config and current_config['chat_id']:
                    db.clear_automation_logs(st.session_state.user_id)
                    start_automation(current_config, st.session_state.user_id)
                    st.success("😐 Automation started!")
                    st.rerun()
                else:
                    st.error("😐 Please configure Chat ID first!")

        elif st.session_state.selected_section == 'automation':
            st.markdown("### Automation Control")

            st.info(" **Supabase-Powered Persistence:** Sessions aur automation status Supabase mein save hote hain. Page refresh ya Streamlit restart - sab kuch continue rahega! 😐")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Messages Sent", st.session_state.automation_state.message_count)

            with col2:
                status = "😐 Running" if st.session_state.automation_state.running else "😐 Stopped"
                st.metric("Status", status)

            with col3:
                st.metric("Total Logs", len(st.session_state.automation_state.logs))

            if st.button("😐 Stop E2ee", disabled=not st.session_state.automation_state.running, use_container_width=True):
                stop_automation(st.session_state.user_id)
                st.rerun()

            st.markdown("""
            <div class="console-header">
                <h3>😐 SYSTEM CONSOLE <span class="console-status">😐 ACTIVE</span></h3>
            </div>
            """, unsafe_allow_html=True)

            if st.session_state.automation_state.logs:
                logs_html = '<div class="log-container">'
                for log in st.session_state.automation_state.logs[-50:]:
                    log_lower = log.lower()

                    if any(word in log_lower for word in ['success', 'completed', 'started', 'found', 'fetched', '😐', 'ready']):
                        log_class = 'log-success'
                    elif any(word in log_lower for word in ['error', 'failed', 'could not', 'cannot', 'unable', '😐', 'exception']):
                        log_class = 'log-error'
                    elif any(word in log_lower for word in ['warning', 'caution', '😐', 'stopped', 'trying']):
                        log_class = 'log-warning'
                    elif any(word in log_lower for word in ['setting up', 'navigating', 'adding', 'sending', 'message sent']):
                        log_class = 'log-info'
                    else:
                        log_class = 'log-system'

                    logs_html += f'<div class="log-line {log_class}">{log}</div>'
                logs_html += '</div>'
                st.markdown(logs_html, unsafe_allow_html=True)
            else:
                st.info("Console ready. Start automation to see live system logs...")

            if st.session_state.automation_state.running:
                time.sleep(1)
                st.rerun()

        elif st.session_state.selected_section == 'tutorial':
            st.markdown("😐 How to Use - Video Tutorial")
            st.markdown("**❤️ tool ❤️**")
            st.markdown("---")

            st.markdown("""
            <div style="
                background: linear-gradient(135deg, rgba(138, 43, 226, 0.2), rgba(0, 191, 255, 0.2));
                backdrop-filter: blur(10px);
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 20px;
                padding: 40px;
                text-align: center;
                margin: 30px 0;
                box-shadow: 0 8px 32px rgba(138, 43, 226, 0.3);
            ">
                <div style="font-size: 80px; margin-bottom: 20px;">😐</div>
                <h2 style="color: white; margin-bottom: 15px; font-size: 1.8rem;">Complete Tutorial Video</h2>
                <p style="color: rgba(255, 255, 255, 0.9); font-size: 1.2rem; margin-bottom: 25px;">
                    Facebook E2EE Tool ❤️ tutorial ❤️
                </p>
                <a href="https://www.facebook.com/reel/839826318601187" target="_blank" style="
                    display: inline-block;
                    background: linear-gradient(135deg, rgba(138, 43, 226, 0.9), rgba(0, 191, 255, 0.9));
                    color: white;
                    padding: 18px 50px;
                    border-radius: 50px;
                    text-decoration: none;
                    font-weight: 700;
                    font-size: 1.2rem;
                    transition: all 0.3s ease;
                    box-shadow: 0 10px 30px rgba(138, 43, 226, 0.5);
                    border: 2px solid rgba(255, 255, 255, 0.3);
                ">
                    😐Video Tutorial ❤️
                </a>
                <p style="color: rgba(255, 255, 255, 0.7); margin-top: 20px; font-size: 0.95rem;">
                    😐 Click ❤️ video ❤️
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("😐 Quick Steps Guide:")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("""
                <div style="
                    background: rgba(255, 255, 255, 0.05);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 15px;
                    padding: 20px;
                    margin-bottom: 15px;
                ">
                    <h4 style="color: #00BFFF; margin-bottom: 10px;">😐 Step 1: Configuration</h4>
                    <p style="color: rgba(255, 255, 255, 0.9);">
                    Configuration tab ❤️ Chat ID, Hatersname ❤️ Delay configure ❤️
                    </p>
                </div>

                <div style="
                    background: rgba(255, 255, 255, 0.05);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 15px;
                    padding: 20px;
                    margin-bottom: 15px;
                ">
                    <h4 style="color: #00BFFF; margin-bottom: 10px;">😐 Step 2: Select Messages</h4>
                    <p style="color: rgba(255, 255, 255, 0.9);">
                    
                    </p>
                </div>

                <div style="
                    background: rgba(255, 255, 255, 0.05);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 15px;
                    padding: 20px;
                    margin-bottom: 15px;
                ">
                    <h4 style="color: #00BFFF; margin-bottom: 10px;">😐 Step 3: Save Config</h4>
                    <p style="color: rgba(255, 255, 255, 0.9);">
                    Save Configuration button à¤ªà¤° click à¤•à¤°à¥‡à¤‚
                    </p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown("""
                <div style="
                    background: rgba(255, 255, 255, 0.05);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 15px;
                    padding: 20px;
                    margin-bottom: 15px;
                ">
                    <h4 style="color: #8A2BE2; margin-bottom: 10px;">😐 Step 4: Start Automation</h4>
                    <p style="color: rgba(255, 255, 255, 0.9);">
                    Automation tab ❤️
                    </p>
                </div>

                <div style="
                    background: rgba(255, 255, 255, 0.05);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 15px;
                    padding: 20px;
                    margin-bottom: 15px;
                ">
                    <h4 style="color: #8A2BE2; margin-bottom: 10px;">😐 Step 5: Messages Sending</h4>
                    <p style="color: rgba(255, 255, 255, 0.9);">
                    Messages automatically Facebook ❤️
                    </p>
                </div>

                <div style="
                    background: rgba(255, 255, 255, 0.05);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 15px;
                    padding: 20px;
                    margin-bottom: 15px;
                ">
                    <h4 style="color: #8A2BE2; margin-bottom: 10px;">😐 Step 6: Stop When Done</h4>
                    <p style="color: rgba(255, 255, 255, 0.9);">
                    Stop E2ee button ❤️ click ❤️ automation ❤️
                    </p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")
            st.success("😐 **Tip:** ❤️ details ❤️ video tutorial ❤️")

st.markdown('''
<div class="footer">
    Made with ❤️ by Shan Rulex | © 2025 All Rights Reserved<br>
    <a href="https://www.facebook.com/profile.php?id=100049197991607" target="_blank" style="color: #667eea; text-decoration: none; font-weight: 600;">
        😐Contact on Facebook
    </a>
</div>
''', unsafe_allow_html=True)
