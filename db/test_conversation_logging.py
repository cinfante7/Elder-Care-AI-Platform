import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from voice.stt_engine import listen
from voice.tts_engine import speak
from db.database import get_connection

print("Say something (or wait for timeout)...")
user_text = listen(timeout=5)
print(f"User said: {user_text}")

response = f"You said: {user_text}"
print(f"Assistant will say: {response}")
speak(response)

# Print the last 5 conversation logs
conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT timestamp, speaker, text FROM conversations ORDER BY id DESC LIMIT 5")
rows = cursor.fetchall()
print("\nLast 5 conversation logs:")
for row in reversed(rows):
    print(f"[{row[0]}] {row[1]}: {row[2]}")
conn.close() 