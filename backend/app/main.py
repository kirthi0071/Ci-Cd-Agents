from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.transport_security import TransportSecuritySettings

from .mcp_server import mcp


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp.session_manager.run():
        yield


app = FastAPI(
    title="AI CI/CD Platform Engineer Agent",
    version="0.5.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"],
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


def github_get_text(path: str) -> str:
    request = Request(f"{GITHUB_API}{path}", headers=GITHUB_HEADERS)
    with urlopen(request, timeout=15) as response:
        return response.read().decode("utf-8", errors="replace")


def fetch_deployment_runs() -> list[dict]:
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


def extract_log_evidence(log_text: str) -> list[str]:
    patterns = (
        "error",
        "exception",
        "failed",
        "failure",
        "traceback",
        "modulenotfounderror",
        "permission denied",
        "exit code",
    )
    evidence: list[str] = []
    for raw_line in log_text.splitlines():
        line = raw_line.strip()
        if not line or len(line) > 500:
            continue
        lower = line.lower()
        if any(pattern in lower for pattern in patterns):
            if line not in evidence:
                evidence.append(line)
        if len(evidence) >= 12:
            break
    return evidence


def build_incident(incident_id: str) -> dict:
    if incident_id != "INC-1024":
        return {"incident": None, "evidence": []}

    runs = fetch_deployment_runs()
    failed_runs = [
        run for run in runs
        if run.get("status") == "completed" and run.get("conclusion") != "success"
    ]
    if not failed_runs:
        return {
            "incident": {
                "id": incident_id,
                "service": "ai-cicd-agent",
                "environment": "production",
                "severity": "HIGH",
                "status": "RESOLVED",
                "summary": "No failed GitHub Actions deployment is currently available for investigation.",
            },
            "evidence": [],
        }

    run = failed_runs[0]
    jobs_data = github_get(
        f"/repos/{GITHUB_REPOSITORY}/actions/runs/{run['id']}/jobs",
        {"per_page": 100},
    )
    jobs = jobs_data.get("jobs", []) if isinstance(jobs_data, dict) else []
    failed_jobs = [job for job in jobs if job.get("conclusion") == "failure"]

    evidence = [
        {
            "source": "github_actions",
            "type": "workflow_run",
            "finding": f"{run.get('name', 'GitHub Actions')} run #{run.get('run_number')} failed",
            "run_id": run.get("id"),
            "commit": (run.get("head_sha") or "")[:7],
            "url": run.get("html_url"),
        }
    ]

    for job in failed_jobs[:3]:
        job_evidence = {
            "source": "github_actions",
            "type": "job",
            "finding": f"Job '{job.get('name')}' failed",
            "job_id": job.get("id"),
            "url": job.get("html_url"),
        }
        try:
            logs = github_get_text(
                f"/repos/{GITHUB_REPOSITORY}/actions/jobs/{job['id']}/logs"
            )
            matches = extract_log_evidence(logs)
            if matches:
                job_evidence["log_evidence"] = matches
        except (HTTPError, URLError, TimeoutError):
            job_evidence["log_evidence"] = []
        evidence.append(job_evidence)

    return {
        "incident": {
            "id": incident_id,
            "service": "ai-cicd-agent",
            "environment": "production",
            "severity": "HIGH",
            "status": "INVESTIGATING",
            "summary": f"GitHub Actions deployment run #{run.get('run_number')} failed and requires investigation.",
            "deployment": normalize_run(run),
        },
        "evidence": evidence,
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ai-cicd-agent"}


@app.get("/api/v1/deployments")
def deployments() -> list[dict]:
    try:
        runs = fetch_deployment_runs()
        return [normalize_run(run) for run in runs]
    except (HTTPError, URLError, TimeoutError, ValueError):
        return []


@app.get("/api/v1/deployments/{run_id}")
def deployment_details(run_id: int) -> dict:
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


@app.get("/api/v1/incidents")
def incidents() -> list[dict]:
    try:
        result = build_incident("INC-1024")
        return [result["incident"]] if result["incident"] else []
    except (HTTPError, URLError, TimeoutError, ValueError):
        return []


@app.get("/api/v1/incidents/{incident_id}")
def incident_details(incident_id: str) -> dict:
    try:
        return build_incident(incident_id)
    except (HTTPError, URLError, TimeoutError, ValueError):
        return {"incident": None, "evidence": []}


@app.get("/api/v1/overview")
def overview() -> dict:
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
            "active_incidents": 1 if failed else 0,
            "ai_investigations": 1 if failed else 0,
        }
    except (HTTPError, URLError, TimeoutError, ValueError):
        return {
            "deployments": {"total": 0, "successful": 0, "failed": 0},
            "active_incidents": 0,
            "ai_investigations": 0,
        }


# MCP is mounted beside the REST API. Cloud Run provides the stable run.app host.
mcp_transport_security = TransportSecuritySettings(
    allowed_hosts=[
        "ai-cicd-agent-jeal5mhmha-el.a.run.app",
        "ai-cicd-agent-jeal5mhmha-el.a.run.app:*",
    ],
)
app.mount(
    "/mcp",
    mcp.streamable_http_app(
        transport_security=mcp_transport_security,
    ),
)
