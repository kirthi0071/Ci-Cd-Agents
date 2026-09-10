from mcp.server import MCPServer

mcp = MCPServer(
    "AI CI/CD Platform Agent",
    instructions=(
        "Use these read-only tools to collect CI/CD evidence before diagnosis. "
        "Do not modify production resources."
    ),
)


@mcp.tool()
def get_incident_evidence(incident_id: str) -> dict:
    """Collect GitHub Actions evidence for a known incident."""
    from .main import build_incident

    return build_incident(incident_id)


@mcp.tool()
def get_deployment_evidence(run_id: int) -> dict:
    """Return a GitHub Actions deployment run with jobs and step results."""
    from .main import github_get, normalize_job, normalize_run, GITHUB_REPOSITORY

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


@mcp.tool()
def get_job_logs(job_id: int) -> dict:
    """Fetch a GitHub Actions job log and return filtered failure evidence."""
    from .main import extract_log_evidence, github_get_text, GITHUB_REPOSITORY

    logs = github_get_text(f"/repos/{GITHUB_REPOSITORY}/actions/jobs/{job_id}/logs")
    return {
        "job_id": job_id,
        "evidence": extract_log_evidence(logs),
        "log_available": bool(logs),
    }


@mcp.tool()
def get_cloud_run_evidence(service: str = "") -> dict:
    """Return read-only Cloud Run service readiness and revision evidence."""
    from .gcp_evidence import get_cloud_run_evidence as collect_cloud_run

    try:
        return collect_cloud_run(service or None)
    except Exception as exc:
        return {
            "source": "cloud_run",
            "available": False,
            "error": str(exc),
        }


@mcp.tool()
def get_cloud_logging_evidence(service: str = "", limit: int = 30) -> dict:
    """Return recent Cloud Run error logs for evidence collection."""
    from .gcp_evidence import get_cloud_logging_evidence as collect_logs

    try:
        return collect_logs(service or None, max(1, min(limit, 100)))
    except Exception as exc:
        return {
            "source": "cloud_logging",
            "available": False,
            "error": str(exc),
        }


@mcp.tool()
def investigate_incident(incident_id: str) -> dict:
    """Collect incident evidence and produce a structured diagnosis."""
    from .main import build_incident
    from .investigator import investigate_incident as run_investigation

    evidence = build_incident(incident_id)
    if not evidence.get("incident"):
        return {
            "incident_id": incident_id,
            "status": "NOT_FOUND",
        }

    investigation = run_investigation(evidence)
    return {
        "incident_id": incident_id,
        "status": "ANALYZED",
        "investigation": investigation,
        "source_evidence": evidence,
    }
