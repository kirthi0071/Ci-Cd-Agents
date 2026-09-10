from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI CI/CD Platform Engineer Agent", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ai-cicd-agent"}


@app.get("/api/v1/overview")
def overview() -> dict:
    return {
        "deployments": {"total": 24, "successful": 21, "failed": 3},
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
