import streamlit as st
import os
import json
import datetime
import pandas as pd
from flask import Flask
from ui.document_upload import document_upload_bp
import threading

# === Import the login and logout functions from auth.py ===
from app.auth import login, logout

# === Import the voice functions ===
from voice.tts_engine import speak
from voice.stt_engine import listen
from core.document_indexer import search_knowledge_base
from core.config_manager import load_user_config, update_user_config
from utils.emergency import trigger_emergency
from core.reminder_manager import init_reminders, add_med_reminder, update_med_status, get_pending_reminders, load_reminders, init_community_events, get_upcoming_community_events, add_community_event
from core.calendar_manager import init_calendar, add_calendar_event, get_events_for_date, update_event_status
from core.reminder_manager import load_reminders
from db.database import get_last_n_conversations, add_post, get_recent_posts, get_conversations_by_date, get_conversations_by_keyword, log_conversation
from core.news_fetcher import fetch_top_headlines

def is_retrieval_request(text):
    retrieval_phrases = [
        "what was my previous conversation",
        "show my last 5 conversations",
        "what did i say last week",
        "show my conversation history",
        "show previous conversations",
        "what did i say before",
        "what did we discuss about",
        "what did i say about",
        "what did we talk about",
        "conversation about",
        "talked about",
        "mentioned about",
        "said about"
    ]
    return any(phrase in text.lower() for phrase in retrieval_phrases)

# === Initialize Flask app ===
def run_flask_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "dev_key")  # Required for session management
    # Register the document upload blueprint
    app.register_blueprint(document_upload_bp)
    # Ensure the upload folder exists
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'data', 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=False)

# === Streamlit app code starts here ===
st.set_page_config(page_title="Elder Assistant", page_icon="👴", layout="wide")

# === Initialize session state variables ===
if 'user' not in st.session_state:
    st.session_state.user = None
if 'pending_emergency' not in st.session_state:
    st.session_state.pending_emergency = False

# === Login/Logout functionality ===
if st.session_state.user is None:
    login()
# Remove the old logout button from sidebar since we now have it in top right

# === Main app interface ===
if st.session_state.user:
    # Add skip link for accessibility
    st.markdown("""
        <a href="#main-content" class="skip-link" style="position: absolute; left: -9999px; z-index: 9999;">
            Skip to main content
        </a>
    """, unsafe_allow_html=True)
    
    # Add logout button to top right
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        if st.session_state.user_type == "admin":
            st.title(f"🏢 Admin Dashboard - Welcome, {st.session_state.user}!")
        else:
            st.title(f"Welcome, {st.session_state.user}!")
    with col3:
        if st.button("🚪 Logout", key="top_logout"):
            logout()
            st.rerun()
    
    # === Emergency Alert System ===
    st.header("🚨 Emergency Alert System")
    if st.button("Trigger Emergency Alert"):
        st.session_state.pending_emergency = True
        st.warning("Emergency alert triggered! Please confirm.")
    
    if st.session_state.pending_emergency:
        st.warning("Emergency alert is pending confirmation!")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Confirm Emergency"):
                # Here you would implement the actual emergency response
                st.error("EMERGENCY ALERT SENT! Emergency services have been notified.")
                st.session_state.pending_emergency = False
        with col2:
            if st.button("Cancel Emergency"):
                st.session_state.pending_emergency = False
                st.success("Emergency alert canceled.")

# === Add viewport meta tag for mobile responsiveness ===
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
""", unsafe_allow_html=True)
# === Add viewport and PWA meta tags ===
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<link rel="manifest" href="/static/manifest.json">
<meta name="theme-color" content="#2196f3">
<script>
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/service-worker.js')
            .then(reg => console.log('Service Worker registered'))
            .catch(err => console.error('Service Worker registration failed:', err));
    }
</script>
""", unsafe_allow_html=True)

# === Load external CSS with dynamic font size ===
def load_css(file_path, font_size):
    with open(file_path) as f:
        css = f.read()
        # Inject dynamic font size
        css += f"\n:root {{ --font-size: {font_size}px; }}"
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# === Initialize calendar and reminders once ===
init_calendar()
init_reminders()
init_community_events()

# === Load user preferences ===
user_config = load_user_config()
font_size = user_config["font_size"]
speech_rate = user_config["speech_rate"]
voice_type = user_config["voice_type"]

# Load CSS with initial font size
load_css("static/main.css", font_size)

# === Initialize session state ===
st.session_state.setdefault("history", [])
st.session_state.setdefault("pending_emergency", False)
st.session_state.setdefault("conversation_context", {})
st.session_state.setdefault("med_reminders", [])
st.session_state.setdefault("todays_events", [])
st.session_state.setdefault("last_reload", datetime.datetime.now())

# === Refresh reminders and calendar with optimization ===
def reload_reminders_and_calendar():
    # Only reload if last reload was more than 60 seconds ago
    if (datetime.datetime.now() - st.session_state.last_reload).seconds > 60:
        try:
            # Load all reminders fresh from file
            reminders, next_id = load_reminders()
            st.session_state.med_reminders = reminders
            st.session_state.next_med_id = next_id
        except Exception:
            st.session_state.med_reminders = []
            st.session_state.next_med_id = 1

        try:
            today_str = datetime.date.today().strftime("%Y-%m-%d")
            st.session_state.todays_events = get_events_for_date(today_str) or []
        except Exception:
            st.session_state.todays_events = []

        st.session_state.last_reload = datetime.datetime.now()

reload_reminders_and_calendar()

# === Sidebar settings ===
with st.sidebar:
    st.header("📊 Quick Stats")
    
    med_count = len([m for m in st.session_state.med_reminders if m["status"] == "pending"])
    event_count = len([e for e in st.session_state.todays_events if e.get("status") in ("pending", "upcoming")])

    st.markdown(f"""
        <div class='sidebar-stat'>
            🩺 Pending Medications: {med_count}<br>
            📅 Today's Events: {event_count}
        </div>
    """, unsafe_allow_html=True)

    if st.button("🚨 Trigger Emergency Now"):
        st.session_state.pending_emergency = True

    st.markdown("""
        <div class='sidebar-tip'>
        💡 Tip: Stay positive! Regular interaction helps your well-being.
        </div>
    """, unsafe_allow_html=True)

    # === Add link to document upload page in sidebar ===
    st.markdown("---")
    st.markdown("### Document Upload")
    st.markdown("[Upload Documents](http://localhost:5000/upload)")

# === Main layout tabs ===
if st.session_state.user_type == "admin":
    # Admin-only interface
    admin_tabs = st.tabs(["📅 Manage Events", "👥 Resident Info", "📊 Reports", "⚙️ Admin Settings"])
else:
    # Regular user interface
    tabs = st.tabs(["Chat", "Voice Recording", "Community", "Health", "Settings"])

# === ADMIN INTERFACE ===
if st.session_state.user_type == "admin":
    # Events Management Tab
    with admin_tabs[0]:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.title("📅 Community Events Management")
        
        # Add new event form
        st.markdown("### ➕ Create New Event")
        with st.form("admin_add_event_form"):
            event_name = st.text_input("Event Name", key="admin_event_name")
            event_description = st.text_area("Description", key="admin_event_description")
            col1, col2 = st.columns(2)
            with col1:
                event_day = st.selectbox("Day", 
                                       ["Monday", "Tuesday", "Wednesday", "Thursday", 
                                        "Friday", "Saturday", "Sunday"], 
                                       key="admin_event_day")
            with col2:
                event_time = st.time_input("Time", key="admin_event_time")
            event_location = st.text_input("Location", key="admin_event_location")
            event_recurrence = st.selectbox("Recurrence", 
                                          ["weekly", "monthly", "one-time"], 
                                          key="admin_event_recurrence")
            
            if st.form_submit_button("🎉 Create Event"):
                if event_name.strip() and event_description.strip():
                    add_community_event(
                        event_name.strip(),
                        event_description.strip(),
                        event_day,
                        event_time.strftime("%H:%M"),
                        event_location.strip(),
                        event_recurrence
                    )
                    st.success(f"✅ Event '{event_name}' created successfully!")
                    st.rerun()
                else:
                    st.error("❌ Please fill in all required fields.")
        
        st.markdown("---")
        
        # Current events management
        st.markdown("### 📋 Current Events")
        events = get_upcoming_community_events()
        
        if events:
            for i, event in enumerate(events):
                with st.expander(f"🎪 {event['name']} - {event['day']} at {event['time']}"):
                    st.markdown(f"**Description:** {event['description']}")
                    st.markdown(f"**Location:** {event['location']}")
                    st.markdown(f"**Recurrence:** {event['recurrence']}")
                    st.markdown(f"**Status:** {event['status']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"✏️ Edit", key=f"edit_event_{event['id']}"):
                            st.info("Event editing feature coming soon!")
                    with col2:
                        if st.button(f"🗑️ Deactivate", key=f"deactivate_event_{event['id']}"):
                            st.warning("Event deactivation feature coming soon!")
        else:
            st.info("No active events found.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Resident Info Tab
    with admin_tabs[1]:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.title("👥 Resident Information")
        st.markdown("### 📊 System Usage Overview")
        
        # Mock resident data for demonstration
        st.markdown("#### Active Residents")
        resident_data = {
            "Total Residents": 45,
            "Active Users Today": 12,
            "Voice Interactions": 28,
            "Text Messages": 156,
            "Emergency Alerts": 0
        }
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Residents", resident_data["Total Residents"])
        with col2:
            st.metric("Active Today", resident_data["Active Users Today"])
        with col3:
            st.metric("Voice Interactions", resident_data["Voice Interactions"])
        with col4:
            st.metric("Text Messages", resident_data["Text Messages"])
        with col5:
            st.metric("Emergency Alerts", resident_data["Emergency Alerts"], delta="0")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Reports Tab
    with admin_tabs[2]:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.title("📊 Reports & Analytics")
        
        st.markdown("### 📈 Usage Statistics")
        # Mock data for demonstration
        chart_data = pd.DataFrame({
            'Day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'Voice Interactions': [15, 23, 18, 31, 28, 12, 8],
            'Text Messages': [45, 67, 52, 89, 76, 34, 23]
        })
        
        st.line_chart(chart_data.set_index('Day'))
        
        st.markdown("### 📋 Event Participation")
        event_participation = pd.DataFrame({
            'Event': ['Bingo Night', 'Movie Night', 'Exercise Class', 'Music Therapy'],
            'Participants': [23, 18, 15, 12]
        })
        
        st.bar_chart(event_participation.set_index('Event'))
        
        if st.button("📄 Generate Full Report"):
            st.info("Full report generation feature coming soon!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Admin Settings Tab
    with admin_tabs[3]:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.title("⚙️ Admin Settings")
        st.markdown(f"**Admin:** {st.session_state.user}")
        st.markdown(f"**Role:** {st.session_state.admin_role.replace('_', ' ').title()}")
        st.markdown("### System Configuration")
        st.info("Admin settings panel - coming soon!")
        st.markdown('</div>', unsafe_allow_html=True)

# === REGULAR USER INTERFACE ===
else:
    # === Chat Tab ===
    with tabs[0]:
        st.markdown('<div class="panel" id="main-content">', unsafe_allow_html=True)
        st.title("👵 Elder Assistant (Prototype)")
        st.markdown("### 👋 How can I assist you today?")

    # Add a button to retrieve previous conversations
    with st.expander("🔎 Retrieve Previous Conversations", expanded=False):
        if st.button("Show Last 5 Conversations", key="retrieve_convos"):
            last_convos = get_last_n_conversations(5)
            for ts, speaker, text in last_convos:
                st.markdown(f"**[{ts}] {speaker.capitalize()}:** {text}")

    st.markdown('<div class="chat-history" role="log" aria-label="Chat conversation history">', unsafe_allow_html=True)
    for entry in st.session_state.history:
        st.markdown(f"<div class='chat-message' role='article' aria-label='{entry['role']} message'><b>{entry['role']}:</b> {entry['text']}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Text-only chat interface
    user_input = st.text_input("You:", "", key="chat_input", placeholder="Type your message here...", 
                              help="Type your message and press Enter to send")

    send_button_clicked = st.button("Send")
    
    if send_button_clicked and user_input.strip():
        # Log user input to conversation history
        log_conversation("user", user_input)
        st.session_state.history.append({"role": "You", "text": user_input})
        if "i need help" in user_input.lower():
            st.session_state.pending_emergency = True
        elif is_retrieval_request(user_input):
            # Enhanced conversation recall with keyword and date extraction
            import re
            from datetime import datetime, timedelta
            
            # Extract keywords (look for "about X" patterns)
            keyword = None
            about_match = re.search(r'(?:about|regarding|concerning)\s+(\w+)', user_input.lower())
            if about_match:
                keyword = about_match.group(1)
            
            # Extract date references
            start_date = None
            end_date = None
            today = datetime.now().date()
            
            if "yesterday" in user_input.lower():
                yesterday = today - timedelta(days=1)
                start_date = yesterday.isoformat()
                end_date = yesterday.isoformat()
            elif "last week" in user_input.lower():
                week_ago = today - timedelta(days=7)
                start_date = week_ago.isoformat()
                end_date = today.isoformat()
            elif "today" in user_input.lower():
                start_date = today.isoformat()
                end_date = today.isoformat()
            
            # Search conversations based on extracted criteria
            if keyword and start_date and end_date:
                results = get_conversations_by_keyword(keyword, start_date, end_date)
                response = f"Here are conversations about '{keyword}' from {start_date} to {end_date}:\n"
            elif keyword:
                results = get_conversations_by_keyword(keyword)
                response = f"Here are all conversations about '{keyword}':\n"
            elif start_date and end_date:
                results = get_conversations_by_date(start_date, end_date)
                response = f"Here are conversations from {start_date} to {end_date}:\n"
            else:
                results = get_last_n_conversations(5)
                response = "Here are your last 5 conversations:\n"
            
            if results:
                for ts, speaker, text in results:
                    response += f"[{ts[:19].replace('T', ' ')}] {speaker.capitalize()}: {text}\n"
            else:
                if keyword:
                    response = f"No conversations found about '{keyword}'"
                    if start_date:
                        response += f" from {start_date} to {end_date}"
                else:
                    response = "No conversations found for the specified criteria."
            
            st.session_state.history.append({"role": "Assistant", "text": response})
            log_conversation("assistant", response)
            speak(response)
        else:
            response, ctx = search_knowledge_base(user_input, st.session_state.conversation_context)
            st.session_state.conversation_context = ctx
            st.session_state.history.append({"role": "Assistant", "text": response})
            log_conversation("assistant", response)
            speak(response)
            reload_reminders_and_calendar()
        st.rerun()  # Refresh to show new messages

    # === Voice Recording Tab ===
    with tabs[1]:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.title("🎤 Voice Recording")
        st.markdown("### 👂 Record Voice")
        st.info("💡 **How it works:** Click 'Start Recording', speak clearly when you see the 'Listening...' message, then optionally use AI to extract information from your recording.")
        
        # Initialize voice recordings if not exists
        if "voice_recordings" not in st.session_state:
            st.session_state.voice_recordings = []
        
        # Show current status
        recording_count = len(st.session_state.voice_recordings)
        if recording_count > 0:
            st.markdown(f"📊 **Current recordings:** {recording_count} stored")
        else:
            st.markdown("📊 **No recordings yet** - Start by clicking the microphone below")
        
        # Voice recording controls
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown("**🎙️ Ready to record:**")
            st.markdown("*Speak clearly and at normal volume*")
        
        with col2:
            # Enhanced recording button with better visual feedback
            recording_button = st.button(
                "🎤 Start Recording", 
                key="voice_record_button", 
                help="Click to record your voice (10 second limit)",
                type="primary"
            )
            
            if recording_button:
                # Pre-recording instructions
                st.info("🎤 **Recording starting...** Get ready to speak!")
                
                # Progress indicator during recording
                progress_container = st.empty()
                status_container = st.empty()
                
                with status_container:
                    st.markdown("🔴 **RECORDING NOW** - Speak clearly!")
                
                # Actually record
                spoken_text = listen()
                
                # Clear progress indicators
                progress_container.empty()
                status_container.empty()
                
                # Process results with better feedback
                if spoken_text and spoken_text != "Listening timed out." and spoken_text != "Sorry, I couldn't hear you.":
                    # Add recorded voice to list
                    recording_entry = {
                        "id": len(st.session_state.voice_recordings) + 1,
                        "text": spoken_text,
                        "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "ai_processed": False,
                        "ai_info": "",
                        "duration": "~10s",  # Approximate duration
                        "quality": "Good" if len(spoken_text) > 10 else "Short"
                    }
                    st.session_state.voice_recordings.append(recording_entry)
                    
                    # Enhanced success feedback
                    st.success("✅ **Recording successful!**")
                    with st.expander("🎯 Just recorded:", expanded=True):
                        st.markdown(f"**Text:** {spoken_text}")
                        st.markdown(f"**Length:** {len(spoken_text)} characters")
                        st.markdown("*Use 'Extract AI Info' below to analyze this recording*")
                    
                    st.rerun()
                else:
                    # Enhanced error feedback
                    if spoken_text == "Listening timed out.":
                        st.warning("⏱️ **Recording timed out** - No speech detected within 10 seconds.")
                        with st.expander("💡 Tips to improve recording:"):
                            st.markdown("• Speak immediately after clicking 'Start Recording'")
                            st.markdown("• Ensure your microphone is working")
                            st.markdown("• Speak clearly and at normal volume")
                    elif spoken_text == "Sorry, I couldn't hear you.":
                        st.error("❌ **Audio not clear** - Could not understand the recording.")
                        with st.expander("🔧 Troubleshooting:"):
                            st.markdown("• Check your microphone permissions")
                            st.markdown("• Move closer to your microphone")
                            st.markdown("• Reduce background noise")
                    else:
                        st.error(f"❌ **Unexpected error:** {spoken_text}")
                        st.markdown("*Please try recording again*")
        
        with col3:
            if st.button("🗑️ Clear Recordings", key="clear_voice_recordings", help="Clear all voice recordings"):
                st.session_state.voice_recordings = []
                st.success("Voice recordings cleared!")
                st.rerun()
        
        # Display recorded voices
        st.markdown("---")
        st.markdown("### 📝 Your Voice Recordings")
        
        if st.session_state.voice_recordings:
            for recording in st.session_state.voice_recordings:
                # Enhanced recording display with status indicators
                status_icon = "✅" if recording['ai_processed'] else "⏳"
                quality_icon = "🟢" if recording.get('quality', 'Good') == 'Good' else "🟡"
                
                with st.expander(f"{status_icon} Recording #{recording['id']} - {recording['timestamp']} {quality_icon}"):
                    # Recording details
                    col_info1, col_info2 = st.columns([2, 1])
                    with col_info1:
                        st.markdown(f"**📝 Recorded Text:** {recording['text']}")
                        st.markdown(f"**🕐 Duration:** {recording.get('duration', 'Unknown')}")
                    with col_info2:
                        st.markdown(f"**📊 Quality:** {recording.get('quality', 'Good')}")
                        st.markdown(f"**🔍 Status:** {'Processed' if recording['ai_processed'] else 'Waiting for AI'}")
                    
                    st.markdown("---")
                    
                    if not recording['ai_processed']:
                        # AI processing section
                        st.markdown("**🤖 AI Analysis Options:**")
                        col_ai1, col_ai2 = st.columns([2, 1])
                        
                        with col_ai1:
                            ai_button = st.button(
                                f"🤖 Extract AI Info", 
                                key=f"ai_process_{recording['id']}",
                                help="Analyze this recording with AI assistant",
                                type="secondary"
                            )
                            
                            if ai_button:
                                with st.spinner("🧠 AI is analyzing your recording..."):
                                    # Process with AI
                                    if "i need help" in recording['text'].lower():
                                        st.session_state.pending_emergency = True
                                        ai_response = "🚨 Emergency alert has been triggered based on your recording."
                                    elif is_retrieval_request(recording['text']):
                                        # Enhanced conversation recall for voice recordings
                                        import re
                                        from datetime import datetime, timedelta
                                        
                                        # Extract keywords (look for "about X" patterns)
                                        keyword = None
                                        about_match = re.search(r'(?:about|regarding|concerning)\s+(\w+)', recording['text'].lower())
                                        if about_match:
                                            keyword = about_match.group(1)
                                        
                                        # Extract date references
                                        start_date = None
                                        end_date = None
                                        today = datetime.now().date()
                                        
                                        if "yesterday" in recording['text'].lower():
                                            yesterday = today - timedelta(days=1)
                                            start_date = yesterday.isoformat()
                                            end_date = yesterday.isoformat()
                                        elif "last week" in recording['text'].lower():
                                            week_ago = today - timedelta(days=7)
                                            start_date = week_ago.isoformat()
                                            end_date = today.isoformat()
                                        elif "today" in recording['text'].lower():
                                            start_date = today.isoformat()
                                            end_date = today.isoformat()
                                        
                                        # Search conversations based on extracted criteria
                                        if keyword and start_date and end_date:
                                            results = get_conversations_by_keyword(keyword, start_date, end_date)
                                            ai_response = f"📚 Here are conversations about '{keyword}' from {start_date} to {end_date}:\n"
                                        elif keyword:
                                            results = get_conversations_by_keyword(keyword)
                                            ai_response = f"📚 Here are all conversations about '{keyword}':\n"
                                        elif start_date and end_date:
                                            results = get_conversations_by_date(start_date, end_date)
                                            ai_response = f"📚 Here are conversations from {start_date} to {end_date}:\n"
                                        else:
                                            results = get_last_n_conversations(5)
                                            ai_response = "📚 Here are your last 5 conversations:\n"
                                        
                                        if results:
                                            for ts, speaker, text in results:
                                                ai_response += f"[{ts[:19].replace('T', ' ')}] {speaker.capitalize()}: {text}\n"
                                        else:
                                            if keyword:
                                                ai_response = f"📚 No conversations found about '{keyword}'"
                                                if start_date:
                                                    ai_response += f" from {start_date} to {end_date}"
                                            else:
                                                ai_response = "📚 No conversations found for the specified criteria."
                                    else:
                                        ai_response, ctx = search_knowledge_base(recording['text'], st.session_state.conversation_context)
                                        st.session_state.conversation_context = ctx
                                    
                                    # Update recording with AI info
                                    for i, rec in enumerate(st.session_state.voice_recordings):
                                        if rec['id'] == recording['id']:
                                            st.session_state.voice_recordings[i]['ai_processed'] = True
                                            st.session_state.voice_recordings[i]['ai_info'] = ai_response
                                            break
                                    
                                    speak(ai_response)
                                    st.success("✅ AI analysis complete! Check below for results.")
                                    st.rerun()
                        
                        with col_ai2:
                            if st.button(f"🗑️ Delete", key=f"delete_{recording['id']}", help="Remove this recording"):
                                st.session_state.voice_recordings = [r for r in st.session_state.voice_recordings if r['id'] != recording['id']]
                                st.success("Recording deleted!")
                                st.rerun()
                    else:
                        # Processed recording display
                        st.markdown("**🤖 AI Analysis Results:**")
                        st.info(recording['ai_info'])
                        
                        col_actions1, col_actions2 = st.columns([2, 1])
                        with col_actions1:
                            if st.button(f"🔄 Re-analyze", key=f"reprocess_{recording['id']}", help="Process this recording again"):
                                # Reset AI processing status
                                for i, rec in enumerate(st.session_state.voice_recordings):
                                    if rec['id'] == recording['id']:
                                        st.session_state.voice_recordings[i]['ai_processed'] = False
                                        st.session_state.voice_recordings[i]['ai_info'] = ""
                                        break
                                st.info("Recording reset - you can now analyze it again!")
                                st.rerun()
                        
                        with col_actions2:
                            if st.button(f"🗑️ Delete", key=f"delete_processed_{recording['id']}", help="Remove this recording"):
                                st.session_state.voice_recordings = [r for r in st.session_state.voice_recordings if r['id'] != recording['id']]
                                st.success("Recording deleted!")
                                st.rerun()
        else:
            st.info("No voice recordings yet. Click 'Start Recording' to begin.")
        
        st.markdown("---")
        st.markdown("### 📋 Voice Recording Tips:")
        st.markdown("""
        - Speak clearly and at normal volume
        - Wait for the 'Listening...' indicator before speaking
        - Recording will timeout after 10 seconds of silence
        - Use 'Extract AI Info' to get AI analysis of your recording
        - Recordings are stored until you delete them or clear all
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    # === Community Tab ===
    with tabs[2]:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.title("👥 Community")
        
        # Sub-tabs for Community features
        community_tabs = st.tabs(["Social Feed", "Events", "Conversation Recall"])
        
        # Social Feed Sub-tab
        with community_tabs[0]:
            st.markdown("### 📱 Social Feed")
            st.markdown("Share updates and photos with your community!")

            # Display upcoming community events
            upcoming_events = get_upcoming_community_events()
            if upcoming_events:
                st.markdown("### 🎉 Upcoming Community Events")
                for event in upcoming_events:
                    st.markdown(f"""
                        <div style='border:1px solid #4CAF50; border-radius:8px; padding:12px; margin-bottom:8px; background:#E8F5E8;'>
                            <span style='font-size:16px; font-weight:bold; color:#2E7D32'>🎪 {event['name']}</span><br>
                            <span style='font-size:14px'>{event['description']}</span><br>
                            <span style='color:#666; font-size:12px'>📅 {event['day']} at {event['time']} | 📍 {event['location']}</span>
                        </div>
                    """, unsafe_allow_html=True)
                st.markdown("---")

            # Post form
            with st.form("post_form", clear_on_submit=True):
                post_text = st.text_area("What's on your mind?", max_chars=500)
                post_image = st.file_uploader("Upload a photo (optional)", type=["jpg", "jpeg", "png"], key="feed_image")
                submitted = st.form_submit_button("Post")
                if submitted:
                    image_path = None
                    if post_image is not None:
                        upload_dir = os.path.join("data", "uploads")
                        os.makedirs(upload_dir, exist_ok=True)
                        image_path = os.path.join(upload_dir, f"{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{post_image.name}")
                        with open(image_path, "wb") as f:
                            f.write(post_image.getbuffer())
                    author = st.session_state.user if st.session_state.user else "Anonymous"
                    add_post(author, post_text, image_path)
                    st.success("Your post has been shared!")

            # Display posts
            st.markdown("---")
            st.subheader("Recent Posts")
            posts = get_recent_posts(20)
            if posts:
                for ts, author, text, image_path in reversed(posts):
                    st.markdown(f"**{author}**  ")
                    st.markdown(f"<span style='color:gray;font-size:12px'>{ts[:19].replace('T',' ')}</span>", unsafe_allow_html=True)
                    if text:
                        st.markdown(f"{text}")
                    if image_path and os.path.exists(image_path):
                        st.image(image_path, width=350)
                    st.markdown("---")
            else:
                st.info("No posts yet. Be the first to share!")
        
        # Events Sub-tab
        with community_tabs[1]:
            st.markdown("### 📅 Community Events")
            st.markdown("View and manage community activities.")
            
            # Display all community events
            all_events = st.session_state.get("community_events", [])
            if all_events:
                for event in all_events:
                    if event["status"] == "active":
                        st.markdown(f"""
                            <div style='border:1px solid #ddd; border-radius:8px; padding:12px; margin-bottom:8px;'>
                                <span style='font-size:16px; font-weight:bold'>🎪 {event['name']}</span><br>
                                <span style='font-size:14px'>{event['description']}</span><br>
                                <span style='color:#666; font-size:12px'>📅 {event['day']} at {event['time']} | 📍 {event['location']}</span>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No community events scheduled.")
        
        # Conversation Recall Sub-tab
        with community_tabs[2]:
            st.markdown("### 🔎 Conversation Recall")
            st.markdown("Search your past conversations by date or keyword.")

            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start date", value=datetime.date.today())
            with col2:
                end_date = st.date_input("End date", value=datetime.date.today())
            keyword = st.text_input("Keyword (optional)", "")

            if st.button("Search Conversations"):
                if keyword.strip():
                    results = get_conversations_by_keyword(keyword.strip(), start_date.isoformat(), end_date.isoformat())
                else:
                    results = get_conversations_by_date(start_date.isoformat(), end_date.isoformat())
                if results:
                    for ts, speaker, text in results:
                        st.markdown(f"**[{ts[:19].replace('T',' ')}] {speaker.capitalize()}:** {text}")
                else:
                    st.info("No conversations found for the selected criteria.")

    # === Health Tab ===
    with tabs[3]:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.title("🏥 Health & Wellness")
        
        # Sub-tabs for Health features
        health_tabs = st.tabs(["Medications", "Calendar", "News"])
        
        # Medications Sub-tab
        with health_tabs[0]:
            st.markdown("## 💊 Medication Reminders")

        with st.form("add_reminder_form"):
            med_name = st.text_input("Medication Name", key="med_name")
            reminder_time = st.time_input("Reminder Time", value=datetime.time(9, 0), key="reminder_time")
            recurrence = st.selectbox("Repeat", ["none", "daily", "weekly"], key="recurrence")
            note = st.text_area("Notes (optional)", "", key="note")

            if st.form_submit_button("Add Reminder") and med_name.strip():
                add_med_reminder(
                    med_name.strip(),
                    reminder_time.strftime("%H:%M"),
                    recurrence=recurrence,
                    note=note.strip()
                )
                reload_reminders_and_calendar()
                st.success(f"Added reminder for {med_name} at {reminder_time.strftime('%H:%M')}")

        st.markdown("### 📋 All Reminders")
        for reminder in st.session_state.med_reminders:
            if reminder["status"] == "pending":
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown(f"**{reminder['med_name']}** at {reminder['time']}")
                    if reminder['note']:
                        st.markdown(f"*{reminder['note']}*")
                with col2:
                    if st.button("✅ Taken", key=f"taken_{reminder['id']}"):
                        update_med_status(reminder['id'], "taken")
                        reload_reminders_and_calendar()
                with col3:
                    if st.button("❌ Skipped", key=f"skipped_{reminder['id']}"):
                        update_med_status(reminder['id'], "skipped")
                        reload_reminders_and_calendar()
    
    # Calendar Sub-tab
    with health_tabs[1]:
        st.markdown("## 📅 Calendar")

        # Add new event
        with st.form("add_event_form"):
            event_title = st.text_input("Event Title", key="event_title")
            event_date = st.date_input("Event Date", key="event_date")
            event_time = st.time_input("Event Time", key="event_time")
            event_description = st.text_area("Description (optional)", key="event_description")

            if st.form_submit_button("Add Event") and event_title.strip():
                add_calendar_event(
                    event_title.strip(),
                    event_date.strftime("%Y-%m-%d"),
                    event_time.strftime("%H:%M"),
                    event_description.strip()
                )
                reload_reminders_and_calendar()
                st.success(f"Added event: {event_title}")

        # Display today's events
        st.markdown("### 📋 Today's Events")
        today_events = get_events_for_date(datetime.date.today().strftime("%Y-%m-%d"))
        if today_events:
            for event in today_events:
                if event.get("status") in ("pending", "upcoming"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{event['title']}** at {event['time']}")
                        if event.get('description'):
                            st.markdown(f"*{event['description']}*")
                    with col2:
                        if st.button("✅ Done", key=f"done_{event['id']}"):
                            update_event_status(event['id'], "completed")
                            reload_reminders_and_calendar()
        else:
            st.info("No events scheduled for today.")
    
    # News Sub-tab
    with health_tabs[2]:
        st.markdown("## 📰 Latest Health News (US)")
        # Topic/category selection
        categories = [
            "health", "wellness", "technology", "science", "sports", "business", "entertainment", "general"
        ]
        # Use saved defaults if available
        default_topic = st.session_state.get("default_news_topic", "health")
        default_state = st.session_state.get("default_news_state", "All States (General News)")
        selected_category = st.selectbox("News Topic", categories, index=categories.index(st.session_state.get("news_category", default_topic)),
                                        help="Select a news category to filter articles")
        st.session_state["news_category"] = selected_category

        # Show current state selection
        current_state = st.session_state.get("user_state", "All States (General News)")
        if current_state != "All States (General News)":
            st.info(f"📍 News will be filtered for: **{current_state}**")
        else:
            st.info("📍 Showing general US news (no state filter)")

        # Save as default button
        if st.button("Save as my default news topic and state", key="save_news_prefs", 
                     help="Save your current news preferences for future use"):
            st.session_state["default_news_topic"] = selected_category
            st.session_state["default_news_state"] = st.session_state.get("user_state", "All States (General News)")
            st.success(f"Saved {selected_category} and {st.session_state['default_news_state']} as your default news preferences.")

        if st.button("Fetch Top Headlines", key="fetch_news", help="Get the latest news articles"):
            state_arg = None if st.session_state.get("user_state") == "All States (General News)" else st.session_state.get("user_state")
            topic_arg = st.session_state.get("news_category", "health")
            news, error = fetch_top_headlines(state_arg, topic=topic_arg)
            if news:
                # Show what was searched
                search_info = f"📰 {topic_arg.title()} news"
                if state_arg:
                    search_info += f" for {state_arg}"
                st.success(f"{search_info} - Found {len(news)} articles")
                
                for idx, article in enumerate(news):
                    st.markdown(f"""
                        <div class='news-article' role='article' aria-label='News article {idx + 1}'>
                            <h3 style='font-size:18px; font-weight:bold; margin-bottom:8px;'>{article['title']}</h3>
                            <p style='color:gray; font-size:13px; margin-bottom:8px;'>Published: {article['publishedAt'][:10]}</p>
                            <p style='font-size:15px; margin-bottom:12px;'>{article['description']}</p>
                            <a href='{article['url']}' target='_blank' aria-label='Read full article: {article['title']}'>Read more</a>
                        </div>
                    """, unsafe_allow_html=True)
                    share_key = f"share_news_{idx}"
                    if st.button("Share to Feed", key=share_key, help=f"Share this article to your community feed"):
                        author = st.session_state.user if st.session_state.user else "Anonymous"
                        post_text = f"{article['title']}\n\n{article['description']}\n\nRead more: {article['url']}"
                        add_post(author, post_text)
                        st.success("Shared to your feed!")
            elif error:
                st.error(f"NewsAPI Error: {error}")
            else:
                st.info("No news found.")

    # === Settings Tab ===
    with tabs[4]:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.title("⚙️ Settings")
        
        # Sub-tabs for Settings
        settings_tabs = st.tabs(["Personal Info", "Personalization", "Face Login", "Document Upload"])
    
    # Personal Info Sub-tab
    with settings_tabs[0]:
        st.markdown("## 👤 Personal Information")
        if st.session_state.user:
            with st.form("personal_info_form"):
                name = st.text_input("Full Name", value=st.session_state.get("user_name", ""))
                age = st.number_input("Age", min_value=1, max_value=120, value=st.session_state.get("user_age", 65))
                emergency_contact = st.text_input("Emergency Contact", value=st.session_state.get("emergency_contact", ""))
                medical_conditions = st.text_area("Medical Conditions (optional)", value=st.session_state.get("medical_conditions", ""))
                
                if st.form_submit_button("Save Information"):
                    st.session_state.user_name = name
                    st.session_state.user_age = age
                    st.session_state.emergency_contact = emergency_contact
                    st.session_state.medical_conditions = medical_conditions
                    st.success("Personal information saved!")
        else:
            st.warning("Please log in to enter personal information.")
    
    # Personalization Sub-tab
    with settings_tabs[1]:
        st.markdown("## 🎛️ Personalize Your Experience")
        
        with st.form("personalization_form"):
            st.markdown("### Font and Text Settings")
            new_font_size = st.slider("Font Size", 12, 36, font_size, step=2, 
                                     help="Adjust the font size for better readability")
            if new_font_size != font_size:
                update_user_config("font_size", new_font_size)
                load_css("static/main.css", font_size)  # Reload CSS with new font size

            st.markdown("### Voice and Speech Settings")
            new_speech_rate = st.slider("Speech Rate", 0.5, 2.0, speech_rate, step=0.1,
                                       help="Adjust how fast the voice speaks")
            if new_speech_rate != speech_rate:
                update_user_config("speech_rate", new_speech_rate)

            new_voice_type = st.selectbox("Voice Type", ["default", "male", "female"],
                                          index=["default", "male", "female"].index(voice_type),
                                          help="Choose your preferred voice type")
            if new_voice_type != voice_type:
                update_user_config("voice_type", new_voice_type)

            st.markdown("### Location and News Settings")
            # Add state selection
            states = [
                "All States (General News)",
                "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia",
                "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts",
                "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico",
                "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina",
                "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
            ]
            selected_state = st.selectbox("Your State", states, 
                                         index=states.index(st.session_state.get("user_state", "All States (General News)")),
                                         help="Select your state to get local news and information")
            st.session_state["user_state"] = selected_state
            
            # Save personalization settings
            if st.form_submit_button("💾 Save Personalization Settings", 
                                   help="Save all your personalization preferences"):
                st.success("Personalization settings saved!")
    
    # Face Login Sub-tab
    with settings_tabs[2]:
        from app.face_auth import face_auth_tab
        face_auth_tab()
    
    # Document Upload Sub-tab
    with settings_tabs[3]:
        st.markdown("## 📄 Document Upload")
        st.markdown("Upload important documents for easy access.")
        st.markdown("[Upload Documents](http://localhost:5000/upload)")


# === Emergency confirmation ===
if st.session_state.pending_emergency:
    st.warning("🚨 Do you really want to trigger an emergency alert?")
    col1, col2 = st.columns([1, 1])  # Equal ratio for mobile
    with col1:
        if st.button("Yes, I need help!"):
            message = trigger_emergency()
            st.session_state.history.append({"role": "System", "text": message})
            speak("Emergency alert triggered. Help is on the way.")
            st.session_state.pending_emergency = False
    with col2:
        if st.button("Cancel"):
            st.session_state.pending_emergency = False
            st.success("Emergency alert canceled.")


# === Run Flask app in a separate thread ===
if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()
    # Streamlit runs automatically, no need to call st.run()