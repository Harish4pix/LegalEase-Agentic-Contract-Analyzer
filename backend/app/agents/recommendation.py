from ..models import ClauseRisk


class RecommendationAgent:
    """Checks that every identified risk has a practical negotiating action."""

    FALLBACKS = {
        "high": "Do not accept this provision unchanged. Ask a qualified lawyer to revise it and add clear limits, exceptions, and mutual obligations.",
        "medium": "Clarify the wording, add objective limits or timelines, and confirm the revised language in writing before signing.",
        "low": "Confirm the commercial details and keep the final agreed wording in the signed copy.",
    }

    def complete(self, risks: list[ClauseRisk]) -> list[ClauseRisk]:
        for risk in risks:
            if len(risk.recommendation.strip()) < 20:
                risk.recommendation = self.FALLBACKS[risk.risk_level]
        return risks
