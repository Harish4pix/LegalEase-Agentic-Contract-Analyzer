from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4

from ..agents.clause_segmentation import ClauseSegmentationAgent
from ..agents.document_ingestion import DocumentIngestionAgent
from ..agents.recommendation import RecommendationAgent
from ..agents.report_compiler import ReportCompilerAgent
from ..agents.risk_analysis import RiskAnalysisAgent
from ..agents.risk_scoring import RiskScoringAgent
from ..config import Settings
from ..models import AnalysisResult
from .llm_client import LLMClient
from .storage import AnalysisStore


class ContractAnalysisPipeline:
    """Runs each single-purpose agent in a predictable, testable order."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.ingestion = DocumentIngestionAgent()
        self.segmentation = ClauseSegmentationAgent()
        self.client = LLMClient(settings)
        self.analysis = RiskAnalysisAgent(self.client)
        self.scoring = RiskScoringAgent()
        self.recommendations = RecommendationAgent()
        self.report = ReportCompilerAgent()
        self.store = AnalysisStore(settings.data_dir)

    async def run(self, filename: str, content: bytes) -> AnalysisResult:
        started = perf_counter()
        text = self.ingestion.extract(filename, content)
        if len(text) > self.settings.max_contract_chars:
            raise ValueError(
                f"This contract is too long for the current limit ({self.settings.max_contract_chars:,} characters)."
            )
        clauses = self.segmentation.segment(text)
        contract_type, findings = await self.analysis.analyze(clauses)
        findings, score, level, distribution = self.scoring.calibrate(findings)
        findings = self.recommendations.complete(findings)

        result = AnalysisResult(
            contract_id=str(uuid4()),
            filename=filename,
            contract_type=contract_type,
            summary=self.report.summarize(contract_type, findings),
            overall_risk_score=score,
            overall_risk_level=level,
            clauses_reviewed=len(clauses),
            contract_clauses=clauses,
            risky_clauses=sorted(findings, key=lambda risk: risk.risk_score, reverse=True),
            risk_distribution=distribution,
            model_provider=self.client.active_provider,
            processing_seconds=round(perf_counter() - started, 2),
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self.store.save(result)
        return result
