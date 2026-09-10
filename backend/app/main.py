from datetime import datetime, timedelta, timezone

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI CI/CD Platform Engineer Agent", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GITHUB_REPOSITORY = "kirthi0071/Ci-Cd-Agents"
GITHUB_API = "https://api.github.com"


async def fetch_deployment_runs() -> list[dict]:
    """Fetch recent GitHub Actions deployment runs for this platform repo."""
    url = f"{GITHUB_API}/repos/{GITHUB_REPOSITORY}/actions/runs"
    params = {"per_page": 20, "event": "push", "branch": "main"}
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "ai-cicd-platform-agent",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json().get("workflow_runs", [])


def normalize_run(run: dict) -> dict:
    conclusion = run.get("conclusion")
    status = run.get("status")

    if status != "completed":
        display_status = "RUNNING"
    elif conclusion == "success":
        display_status = "SUCCESS"
    else:
        display_status = "FAILED"

    created_at = run.get("created_at")
    started = datetime.fromisoformat(created_at.replace("Z", "+00:00")) if created_at else None
    now = datetime.now(timezone.utc)

    if not started:
        relative_time = "unknown"
    else:
        seconds = max(0, int((now - started).total_seconds()))
        if seconds < 60:
            relative_time = f"{seconds}s ago"
        elif seconds < 3600:
            relative_time = f"{seconds // 60}m ago"
        elif seconds < 86400:
            relative_time = f"{seconds // 3600}h ago"
        else:
            relative_time = f"{seconds // 86400}d ago"

    return {
        "id": run.get("id"),
        "workflow": run.get("name", "GitHub Actions"),
        "service": "ai-cicd-agent",
        "environment": "production",
        "status": display_status,
        "conclusion": conclusion,
        "branch": run.get("head_branch", "main"),
        "commit": (run.get("head_sha") or "")[:7],
        "time": relative_time,
        "created_at": created_at,
        "url": run.get("html_url"),
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ai-cicd-agent"}


@app.get("/api/v1/deployments")
async def deployments() -> list[dict]:
    """Return recent production deployments from GitHub Actions."""
    try:
        runs = await fetch_deployment_runs()
        return [normalize_run(run) for run in runs]
    except (httpx.HTTPError, ValueError):
        return []


@app.get("/api/v1/overview")
async def overview() -> dict:
    """Build overview metrics from the latest GitHub Actions runs."""
    try:
        runs = await fetch_deployment_runs()
        deployments_24h = []
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

        for run in runs:
            created_at = run.get("created_at")
            if not created_at:
                continue
            created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            if created >= cutoff:
                deployments_24h.append(run)

        successful = sum(1 for run in deployments_24h if run.get("conclusion") == "success")
        failed = sum(
            1
            for run in deployments_24h
            if run.get("status") == "completed" and run.get("conclusion") != "success"
        )

        return {
            "deployments": {
                "total": len(deployments_24h),
                "successful": successful,
                "failed": failed,
            },
            "active_incidents": 1,
            "ai_investigations": 1,
        }
    except (httpx.HTTPError, ValueError):
        return {
            "deployments": {"total": 0, "successful": 0, "failed": 0},
            "active_incidents": 1,
            "ai_investigations": 1,
        }


@app.get("/api/v1/incidents")
def incidents() -> list[dict]:
    return [
        {
            "id": "INC-1024",
            "service": "user-service",
            "environment": "production",
            "severity": "HIGH",
            "status": "INVESTIGATING",
            "summary": "Cloud Run deployment failed startup checks",
        }
    ]
