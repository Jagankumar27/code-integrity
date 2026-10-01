import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from xml.sax.saxutils import escape
from .. import config

def build_pdf(c, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    st = getSampleStyleSheet(); s = c["scores"]
    doc = SimpleDocTemplate(path, pagesize=A4, title="AI Code Integrity Report")
    E = [Paragraph("AI Code Integrity Report", st["Title"]),
         Paragraph(f"Generated {datetime.utcnow():%Y-%m-%d %H:%M} UTC &middot; Comparison #{c['id']}", st["Normal"]), Spacer(1, 12),
         Paragraph("Submission details", st["Heading2"])]
    t = Table([["", "Submission A", "Submission B"], ["Student", c["a"]["student"], c["b"]["student"]],
               ["File", c["a"]["filename"], c["b"]["filename"]], ["Language", c["a"]["language"], c["b"]["language"]]],
              colWidths=[80, 190, 190])
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), .5, colors.grey), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e0e7ff"))]))
    E += [t, Spacer(1, 12), Paragraph("Similarity scores (potential similarity)", st["Heading2"])]
    rows = [["Metric", "Score"], ["Text similarity", f"{s['text']}%"], ["Token similarity", f"{s['token']}%"],
            ["Structural similarity", f"{s['structural']}%"], ["Semantic similarity", f"{s['semantic']}%"],
            ["Overall similarity", f"{s['overall']}%"], ["Similarity risk level", c["risk"]]]
    t2 = Table(rows, colWidths=[200, 120])
    t2.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), .5, colors.grey), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e0e7ff")),
                            ("FONTNAME", (0, 5), (-1, 6), "Helvetica-Bold")]))
    E += [t2, Spacer(1, 12), Paragraph("Reasons this pair was flagged", st["Heading2"])]
    for e in c["explanations"]:
        E.append(Paragraph(f"&bull; <b>{escape(e['title'])}</b>: {escape(e['evidence'])}", st["Normal"]))
    total = sum(b["lines"] for b in c["blocks"])
    E += [Spacer(1, 12), Paragraph("Comparison summary", st["Heading2"]),
          Paragraph(f"{len(c['blocks'])} aligned code blocks covering {total} normalised lines. Analysis method: {escape(c['method'])}.", st["Normal"]),
          Spacer(1, 18), Paragraph(f"<i>{config.NOTE}</i>", st["Normal"])]
    doc.build(E)
    return path
