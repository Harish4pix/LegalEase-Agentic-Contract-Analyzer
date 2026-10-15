from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from xml.sax.saxutils import escape

from ..models import AnalysisResult


RISK_COLORS = {
    "high": colors.HexColor("#B42318"),
    "medium": colors.HexColor("#B54708"),
    "low": colors.HexColor("#027A48"),
}


def build_pdf_report(analysis: AnalysisResult) -> bytes:
    output = BytesIO()
    document = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=f"LegalEase analysis — {analysis.filename}",
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Brand", parent=styles["Title"], textColor=colors.HexColor("#0B2B32"), fontSize=24, leading=28))
    styles.add(ParagraphStyle(name="RiskTitle", parent=styles["Heading2"], fontSize=13, leading=17, spaceAfter=5, textColor=colors.HexColor("#172B4D")))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8.5, leading=11, textColor=colors.HexColor("#596773")))
    styles.add(ParagraphStyle(name="BodyClean", parent=styles["BodyText"], fontSize=9.5, leading=13, alignment=TA_LEFT, spaceAfter=6))

    story = [
        Paragraph("LegalEase", styles["Brand"]),
        Paragraph("Agentic AI Contract Risk Analysis Report", styles["Heading2"]),
        Spacer(1, 5 * mm),
    ]
    metadata = [
        ["Contract", Paragraph(escape(analysis.filename), styles["BodyClean"])],
        ["Type", Paragraph(escape(analysis.contract_type), styles["BodyClean"])],
        ["Overall risk", f"{analysis.overall_risk_level.upper()} · {analysis.overall_risk_score}/100"],
        ["Reviewed", f"{analysis.clauses_reviewed} clauses · {len(analysis.risky_clauses)} flagged"],
    ]
    table = Table(metadata, colWidths=[34 * mm, 120 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F0F1")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#0B2B32")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C9D5D8")),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#9EB0B4")),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.extend([table, Spacer(1, 7 * mm), Paragraph("Executive summary", styles["Heading2"]), Paragraph(escape(analysis.summary), styles["BodyClean"]), Spacer(1, 4 * mm), Paragraph("Flagged clauses", styles["Heading2"])])

    if not analysis.risky_clauses:
        story.append(Paragraph("No material risk signals were identified by the selected analysis mode.", styles["BodyClean"]))

    for index, risk in enumerate(analysis.risky_clauses, 1):
        badge = Table([[risk.risk_level.upper(), f"{risk.risk_score}/100"]], colWidths=[25 * mm, 25 * mm])
        badge.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), RISK_COLORS[risk.risk_level]),
            ("TEXTCOLOR", (0, 0), (0, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("BOX", (0, 0), (-1, -1), 0.5, RISK_COLORS[risk.risk_level]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.extend([
            Spacer(1, 3 * mm),
            Paragraph(f"{index}. {escape(risk.title)}", styles["RiskTitle"]),
            badge,
            Spacer(1, 2 * mm),
            Paragraph(f"<b>Why it matters:</b> {escape(risk.explanation)}", styles["BodyClean"]),
            Paragraph(f"<b>Recommendation:</b> {escape(risk.recommendation)}", styles["BodyClean"]),
            Paragraph(f"<b>Contract text:</b> {escape(risk.clause_text[:1600])}", styles["Small"]),
        ])

    story.extend([
        Spacer(1, 8 * mm),
        Paragraph("Important notice", styles["Heading2"]),
        Paragraph(escape(analysis.disclaimer), styles["Small"]),
    ])
    document.build(story)
    return output.getvalue()
