# LegalEase — Agentic AI Contract Risk Analyzer

LegalEase is a working, multi-page full-stack contract review application. A user uploads a PDF, DOCX, or TXT contract; focused Python agents extract and segment the text, identify risky clauses, calibrate each risk from 0–100, add recommendations, compile a PDF report, and ground a contract-only chatbot in the completed analysis.

## What is included

- Adaptive React + Vite interface with drag-and-drop upload
- Five responsive routes: Home, Analyzer, How It Works, Solutions, and Security
- Mobile navigation, interactive contract-type explorer, FAQ accordion, loading pipeline, result filters, and expandable findings
- FastAPI backend with six single-purpose Python agents
- Low / medium / high clause risks and calibrated 0–100 scores
- Plain-language explanation and recommendation for every finding
- Downloadable, professionally formatted PDF analysis report
- Contract-only assistant with deterministic off-topic refusal
- PDF, DOCX, and TXT extraction; 10 MB default upload limit
- Gemini, Groq, Ollama, and no-key demo providers
- No database or paid service required
- Automated tests and a sample agreement

## Legal-firm admin portal

The public analyzer continues to work normally. Authorized firm users sign in separately at `/admin/login`. The protected portal provides portfolio metrics, contract tracking, review status and assignment, client and team directories, risk analytics, renewal alerts, PDF access, and an audit history.

Set `ADMIN_EMAIL`, `ADMIN_PASSWORD`, and `ADMIN_SECRET` in `.env`. For local demonstration only, the fallback login is `admin@legalease.local` with password `Admin@123`. Change these values before sharing or deploying the application.

## GitHub and production deployment

1. Copy `.env.example` to `.env` and add local secrets.
2. Create an empty GitHub repository.
3. Run `git init`, `git add .`, `git commit -m "Complete LegalEase platform"`, add the GitHub remote, and push the `main` branch.
4. In Render, create a Blueprint from the GitHub repository. The included `render.yaml` installs the Python and Node dependencies, builds React, and runs FastAPI as one web service.
5. Add `GEMINI_API_KEY`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, and the deployed URL as `FRONTEND_ORIGIN` in the hosting dashboard.

FastAPI serves the compiled React application in production, including direct routes such as `/analyzer`, `/admin/login`, and `/admin`.

## Agent pipeline

1. `DocumentIngestionAgent` validates and extracts the document.
2. `ClauseSegmentationAgent` splits it into reviewable provisions.
3. `RiskAnalysisAgent` identifies material legal/commercial issues.
4. `RiskScoringAgent` normalizes clause and overall scores.
5. `RecommendationAgent` ensures every finding has a usable action.
6. `ReportCompilerAgent` creates the executive summary; `ContractChatAgent` answers grounded follow-up questions.

The LLM analyzes batches of clauses. Scoring, validation, access control, document handling, report generation, and off-topic refusal stay in application code so they remain testable and predictable.

## Recommended free model

The default configuration uses **Gemini 2.5 Flash-Lite** through the Gemini Developer API. It is fast, has a free tier, supports long inputs, and works well with structured JSON. Actual free quotas can change by account, region, and model, so the app exposes the model through `.env` instead of hard-coding provider assumptions.

For confidential contracts, use **Ollama** locally because hosted free tiers may process or retain content under their provider terms. `qwen2.5:7b` is the included default example; larger local models generally improve legal nuance if your computer can run them.

Demo mode requires no API key, but it uses transparent keyword rules and is only meant to verify the complete workflow.

## Requirements

- Python 3.10 or newer
- Node.js 18 or newer
- npm

## Windows quick start

1. Extract the ZIP and open Command Prompt in the project folder.
2. Run:

```bat
setup_windows.bat
```

3. Open `.env`, add your Gemini API key, and save it. Get a key from Google AI Studio.
4. Start the application:

```bat
.venv\Scripts\activate
python start.py
```

5. Open `http://localhost:5173`.

To test without an API key, set `LLM_PROVIDER=demo` in `.env`.

## macOS / Linux quick start

```bash
chmod +x setup_unix.sh
./setup_unix.sh
source .venv/bin/activate
python start.py
```

Then open `http://localhost:5173`.

## Provider configuration

Copy `.env.example` to `.env` if the setup script did not do it.

### Gemini free tier (recommended)

1. Open Google AI Studio and sign in.
2. Open **Dashboard → API Keys** and choose **Create API key**.
3. Copy the new key. Do not paste it into frontend code or share it publicly.
4. Open the project `.env` file and use the configuration below.

```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini-3.5-flash-lite
GEMINI_API_KEY=your_key
```

Save `.env`, stop the running app with `Ctrl+C`, and start it again with `python start.py`. The Analyzer page should show the Gemini model instead of Demo rules.

### Groq

```env
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
GROQ_API_KEY=your_key
```

### Ollama (fully local)

Install Ollama, then run:

```bash
ollama pull qwen2.5:7b
```

Configure:

```env
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5:7b
OLLAMA_BASE_URL=http://localhost:11434
```

## Run frontend and backend separately

Terminal 1:

```bash
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m uvicorn backend.app.main:app --reload --port 8000
```

Terminal 2:

```bash
npm run dev
```

API documentation is available at `http://localhost:8000/docs`.

## Test and build

```bash
python -m unittest discover -s backend/tests -v
npm run build
```

## Privacy and production notes

- Uploaded originals are processed in memory and are not saved by this project.
- Analysis JSON is stored locally in `backend/data/analyses` so report and chat routes work after refresh.
- Do not send confidential contracts to a hosted free API without reviewing its current data-use terms. Prefer Ollama for private/offline use.
- Add authentication, encrypted storage, rate limiting, malware scanning, OCR, audit logs, retention controls, and jurisdiction-specific lawyer review before production use.
- AI review can miss context or produce incorrect findings. LegalEase clearly presents its output as informational, not legal advice.

## Project structure

```text
legalease/
├── src/                         React interface
│   ├── pages/                   Five responsive product pages
│   └── components/              Navigation, footer, chatbot, and risk UI
├── backend/app/agents/          Single-purpose Python agents
├── backend/app/services/        LLM, pipeline, storage, and PDF services
├── backend/tests/               Automated tests
├── sample_contracts/            Local test contract
├── .env.example                 Provider configuration
├── setup_windows.bat            Windows setup
├── setup_unix.sh                macOS/Linux setup
└── start.py                     Starts both services
```
