#!/usr/bin/env bash
# Build a CS-213-only catalog and print orchestrator .env hints.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
REGISTRY="$ROOT/skills-registry"
ORCH="$ROOT/skills-orchestrator"
SKILLS="$ROOT/CS-213-skills/skills"

echo "==> Building catalog from $SKILLS"
mkdir -p "$REGISTRY/local"
python3 "$REGISTRY/scripts/catalog_builder_mentora_skills.py" \
  --package "$SKILLS" \
  --output "$REGISTRY/local/catalog-cs213.json" \
  --report "$REGISTRY/local/build_report-cs213.md" \
  --changelog "$REGISTRY/local/catalog_changelog-cs213.json" \
  --meta "$REGISTRY/local/catalog_meta-cs213.json" \
  --strict

echo ""
echo "==> Catalog ready: $REGISTRY/local/catalog-cs213.json"
echo "    Report:       $REGISTRY/local/build_report-cs213.md"
echo ""
echo "Orchestrator .env should include:"
echo "  MENTORA_SKILLS_PATH=../CS-213-skills/skills"
echo "  REGISTRY_URL=../skills-registry/local/catalog-cs213.json"
echo "  REGISTRY_CACHE_TTL=0"
echo ""
echo "Start orchestrator (from skills-orchestrator):"
echo "  make dev"
echo ""
echo "Then open skills-ui or:"
echo "  curl http://localhost:8080/healthz"
echo "  curl -s http://localhost:8080/sessions/{id}/debug | jq"
