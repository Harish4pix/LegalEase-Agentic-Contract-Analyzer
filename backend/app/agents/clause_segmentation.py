import re

from ..models import ContractClause


class ClauseSegmentationAgent:
    """Splits contract text into reviewable clauses without interpreting risk."""

    HEADING = re.compile(
        r"(?im)^(?P<heading>(?:section\s+)?(?:\d+(?:\.\d+)*|[A-Z])[.)]?\s+"
        r"[A-Z][^\n]{2,90}|[A-Z][A-Z /&-]{4,70})$"
    )

    def segment(self, text: str) -> list[ContractClause]:
        matches = list(self.HEADING.finditer(text))
        clauses: list[ContractClause] = []

        if matches:
            for index, match in enumerate(matches):
                start = match.start()
                end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
                raw = text[start:end].strip()
                if len(raw) < 45:
                    continue
                heading = match.group("heading").strip()
                body = raw[len(heading):].strip(" \n:-") or raw
                clauses.extend(self._split_long(heading, body, len(clauses)))
        else:
            paragraphs = [p.strip() for p in re.split(r"\n{1,}|(?<=[.;])\s{2,}", text) if p.strip()]
            buffer = ""
            for paragraph in paragraphs:
                if len(buffer) + len(paragraph) < 1800:
                    buffer = f"{buffer}\n{paragraph}".strip()
                else:
                    clauses.append(self._clause(len(clauses), "Contract provision", buffer))
                    buffer = paragraph
            if buffer:
                clauses.append(self._clause(len(clauses), "Contract provision", buffer))

        return clauses or [self._clause(0, "Contract", text[:6000])]

    def _split_long(self, heading: str, body: str, start_index: int) -> list[ContractClause]:
        if len(body) <= 2600:
            return [self._clause(start_index, heading, body)]
        parts = [body[i : i + 2400] for i in range(0, len(body), 2400)]
        return [
            self._clause(start_index + i, f"{heading} — part {i + 1}", part)
            for i, part in enumerate(parts)
        ]

    @staticmethod
    def _clause(index: int, title: str, text: str) -> ContractClause:
        return ContractClause(id=f"clause-{index + 1}", title=title[:100], text=text.strip())
