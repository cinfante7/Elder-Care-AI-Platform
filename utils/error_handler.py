"""
Enhanced Error Handling and Stability Improvements
For Elder Assistant System Testing Phase
"""

import streamlit as st
import functools
import traceback
import logging
import os
from datetime import datetime

# Configure logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{log_dir}/elder_assistant.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def safe_execute(func_name="Unknown Function"):
    """Decorator for safe execution with error handling"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except FileNotFoundError as e:
                error_msg = f"File not found in {func_name}: {str(e)}"
                logger.error(error_msg)
                st.error(f"❌ **System Error:** Required file missing. Please contact support.")
                return None
            except PermissionError as e:
                error_msg = f"Permission denied in {func_name}: {str(e)}"
                logger.error(error_msg)
                st.error(f"❌ **Access Error:** Permission denied. Check file permissions.")
                return None
            except ConnectionError as e:
                error_msg = f"Connection error in {func_name}: {str(e)}"
                logger.error(error_msg)
                st.error(f"🌐 **Network Error:** Connection failed. Check your internet connection.")
                return None
            except Exception as e:
                error_msg = f"Unexpected error in {func_name}: {str(e)}"
                logger.error(error_msg)
                logger.error(traceback.format_exc())
                st.error(f"❌ **Unexpected Error:** Something went wrong. Error logged for support.")
                return None
        return wrapper
    return decorator

def validate_session_state():
    """Validate and fix session state issues"""
    required_keys = {
        'user': None,
        'user_type': None,
        'logged_in': False,
        'voice_recordings': [],
        'conversation_context': {},
        'history': []
    }
    
    issues_fixed = []
    
    for key, default_value in required_keys.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
            issues_fixed.append(f"Added missing session key: {key}")
    
    # Validate user_type consistency
    if st.session_state.get('logged_in', False) and not st.session_state.get('user_type'):
        st.session_state.user_type = "resident"  # Default assumption
        issues_fixed.append("Fixed missing user_type")
    
    # Validate voice recordings structure
    if not isinstance(st.session_state.get('voice_recordings', []), list):
        st.session_state.voice_recordings = []
        issues_fixed.append("Reset corrupted voice_recordings")
    
    if issues_fixed:
        logger.info(f"Session state issues fixed: {issues_fixed}")
        
    return len(issues_fixed) > 0

def check_system_prerequisites():
    """Check if all system prerequisites are met"""
    issues = []
    
    # Check critical files
    critical_files = [
        "data/admin_credentials.json",
        "data/config.json",
        "models/vosk-model-small-en-us-0.15",
        "db/elder_assistant.db"
    ]
    
    for file_path in critical_files:
        if not os.path.exists(file_path):
            issues.append(f"Missing: {file_path}")
    
    # Check write permissions
    try:
        test_file = "temp_write_test.tmp"
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
    except Exception:
        issues.append("No write permissions in project directory")
    
    return issues

@safe_execute("Voice Recording")
def safe_voice_recording():
    """Safe wrapper for voice recording functionality"""
    from voice.stt_engine import listen
    
    # Pre-recording checks
    if not os.path.exists("models/vosk-model-small-en-us-0.15"):
        st.error("❌ Voice model not found. Please contact administrator.")
        return None
    
    # Record with timeout handling
    try:
        result = listen()
        if result and result not in ["Listening timed out.", "Sorry, I couldn't hear you."]:
            logger.info(f"Successful recording: {len(result)} characters")
        return result
    except Exception as e:
        logger.error(f"Voice recording failed: {str(e)}")
        st.error("🎤 Recording failed. Please check your microphone settings.")
        return None

@safe_execute("AI Processing")
def safe_ai_processing(text, context):
    """Safe wrapper for AI knowledge base processing"""
    from core.document_indexer import search_knowledge_base
    
    if not text or len(text.strip()) == 0:
        return "No text to process.", context
    
    try:
        response, updated_context = search_knowledge_base(text, context)
        logger.info(f"AI processing successful for text: {text[:50]}...")
        return response, updated_context
    except Exception as e:
        logger.error(f"AI processing failed: {str(e)}")
        return "Sorry, I couldn't process that right now. Please try again.", context

@safe_execute("Database Operation")
def safe_database_operation(operation_func, *args, **kwargs):
    """Safe wrapper for database operations"""
    try:
        return operation_func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Database operation failed: {str(e)}")
        st.error("📊 Database error. Some features may not work properly.")
        return None

def display_system_status():
    """Display system health status to admins"""
    if st.session_state.get('user_type') == 'admin':
        issues = check_system_prerequisites()
        session_fixed = validate_session_state()
        
        if issues or session_fixed:
            with st.expander("🔧 System Status", expanded=False):
                if issues:
                    st.warning(f"⚠️ System Issues Detected ({len(issues)}):")
                    for issue in issues:
                        st.markdown(f"• {issue}")
                
                if session_fixed:
                    st.info("✅ Session state issues automatically fixed")
                
                st.markdown(f"**Last Check:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def log_user_action(action, details=None):
    """Log user actions for analytics and debugging"""
    user = st.session_state.get('user', 'Unknown')
    user_type = st.session_state.get('user_type', 'Unknown')
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'user': user,
        'user_type': user_type,
        'action': action,
        'details': details or {}
    }
    
    logger.info(f"User Action: {log_entry}")

# Error monitoring for testing phase
class TestingMetrics:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.user_actions = []
    
    def record_error(self, error_type, message, function_name):
        self.errors.append({
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'message': message,
            'function': function_name
        })
    
    def record_warning(self, message, function_name):
        self.warnings.append({
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'function': function_name
        })
    
    def record_user_action(self, action, success, duration=None):
        self.user_actions.append({
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'success': success,
            'duration': duration
        })
    
    def get_summary(self):
        return {
            'total_errors': len(self.errors),
            'total_warnings': len(self.warnings),
            'total_actions': len(self.user_actions),
            'success_rate': (
                sum(1 for action in self.user_actions if action['success']) / 
                len(self.user_actions) * 100 if self.user_actions else 0
            )
        }

# Global testing metrics instance
testing_metrics = TestingMetrics()