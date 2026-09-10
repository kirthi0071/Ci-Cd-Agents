import json
import os
import re

from google import genai
from google.genai.types import HttpOptions


PROJECT_ID = os.getenv(
    "GOOGLE_CLOUD_PROJECT",
    "project-c98d2dac-2409-44bd-aba",
)

MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash-lite",
)


INVESTIGATION_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "root_cause": {"type": "STRING"},
        "category": {
            "type": "STRING",
            "enum": [
                "BUILD_FAILURE",
                "STARTUP_FAILURE",
                "IAM_FAILURE",
                "RUNTIME_FAILURE",
                "UNKNOWN",
            ],
        },
        "confidence": {"type": "NUMBER"},
        "evidence": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
        },
        "recommended_fix": {"type": "STRING"},
        "risk": {"type": "STRING"},
        "requires_approval": {"type": "BOOLEAN"},
    },
    "required": [
        "root_cause",
        "category",
        "confidence",
        "evidence",
        "recommended_fix",
        "risk",
        "requires_approval",
    ],
}


def deterministic_diagnosis(evidence: dict) -> dict | None:
    """Fast deterministic diagnosis for known failure patterns."""
    evidence_text = json.dumps(evidence).lower()

    if "modulenotfounderror" in evidence_text:
        match = re.search(
            r"modulenotfounderror.*?no module named ['\"]([^'\"]+)",
            evidence_text,
        )
        module = match.group(1) if match else "required dependency"
        return {
            "root_cause": f"The container is missing the Python dependency '{module}'.",
            "category": "BUILD_FAILURE",
            "confidence": 0.98,
            "evidence": [
                "GitHub Actions deployment failed.",
                f"Runtime reported ModuleNotFoundError for '{module}'.",
            ],
            "recommended_fix": (
                f"Add '{module}' to backend/requirements.txt, rebuild the container, "
                "and redeploy through CI/CD."
            ),
            "risk": "LOW",
            "requires_approval": True,
        }

    if "permission denied" in evidence_text or "403" in evidence_text:
        return {
            "root_cause": "The deployment or runtime operation was rejected because of insufficient IAM permissions.",
            "category": "IAM_FAILURE",
            "confidence": 0.95,
            "evidence": ["Deployment evidence contains a permission failure."],
            "recommended_fix": "Identify the calling service account and grant only the minimum required IAM role.",
            "risk": "MEDIUM",
            "requires_approval": True,
        }

    if "port" in evidence_text and (
        "startup" in evidence_text
        or "failed to start" in evidence_text
        or "container failed" in evidence_text
    ):
        return {
            "root_cause": "The Cloud Run container failed its startup requirement, most likely because the application did not listen on the expected PORT.",
            "category": "STARTUP_FAILURE",
            "confidence": 0.92,
            "evidence": [
                "Deployment evidence contains a container startup failure.",
                "Evidence references PORT/startup behavior.",
            ],
            "recommended_fix": "Verify the application listens on 0.0.0.0:$PORT and redeploy through CI/CD.",
            "risk": "LOW",
            "requires_approval": True,
        }

    if "http 500" in evidence_text or "status code 500" in evidence_text:
        return {
            "root_cause": "The deployed application is returning an HTTP 500 runtime error.",
            "category": "RUNTIME_FAILURE",
            "confidence": 0.90,
            "evidence": ["Runtime evidence contains an HTTP 500 response."],
            "recommended_fix": "Inspect application runtime logs and identify the failing request path before proposing a code change.",
            "risk": "MEDIUM",
            "requires_approval": True,
        }

    return None


def gemini_diagnosis(evidence: dict) -> dict:
    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=os.getenv("GOOGLE_CLOUD_LOCATION", "global"),
        http_options=HttpOptions(api_version="v1"),
    )

    prompt = f"""
You are an expert SRE and CI/CD platform engineer.

Investigate the CI/CD incident using ONLY the evidence supplied below.
Do not invent logs, infrastructure state, or events.

Determine:
1. The most likely root cause.
2. The failure category.
3. Confidence from 0.0 to 1.0.
4. The evidence supporting the diagnosis.
5. A recommended remediation.
6. Risk of the remediation.
7. Whether human approval is required.

Production resources must never be modified directly.

Incident evidence:
{json.dumps(evidence, indent=2)}
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": INVESTIGATION_SCHEMA,
        },
    )
    return json.loads(response.text)


def investigate_incident(evidence: dict) -> dict:
    """Deterministic rules first; Gemini is used for unknown patterns."""
    deterministic = deterministic_diagnosis(evidence)
    if deterministic:
        deterministic["engine"] = "deterministic"
        return deterministic

    try:
        result = gemini_diagnosis(evidence)
        result["engine"] = "gemini"
        return result
    except Exception as exc:
        return {
            "root_cause": "Unable to determine the root cause automatically.",
            "category": "UNKNOWN",
            "confidence": 0.0,
            "evidence": [
                "Available evidence was insufficient for deterministic diagnosis."
            ],
            "recommended_fix": "Review the collected CI/CD evidence manually.",
            "risk": "UNKNOWN",
            "requires_approval": True,
            "engine": "fallback",
            "error": str(exc),
        }
