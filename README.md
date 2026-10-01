# AI-Powered Code Integrity & Plagiarism Intelligence

## Problem
Text-diff plagiarism checkers are beaten by renaming variables, reformatting or lightly editing code. Teachers need a tool that compares *logic*, explains its findings, and leaves the judgement to a human.

## Solution
Teachers upload many submissions; the backend normalises each file (comments, whitespace, identifiers, literals), then scores every pair on four independent axes and explains *why* the pair was flagged. All results are labelled **potential similarity** and **require human review** – similarity is never treated as proof.

## Features
Landing/login (teacher & student roles) · multi-file upload · 4 scores + weighted overall · configurable risk bands · evidence-based "Why flagged?" · side-by-side highlighted diff · interactive similarity matrix · dashboard (stats, histogram, language pie, top pairs, network graph) · history · PDF report · demo data.

## Architecture
`React (Vite) → FastAPI → services/pipeline → analyzers (normalize, similarity) → SQLAlchemy/SQLite → dashboard`. Uploaded code is only read as text – **never executed**.

## Algorithm
1. **Normalise** – strip comments (string-aware), tokenise, map user identifiers → `ID`, numbers → `NUM`, strings → `STR`; keep keywords and well-known library names.
2. **Text** – line-sequence ratio on comment-free, whitespace-collapsed source.
3. **Token** – Dice coefficient over 4-gram shingles of the normalised token stream (rename-proof).
4. **Structural** – Python: pre-order AST node-type sequence (no names) → 0.6·sequence ratio + 0.4·node-profile cosine. Java/C/C++: same measure over a keyword/punctuation skeleton (fallback; swap in Tree-sitter in `structural()`).
5. **Semantic** – TF-IDF (uni+bigrams of normalised tokens, sublinear tf) fitted on the batch, cosine similarity. Vocabulary/operation-level similarity; a local embedding model (e.g. UniXcoder) can replace it behind the same function.
6. **Overall** = `0.20·text + 0.25·token + 0.30·structural + 0.25·semantic` (`backend/app/config.py`, or env `SIM_WEIGHTS`). Risk bands: 0–30 Low, 30–60 Moderate, 60–80 High, 80–100 Very High (`RISK_BANDS`).
7. **Explanations** are generated only from measurements (rename map from aligned lines, control-keyword counts, function counts, operator profiles, aligned-line coverage).

## Setup
```bash
# Backend (Python 3.10+)
cd backend
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r ../requirements.txt
uvicorn app.main:app --reload --port 8000               # creates SQLite DB + demo users on start

# Frontend (Node 18+), new terminal
cd frontend && npm install && npm run dev               # http://localhost:5173
```
Database: SQLite file `backend/integrity.db`, created automatically. Optional: `python -m app.services.seed` (from `backend/`) pre-loads the 5 demo files.

**Logins:** `teacher / teacher123` · `alice, bob, carol, dave, eve / student123`.

## API (Swagger at http://localhost:8000/docs)
`GET /`, `GET /health`, `POST /api/auth/login`, `POST /api/submissions/upload`, `POST /api/analyze` (one vs others), `POST /api/analyze/multiple` (teacher, all pairs), `GET /api/submissions[/id]`, `GET /api/comparisons[/id]`, `GET /api/dashboard`, `GET /api/reports/{id}` (PDF), plus `GET /api/matrix`, `POST /api/demo/load`.

## Testing
`cd backend && python tests/test_engine.py` (or `pytest`).

## Demo (3–5 min)
1. Login as teacher → **Upload** → *Load & analyze demo data* (or upload the 5 files in `backend/app/sample_data/`, select all, Analyze).
2. Dashboard: stats, charts, network. 3. **Matrix** → click the alice↔bob cell (very high risk: same logic, renamed variables, comments added).
4. Show the 4 scores, "Why was this pair flagged?", side-by-side highlights. 5. Download the PDF. 6. Log in as a student to show the privacy-preserving view.

## 3-minute pitch
*Problem* (0:30): diff tools fail when variables are renamed. *Solution* (0:30): we compare normalised tokens, ASTs and TF-IDF semantics. *Live demo* (1:30): matrix → pair → explanation → PDF. *Responsible AI* (0:30): flags "potential similarity", human decides, students never see others' code.

## Innovation
Multi-level scoring with configurable weights · evidence-based explanations (no invented reasons) · rename detection from aligned lines · privacy-aware student view · execution-free, secure-by-design pipeline.

## Judge Q&A
- **False positives?** Short/standard algorithms look alike; we show evidence, use bands, and require human review. **Next:** template-code exclusion.
- **Why not just MOSS/JPlag?** Those are token tools; we add explainable multi-signal scores, dashboard, roles and reports, locally and free.
- **Is "semantic" real AI?** Currently TF-IDF vectors (fast, offline); the module is built to swap in a code-embedding model.
- **AI-generated code?** Out of scope for MVP; listed as future work (probabilistic signal only).
- **Security?** Extension allow-list, size cap, random stored names, sanitised names, no execution, JWT auth.

## Future improvements
Tree-sitter ASTs for Java/C/C++ · code embeddings (UniXcoder) · template-code exclusion · Git-history and style-shift analysis · AI-generated-code signal · cross-language matching · LMS integration.
