from typing import Literal

from pydantic import BaseModel, Field


RiskLevel = Literal["low", "medium", "high"]


class ContractClause(BaseModel):
    id: str
    title: str
    text: str


class ClauseRisk(BaseModel):
    id: str
    title: str
    clause_text: str
    risk_level: RiskLevel
    risk_score: int = Field(ge=0, le=100)
    risk_factors: list[str] = Field(default_factory=list)
    explanation: str
    recommendation: str
    confidence: int = Field(default=75, ge=0, le=100)


class RiskDistribution(BaseModel):
    high: int = 0
    medium: int = 0
    low: int = 0


class AnalysisResult(BaseModel):
    contract_id: str
    filename: str
    contract_type: str
    summary: str
    overall_risk_score: int = Field(ge=0, le=100)
    overall_risk_level: RiskLevel
    clauses_reviewed: int
    contract_clauses: list[ContractClause] = Field(default_factory=list)
    risky_clauses: list[ClauseRisk]
    risk_distribution: RiskDistribution
    model_provider: str
    processing_seconds: float
    created_at: str
    disclaimer: str = (
        "This AI review is for informational purposes and is not a substitute "
        "for advice from a qualified lawyer in the relevant jurisdiction."
    )


class ChatRequest(BaseModel):
    contract_id: str
    message: str = Field(min_length=2, max_length=2000)


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = Field(default_factory=list)
    refused: bool = False


class AdminLoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=6, max_length=200)


class ContractAdminUpdate(BaseModel):
    status: Literal["pending", "under_review", "approved", "rejected", "archived"] | None = None
    client: str | None = Field(default=None, max_length=120)
    reviewer: str | None = Field(default=None, max_length=120)
    review_note: str | None = Field(default=None, max_length=2000)
    expiry_date: str | None = Field(default=None, max_length=20)


class DirectoryEntry(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(default="", max_length=160)
    role: str = Field(default="Client", max_length=80)
