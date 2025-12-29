"""
Simple JSON File Database Module
MongoDB ki jagah local JSON files use karta hai
Bot-hosting.net ke liye optimized
"""

import hashlib
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from pathlib import Path
import secrets
import os
import json
import uuid
import threading

DATA_DIR = Path(__file__).parent / 'data'
DATA_DIR.mkdir(exist_ok=True)

USERS_FILE = DATA_DIR / 'users.json'
SESSIONS_FILE = DATA_DIR / 'sessions.json'
CONFIGS_FILE = DATA_DIR / 'user_configs.json'
LOGS_FILE = DATA_DIR / 'automation_logs.json'
LOCKS_FILE = DATA_DIR / 'automation_locks.json'
INSTANCES_FILE = DATA_DIR / 'instances.json'

_file_lock = threading.Lock()

ENCRYPTION_KEY_FILE = Path(__file__).parent / '.encryption_key'

def get_encryption_key():
    """Get encryption key for cookie storage"""
    env_key = os.environ.get('ENCRYPTION_KEY')
    if env_key:
        if isinstance(env_key, str):
            env_key = env_key.encode('utf-8')
        print("Using shared encryption key from Environment Variable")
        return env_key
    
    if ENCRYPTION_KEY_FILE.exists():
        with open(ENCRYPTION_KEY_FILE, 'rb') as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(ENCRYPTION_KEY_FILE, 'wb') as f:
            f.write(key)
        print("Generated new encryption key")
        return key

ENCRYPTION_KEY = get_encryption_key()
cipher_suite = Fernet(ENCRYPTION_KEY)

def _load_json(file_path, default=None):
    """Load JSON file safely"""
    if default is None:
        default = {}
    try:
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
    return default

def _save_json(file_path, data):
    """Save JSON file safely"""
    try:
        with _file_lock:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        print(f"Error saving {file_path}: {e}")
        return False

def init_db():
    """Initialize database files"""
    DATA_DIR.mkdir(exist_ok=True)
    
    for file_path in [USERS_FILE, SESSIONS_FILE, CONFIGS_FILE, LOGS_FILE, LOCKS_FILE, INSTANCES_FILE]:
        if not file_path.exists():
            _save_json(file_path, {})
    
    print("Database initialized successfully!")
    return True

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def hash_token(token):
    """Hash session token using SHA-256"""
    return hashlib.sha256(token.encode()).hexdigest()

def create_user(username, password):
    """Create new user"""
    try:
        users = _load_json(USERS_FILE, {})
        
        for user_id, user in users.items():
            if user.get('username') == username:
                return False, "Username already exists!"
        
        password_hash = hash_password(password)
        user_id = str(uuid.uuid4())
        
        users[user_id] = {
            "username": username,
            "password_hash": password_hash,
            "created_at": datetime.utcnow().isoformat()
        }
        _save_json(USERS_FILE, users)
        
        configs = _load_json(CONFIGS_FILE, {})
        configs[user_id] = {
            "user_id": user_id,
            "chat_id": "",
            "name_prefix": "",
            "delay": 30,
            "cookies_encrypted": "",
            "messages": "",
            "automation_running": 0,
            "fb_profile_id": "",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        _save_json(CONFIGS_FILE, configs)
        
        print(f"User created: {username}")
        return True, "Account created successfully!"
    except Exception as e:
        print(f"Error creating user: {e}")
        return False, f"Error: {str(e)}"

def verify_user(username, password):
    """Verify user credentials and return user_id"""
    try:
        users = _load_json(USERS_FILE, {})
        password_hash = hash_password(password)
        
        for user_id, user in users.items():
            if user.get('username') == username and user.get('password_hash') == password_hash:
                return user_id
        return None
    except Exception as e:
        print(f"Error verifying user: {e}")
        return None

def get_user_id(username):
    """Get user ID from username"""
    try:
        users = _load_json(USERS_FILE, {})
        for user_id, user in users.items():
            if user.get('username') == username:
                return user_id
        return None
    except Exception as e:
        print(f"Error getting user ID: {e}")
        return None

def create_session(username):
    """Create session token for user"""
    try:
        user_id = get_user_id(username)
        if not user_id:
            return None
        
        token = secrets.token_urlsafe(32)
        token_hash = hash_token(token)
        expires_at = datetime.utcnow() + timedelta(days=7)
        
        sessions = _load_json(SESSIONS_FILE, {})
        sessions[token_hash] = {
            "user_id": user_id,
            "issued_at": datetime.utcnow().isoformat(),
            "expires_at": expires_at.isoformat(),
            "revoked": False
        }
        _save_json(SESSIONS_FILE, sessions)
        
        print(f"Session created for user: {username}")
        return token
    except Exception as e:
        print(f"Error creating session: {e}")
        return None

def verify_session(token):
    """Verify session token and return user data dict"""
    try:
        token_hash = hash_token(token)
        sessions = _load_json(SESSIONS_FILE, {})
        
        session = sessions.get(token_hash)
        if not session:
            return None
        
        if session.get('revoked'):
            return None
        
        expires_at = datetime.fromisoformat(session['expires_at'])
        if expires_at < datetime.utcnow():
            return None
        
        user_id = session['user_id']
        users = _load_json(USERS_FILE, {})
        user = users.get(user_id)
        
        if user:
            return {
                'user_id': user_id,
                'username': user['username']
            }
        return None
    except Exception as e:
        print(f"Error verifying session: {e}")
        return None

def revoke_session(token):
    """Revoke session token"""
    try:
        token_hash = hash_token(token)
        sessions = _load_json(SESSIONS_FILE, {})
        
        if token_hash in sessions:
            sessions[token_hash]['revoked'] = True
            _save_json(SESSIONS_FILE, sessions)
        return True
    except Exception as e:
        print(f"Error revoking session: {e}")
        return False

def revoke_session_token(token):
    """Alias for revoke_session"""
    return revoke_session(token)

def save_user_config(username, chat_id, name_prefix, delay, cookies_json, messages, fb_profile_id=""):
    """Save user configuration"""
    try:
        user_id = get_user_id(username)
        if not user_id:
            return False
        
        cookies_encrypted = cipher_suite.encrypt(cookies_json.encode()).decode()
        
        configs = _load_json(CONFIGS_FILE, {})
        configs[user_id] = {
            "user_id": user_id,
            "chat_id": chat_id,
            "name_prefix": name_prefix,
            "delay": delay,
            "cookies_encrypted": cookies_encrypted,
            "messages": messages,
            "fb_profile_id": fb_profile_id,
            "automation_running": configs.get(user_id, {}).get('automation_running', 0),
            "updated_at": datetime.utcnow().isoformat()
        }
        _save_json(CONFIGS_FILE, configs)
        
        print(f"Config saved for user: {username}")
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def get_user_config(user_id_or_username):
    """Get user configuration"""
    try:
        if not user_id_or_username:
            return None
            
        configs = _load_json(CONFIGS_FILE, {})
        
        if user_id_or_username in configs:
            user_id = user_id_or_username
        else:
            user_id = get_user_id(user_id_or_username)
        
        if not user_id or user_id not in configs:
            return None
        
        config = configs[user_id]
        
        try:
            if config.get('cookies_encrypted'):
                cookies_json = cipher_suite.decrypt(config['cookies_encrypted'].encode()).decode()
            else:
                cookies_json = ""
        except:
            cookies_json = ""
        
        return {
            'chat_id': config.get('chat_id', ''),
            'name_prefix': config.get('name_prefix', ''),
            'delay': config.get('delay', 30),
            'cookies': cookies_json,
            'messages': config.get('messages', ''),
            'automation_running': config.get('automation_running', 0),
            'fb_profile_id': config.get('fb_profile_id', '')
        }
    except Exception as e:
        print(f"Error getting config: {e}")
        return None

def set_automation_status(username, status):
    """Set automation running status"""
    return set_automation_running(get_user_id(username), status)

def set_automation_running(user_id, status):
    """Set automation running status"""
    try:
        configs = _load_json(CONFIGS_FILE, {})
        user_id_str = str(user_id)
        
        if user_id_str in configs:
            configs[user_id_str]['automation_running'] = 1 if status else 0
            configs[user_id_str]['updated_at'] = datetime.utcnow().isoformat()
            _save_json(CONFIGS_FILE, configs)
            print(f"User {user_id} automation status set to {status}")
            return True
        else:
            configs[user_id_str] = {
                "user_id": user_id_str,
                "automation_running": 1 if status else 0,
                "updated_at": datetime.utcnow().isoformat()
            }
            _save_json(CONFIGS_FILE, configs)
            return True
    except Exception as e:
        print(f"Error setting automation status: {e}")
        return False

def get_automation_running(user_id):
    """Get automation running status"""
    try:
        configs = _load_json(CONFIGS_FILE, {})
        user_id_str = str(user_id)
        
        if user_id_str in configs:
            return configs[user_id_str].get('automation_running', 0)
        return None
    except Exception as e:
        print(f"Error getting automation status: {e}")
        return None

def deduplicate_user_config(user_id):
    """No duplicates possible with dict structure"""
    return True

def get_username(user_id):
    """Get username from user ID"""
    try:
        users = _load_json(USERS_FILE, {})
        user = users.get(user_id)
        return user['username'] if user else None
    except Exception as e:
        print(f"Error getting username: {e}")
        return None

def get_all_running_users():
    """Get all users with automation running"""
    try:
        configs = _load_json(CONFIGS_FILE, {})
        running_users = []
        
        for user_id, config in configs.items():
            if config.get('automation_running') == 1:
                username = get_username(user_id)
                if username:
                    running_users.append({
                        'user_id': user_id,
                        'username': username,
                        'chat_id': config.get('chat_id', '')
                    })
        
        return running_users
    except Exception as e:
        print(f"Error getting running users: {e}")
        return []

def validate_session_token(token):
    """Alias for verify_session"""
    return verify_session(token)

def cleanup_expired_sessions():
    """Clean up expired sessions"""
    try:
        sessions = _load_json(SESSIONS_FILE, {})
        now = datetime.utcnow()
        
        expired_keys = []
        for token_hash, session in sessions.items():
            expires_at = datetime.fromisoformat(session['expires_at'])
            if expires_at < now:
                expired_keys.append(token_hash)
        
        for key in expired_keys:
            del sessions[key]
        
        _save_json(SESSIONS_FILE, sessions)
        return len(expired_keys)
    except Exception as e:
        print(f"Error cleaning up sessions: {e}")
        return 0

def get_automation_logs(user_id):
    """Get automation logs for user"""
    try:
        logs = _load_json(LOGS_FILE, {})
        user_logs = logs.get(str(user_id), {})
        logs_text = user_logs.get('logs', '')
        return logs_text.split('\n') if logs_text else []
    except Exception as e:
        print(f"Error getting logs: {e}")
        return []

def save_automation_logs(user_id, logs):
    """Save automation logs for user"""
    try:
        all_logs = _load_json(LOGS_FILE, {})
        logs_text = '\n'.join(logs) if isinstance(logs, list) else logs
        
        all_logs[str(user_id)] = {
            "logs": logs_text,
            "timestamp": datetime.utcnow().isoformat()
        }
        _save_json(LOGS_FILE, all_logs)
        return True
    except Exception as e:
        print(f"Error saving logs: {e}")
        return False

def clear_automation_logs(user_id):
    """Clear automation logs for user"""
    try:
        all_logs = _load_json(LOGS_FILE, {})
        if str(user_id) in all_logs:
            del all_logs[str(user_id)]
            _save_json(LOGS_FILE, all_logs)
        return True
    except Exception as e:
        print(f"Error clearing logs: {e}")
        return False

def get_instance_id():
    """Get or generate unique instance ID"""
    instance_file = Path(__file__).parent / '.instance_id'
    if instance_file.exists():
        with open(instance_file, 'r') as f:
            return f.read().strip()
    else:
        instance_id = str(uuid.uuid4())
        with open(instance_file, 'w') as f:
            f.write(instance_id)
        return instance_id

def acquire_automation_lock(user_id, instance_id=None, ttl_seconds=20):
    """Acquire automation lock"""
    try:
        if instance_id is None:
            instance_id = get_instance_id()
        
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=ttl_seconds)
        
        locks = _load_json(LOCKS_FILE, {})
        user_id_str = str(user_id)
        
        existing = locks.get(user_id_str)
        if existing:
            existing_expires = datetime.fromisoformat(existing['expires_at'])
            if existing_expires > now and existing['instance_id'] != instance_id:
                return False
        
        locks[user_id_str] = {
            "instance_id": instance_id,
            "acquired_at": now.isoformat(),
            "expires_at": expires_at.isoformat()
        }
        _save_json(LOCKS_FILE, locks)
        return True
    except Exception as e:
        print(f"Error acquiring lock: {e}")
        return False

def release_automation_lock(user_id, instance_id=None):
    """Release automation lock"""
    try:
        locks = _load_json(LOCKS_FILE, {})
        user_id_str = str(user_id)
        
        if user_id_str in locks:
            del locks[user_id_str]
            _save_json(LOCKS_FILE, locks)
        return True
    except Exception as e:
        print(f"Error releasing lock: {e}")
        return False

def cleanup_expired_locks():
    """Clean up expired automation locks"""
    try:
        locks = _load_json(LOCKS_FILE, {})
        now = datetime.utcnow()
        
        expired_keys = []
        for user_id, lock in locks.items():
            expires_at = datetime.fromisoformat(lock['expires_at'])
            if expires_at < now:
                expired_keys.append(user_id)
        
        for key in expired_keys:
            del locks[key]
        
        _save_json(LOCKS_FILE, locks)
        return len(expired_keys)
    except Exception as e:
        print(f"Error cleaning up locks: {e}")
        return 0

def update_lock_heartbeat(user_id, instance_id=None, ttl_seconds=20):
    """Update lock heartbeat"""
    try:
        if instance_id is None:
            instance_id = get_instance_id()
        
        locks = _load_json(LOCKS_FILE, {})
        user_id_str = str(user_id)
        
        if user_id_str in locks and locks[user_id_str]['instance_id'] == instance_id:
            now = datetime.utcnow()
            locks[user_id_str]['heartbeat_at'] = now.isoformat()
            locks[user_id_str]['expires_at'] = (now + timedelta(seconds=ttl_seconds)).isoformat()
            _save_json(LOCKS_FILE, locks)
            return True
        return False
    except Exception as e:
        print(f"Error updating heartbeat: {e}")
        return False

def get_lock_owner(user_id):
    """Get current lock owner for user"""
    try:
        locks = _load_json(LOCKS_FILE, {})
        user_id_str = str(user_id)
        
        lock = locks.get(user_id_str)
        if not lock:
            return None
        
        expires_at = datetime.fromisoformat(lock['expires_at'])
        if expires_at < datetime.utcnow():
            return None
        
        return lock['instance_id']
    except Exception as e:
        print(f"Error getting lock owner: {e}")
        return None

def register_automation_instance(user_id, instance_id=None):
    """Register automation instance"""
    try:
        if instance_id is None:
            instance_id = get_instance_id()
        
        instances = _load_json(INSTANCES_FILE, {})
        now = datetime.utcnow()
        
        instances[instance_id] = {
            "user_id": str(user_id),
            "registered_at": now.isoformat(),
            "heartbeat_at": now.isoformat(),
            "active": True
        }
        _save_json(INSTANCES_FILE, instances)
        return True
    except Exception as e:
        print(f"Error registering instance: {e}")
        return False

def update_instance_heartbeat(user_id, instance_id=None, ttl_seconds=60):
    """Update instance heartbeat"""
    try:
        if instance_id is None:
            instance_id = get_instance_id()
        
        instances = _load_json(INSTANCES_FILE, {})
        now = datetime.utcnow()
        
        if instance_id in instances:
            instances[instance_id]['heartbeat_at'] = now.isoformat()
            instances[instance_id]['active'] = True
            _save_json(INSTANCES_FILE, instances)
            return True
        return False
    except Exception as e:
        print(f"Error updating instance heartbeat: {e}")
        return False

def deactivate_automation_instance(user_id, instance_id=None):
    """Deactivate automation instance"""
    try:
        if instance_id is None:
            instance_id = get_instance_id()
        
        instances = _load_json(INSTANCES_FILE, {})
        
        if instance_id in instances:
            instances[instance_id]['active'] = False
            _save_json(INSTANCES_FILE, instances)
        return True
    except Exception as e:
        print(f"Error deactivating instance: {e}")
        return False

def register_global_instance_heartbeat(instance_id, role='secondary', ttl_seconds=20):
    """Register global instance heartbeat"""
    try:
        instances = _load_json(INSTANCES_FILE, {})
        now = datetime.utcnow()
        
        instances[instance_id] = {
            "role": role,
            "heartbeat_at": now.isoformat(),
            "expires_at": (now + timedelta(seconds=ttl_seconds)).isoformat(),
            "active": True
        }
        _save_json(INSTANCES_FILE, instances)
        return True
    except Exception as e:
        print(f"Error registering global heartbeat: {e}")
        return False

def deactivate_global_instance(instance_id):
    """Deactivate global instance"""
    try:
        instances = _load_json(INSTANCES_FILE, {})
        
        if instance_id in instances:
            instances[instance_id]['active'] = False
            _save_json(INSTANCES_FILE, instances)
        return True
    except Exception as e:
        print(f"Error deactivating global instance: {e}")
        return False

def check_primary_instance_alive():
    """Check if primary instance is alive"""
    try:
        instances = _load_json(INSTANCES_FILE, {})
        now = datetime.utcnow()
        
        for instance_id, instance in instances.items():
            if instance.get('role') == 'primary' and instance.get('active'):
                expires_at = datetime.fromisoformat(instance['expires_at'])
                if expires_at > now:
                    return True
        return False
    except Exception as e:
        print(f"Error checking primary instance: {e}")
        return False

def get_app_uptime():
    """Get app uptime data"""
    try:
        instances = _load_json(INSTANCES_FILE, {})
        uptime_data = instances.get('_app_uptime', {})
        
        if uptime_data and 'started_at' in uptime_data:
            return uptime_data['started_at']
        return None
    except Exception as e:
        print(f"Error getting app uptime: {e}")
        return None

def set_app_uptime():
    """Set app uptime start time"""
    try:
        instances = _load_json(INSTANCES_FILE, {})
        
        if '_app_uptime' not in instances or 'started_at' not in instances.get('_app_uptime', {}):
            instances['_app_uptime'] = {
                "started_at": datetime.utcnow().isoformat()
            }
            _save_json(INSTANCES_FILE, instances)
        return True
    except Exception as e:
        print(f"Error setting app uptime: {e}")
        return False

def remove_automation_instance(user_id, instance_id=None):
    """Remove automation instance (alias for deactivate)"""
    return deactivate_automation_instance(user_id, instance_id)

def get_app_uptime_string():
    """Get app uptime as formatted string"""
    try:
        started_at = get_app_uptime()
        if not started_at:
            set_app_uptime()
            return "Just started"
        
        start_time = datetime.fromisoformat(started_at)
        now = datetime.utcnow()
        delta = now - start_time
        
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0 or not parts:
            parts.append(f"{minutes}m")
        
        return " ".join(parts)
    except Exception as e:
        print(f"Error getting uptime string: {e}")
        return "Unknown"

def clear_all_database_data():
    """Clear all database data (DANGEROUS - for admin use only)"""
    try:
        for file_path in [USERS_FILE, SESSIONS_FILE, CONFIGS_FILE, LOGS_FILE, LOCKS_FILE, INSTANCES_FILE]:
            if file_path.exists():
                _save_json(file_path, {})
        print("All database data cleared!")
        return True
    except Exception as e:
        print(f"Error clearing database: {e}")
        return False

init_db()
print("Using JSON file database for data storage")
