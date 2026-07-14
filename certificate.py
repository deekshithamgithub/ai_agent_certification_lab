"""
Generates a polished PDF certificate for users who pass the final
certification exam, using reportlab.
"""

from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


NAVY = HexColor("#0f172a")
GOLD = HexColor("#c9a227")
SLATE = HexColor("#475569")
LIGHT = HexColor("#f8fafc")


def generate_certificate(filepath, full_name, cert_id, score, issue_date):
    page_size = landscape(letter)
    width, height = page_size
    c = canvas.Canvas(filepath, pagesize=page_size)

    # Background
    c.setFillColor(LIGHT)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # Outer border
    margin = 0.4 * inch
    c.setStrokeColor(NAVY)
    c.setLineWidth(3)
    c.rect(margin, margin, width - 2 * margin, height - 2 * margin, fill=0, stroke=1)

    # Inner gold border
    inner_margin = 0.55 * inch
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.5)
    c.rect(inner_margin, inner_margin, width - 2 * inner_margin, height - 2 * inner_margin, fill=0, stroke=1)

    # Header
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - 1.1 * inch, "AI AGENT CERTIFICATION LAB")

    c.setFont("Helvetica", 11)
    c.setFillColor(SLATE)
    c.drawCentredString(width / 2, height - 1.35 * inch, "Certificate of Completion")

    # Gold divider
    c.setStrokeColor(GOLD)
    c.setLineWidth(1)
    c.line(width / 2 - 1.5 * inch, height - 1.55 * inch, width / 2 + 1.5 * inch, height - 1.55 * inch)

    # Main title
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(width / 2, height - 2.3 * inch, "Certified AI Agent Developer")

    # Presented to
    c.setFont("Helvetica", 12)
    c.setFillColor(SLATE)
    c.drawCentredString(width / 2, height - 2.9 * inch, "This certifies that")

    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(NAVY)
    c.drawCentredString(width / 2, height - 3.4 * inch, full_name)

    c.setFont("Helvetica", 12)
    c.setFillColor(SLATE)
    body_text = (
        "has successfully completed all modules of the AI Agent Certification "
        "Lab curriculum — covering agent foundations, tool use and function "
        "calling, and multi-agent orchestration and safety — and has passed "
        "the final certification exam."
    )
    text_obj = c.beginText(width / 2 - 3.6 * inch, height - 3.9 * inch)
    text_obj.setFont("Helvetica", 11)
    import textwrap
    for line in textwrap.wrap(body_text, width=95):
        text_obj.textLine(line)
    c.drawText(text_obj)

    # Score
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(NAVY)
    c.drawCentredString(width / 2, height - 4.55 * inch, f"Final Exam Score: {score}%")

    # Footer details: date, cert id
    c.setFont("Helvetica", 9)
    c.setFillColor(SLATE)
    c.drawString(inner_margin + 0.4 * inch, margin + 0.5 * inch,
                 f"Issued: {issue_date.strftime('%B %d, %Y')}")
    c.drawRightString(width - inner_margin - 0.4 * inch, margin + 0.5 * inch,
                       f"Certificate ID: {cert_id}")

    # Signature line
    sig_x = width / 2
    c.setStrokeColor(SLATE)
    c.line(sig_x - 1.5 * inch, margin + 0.95 * inch, sig_x + 1.5 * inch, margin + 0.95 * inch)
    c.setFont("Helvetica", 9)
    c.drawCentredString(sig_x, margin + 0.78 * inch, "AI Agent Certification Lab — Program Director")

    c.showPage()
    c.save()
    return filepath
