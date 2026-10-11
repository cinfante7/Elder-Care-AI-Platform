# Elder Care Assistant — educational prototype

A Python/Streamlit portfolio project exploring voice interaction, reminders, conversation recall, and an admin interface. The assistant matches words against a local sample FAQ; this is not evidence of a deployed clinical AI system.

**Simulation only.** Emergency controls do not contact emergency services. Dashboard counts and charts are hardcoded demonstration data. Do not use this prototype for medical decisions, emergency response, or real patient information.

## Implemented components and limits

- Streamlit resident/admin interface branches; these are not proof of enforced authorization across data and routes.
- SQLite conversation and post storage; conversation queries have no user ownership filter.
- Local JSON reminders and settings, Vosk speech recognition, and pyttsx3 speech output.
- Flask document upload route with extension checks and filename sanitization; end-to-end session integration is unverified.
- Local emergency event logging in one confirmation path; another path only displays a simulation message.
- Manifest assets exist, but `static/service-worker.js` contains manifest JSON. Offline operation is unverified.

## GRC evidence

[Architecture and data flow](docs/ARCHITECTURE.md), [control evidence](docs/CONTROL_EVIDENCE.md), [risk register](docs/RISK_REGISTER.md), and [validation instructions](docs/VALIDATION.md) distinguish observed code, gaps, and proposed acceptance criteria. This repository does not establish HIPAA compliance, audited security, WCAG conformance, production readiness, or clinical effectiveness.

## Local setup — unverified prerequisites

Use an isolated local environment with synthetic content only. No setup or runtime test was executed in this documentation pass.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The current requirements file is incomplete: `app/auth.py` unconditionally imports `face_recognition`, NumPy, and Pillow. Face recognition may require platform-specific native build dependencies. Resolve those prerequisites before attempting startup; this pass does not certify a working installation.

`voice/stt_engine.py` loads `models/vosk-model-small-en-us-0.15` during import; download the appropriate Vosk model separately. Review sample JSON files and [admin setup](docs/ADMIN_SETUP.md) before creating ignored local configuration. Demo authentication is unsuitable for real users or sensitive data; do not reuse personal credentials or register real biometric data.

After prerequisites are independently resolved, the intended entry point from the repository root is:

```powershell
streamlit run main.py
```

See [validation](docs/VALIDATION.md) for safe source checks and the limits of legacy test utilities. The [historical testing guide](docs/TESTING_GUIDE.md) is a plan with unchecked items, not a test result.
