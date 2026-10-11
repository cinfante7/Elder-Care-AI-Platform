import datetime
import os

LOG_PATH = os.path.join("data", "emergency_log.txt")

def trigger_emergency(user="User"):
    """Logs a simulated event locally; does not contact emergency services."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"[{timestamp}] Simulated emergency event by {user}. No emergency services have been contacted.\n"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(message)
    return message
