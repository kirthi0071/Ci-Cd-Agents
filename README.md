# AI CI/CD Platform Engineer Agent

Part 2 of the CI/CD platform learning project.

This repository will evolve into an AI agent that investigates CI/CD and Cloud Run failures using evidence from GitHub and GCP, then proposes fixes through GitHub pull requests with human approval before production changes.

## Initial target architecture

GitHub Actions → Workload Identity Federation → GCP → Artifact Registry → Cloud Run → Cloud Logging

Later:

Failure → AI Agent → MCP tools → Evidence → Diagnosis → Recommended Fix → GitHub PR → Human Review → CI/CD

## GCP

- Project ID: `project-c98d2dac-2409-44bd-aba`
- Region: `asia-south1`
- Artifact Registry repository: `cloud-run-agent`
- Authentication: GitHub OIDC / Workload Identity Federation

No long-lived GCP service-account keys should be stored in this repository.
