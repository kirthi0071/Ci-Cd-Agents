import logging
import os
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import Json

logger = logging.getLogger(__name__)

DB_NAME = os.getenv("DB_NAME", "")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME", "")


def enabled() -> bool:
    return bool(DB_NAME and DB_USER and DB_PASSWORD and INSTANCE_CONNECTION_NAME)


@contextmanager
def connection():
    if not enabled():
        raise RuntimeError("Database is not configured")
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=f"/cloudsql/{INSTANCE_CONNECTION_NAME}",
        connect_timeout=5,
    )
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    if not enabled():
        logger.info("PostgreSQL persistence disabled; DB environment is not configured")
        return
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS investigations (
                    id BIGSERIAL PRIMARY KEY,
                    incident_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    failure_category TEXT,
                    confidence DOUBLE PRECISION,
                    risk TEXT,
                    root_cause TEXT,
                    recommended_remediation TEXT,
                    investigation JSONB NOT NULL,
                    source_evidence JSONB NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_investigations_incident_created
                ON investigations (incident_id, created_at DESC)
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_events (
                    id BIGSERIAL PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    incident_id TEXT,
                    actor TEXT NOT NULL DEFAULT 'agent',
                    details JSONB NOT NULL DEFAULT '{}'::jsonb,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )


def save_investigation(incident_id: str, status: str, investigation: dict, source_evidence: dict) -> None:
    if not enabled():
        return
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO investigations (
                    incident_id, status, failure_category, confidence, risk,
                    root_cause, recommended_remediation, investigation, source_evidence
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    incident_id,
                    status,
                    investigation.get("category"),
                    investigation.get("confidence"),
                    investigation.get("risk"),
                    investigation.get("root_cause"),
                    investigation.get("recommended_fix"),
                    Json(investigation),
                    Json(source_evidence),
                ),
            )
            cur.execute(
                """
                INSERT INTO audit_events (event_type, incident_id, details)
                VALUES (%s, %s, %s)
                """,
                ("incident.investigated", incident_id, Json({"status": status})),
            )


def latest_investigation(incident_id: str) -> dict | None:
    if not enabled():
        return None
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT investigation, source_evidence, status, created_at
                FROM investigations
                WHERE incident_id = %s
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (incident_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
            investigation, source_evidence, status, created_at = row
            return {
                "status": status,
                "investigation": investigation,
                "source_evidence": source_evidence,
                "created_at": created_at.isoformat(),
            }
