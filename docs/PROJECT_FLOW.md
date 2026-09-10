# AI CI/CD Platform Engineer Agent — Project Flow

## End-to-End Flow

```text
Developer
   ↓
GitHub
   ↓
GitHub Actions
   ↓
Build / Test / Docker
   ↓
Artifact Registry
   ↓
Cloud Run
   │
   ├── Success → Service running
   │
   └── Failure
         ↓
      Automatic Incident Workflow
         ↓
      Collect Evidence
         ↓
      MCP / Agent Tools
         ↓
      AI Investigation
         ↓
      Root Cause + Evidence + Confidence
         ↓
      Recommended Fix
         ↓
      Remediation Branch
         ↓
      GitHub Pull Request
         ↓
      Human Review / Merge
         ↓
      GitHub Actions
         ↓
      Cloud Run
         ↓
      Verify
         ↓
      Incident Resolved
```

## Current State

- Foundation, GCP infrastructure, and CI/CD are working.
- Cloud SQL persistence and the investigation UI are implemented.
- Evidence collection and automatic incident investigation are implemented.
- MCP tools expose GitHub Actions, Cloud Run, and Cloud Logging evidence.
- AI investigation returns root cause, category, confidence, evidence, recommended fix, risk, and approval requirement.
- A minimal controlled remediation PR flow is implemented for the demo failure marker.

## Minimal Demo

Create `backend/DEMO_FAIL` and push it to `main`.

The deployment workflow intentionally fails when that marker exists. The automatic incident workflow then collects the failed logs, sends evidence to the agent, and creates a remediation PR that removes the marker. After the PR is merged, normal CI/CD runs and Cloud Run deploys successfully.

```text
DEMO_FAIL
   ↓
Deploy fails
   ↓
Incident workflow
   ↓
Evidence
   ↓
AI investigation
   ↓
Remove DEMO_FAIL
   ↓
PR
   ↓
Merge
   ↓
Deploy
   ↓
Verify
```

## Remaining Core Work

1. Make the agent orchestration more tool-driven instead of mostly deterministic.
2. Expand remediation beyond the controlled demo marker.
3. Add post-deployment verification to the incident lifecycle.
4. Connect the final incident state to the frontend.

Security hardening and extensive UI polish are intentionally secondary for this project phase.
