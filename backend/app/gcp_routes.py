from fastapi import APIRouter

from .gcp_evidence import get_cloud_logging_evidence, get_cloud_run_evidence

router = APIRouter(prefix="/api/v1/gcp", tags=["gcp-evidence"])


@router.get("/cloud-run")
def cloud_run_evidence(service: str = "") -> dict:
    try:
        return get_cloud_run_evidence(service or None)
    except Exception as exc:
        return {
            "source": "cloud_run",
            "available": False,
            "error": str(exc),
        }


@router.get("/logging")
def cloud_logging_evidence(service: str = "", limit: int = 30) -> dict:
    try:
        return get_cloud_logging_evidence(service or None, max(1, min(limit, 100)))
    except Exception as exc:
        return {
            "source": "cloud_logging",
            "available": False,
            "error": str(exc),
        }
