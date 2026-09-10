from datetime import datetime, timedelta, timezone
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI CI/CD Platform Engineer Agent", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GITHUB_REPOSITORY = "kirthi0071/Ci-Cd-Agents"
GITHUB_API = "https://api.github.com"
GITHUB_HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "ai-cicd-platform-agent",
}


def github_get(path: str, params: dict | None = None) -> dict | list:
    query = f"?{urlencode(params)}" if params else ""
    request = Request(f"{GITHUB_API}{path}{query}", headers=GITHUB_HEADERS)
    with urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_deployment_runs() -> list[dict]:
    """Fetch recent GitHub Actions deployment runs for this platform repo."""
    data = github_get(
        f"/repos/{GITHUB_REPOSITORY}/actions/runs",
        {"per_page": 20, "event": "push", "branch": "main"},
    )
    return data.get("workflow_runs", []) if isinstance(data, dict) else []


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


def normalize_job(job: dict) -> dict:
    return {
        "id": job.get("id"),
        "name": job.get("name", "GitHub Actions job"),
        "status": job.get("status"),
        "conclusion": job.get("conclusion"),
        "started_at": job.get("started_at"),
        "completed_at": job.get("completed_at"),
        "url": job.get("html_url"),
        "steps": [
            {
                "number": step.get("number"),
                "name": step.get("name"),
                "status": step.get("status"),
                "conclusion": step.get("conclusion"),
                "started_at": step.get("started_at"),
                "completed_at": step.get("completed_at"),
            }
            for step in (job.get("steps") or [])
        ],
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ai-cicd-agent"}


@app.get("/api/v1/deployments")
def deployments() -> list[dict]:
    """Return recent production deployments from GitHub Actions."""
    try:
        runs = fetch_deployment_runs()
        return [normalize_run(run) for run in runs]
    except (HTTPError, URLError, TimeoutError, ValueError):
        return []


@app.get("/api/v1/deployments/{run_id}")
def deployment_details(run_id: int) -> dict:
    """Return a deployment plus its GitHub Actions jobs and step results."""
    try:
        run = github_get(f"/repos/{GITHUB_REPOSITORY}/actions/runs/{run_id}")
        jobs_data = github_get(
            f"/repos/{GITHUB_REPOSITORY}/actions/runs/{run_id}/jobs",
            {"per_page": 100},
        )
        jobs = jobs_data.get("jobs", []) if isinstance(jobs_data, dict) else []
        return {
            "deployment": normalize_run(run),
            "jobs": [normalize_job(job) for job in jobs],
        }
    except (HTTPError, URLError, TimeoutError, ValueError):
        return {"deployment": None, "jobs": []}


@app.get("/api/v1/overview")
def overview() -> dict:
    """Build overview metrics from the latest GitHub Actions runs."""
    try:
        runs = fetch_deployment_runs()
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
    except (HTTPError, URLError, TimeoutError, ValueError):
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
