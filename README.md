# AI-Powered Elder Care Platform (GRC-Aligned System)

## Overview
This project is a full-stack AI-powered platform designed to support elderly users through voice interaction, health management, social engagement, and administrative oversight.

It demonstrates system design concepts aligned with governance, risk, and compliance (GRC), including authentication, audit logging, monitoring, testing, and secure data handling.

## Features
- Multi-user authentication (Resident and Admin)
- Voice-enabled interaction (speech-to-text and text-to-speech)
- AI knowledge engine with contextual responses
- Conversation logging and retrieval
- Calendar and medication reminder management
- Community events and social feed
- Secure document upload workflow
- News API integration
- Progressive Web App support
- Accessibility-focused interface
- System monitoring, error handling, and automated testing

## Tech Stack
- Python
- Streamlit
- Flask
- SQLite
- Vosk
- pyttsx3
- pandas
- requests

## Project Structure
- `app/` authentication and access logic
- `core/` business logic and platform services
- `db/` database access and logging
- `voice/` speech input and output
- `ui/` upload routes
- `utils/` testing, monitoring, and error handling
- `docs/` project documentation
- `static/` PWA files
- `templates/` Flask HTML templates
- `data/` local sample/config data

## Setup

### 1. Install dependencies
    pip install -r requirements.txt

### 2. Create local config files
Inside the `data/` folder, copy and rename:

- `admin_credentials.sample.json` → `admin_credentials.json`
- `config.sample.json` → `config.json`
- `community_events.sample.json` → `community_events.json`
- `calendar_events.sample.json` → `calendar_events.json`
- `med_reminders.sample.json` → `med_reminders.json`
- `faq.sample.json` → `faq.json`

### 3. Create environment file
Create a file named `.env` in the root folder with:

    NEWSAPI_KEY=your_newsapi_key_here

### 4. Download voice model
Download from:
https://alphacephei.com/vosk/models

Extract into:

    models/vosk-model-small-en-us-0.15

### 5. Run the application

    streamlit run main.py

## Privacy Note
All sensitive data, credentials, logs, biometric files, and user-specific records have been removed or anonymized before publishing.

## Why This Project Matters
This project demonstrates the ability to design and manage systems that:
- Handle sensitive user data
- Implement access control and authentication
- Maintain audit trails and logging
- Monitor system health and performance
- Validate system functionality through testing
- Support secure file handling and user workflows

These are core components of governance, risk, and compliance (GRC), particularly in regulated environments such as healthcare.