# Local orchestrator testing (CS-213)

Test your skills against the real orchestrator **before** waiting for sync to `mentora-skills`.

## Layout

```
mentora/
  CS-213-skills/skills/     ← your skills (folder names must match skill_id, e.g. cache-opt-code/)
  skills-registry/
  skills-orchestrator/      ← API on :8080
  skills-ui/                ← optional chat UI
```

## One-time setup

```bash
# Orchestrator deps
cd skills-orchestrator
pip install -e ".[dev]"

# Catalog builder deps
pip install pyyaml
```

Set an API key in `skills-orchestrator/.env` (`GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, etc.).

## Build catalog + configure orchestrator

From repo root:

```bash
bash CS-213-skills/scripts/test-local.sh
```

Or manually:

```bash
cd skills-registry
python scripts/catalog_builder_mentora_skills.py \
  --package ../CS-213-skills/skills \
  --output local/catalog-cs213.json \
  --report local/build_report-cs213.md \
  --strict
```

In `skills-orchestrator/.env`:

```bash
MENTORA_SKILLS_PATH=../CS-213-skills/skills
REGISTRY_URL=../skills-registry/local/catalog-cs213.json
REGISTRY_CACHE_TTL=0
LOG_LEVEL=DEBUG
```

## Run

```bash
cd skills-orchestrator
make dev
```

Health check:

```bash
curl http://localhost:8080/healthz
```

## Debug skill selection

After a few chat turns, copy the session id from the orchestrator logs and run:

```bash
curl -s http://localhost:8080/sessions/YOUR_SESSION_ID/debug | jq
```

Check `lastSkill.skillId`, `lastSkill.reasons`, and `currentStance`.

## Sample messages

| Message | Expected skill |
|---------|----------------|
| Paste assembly + “translate this to C” | `asm-translation` |
| Paste C + “segfault” | `c-debugger` |
| “Hand trace these instructions” | `execution-trace` |
| “Where does push write on the stack?” | `stack-visualizer` |
| “My matrix multiply is slow” + loops | `cache-opt-code` |

## Revert after testing

In `skills-orchestrator/.env`:

```bash
MENTORA_SKILLS_PATH=../mentora-skills/mentora_skills/skills
REGISTRY_URL=../skills-registry/catalog.json
REGISTRY_CACHE_TTL=300
LOG_LEVEL=INFO
```

Rebuild the full catalog:

```bash
cd skills-registry
python scripts/catalog_builder_mentora_skills.py \
  --package ../mentora-skills/mentora_skills/skills \
  --output catalog.json
```
