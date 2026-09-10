#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="project-c98d2dac-2409-44bd-aba"
REGION="asia-south1"
INSTANCE="ai-cicd-agent-db"
DB_NAME="agentdb"
DB_USER="agent"
RUNTIME_SA="ai-cicd-agent-runtime@${PROJECT_ID}.iam.gserviceaccount.com"
IMPERSONATE_SA="ai-cicd-agent-admin@${PROJECT_ID}.iam.gserviceaccount.com"

G=(gcloud --project="${PROJECT_ID}" --impersonate-service-account="${IMPERSONATE_SA}")

"${G[@]}" services enable sqladmin.googleapis.com secretmanager.googleapis.com

if ! "${G[@]}" sql instances describe "${INSTANCE}" >/dev/null 2>&1; then
  "${G[@]}" sql instances create "${INSTANCE}" \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region="${REGION}" \
    --storage-type=HDD \
    --storage-size=10GB \
    --no-storage-auto-increase \
    --availability-type=zonal \
    --no-backup
fi

if ! "${G[@]}" sql databases describe "${DB_NAME}" --instance="${INSTANCE}" >/dev/null 2>&1; then
  "${G[@]}" sql databases create "${DB_NAME}" --instance="${INSTANCE}"
fi

DB_PASSWORD="$(openssl rand -hex 24)"
"${G[@]}" sql users create "${DB_USER}" --instance="${INSTANCE}" --password="${DB_PASSWORD}" 2>/dev/null || \
  "${G[@]}" sql users set-password "${DB_USER}" --instance="${INSTANCE}" --password="${DB_PASSWORD}"

for secret in cloud-sql-db-user cloud-sql-db-password; do
  if ! "${G[@]}" secrets describe "${secret}" >/dev/null 2>&1; then
    "${G[@]}" secrets create "${secret}" --replication-policy=automatic
  fi
done

printf '%s' "${DB_USER}" | "${G[@]}" secrets versions add cloud-sql-db-user --data-file=-
printf '%s' "${DB_PASSWORD}" | "${G[@]}" secrets versions add cloud-sql-db-password --data-file=-

"${G[@]}" projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${RUNTIME_SA}" \
  --role="roles/cloudsql.client" \
  --quiet

for secret in cloud-sql-db-user cloud-sql-db-password; do
  "${G[@]}" secrets add-iam-policy-binding "${secret}" \
    --member="serviceAccount:${RUNTIME_SA}" \
    --role="roles/secretmanager.secretAccessor" \
    --quiet
done

echo "Cloud SQL setup complete."
echo "Instance: ${PROJECT_ID}:${REGION}:${INSTANCE}"
echo "Database: ${DB_NAME}"
echo "User: ${DB_USER}"
