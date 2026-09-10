# AI CI/CD Platform Engineer Agent

An AI-assisted CI/CD platform engineering system that detects failed deployments, collects evidence from GitHub Actions and Google Cloud, investigates the failure, recommends a fix, and proposes remediation through a GitHub pull request.

## Goal

Build a practical Platform Engineering Agent with an evidence-first workflow.

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
- **Evidence:** GitHub Actions logs, Cloud Run state, and Cloud Logging

## Current Flow

1. GitHub Actions builds and deploys the application.
2. A failed deployment triggers the incident investigation workflow automatically.
3. The workflow collects the failed run, jobs, and relevant log lines.
4. Evidence is submitted to the agent.
5. MCP tools expose GitHub, Cloud Run, and Cloud Logging evidence.
6. The investigator determines the likely root cause.
7. The result contains category, confidence, evidence, recommended fix, risk, and approval requirement.
8. Investigations and audit events can be persisted in Cloud SQL.
9. The frontend displays deployment evidence and AI investigation results.

## Remaining Core Flow

```text
Diagnosis
   → Generate Fix
   → Create Branch
   → Commit Patch
   → Create Pull Request
   → Human Review / Merge
   → CI/CD
   → Cloud Run
   → Verify
   → Resolve Incident
```

The agent should propose changes through GitHub rather than directly changing production.

## Failure Types

Current deterministic investigation includes:

- `ModuleNotFoundError` → build failure
- permission denied / `403` → IAM failure
- port or startup errors → startup failure
- HTTP `500` → runtime failure

Other failures can be investigated using Gemini.

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

The current goal is the **working end-to-end flow**, not enterprise-level hardening. Advanced security controls, extensive UI polish, and other production hardening can be added later.

## Expected Outcome

The finished system should take a CI/CD failure through:

```text
Failure
  → Evidence
  → Investigation
  → Root Cause
  → Fix Proposal
  → GitHub PR
  → CI/CD
  → Verification
```

and provide a clear audit trail of what happened and why.

## GCP

- Project ID: `project-c98d2dac-2409-44bd-aba`
- Region: `asia-south1`
- Artifact Registry repository: `cloud-run-agent`
- Cloud Run service: `ai-cicd-agent`
- Cloud SQL instance: `ai-cicd-agent-db`
- Database: `agentdb`
- Authentication: GitHub OIDC / Workload Identity Federation
