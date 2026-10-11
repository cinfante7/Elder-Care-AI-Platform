# Reproducible ordinary validation

Use the repository root, a pinned commit, and synthetic data only. Source checks do not import application modules, use credentials, contact emergency services, exercise security attacks, or prove runtime behavior.

## Source syntax check

Python standard library only; no app dependency installation is required:

```powershell
@'
import ast
from pathlib import Path
files = ["main.py", "utils/emergency.py"]
for name in files:
    ast.parse(Path(name).read_text(encoding="utf-8-sig"), filename=name)
    print("Syntax parsed:", name)
'@ | python -
```

## Documentation and wording review

```powershell
git diff --check
git grep -n -i -E "emergency services have been notified|help is on the way|emergency alert sent" -- main.py utils/emergency.py
git grep -n "Synthetic demonstration" -- main.py
```

The prohibited-assurance search should return no matches (git grep exit 1 means no match). Review all emergency call sites and returned/spoken text; this check alone cannot prove all semantic wording safe. Confirm local document links resolve and Markdown fences close.

## Legacy utilities and future runtime work

The historical TESTING_GUIDE.md has unchecked items, not recorded passes. Its `cd testing` command does not match the current utils/ location. utils/run_tests.py expects a root auth.py although auth lives in app/, creates result files, and includes credential/configuration checks and unconditional stakeholder status claims. It was not run in this pass and is not an acceptance gate.

Future ordinary runtime verification requires an isolated environment, complete dependencies, Vosk model, synthetic configuration and separately approved scope. Record command, commit, dependency versions, environment, timestamp, outputs and failures. Keep source inspection, runtime functional checks, accessibility evaluation, and compliance assessment distinct. Do not use demo credentials against live systems or test emergency dispatch.

## This pass

The PR records the exact final source-check results. No application startup, browser/rendered QA, microphone/camera test, credential test, legacy test runner, clinical validation, accessibility audit, performance benchmark or compliance audit was executed.
