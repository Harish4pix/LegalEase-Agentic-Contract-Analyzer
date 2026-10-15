import json
from pathlib import Path

from ..models import AnalysisResult


class AnalysisStore:
    def __init__(self, directory: Path):
        self.directory = directory
        self.directory.mkdir(parents=True, exist_ok=True)

    def save(self, analysis: AnalysisResult) -> None:
        target = self.directory / f"{analysis.contract_id}.json"
        target.write_text(analysis.model_dump_json(indent=2), encoding="utf-8")

    def get(self, contract_id: str) -> AnalysisResult | None:
        if not contract_id.replace("-", "").isalnum():
            return None
        target = self.directory / f"{contract_id}.json"
        if not target.exists():
            return None
        return AnalysisResult.model_validate(json.loads(target.read_text(encoding="utf-8")))
