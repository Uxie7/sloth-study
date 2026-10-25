# Sloth Study — 3-Phase Build Plan

> **Read before touching code.** Nothing gets implemented until the user reviews and approves each phase.
> Stack: Python 3.11 backend · Next.js 16 (JS) frontend · Ollama + Gemma · PyMuPDF · Piper · SQLite

---

## Design Token Reference (from `index.html`)

| Token | Value |
|---|---|
| `--bg` | `#E7EBE2` |
| `--surface` | `#F3F5EF` |
| `--ink` | `#2B2622` |
| `--muted` | `#625D55` |
| `--line` | `#C2CABB` |
| `--accent` | `#2F5D50` |
| `--tint` | `#D3DFD2` |
| `--onaccent` | `#F3F5EF` |
| `--bad` | `#8A3B2E` |
| `--serif` | `Charter, "Bitstream Charter", Cambria, serif` |

Dark mode tokens already exist in `index.html` and will be ported to `globals.css`.

---

## Repository Layout (target)

```
sloth-study/
├─ frontend/                     ← Next.js 16 app (already exists)
│  └─ src/app/
│     ├─ globals.css             ← design system (Phase 1)
│     ├─ layout.js               ← root layout + fonts
│     ├─ page.js                 ← Home page (landing)
│     ├─ library/page.js         ← Kit library
│     ├─ upload/page.js          ← Upload + build trigger
│     ├─ kit/[id]/page.js        ← Kit viewer (summary/cards/quiz/audio)
│     └─ components/
│        ├─ Header.js
│        ├─ FlashCard.js         ← 3-D flip card
│        ├─ Quiz.js
│        ├─ AudioPlayer.js
│        └─ ProgressView.js
├─ src/                          ← Python backend
│  ├─ pipeline.py                ← build_kit() orchestration
│  ├─ domain/
│  │  ├─ schemas.py              ← Pydantic models
│  │  ├─ chunker.py
│  │  ├─ prompts.py
│  │  └─ scoring.py
│  ├─ adapters/
│  │  ├─ interfaces.py           ← Protocol definitions
│  │  ├─ llm_ollama.py
│  │  ├─ pdf_pymupdf.py
│  │  ├─ tts_piper.py
│  │  ├─ tts_elevenlabs.py
│  │  └─ store_sqlite.py
│  ├─ api.py                     ← FastAPI server (replaces Streamlit)
│  ├─ config.py
│  └─ observability.py
├─ samples/                      ← test PDFs (unzipped from zip)
├─ data/                         ← SQLite + audio (gitignored)
├─ models/                       ← Piper voice (gitignored)
├─ tests/
│  └─ test_pipeline_smoke.py
├─ .env.example
└─ requirements.txt
```

> **Key deviation from SLOTH_STUDY.md §3:** The doc says Streamlit; you said Next.js. We replace the UI layer with Next.js + a thin **FastAPI** JSON API server that the frontend talks to. The Python layers (domain, adapters, pipeline) are **unchanged**. The arch diagram still holds; "Layer 1: Presentation" is now Next.js + FastAPI instead of Streamlit.

---

## Phase 1 — Foundation: Design System + Core Python Backend

**Goal:** The backend pipeline works end-to-end in a terminal; the Next.js app renders the landing page, library, and upload shell — all pixel-matched to `index.html`.

### 1A: Frontend Shell (Next.js)

**Files to create/modify:**

| File | What changes |
|---|---|
| `frontend/src/app/globals.css` | Replace placeholder CSS with full design system from `index.html` — all CSS custom properties, typography, `.btn`, `.drop`, `.tabs`, `.deck`, `.opt`, `.player`, responsive breakpoints |
| `frontend/src/app/layout.js` | Import Charter / system-serif via Google Fonts fallback; set `<html lang="en">`; mount `<Header>` |
| `frontend/src/app/components/Header.js` | Logo + nav (Home / Library / New kit) matching `index.html` header |
| `frontend/src/app/page.js` | Landing page: hero grid, `.out` output list, two "band" sections — all content from `index.html` |
| `frontend/src/app/library/page.js` | Static shell: `<h1>Your kits</h1>` + empty `.list` + "Make a new kit" button |
| `frontend/src/app/upload/page.js` | Upload shell: drop zone, voice radio group, Build/Sample buttons (all disabled / no backend yet) |

**Testing Phase 1A:**
- `npm run dev` in `frontend/`
- Visual diff against `index.html` in a browser — colors, fonts, spacing must match
- All nav links route without 404

---

### 1B: Python Backend Core

**Files to create:**

| File | What it does |
|---|---|
| `src/domain/schemas.py` | Pydantic v2 models: `Flashcard`, `QuizQuestion`, `ChunkOutput`, `Summary`, `Kit` (verbatim from §9) |
| `src/domain/chunker.py` | `chunk_text(text, max_tokens=1500) → list[str]` — split on paragraph boundaries, tiktoken for counting |
| `src/domain/prompts.py` | `chunk_prompt(chunk, idx)` and `summary_prompt(key_points)` — few-shot examples baked in, grounding instruction, JSON-only output |
| `src/domain/scoring.py` | `score_quiz(quiz, answers) → int` — pure function, no I/O |
| `src/adapters/interfaces.py` | Protocol classes: `LLM`, `TTS`, `PdfParser`, `Store` |
| `src/adapters/llm_ollama.py` | `OllamaLLM.generate_json()` — openai SDK pointed at `LLM_BASE_URL`; 1 retry on Pydantic failure |
| `src/adapters/pdf_pymupdf.py` | `PyMuPdfParser.extract(bytes) → str` |
| `src/adapters/tts_piper.py` | `PiperTTS.speak(text, out_path) → Path` — subprocess call to piper binary |
| `src/adapters/tts_elevenlabs.py` | `ElevenLabsTTS.speak()` — guarded by try/except + fallback to Piper |
| `src/adapters/store_sqlite.py` | `SqliteStore`: `save_kit`, `get_kit`, `list_kits` — creates `data/sloth.db` on first run |
| `src/config.py` | `python-dotenv` loader; exports typed constants |
| `src/observability.py` | No-op when `SENTRY_DSN` is empty; `init_sentry()` + `span(name)` context manager |
| `src/pipeline.py` | `build_kit(file_bytes, filename, tts_provider) → Kit` — parallel chunks (ThreadPoolExecutor, max 3 workers), progress callback |
| `.env.example` | All vars from §12 |
| `requirements.txt` | `openai pymupdf pydantic python-dotenv fastapi uvicorn piper-tts sentry-sdk tiktoken` |

**Testing Phase 1B (smoke test — terminal only):**

```python
# tests/test_pipeline_smoke.py — Phase 1 subset
def test_chunker_splits_correctly():
    ...  # assert len(chunks) and each chunk <= 1500 tokens

def test_schemas_valid():
    ...  # construct a Kit from fixture JSON, assert no ValidationError

def test_pdf_extract_nonempty():
    # uses samples/finance-basics.pdf
    parser = PyMuPdfParser()
    text = parser.extract(open("samples/finance-basics.pdf","rb").read())
    assert len(text) > 100
```

Run: `pytest tests/ -k "phase1"` → all green before Phase 2.

---

## Phase 2 — Integration: FastAPI + Full UI

**Goal:** Upload a PDF in the browser, watch progress, see real summary/flashcards/quiz/audio from Gemma. Kits saved to SQLite and viewable from Library.

### 2A: FastAPI API Layer

| File | Endpoints |
|---|---|
| `src/api.py` | `POST /api/kits` — accepts `multipart/form-data` (pdf file + tts_provider), streams SSE progress events, returns `kit_id` |
| | `GET /api/kits` — returns `list[{id, title, created_at}]` |
| | `GET /api/kits/{id}` — returns full `Kit` JSON |
| | `GET /api/audio/{id}` — streams the `.wav` file |

SSE event shape:
```json
{ "step": "chunking", "pct": 15, "note": "Splitting into 6 sections…" }
{ "step": "cards", "pct": 45, "note": "8 cards written so far." }
{ "step": "done", "pct": 100, "kit_id": "abc123" }
```

### 2B: Next.js Pages

| File | What it does |
|---|---|
| `frontend/src/app/upload/page.js` | Sends file to `POST /api/kits`; opens SSE stream; shows `<ProgressView>` |
| `frontend/src/app/components/ProgressView.js` | `.steps` list + `.pbar` exactly like `index.html` §v-processing |
| `frontend/src/app/kit/[id]/page.js` | Fetches `GET /api/kits/{id}`; renders tabs: Summary / Flashcards / Quiz / Audio |
| `frontend/src/app/components/FlashCard.js` | 3-D CSS flip card — `.deck`, `.deck-in`, `.face`, `.face.back` — with Prev / Again / Got it |
| `frontend/src/app/components/Quiz.js` | `.opt` buttons, right/wrong state, score screen, retry |
| `frontend/src/app/components/AudioPlayer.js` | `<audio>` element + custom Play/Pause bar matching `.player` styles |
| `frontend/src/app/library/page.js` | Fetches `GET /api/kits`; renders `.list` of `.row` buttons linking to `/kit/[id]` |

**`next.config.mjs` additions:**
```js
rewrites: async () => [
  { source: '/api/:path*', destination: 'http://localhost:8000/api/:path*' }
]
```
This proxies `/api/*` to the FastAPI server during dev, no CORS changes needed.

### 2C: Sample PDF wiring
- Unzip `four_separate_study_pdfs.zip` → `samples/`
- Add "Use a sample" button logic: `fetch('/api/kits', { method:'POST', body: sampleFormData })`
- Hardcode the 3–4 sample filenames as buttons

**Testing Phase 2 (integration):**

```python
# tests/test_pipeline_smoke.py — Phase 2 additions
@pytest.mark.integration  # needs Ollama running
def test_build_kit_finance():
    pdf = open("samples/finance-basics.pdf","rb").read()
    kit = build_kit(pdf, "finance-basics.pdf")
    assert len(kit.flashcards) >= 10
    assert len(kit.quiz) >= 5
    assert all(len(q.options) == 4 for q in kit.quiz)

def test_retry_on_bad_json():
    # mock LLM to return garbage once then valid JSON
    ...
    assert kit is not None  # must not crash

def test_sqlite_roundtrip():
    store = SqliteStore(":memory:")
    store.save_kit(fixture_kit)
    loaded = store.get_kit(fixture_kit.id)
    assert loaded.title == fixture_kit.title
```

Browser smoke:
1. Start `uvicorn src.api:app --port 8000`
2. Start `npm run dev` in `frontend/`
3. Open `http://localhost:3000` — landing page matches design
4. Upload `samples/finance-basics.pdf` → progress bar → kit view
5. Flip 3 cards, answer quiz, press Play on audio

---

## Phase 3 — Polish, Resilience & Acceptance Criteria

**Goal:** Every bullet in §16 passes. Optional ElevenLabs toggle works. Sentry no-ops when DSN is empty. README is complete.

### 3A: Resilience hardening
- Verify retry-once logic in `OllamaLLM` — unit test with mocked bad JSON
- Verify `observability.py` makes zero network calls when `SENTRY_DSN=""` (mock `socket`)
- Verify ElevenLabs fallback: if key missing or network down → silently use Piper + show notice in UI

### 3B: UI polish
- Dark mode CSS vars wired (already in globals, test with OS dark mode)
- Reduced-motion media query on flip transition
- Responsive: single-column on < 820 px (matches `index.html` `@media` breakpoint)
- Error state components: toast/banner for "chunk failed, skipped" events from SSE
- "Running on this computer with gemma3:4b. No internet needed." chip on upload page

### 3C: Docs
- `README.md`: local setup steps verbatim from §16 acceptance criteria bullet 8
- `.env.example`: all vars with comments

### 3D: Sample PDF smoke tests (§16 full run)
Run against all 3 sample PDFs with **network disabled** (Windows: disable Wi-Fi adapter):

| Test | Pass condition |
|---|---|
| 10-page PDF → kit | Summary + ≥10 flashcards + 5-question quiz + audio file exists |
| Every flashcard | `len(question) >= 5`, `len(answer) <= 200` (Pydantic already enforces) |
| Every quiz question | Exactly 4 options, `0 ≤ correct_index ≤ 3` |
| Bad JSON chunk | Skip without crash, remaining kit complete |
| `.env` model swap | Change `LLM_MODEL=gemma3:12b`, restart server, upload → kit produced |
| SQLite persistence | Restart server, library shows previous kit |
| `SENTRY_DSN=` (empty) | `tcpdump`/Wireshark or mock shows zero outbound telemetry calls |

**Testing Phase 3 (full acceptance suite):**

```python
# tests/test_pipeline_smoke.py — Phase 3 full
@pytest.mark.parametrize("pdf", ["finance-basics.pdf", "tech-topic.pdf", "domain3.pdf"])
@pytest.mark.offline  # marker reminder: run with network off
def test_acceptance_all_samples(pdf):
    pdf_bytes = open(f"samples/{pdf}", "rb").read()
    kit = build_kit(pdf_bytes, pdf)
    assert len(kit.flashcards) >= 10
    assert len(kit.quiz) >= 5
    assert kit.audio_path is not None
    assert all(len(q.options) == 4 for q in kit.quiz)

def test_sentry_no_calls_when_dsn_empty(monkeypatch):
    monkeypatch.setenv("SENTRY_DSN", "")
    import src.observability as obs
    obs.init_sentry()
    # assert sentry_sdk.Hub.current.client is None
    ...
```

---

## Parallel tracks (no dependencies on each other)

```
Phase 1A (frontend shell) ──┐
                            ├─→ Phase 2 (integration)
Phase 1B (Python backend) ──┘
                                └─→ Phase 3 (polish + acceptance)
```

---

## What we are NOT building (hard stop)

- No fine-tuning
- No auth / user accounts
- No vector DB / chat-with-notes
- No multi-file upload
- No mobile-specific polish beyond the one existing `@media` breakpoint
- No Streamlit (replaced by Next.js + FastAPI)

---

## Open questions before implementation

1. **Samples:** The zip `four_separate_study_pdfs.zip` is in root. Should I unzip it into `samples/` now, or do you want to do that?
2. **Piper binary:** Where is the Piper executable on this machine? (needed to wire `tts_piper.py`)
3. **Ollama:** Is Ollama already installed and is `gemma3:4b` pulled? (`ollama list`)
4. **Port:** FastAPI on `8000`, Next.js on `3000` — any conflicts?
5. **ElevenLabs:** Do you have an API key to test the toggle, or should we stub it out and skip that during dev?
