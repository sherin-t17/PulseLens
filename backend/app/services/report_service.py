"""Builds the PDF report with ReportLab."""

import json
import re
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.services import plot_service
from app.utils.errors import PulseLensError
from app.utils.paths import REPORT_DIR, ensure_folders

DISCLAIMER = (
    "This application is a student research prototype and is not a medical device. "
    "Results may be affected by movement, lighting, camera quality, recording "
    "conditions and other factors. The results should not be used for medical "
    "diagnosis or treatment decisions."
)
IMG_W = 16 * cm
IMG_H = IMG_W * plot_service.FIG_H / plot_service.FIG_W


def _image(buf):
    return Image(buf, width=IMG_W, height=IMG_H)


def build_report(measurements, user_name, client_id):
    """measurements: list of Measurement rows, newest first. Returns the PDF path."""
    ensure_folders()
    safe_id = re.sub(r"[^A-Za-z0-9_-]", "", client_id)[:40] or "anonymous"
    path = REPORT_DIR / f"report_{safe_id}.pdf"   # overwritten on every download
    try:
        _write_pdf(path, measurements, user_name)
    except Exception:
        raise PulseLensError("The PDF report could not be created. Please try again.", 500)
    return path


def _write_pdf(path, measurements, user_name):
    styles = getSampleStyleSheet()
    small = ParagraphStyle("small", parent=styles["Normal"], fontSize=8, textColor=colors.grey)
    latest = measurements[0]
    ppg = json.loads(latest.ppg_json)
    spectrum = json.loads(latest.spectrum_json)

    story = [
        Paragraph("PulseLens Heart Rate Report", styles["Title"]),
        Paragraph(f"User: {escape(user_name)}", styles["Normal"]),
        Paragraph(f"Report generated: {datetime.now().strftime('%d %b %Y, %I:%M %p')}",
                  styles["Normal"]),
        Spacer(1, 0.4 * cm),

        Paragraph("Latest Measurement", styles["Heading2"]),
    ]

    latest_rows = [
        ["Estimated BPM", f"{latest.bpm:.0f}"],
        ["Signal Quality", latest.quality_label.title()],
        ["Quality Score", f"{latest.quality_score:.2f}"],
        ["Measurement Duration", f"{latest.duration_seconds:.0f} s"],
        ["Dominant Frequency", f"{latest.dominant_frequency_hz:.3f} Hz"],
    ]
    t = Table(latest_rows, colWidths=[6 * cm, 6 * cm])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
    ]))
    story += [t, Spacer(1, 0.4 * cm)]

    # History table (last 30 measurements)
    story.append(Paragraph("Measurement History", styles["Heading2"]))
    recent = measurements[:30]
    rows = [["Date", "Time", "BPM", "Quality"]]
    for m in recent:
        rows.append([m.created_at.strftime("%d %b %Y"), m.created_at.strftime("%I:%M %p"),
                     f"{m.bpm:.0f}", m.quality_label.title()])
    ht = Table(rows, colWidths=[4 * cm, 3.5 * cm, 3 * cm, 3.5 * cm], repeatRows=1)
    ht.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e11d48")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),
    ]))
    story += [ht, Spacer(1, 0.4 * cm)]

    # Graphs
    story.append(Paragraph("Latest PPG Signal", styles["Heading2"]))
    story.append(_image(plot_service.ppg_plot(ppg["t"], ppg["y"])))
    story.append(Paragraph("Frequency Spectrum", styles["Heading2"]))
    story.append(_image(plot_service.spectrum_plot(
        spectrum["f"], spectrum["p"], latest.dominant_frequency_hz)))

    if len(recent) >= 2:
        story.append(Paragraph("Heart Rate History", styles["Heading2"]))
        story.append(_image(plot_service.history_plot([m.bpm for m in reversed(recent)])))

    story += [
        Paragraph("Interpretation", styles["Heading2"]),
        Paragraph(escape(latest.interpretation or ""), styles["Normal"]),
        Spacer(1, 0.6 * cm),
        Paragraph("Disclaimer", styles["Heading2"]),
        Paragraph(DISCLAIMER, small),
    ]

    doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm,
                            title="PulseLens Heart Rate Report")
    doc.build(story)