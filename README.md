# AI CI/CD Platform Engineer Agent

A minimal working AI-assisted CI/CD platform engineering system that detects failed deployments, collects evidence, investigates the failure, recommends a fix, creates a GitHub pull request for a controlled remediation, and verifies the deployment after the PR is merged.

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
      Collect GitHub Evidence
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
      Human Merge
         ↓
      GitHub Actions
         ↓
      Cloud Run
         ↓
      Verify
         ↓
      Incident Resolved
```

## Main Components

- **Frontend:** React + TypeScript + Vite
- **Backend:** Python + FastAPI
- **AI:** Gemini through Vertex AI
- **Agent tools:** MCP
- **CI/CD:** GitHub Actions
- **Container:** Docker
- **Registry:** Google Artifact Registry
- **Runtime:** Google Cloud Run
- **Database:** Cloud SQL PostgreSQL
- **Secrets:** Google Secret Manager
- **Evidence:** GitHub Actions logs, Cloud Run, and Cloud Logging

## What Works

1. GitHub Actions builds and deploys the backend.
2. Cloud Run runs the application.
3. Cloud SQL stores investigation results and audit events.
4. A failed deployment automatically triggers the incident workflow.
5. The workflow collects failed jobs and relevant log lines.
6. Evidence is submitted to the agent.
7. The investigator performs deterministic diagnosis first and Gemini reasoning for unknown failures.
8. The investigation returns root cause, category, confidence, evidence, recommended fix, risk, and approval requirement.
9. The frontend can display deployment evidence and investigation results.
10. A controlled demo failure can automatically produce a remediation GitHub PR.

## Minimal Demo

The repository contains a controlled failure switch: `backend/DEMO_FAIL`.

When this file exists, the deployment workflow intentionally fails before deployment. This lets the complete agent flow be demonstrated without breaking the real application.

### Demo sequence

```text
1. Add backend/DEMO_FAIL
        ↓
2. Push to main
        ↓
3. Deploy Backend fails intentionally
        ↓
4. AI Incident Investigation starts automatically
        ↓
5. Failed logs are collected
        ↓
6. Agent investigates INC-1024
        ↓
7. Remediation workflow removes backend/DEMO_FAIL
        ↓
8. Agent creates a GitHub PR
        ↓
9. Review and merge the PR
        ↓
10. Deploy Backend runs again
        ↓
11. Cloud Run deployment succeeds
        ↓
12. Verify the service
```

The demo remediation is intentionally simple: the agent removes the controlled failure marker. This proves the complete **failure → evidence → investigation → remediation PR → CI/CD → successful deployment** loop without requiring enterprise-level automation.

## Failure Types

Current deterministic investigation includes:

- `ModuleNotFoundError` → build failure
- permission denied / `403` → IAM failure
- port or startup errors → startup failure
- HTTP `500` → runtime failure

Other failures can be investigated using Gemini.

## MCP Tools

The agent exposes tools for:

- GitHub incident evidence
- Deployment evidence
- GitHub job logs
- Incident investigation
- Cloud Run evidence
- Cloud Logging evidence

## Project Structure

```text
.
├── backend/
│   └── app/
├── frontend/
├── infra/
├── docs/
│   └── PROJECT_FLOW.md
└── .github/
    └── workflows/
```

## Development Focus

This project intentionally focuses on a **minimal working end-to-end flow** rather than enterprise-level hardening. Advanced authentication, security controls, extensive UI polish, multi-environment deployments, and other production features can be added later.

## GCP

- Project ID: `project-c98d2dac-2409-44bd-aba`
- Region: `asia-south1`
- Artifact Registry repository: `cloud-run-agent`
- Cloud Run service: `ai-cicd-agent`
- Cloud SQL instance: `ai-cicd-agent-db`
- Database: `agentdb`
- Authentication: GitHub OIDC / Workload Identity Federation
