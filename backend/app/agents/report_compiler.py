from ..models import ClauseRisk


class ReportCompilerAgent:
    """Creates a concise executive summary from scored clause findings."""

    def summarize(self, contract_type: str, risks: list[ClauseRisk]) -> str:
        if not risks:
            return f"No material risk signals were identified in this {contract_type.lower()}. Manual legal review is still recommended."
        ordered = sorted(risks, key=lambda item: item.risk_score, reverse=True)
        top = ", ".join(r.title for r in ordered[:3])
        high_count = sum(r.risk_level == "high" for r in risks)
        return (
            f"The review identified {len(risks)} provision(s) requiring attention, "
            f"including {high_count} high-risk item(s). Priority review areas: {top}."
        )
