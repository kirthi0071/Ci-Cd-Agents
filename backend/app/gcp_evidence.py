import os

from google.cloud import logging as cloud_logging
from google.cloud import run_v2


PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "project-c98d2dac-2409-44bd-aba")
REGION = os.getenv("CLOUD_RUN_REGION", "asia-south1")
SERVICE = os.getenv("CLOUD_RUN_SERVICE", "ai-cicd-agent")


def get_cloud_run_evidence(service: str | None = None) -> dict:
    service_name = service or SERVICE
    client = run_v2.ServicesClient()
    name = f"projects/{PROJECT_ID}/locations/{REGION}/services/{service_name}"
    resource = client.get_service(name=name)

    condition = resource.terminal_condition
    conditions = []
    if condition:
        conditions.append(
            {
                "type": condition.type_,
                "state": condition.state,
                "message": condition.message,
                "reason": condition.reason,
            }
        )

    return {
        "source": "cloud_run",
        "service": service_name,
        "location": REGION,
        "latest_ready_revision": resource.latest_ready_revision,
        "uri": resource.uri,
        "generation": resource.generation,
        "observed_generation": resource.observed_generation,
        "conditions": conditions,
    }


def get_cloud_logging_evidence(
    service: str | None = None,
    limit: int = 30,
) -> dict:
    service_name = service or SERVICE
    client = cloud_logging.Client(project=PROJECT_ID)
    log_filter = (
        f'resource.type="cloud_run_revision" '
        f'resource.labels.service_name="{service_name}" '
        f'(severity>=ERROR OR textPayload:"ERROR" OR jsonPayload.message:"error")'
    )

    entries = []
    for entry in client.list_entries(filter_=log_filter, page_size=limit):
        payload = entry.payload
        if isinstance(payload, dict):
            message = payload.get("message") or str(payload)
        else:
            message = str(payload)
        entries.append(
            {
                "timestamp": entry.timestamp.isoformat() if entry.timestamp else None,
                "severity": entry.severity,
                "message": message[:1000],
            }
        )
        if len(entries) >= limit:
            break

    return {
        "source": "cloud_logging",
        "service": service_name,
        "entries": entries,
        "count": len(entries),
    }
