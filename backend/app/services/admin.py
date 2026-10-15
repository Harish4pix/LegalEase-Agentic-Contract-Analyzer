import base64
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
from pathlib import Path

from ..models import AnalysisResult


class AdminService:
    def __init__(self, data_file: Path, analyses_dir: Path, email: str, password: str, secret: str):
        self.data_file = data_file
        self.analyses_dir = analyses_dir
        self.email = email.lower()
        self.password = password
        self.secret = secret.encode()
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_file.exists():
            self._write({"contracts": {}, "clients": [], "team": [], "audit": []})

    def _read(self):
        try:
            return json.loads(self.data_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {"contracts": {}, "clients": [], "team": [], "audit": []}

    def _write(self, data):
        self.data_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def login(self, email: str, password: str) -> str | None:
        if not (hmac.compare_digest(email.lower(), self.email) and hmac.compare_digest(password, self.password)):
            return None
        payload = {"sub": self.email, "exp": int((datetime.now(timezone.utc) + timedelta(hours=8)).timestamp())}
        body = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode().rstrip("=")
        signature = hmac.new(self.secret, body.encode(), hashlib.sha256).hexdigest()
        self.audit("Admin signed in")
        return f"{body}.{signature}"

    def verify(self, token: str) -> bool:
        try:
            body, signature = token.split(".", 1)
            expected = hmac.new(self.secret, body.encode(), hashlib.sha256).hexdigest()
            payload = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
            return hmac.compare_digest(signature, expected) and payload.get("sub") == self.email and payload.get("exp", 0) > datetime.now(timezone.utc).timestamp()
        except (ValueError, TypeError, json.JSONDecodeError):
            return False

    def analyses(self):
        records = []
        for path in sorted(self.analyses_dir.glob("*.json"), reverse=True):
            try:
                records.append(AnalysisResult.model_validate_json(path.read_text(encoding="utf-8")))
            except (OSError, ValueError):
                continue
        return records

    def contracts(self):
        state = self._read()
        rows = []
        for analysis in self.analyses():
            meta = state["contracts"].get(analysis.contract_id, {})
            rows.append({
                "contract_id": analysis.contract_id, "filename": analysis.filename,
                "contract_type": analysis.contract_type, "risk_score": analysis.overall_risk_score,
                "risk_level": analysis.overall_risk_level, "findings": len(analysis.risky_clauses),
                "created_at": analysis.created_at, "status": meta.get("status", "pending"),
                "client": meta.get("client", "Unassigned"), "reviewer": meta.get("reviewer", "Unassigned"),
                "review_note": meta.get("review_note", ""), "expiry_date": meta.get("expiry_date", ""),
            })
        return rows

    def dashboard(self):
        contracts = self.contracts()
        status = {name: sum(c["status"] == name for c in contracts) for name in ["pending", "under_review", "approved", "rejected", "archived"]}
        risks = {level: sum(c["risk_level"] == level for c in contracts) for level in ["high", "medium", "low"]}
        avg = round(sum(c["risk_score"] for c in contracts) / len(contracts)) if contracts else 0
        upcoming = [c for c in contracts if c["expiry_date"] and c["status"] != "archived"][:5]
        return {"total": len(contracts), "average_risk": avg, "status": status, "risks": risks, "recent": contracts[:5], "alerts": upcoming}

    def update_contract(self, contract_id: str, changes: dict):
        if not any(c["contract_id"] == contract_id for c in self.contracts()):
            return None
        state = self._read()
        record = state["contracts"].setdefault(contract_id, {})
        record.update({k: v for k, v in changes.items() if v is not None})
        record["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._write(state)
        self.audit(f"Contract {contract_id[:8]} updated", changes)
        return next(c for c in self.contracts() if c["contract_id"] == contract_id)

    def directory(self, kind: str):
        return self._read()[kind]

    def add_directory(self, kind: str, entry: dict):
        state = self._read()
        item = {"id": hashlib.sha1(f'{kind}{entry["name"]}{datetime.now().isoformat()}'.encode()).hexdigest()[:10], **entry}
        state[kind].append(item)
        self._write(state)
        self.audit(f'{kind[:-1].title()} added: {entry["name"]}')
        return item

    def audit(self, action: str, details=None):
        state = self._read()
        state["audit"].insert(0, {"action": action, "details": details or {}, "actor": self.email, "timestamp": datetime.now(timezone.utc).isoformat()})
        state["audit"] = state["audit"][:250]
        self._write(state)

    def audit_log(self):
        return self._read()["audit"]
