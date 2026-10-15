from contextlib import asynccontextmanager
from io import BytesIO
import re

from dotenv import load_dotenv

load_dotenv()

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse

from .agents.chat_assistant import ContractChatAgent
from .config import get_settings
from .models import AdminLoginRequest, AnalysisResult, ChatRequest, ChatResponse, ContractAdminUpdate, DirectoryEntry
from .services.admin import AdminService
from .services.llm_client import LLMClient
from .services.pdf_report import build_pdf_report
from .services.pipeline import ContractAnalysisPipeline
from .services.storage import AnalysisStore


settings = get_settings()
pipeline = ContractAnalysisPipeline(settings)
store = AnalysisStore(settings.data_dir)
chat_agent = ContractChatAgent(LLMClient(settings))
admin = AdminService(settings.admin_data_file, settings.data_dir, settings.admin_email, settings.admin_password, settings.admin_secret)


def require_admin(authorization: str = Header(default="")):
    token = authorization.removeprefix("Bearer ").strip()
    if not admin.verify(token):
        raise HTTPException(401, "Admin session is missing or expired.")
    return True


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="LegalEase API",
    version="1.0.0",
    description="Agentic contract risk analysis API",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "provider": pipeline.client.active_provider}


@app.get("/api/config")
async def config() -> dict:
    return {
        "provider": pipeline.client.active_provider,
        "model": settings.model if pipeline.client.active_provider != "demo" else "keyword demo",
        "max_upload_mb": settings.max_upload_mb,
        "supported_files": ["PDF", "DOCX", "TXT"],
    }


@app.post("/api/analyze", response_model=AnalysisResult)
async def analyze_contract(file: UploadFile = File(...)) -> AnalysisResult:
    filename = re.sub(r"[^A-Za-z0-9._ -]", "_", file.filename or "contract")[:160]
    content = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
    if len(content) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, f"File exceeds the {settings.max_upload_mb} MB upload limit.")
    try:
        return await pipeline.run(filename, content)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(502, f"Analysis service error: {str(exc)[:220]}") from exc


@app.get("/api/analyses/{contract_id}", response_model=AnalysisResult)
async def get_analysis(contract_id: str) -> AnalysisResult:
    analysis = store.get(contract_id)
    if not analysis:
        raise HTTPException(404, "Analysis not found.")
    return analysis


@app.get("/api/analyses/{contract_id}/report")
async def download_report(contract_id: str) -> StreamingResponse:
    analysis = store.get(contract_id)
    if not analysis:
        raise HTTPException(404, "Analysis not found.")
    filename = re.sub(r"[^A-Za-z0-9._-]", "_", analysis.filename.rsplit(".", 1)[0])
    return StreamingResponse(
        BytesIO(build_pdf_report(analysis)),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}_LegalEase_Report.pdf"'},
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    analysis = store.get(request.contract_id)
    if not analysis:
        raise HTTPException(404, "Analyze a contract before using the assistant.")
    try:
        return await chat_agent.answer(analysis, request.message)
    except Exception as exc:
        raise HTTPException(502, f"Assistant service error: {str(exc)[:220]}") from exc


@app.post("/api/admin/login")
async def admin_login(request: AdminLoginRequest) -> dict:
    token = admin.login(request.email, request.password)
    if not token:
        raise HTTPException(401, "Incorrect admin email or password.")
    return {"token": token, "admin": {"email": settings.admin_email, "firm": "LegalEase Legal Operations"}}


@app.get("/api/admin/dashboard", dependencies=[Depends(require_admin)])
async def admin_dashboard() -> dict:
    return admin.dashboard()


@app.get("/api/admin/contracts", dependencies=[Depends(require_admin)])
async def admin_contracts() -> list[dict]:
    return admin.contracts()


@app.patch("/api/admin/contracts/{contract_id}", dependencies=[Depends(require_admin)])
async def admin_update_contract(contract_id: str, request: ContractAdminUpdate) -> dict:
    result = admin.update_contract(contract_id, request.model_dump())
    if not result:
        raise HTTPException(404, "Contract not found.")
    return result


@app.get("/api/admin/{kind}", dependencies=[Depends(require_admin)])
async def admin_directory(kind: str) -> list[dict]:
    if kind not in {"clients", "team", "audit"}:
        raise HTTPException(404, "Admin resource not found.")
    return admin.audit_log() if kind == "audit" else admin.directory(kind)


@app.post("/api/admin/{kind}", dependencies=[Depends(require_admin)])
async def admin_add_directory(kind: str, request: DirectoryEntry) -> dict:
    if kind not in {"clients", "team"}:
        raise HTTPException(404, "Admin resource not found.")
    return admin.add_directory(kind, request.model_dump())


# In production, FastAPI serves the Vite build as a single deployable service.
frontend_dist = settings.data_dir.parents[2] / "dist"


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_frontend(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(404, "API route not found.")
    requested = (frontend_dist / full_path).resolve()
    if requested.is_file() and frontend_dist.resolve() in requested.parents:
        return FileResponse(requested)
    index = frontend_dist / "index.html"
    if index.exists():
        return FileResponse(index)
    raise HTTPException(404, "Frontend build not found. Run npm run build.")
