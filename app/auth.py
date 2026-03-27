import streamlit as st
import hashlib
import face_recognition
import numpy as np
import os
import json
from PIL import Image

def hash_password(password):
    return hashlib.sha256(password.strip().encode('utf-8')).hexdigest()

# Set the correct SHA-256 hash for 'Secure@1234'
CORRECT_HASHED_PASSWORD = hash_password("demo_password")

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def save_encoding(username, encoding):
    np.save(os.path.join(DATA_DIR, f"{username}_face.npy"), encoding)

def load_encoding(username):
    path = os.path.join(DATA_DIR, f"{username}_face.npy")
    if os.path.exists(path):
        return np.load(path)
    return None

def login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "user_type" not in st.session_state:
        st.session_state.user_type = None

    if not st.session_state.logged_in:
        st.title("🔒 Secure Login")
        
        # User type selection
        user_type = st.radio("Login as:", ["👴 Resident", "🏢 Admin"])
        
        if user_type == "👴 Resident":
            login_method = st.radio("Choose login method", ["Password", "Face Recognition"])
            
            if login_method == "Password":
                password = st.text_input("Enter Password", type="password")
                if st.button("Login as Resident"):
                    if hash_password(password) == CORRECT_HASHED_PASSWORD:
                        st.session_state.logged_in = True
                        st.session_state.user = "resident"
                        st.session_state.user_type = "resident"
                        st.success("✅ Resident login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Incorrect password. Please try again.")
            else:
                username = st.text_input("Enter your username for face login")
                img_data = st.camera_input("Take a photo to login with your face")
                if img_data and username:
                    img = Image.open(img_data)
                    img_np = np.array(img)
                    encodings = face_recognition.face_encodings(img_np)
                    if encodings:
                        registered = load_encoding(username)
                        if registered is not None:
                            match = face_recognition.compare_faces([registered], encodings[0])[0]
                            if match:
                                st.success("Face match! Login successful.")
                                st.session_state.logged_in = True
                                st.session_state.user = username
                                st.session_state.user_type = "resident"
                                st.rerun()
                            else:
                                st.error("Face does not match.")
                        else:
                            st.error("No registered face found for this user.")
                    else:
                        st.error("No face detected in the captured photo.")
        
        else:  # Admin login
            st.markdown("### 🔐 Admin Login")
            admin_username = st.text_input("Admin Username", key="admin_login_username")
            admin_password = st.text_input("Admin Password", type="password", key="admin_login_password")
            
            if st.button("Login as Admin"):
                # Load admin credentials
                try:
                    with open("data/admin_credentials.json", "r") as f:
                        admin_creds = json.load(f)
                    
                    # Check credentials
                    authenticated = False
                    for user_id, user_data in admin_creds.items():
                        if (user_data["username"] == admin_username and 
                            user_data["password"] == admin_password):
                            st.session_state.logged_in = True
                            st.session_state.user = user_data["name"]
                            st.session_state.user_type = "admin"
                            st.session_state.admin_role = user_data["role"]
                            authenticated = True
                            st.success(f"✅ Welcome, Admin {user_data['name']}!")
                            st.rerun()
                            break
                    
                    if not authenticated:
                        st.error("❌ Invalid admin credentials. Please try again.")
                        
                except Exception as e:
                    st.error(f"❌ Admin login system error: {str(e)}")
        
        st.stop()  # Only stop if NOT logged in

def logout():
    st.session_state.user = None
    st.session_state.logged_in = False
    st.session_state.user_type = None
    if 'admin_role' in st.session_state:
        del st.session_state.admin_role

def logout_button():
    if st.sidebar.button("Logout"):
        logout()
