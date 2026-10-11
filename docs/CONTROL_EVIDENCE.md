# Static control evidence

Baseline: `b2e5a8c24bb8a96060c6846294389969c4ff82bf`; reviewed 2026-10-11. These observations are not an audit, certification, or runtime result.

| ID / objective | Source evidence | Status / limit | Proposed verification |
| --- | --- | --- | --- |
| C01 Identity and access | app/auth.py: hash_password, login; main.py user_type branches | Partial demo implementation. Shared resident password, unsalted SHA-256, plaintext admin comparison. No demonstrated data ownership enforcement | Independent identity design and review; synthetic authorized functional tests after remediation |
| C02 Conversation traceability | db/database.py: log_conversation and get_* functions | Timestamp/speaker/text persistence exists. No user ID, retention policy or tamper protection | Define owner-scoped schema and retention, then verify isolation using synthetic records |
| C03 Upload handling | ui/document_upload.py: allowed_file, upload_document | Filename sanitization and extension allowlist observed; size/content policy and cross-framework login integration unverified | Define size/content restrictions and prove ordinary synthetic upload behavior |
| C04 Emergency communication | main.py confirmation paths; utils/emergency.py: trigger_emergency | Simulation / local log only. Revised labels must state no services contacted | Source wording check; no live dispatch testing |
| C05 Reporting integrity | main.py resident_data, chart_data, event_participation | Hardcoded examples, not measured usage | Keep visible synthetic labels until provenance-backed aggregation exists |
| C06 Configuration | main.py: run_flask_app; core/config_manager.py; .env.example | Environment secret read with development fallback; global JSON settings | Remove unsafe fallback before sensitive use; document separate session and config design |
| C07 Error/health utilities | utils/error_handler.py, utils/system_health.py, utils/run_tests.py | Utilities exist; no execution evidence reviewed. Pending checklists and stale paths limit conclusions | Correct harness separately; record exact commands, environment, output and commit |
| C08 Accessibility | main.py, static/main.css | Interface accommodations exist; no conformance report reviewed | Define WCAG evaluation scope and retain per-criterion evidence |
| C09 Offline capability | static/manifest.json, static/service-worker.js | Worker file contains manifest JSON; offline behavior unverified | Implement valid worker and ordinary offline functional validation separately |

Follow-up risks and acceptance criteria: [risk register](RISK_REGISTER.md). Historical statements do not upgrade any status to verified.
