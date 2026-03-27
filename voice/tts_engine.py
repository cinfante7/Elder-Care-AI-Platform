import subprocess
import os
import shlex
import sys
# Add import for conversation logger
from db.database import log_conversation

def speak(text):
    # Log system output
    log_conversation("system", text)
    # Temporarily disable TTS to avoid comtypes errors during testing
    print(f"[TTS DISABLED]: Would speak: {text}")
    return
    
    safe_text = shlex.quote(text)
    script_path = os.path.join(os.path.dirname(__file__), "speak_once.py")
    python_executable = sys.executable  

    try:
        subprocess.Popen([python_executable, script_path, safe_text])
    except Exception as e:
        print(f"[TTS ERROR]: {e}")
