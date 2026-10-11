# Architecture and data flow

Source review baseline: `b2e5a8c24bb8a96060c6846294389969c4ff82bf`. Static inspection only.

| Input / boundary | Code path | Storage or destination | Limitation |
| --- | --- | --- | --- |
| Resident/admin UI | main.py → app/auth.py | Streamlit session state; local admin JSON | Demo authentication; role selection is not a complete authorization model |
| Text / transcribed speech | main.py, voice/stt_engine.py → core/document_indexer.py | Local sample FAQ; SQLite via db/database.py | Word-overlap FAQ matching; conversation records contain text and speaker, no owner ID |
| Reminders / calendar | core/reminder_manager.py, core/calendar_manager.py | Local JSON under data/ | Shared local persistence; no demonstrated tenant isolation |
| Preferences | core/config_manager.py | data/config.json | Global file, not per-user storage |
| Face registration / login | app/auth.py, app/face_auth.py | data/*_face.npy | Biometric persistence; privacy, consent, retention and protection unverified |
| Upload | ui/document_upload.py Flask blueprint | data/uploads/ | Flask session checks are separate from Streamlit login; extension checks do not establish safe content |
| Emergency confirmation | main.py, utils/emergency.py | UI state or data/emergency_log.txt | Simulation only; no SMS, email or emergency-service connector |
| News | core/news_fetcher.py | External HTTP request | Review configuration and third-party boundary before use |
| Admin metrics | main.py | Literal dict/DataFrame values | Synthetic examples; no operational monitoring evidence |

Trust boundaries include browser input, two separate framework sessions, local filesystem/SQLite, microphone/camera input, and external news requests. There is no evidence of a clinical deployment or emergency dispatch integration. Use only synthetic, non-sensitive inputs.

Conversation persistence is application history, not an independently protected security audit trail. Retention, deletion, encryption, access review and log integrity require design and validation before sensitive use.
