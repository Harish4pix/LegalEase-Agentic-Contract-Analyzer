from ..models import ClauseRisk, RiskDistribution


class RiskScoringAgent:
    """Normalizes scores and calculates the contract's aggregate risk."""

    def calibrate(self, risks: list[ClauseRisk]) -> tuple[list[ClauseRisk], int, str, RiskDistribution]:
        for risk in risks:
            risk.risk_score = max(0, min(100, round(risk.risk_score)))
            risk.risk_level = self.level_for(risk.risk_score)

        distribution = RiskDistribution(
            high=sum(r.risk_level == "high" for r in risks),
            medium=sum(r.risk_level == "medium" for r in risks),
            low=sum(r.risk_level == "low" for r in risks),
        )
        if not risks:
            return risks, 0, "low", distribution

        top = sorted((r.risk_score for r in risks), reverse=True)
        # Critical provisions should not disappear inside a simple average.
        overall = round(0.55 * top[0] + 0.30 * sum(top[:3]) / min(3, len(top)) + 0.15 * sum(top) / len(top))
        return risks, overall, self.level_for(overall), distribution

    @staticmethod
    def level_for(score: int) -> str:
        if score >= 70:
            return "high"
        if score >= 40:
            return "medium"
        return "low"
