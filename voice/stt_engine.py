import queue
import sounddevice as sd
import vosk
import json
import os
import time
# Add import for conversation logger
from db.database import log_conversation

MODEL_PATH = "models/vosk-model-small-en-us-0.15"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Vosk model not found at {MODEL_PATH}")

model = vosk.Model(MODEL_PATH)
q = queue.Queue()

def callback(indata, frames, time_, status):
    if status:
        print(f"Audio status: {status}")
    q.put(bytes(indata))

def listen(timeout=10):
    """Record from mic and return transcribed text (blocking)."""
    try:
        # Check model availability first
        if not model:
            print("❌ Voice model not loaded")
            return "Voice model not available."
        
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                               channels=1, callback=callback):
            rec = vosk.KaldiRecognizer(model, 16000)
            print("🎤 Listening... Speak now.")
            start_time = time.time()

            while True:
                current_time = time.time()
                elapsed = current_time - start_time
                
                # Show progress every 2 seconds
                if int(elapsed) % 2 == 0 and elapsed > 0:
                    remaining = max(0, timeout - elapsed)
                    print(f"🔴 Recording... {remaining:.0f}s remaining")
                
                if elapsed > timeout:
                    print("⏱️ Recording timeout reached.")
                    return "Listening timed out."

                try:
                    data = q.get(timeout=1)  # Add timeout to prevent infinite blocking
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        text = result.get("text", "").strip()
                        
                        if text:
                            print(f"✅ Transcription successful: '{text}' ({len(text)} chars)")
                            # Log user input with error handling
                            try:
                                log_conversation("user", text)
                            except Exception as log_error:
                                print(f"⚠️ Logging failed: {log_error}")
                            
                            return text.lower()
                        
                except queue.Empty:
                    continue  # No audio data yet, continue listening
                    
    except OSError as e:
        print(f"❌ Audio device error: {e}")
        return "Audio device not available. Please check your microphone."
    except Exception as e:
        print(f"❌ Microphone error: {e}")
        return "Sorry, I couldn't hear you."
