import streamlit as st
import face_recognition
import numpy as np
import os
from PIL import Image

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def save_encoding(username, encoding):
    np.save(os.path.join(DATA_DIR, f"{username}_face.npy"), encoding)

def load_encoding(username):
    path = os.path.join(DATA_DIR, f"{username}_face.npy")
    if os.path.exists(path):
        return np.load(path)
    return None

def face_auth_tab():
    st.header("Simple Live Webcam Face Recognition")

    username = st.text_input("Enter your username")
    mode = st.radio("Mode", ["Register", "Login"])

    if username:
        if mode == "Register":
            img_data = st.camera_input("Take a clear photo of your face")
            if img_data:
                img = Image.open(img_data)
                img_np = np.array(img)
                encodings = face_recognition.face_encodings(img_np)
                if encodings:
                    save_encoding(username, encodings[0])
                    st.success("Face registered successfully!")
                else:
                    st.error("No face detected in the captured photo.")
        else:
            img_data = st.camera_input("Take a photo to login")
            if img_data:
                img = Image.open(img_data)
                img_np = np.array(img)
                encodings = face_recognition.face_encodings(img_np)
                if encodings:
                    registered = load_encoding(username)
                    if registered is not None:
                        match = face_recognition.compare_faces([registered], encodings[0])[0]
                        if match:
                            st.success("Face match! Login successful.")
                        else:
                            st.error("Face does not match.")
                    else:
                        st.error("No registered face found for this user.")
                else:
                    st.error("No face detected in the captured photo.") 