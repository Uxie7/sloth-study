# Sloth Study

Sloth Study turns a PDF or lecture notes into a private revision kit: a summary, flashcards, a scored quiz, and an audio revision brief.

The default workflow runs locally with Gemma through Ollama, Piper for speech when a voice model is installed, PyMuPDF for PDF extraction, and SQLite for storage. The Next.js frontend talks to a FastAPI backend.

For low-storage machines, use an installed Ollama model such as `gemma2:2b` and set `TTS_PROVIDER=none`. The summary, flashcards, quiz, and SQLite workflow remain available without downloading a voice model.

## Local setup

1. Install [Ollama](https://ollama.com/).
2. Pull the default model:

   ```bash
   ollama pull gemma3:4b
   ```

3. Download the Piper voice model configured in `.env.example`.
4. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Copy `.env.example` to `.env` and adjust model or provider settings if needed.
6. Start the API:

   ```bash
   uvicorn src.api:app --reload --port 8000
   ```

7. Start the frontend:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

8. Open `http://localhost:3000`.

The sample PDFs are in `samples/`. The default local configuration does not require internet access after Ollama, dependencies, and the Piper model have been installed. Set `SENTRY_DSN` only when hosted observability is wanted.

## Tests

Run the backend tests with:

```bash
pytest tests/
```

Run frontend checks with:

```bash
cd frontend
npm run lint
npm run build
```
