# CS-213 skills chatbot

Small web UI: your message goes to **Google Gemini**, with optional hints from the local skills (`c-debugger`, `asm-translation`, `execution-trace`, `stack-visualizer`) when the text looks like C or assembly.

## Run

From the repo root (folder that contains `chatbot/`):

```bash
cp chatbot/.env.example chatbot/.env
# Edit chatbot/.env: set GEMINI_API_KEY=... (from https://aistudio.google.com/apikey)
bash chatbot/run.sh
```

Open **http://127.0.0.1:8080**

The model is instructed to use skill output as **hints**, give **guided** (not full-solution) answers by default, and keep replies **short**.

First run creates `.venv-chatbot/` and installs `chatbot/requirements.txt`. Stop the server with **Ctrl+C**.

## Config

| Item | Notes |
|------|--------|
| `chatbot/.env` | `GEMINI_API_KEY=` required. Gitignored. |
| `GEMINI_MODEL` | Optional. If you get model `404` errors, set e.g. `GEMINI_MODEL=gemini-2.0-flash`. |
| `PORT` | Optional (default `8080`). |

If a bad `export GEMINI_API_KEY=...` is set in your shell, run `unset GEMINI_API_KEY` before starting.

## Notes

- `skills/execution_trace` is a small Intel-style subset for demos.
- No API key → `/api/chat` returns **503** with a short error.
