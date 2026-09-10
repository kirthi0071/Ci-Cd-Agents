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
      Incident Workflow
         ↓
      Collect Evidence
         ↓
      MCP Tools
         ├── GitHub Actions
         ├── Cloud Run
         └── Cloud Logging
         ↓
      AI Agent / Gemini
         ↓
      Root Cause + Evidence + Confidence
         ↓
      Recommended Fix
         ↓
      GitHub Branch
         ↓
      Pull Request
         ↓
      Human Review / Merge
         ↓
      GitHub Actions
         ↓
      Cloud Run
         ↓
      Post-Fix Verification
         ↓
      Incident Resolved
```

## Current State

- Foundation, GCP infrastructure, and CI/CD are working.
- Evidence collection and automatic incident investigation are implemented.
- MCP tools expose deployment and Google Cloud evidence.
- AI investigation returns root cause, category, confidence, evidence, recommended fix, risk, and approval requirement.
- Cloud SQL persistence and the investigation UI are implemented.

## Remaining Core Work

1. Finish the tool-using agent orchestration.
2. Generate a concrete remediation proposal from the diagnosis.
3. Create a GitHub branch and commit the proposed fix.
4. Create a GitHub PR instead of changing production directly.
5. Run CI/CD after merge.
6. Verify the repaired Cloud Run service and close the incident.

Security hardening and extensive UI polish are intentionally secondary for this project phase.
