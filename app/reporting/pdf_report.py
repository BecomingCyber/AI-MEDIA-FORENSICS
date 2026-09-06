from datetime import datetime
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


BASE_DIR = Path(__file__).resolve().parents[2]
REPORT_FOLDER = BASE_DIR / "reports"

REPORT_FOLDER.mkdir(
    parents=True,
    exist_ok=True,
)


def safe_text(
    value: Any,
) -> str:
    """
    Convert values into display-safe report text.
    """

    if value is None:
        return "Not available"

    return str(value)


def build_report_filename() -> Path:
    """
    Create a timestamped forensic report filename.
    """

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    return (
        REPORT_FOLDER
        / f"media_forensics_report_{timestamp}.pdf"
    )


def generate_pdf_report(
    result: dict[str, Any],
) -> Path:
    """
    Generate a forensic PDF report from an already
    completed analysis result.

    The report documents observed evidence and configured
    forensic signals. It does not independently establish
    authenticity or synthetic-media generation.
    """

    report_path = build_report_filename()

    document = SimpleDocTemplate(
        str(report_path),
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title="AI-Assisted Synthetic Media Forensics Report",
        author="BecomingCyber",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        leading=24,
        spaceAfter=14,
    )

    section_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        spaceBefore=12,
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=13,
        spaceAfter=6,
    )

    warning_style = ParagraphStyle(
        "Warning",
        parent=body_style,
        textColor=colors.HexColor("#8A5A00"),
        backColor=colors.HexColor("#FFF5D6"),
        borderPadding=8,
        spaceBefore=8,
        spaceAfter=12,
    )

    story = []

    file_information = result["file_information"]
    metadata = result["metadata"]
    image_analysis = result["image_analysis"]
    detection = result["detection"]
    explanation = result["explanation"]

    story.append(
        Paragraph(
            "AI-Assisted Synthetic Media Forensics Report",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Digital Evidence Analysis",
            styles["Heading3"],
        )
    )

    story.append(
        Spacer(
            1,
            8,
        )
    )

    story.append(
        Paragraph(
            (
                "<b>Important Notice:</b> This report documents "
                "automated forensic observations and heuristic review "
                "signals. The findings do not independently prove that "
                "media is authentic, manipulated, or AI-generated. "
                "Human verification and additional forensic analysis "
                "may be required."
            ),
            warning_style,
        )
    )

    story.append(
        Paragraph(
            "Executive Summary",
            section_style,
        )
    )

    summary_data = [
        [
            "Original File",
            safe_text(
                result["original_filename"]
            ),
        ],
        [
            "Assessment",
            safe_text(
                detection["assessment"]
            ),
        ],
        [
            "Review Score",
            f'{detection["review_score"]}/100',
        ],
        [
            "Signals Observed",
            safe_text(
                detection["signal_count"]
            ),
        ],
        [
            "AI Explanation Mode",
            safe_text(
                explanation["mode"]
            ),
        ],
        [
            "AI Explanation Model",
            safe_text(
                explanation["model"]
            ),
        ],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[
            1.8 * inch,
            4.8 * inch,
        ],
    )

    summary_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#EAF1F8"),
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#B9C6D3"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    story.append(
        summary_table
    )

    story.append(
        Paragraph(
            "Evidence Information",
            section_style,
        )
    )

    evidence_data = [
        [
            "File Name",
            safe_text(
                result["original_filename"]
            ),
        ],
        [
            "Format",
            safe_text(
                file_information["image_format"]
            ),
        ],
        [
            "Dimensions",
            (
                f'{file_information["width"]} × '
                f'{file_information["height"]}'
            ),
        ],
        [
            "Color Mode",
            safe_text(
                file_information["color_mode"]
            ),
        ],
        [
            "File Size",
            (
                f'{file_information["file_size_bytes"]} bytes'
            ),
        ],
        [
            "SHA-256",
            safe_text(
                file_information["sha256"]
            ),
        ],
    ]

    evidence_table = Table(
        evidence_data,
        colWidths=[
            1.5 * inch,
            5.1 * inch,
        ],
    )

    evidence_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#EEF3F8"),
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#B9C6D3"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8.5,
                ),
                (
                    "WORDWRAP",
                    (0, 0),
                    (-1, -1),
                    "CJK",
                ),
            ]
        )
    )

    story.append(
        evidence_table
    )

    story.append(
        Paragraph(
            "Metadata Analysis",
            section_style,
        )
    )

    story.append(
        Paragraph(
            (
                f"<b>Metadata present:</b> "
                f"{'Yes' if metadata['metadata_present'] else 'No'}"
                f"<br/><b>EXIF field count:</b> "
                f"{metadata['metadata_count']}"
            ),
            body_style,
        )
    )

    if metadata["summary"]:
        metadata_rows = [
            [
                "Field",
                "Value",
            ]
        ]

        for key, value in metadata["summary"].items():
            metadata_rows.append(
                [
                    safe_text(key),
                    safe_text(value),
                ]
            )

        metadata_table = Table(
            metadata_rows,
            colWidths=[
                1.6 * inch,
                5.0 * inch,
            ],
        )

        metadata_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#DCE8F5"),
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor("#B9C6D3"),
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        8.5,
                    ),
                ]
            )
        )

        story.append(
            metadata_table
        )

    else:
        story.append(
            Paragraph(
                "No focused EXIF metadata fields were detected.",
                body_style,
            )
        )

    story.append(
        Paragraph(
            "Image Signal Analysis",
            section_style,
        )
    )

    image_rows = [
        [
            "Measurement",
            "Observed Value",
        ],
        [
            "Width",
            image_analysis["dimensions"]["width"],
        ],
        [
            "Height",
            image_analysis["dimensions"]["height"],
        ],
        [
            "Aspect Ratio",
            image_analysis["dimensions"]["aspect_ratio"],
        ],
        [
            "Mean Brightness",
            image_analysis["brightness"]["mean_brightness"],
        ],
        [
            "Brightness Standard Deviation",
            image_analysis["brightness"]["brightness_std"],
        ],
        [
            "Edge Density",
            image_analysis["edges"]["edge_density"],
        ],
        [
            "Laplacian Variance",
            image_analysis["sharpness"]["laplacian_variance"],
        ],
    ]

    image_table = Table(
        image_rows,
        colWidths=[
            3.0 * inch,
            3.6 * inch,
        ],
    )

    image_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#DCE8F5"),
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#B9C6D3"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8.5,
                ),
            ]
        )
    )

    story.append(
        image_table
    )

    story.append(
        Paragraph(
            "Forensic Signals",
            section_style,
        )
    )

    if detection["signals"]:
        for index, signal in enumerate(
            detection["signals"],
            start=1,
        ):
            story.append(
                Paragraph(
                    (
                        f"<b>{index}. "
                        f"{safe_text(signal['signal'])}</b>"
                        f"<br/>Category: "
                        f"{safe_text(signal['category'])}"
                        f"<br/>Weight: "
                        f"{safe_text(signal['weight'])}"
                        f"<br/>"
                        f"{safe_text(signal['description'])}"
                    ),
                    body_style,
                )
            )
    else:
        story.append(
            Paragraph(
                (
                    "No configured forensic review signals "
                    "were detected."
                ),
                body_style,
            )
        )

    story.append(
        PageBreak()
    )

    story.append(
        Paragraph(
            "AI-Assisted Explanation",
            section_style,
        )
    )

    explanation_text = (
        safe_text(
            explanation["explanation"]
        )
        .replace(
            "&",
            "&amp;",
        )
        .replace(
            "<",
            "&lt;",
        )
        .replace(
            ">",
            "&gt;",
        )
        .replace(
            "\n",
            "<br/>",
        )
    )

    story.append(
        Paragraph(
            explanation_text,
            body_style,
        )
    )

    story.append(
        Paragraph(
            "Methodology and Limitations",
            section_style,
        )
    )

    story.append(
        Paragraph(
            (
                "The application validates supported image files, "
                "computes a SHA-256 hash, extracts available EXIF "
                "metadata, calculates selected image-structure "
                "measurements, applies configured heuristic review "
                "signals, and generates an explanatory summary. "
                "The review score is not a probability of AI "
                "generation. Absence of metadata, editing metadata, "
                "blur, compression, edge characteristics, or other "
                "signals may have legitimate explanations. Results "
                "should be considered alongside source provenance, "
                "original evidence, additional forensic techniques, "
                "and human review."
            ),
            body_style,
        )
    )

    story.append(
        Paragraph(
            "Conclusion",
            section_style,
        )
    )

    story.append(
        Paragraph(
            (
                f"The completed analysis produced the assessment "
                f"<b>{safe_text(detection['assessment'])}</b> "
                f"with a heuristic review score of "
                f"<b>{detection['review_score']}/100</b>. "
                f"{detection['signal_count']} configured forensic "
                f"signal(s) were observed. These findings document "
                f"review indicators and should not be interpreted "
                f"as standalone proof of authenticity, manipulation, "
                f"or synthetic-media generation."
            ),
            body_style,
        )
    )

    document.build(
        story
    )

    return report_path
