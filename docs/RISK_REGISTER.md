# Prototype risk register

Static review baseline: `b2e5a8c24bb8a96060c6846294389969c4ff82bf`. Priorities are qualitative review judgments, not measured incident rates. Owners and dates remain unassigned.

| ID | Priority / risk | Current treatment | Proposed acceptance criterion |
| --- | --- | --- | --- |
| R01 | Critical: emergency assurance could cause reliance | This pass labels controls, spoken response and local log as simulation; no service contact | Every path visibly states no contact occurred; source check passes. No dispatch or clinical use |
| R02 | High: demo authentication unsuitable for sensitive use | Document only; no credential tests | Unique identities, appropriate password storage, credential lifecycle and independent design review before real use |
| R03 | High: conversation recall lacks owner scoping | Document only; no schema change | Every record has authorized owner context; ordinary synthetic functional tests verify intended access |
| R04 | High: sensitive text, uploads and biometric files persist locally | Synthetic-only restriction | Approved minimization, consent, retention/deletion and storage-protection design; verified lifecycle with synthetic files |
| R05 | High: upload/session boundary incomplete | Document only | Document Flask/Streamlit session integration; enforce authorized upload policy and verify normal synthetic uploads |
| R06 | High: unsupported completion/compliance claims | Historical report annotated; current evidence statuses supersede claims | Every performance/accessibility/result claim links dated reproducible evidence; no HIPAA or production assertion without appropriate evaluation |
| R07 | Medium: dashboards could imply actual residents or service activity | Visible synthetic captions | Each metric/chart labels synthetic origin until real aggregation and provenance are implemented |
| R08 | Medium: startup and legacy testing may fail | Missing face dependencies, Vosk prerequisite and stale harness paths disclosed | Clean isolated installation and ordinary deterministic checks produce retained results for a pinned commit |
| R09 | Medium: offline claim unsupported | Documented manifest/worker gap | Valid worker, defined caching scope and ordinary offline verification |
| R10 | High: role UI and global config may be mistaken for access controls | Explicit partial-control status | Define and independently verify server/data authorization and per-user configuration before sensitive use |

No remediation in this pass establishes HIPAA compliance, clinical safety, production readiness, or security certification. Broad identity/storage changes remain a separate scope.
