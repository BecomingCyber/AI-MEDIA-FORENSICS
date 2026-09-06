from pathlib import Path

from app.reporting.pdf_report import (
    build_report_filename,
    generate_pdf_report,
    safe_text,
)


SAMPLE_RESULT = {
    "original_filename": "sample.png",
    "file_information": {
        "file_name": "sample.png",
        "extension": ".png",
        "file_size_bytes": 12345,
        "image_format": "PNG",
        "width": 120,
        "height": 80,
        "color_mode": "RGB",
        "sha256": (
            "0123456789abcdef"
            "0123456789abcdef"
            "0123456789abcdef"
            "0123456789abcdef"
        ),
    },
    "metadata": {
        "metadata_present": False,
        "metadata_count": 0,
        "summary": {},
        "all_metadata": {},
    },
    "image_analysis": {
        "dimensions": {
            "width": 120,
            "height": 80,
            "channels": 3,
            "aspect_ratio": 1.5,
        },
        "brightness": {
            "mean_brightness": 125.5,
            "brightness_std": 22.4,
        },
        "edges": {
            "edge_density": 0.035,
        },
        "sharpness": {
            "laplacian_variance": 250.0,
        },
    },
    "detection": {
        "assessment": "Review Recommended",
        "review_score": 20,
        "signal_count": 1,
        "signals": [
            {
                "signal": "No EXIF metadata detected",
                "category": "metadata",
                "weight": 1,
                "description": (
                    "The image does not contain readable EXIF metadata."
                ),
            }
        ],
        "disclaimer": (
            "The review score is a heuristic indicator."
        ),
    },
    "explanation": {
        "mode": "mock",
        "model": "deterministic-fallback",
        "explanation": (
            "Assessment Summary\n"
            "Review Recommended.\n\n"
            "Limitations\n"
            "The score is not proof of AI generation."
        ),
        "prompt": "test prompt",
    },
}


def test_safe_text_returns_string():
    """
    safe_text should convert supported values to strings.
    """

    assert safe_text(123) == "123"
    assert safe_text("test") == "test"


def test_safe_text_handles_none():
    """
    None should be converted into a readable placeholder.
    """

    assert safe_text(None) == "Not available"


def test_build_report_filename_returns_pdf_path():
    """
    Report filenames should use the expected PDF naming pattern.
    """

    report_path = build_report_filename()

    assert isinstance(
        report_path,
        Path,
    )

    assert (
        report_path.name.startswith(
            "media_forensics_report_"
        )
    )

    assert report_path.suffix == ".pdf"


def test_generate_pdf_report_creates_file(
    tmp_path,
    monkeypatch,
):
    """
    A complete result should generate a non-empty PDF.
    """

    from app.reporting import pdf_report

    monkeypatch.setattr(
        pdf_report,
        "REPORT_FOLDER",
        tmp_path,
    )

    report_path = generate_pdf_report(
        SAMPLE_RESULT,
    )

    assert report_path.exists()
    assert report_path.is_file()
    assert report_path.suffix == ".pdf"
    assert report_path.stat().st_size > 0


def test_generate_pdf_report_has_pdf_signature(
    tmp_path,
    monkeypatch,
):
    """
    The generated output should begin with the standard
    PDF file signature.
    """

    from app.reporting import pdf_report

    monkeypatch.setattr(
        pdf_report,
        "REPORT_FOLDER",
        tmp_path,
    )

    report_path = generate_pdf_report(
        SAMPLE_RESULT,
    )

    with report_path.open("rb") as report_file:
        signature = report_file.read(5)

    assert signature == b"%PDF-"


def test_generate_pdf_report_accepts_metadata_summary(
    tmp_path,
    monkeypatch,
):
    """
    Reports should also generate successfully when focused
    EXIF metadata is present.
    """

    from app.reporting import pdf_report

    monkeypatch.setattr(
        pdf_report,
        "REPORT_FOLDER",
        tmp_path,
    )

    result_with_metadata = {
        **SAMPLE_RESULT,
        "metadata": {
            "metadata_present": True,
            "metadata_count": 3,
            "summary": {
                "Make": "Test Camera",
                "Model": "ForensicCam",
                "Software": "Test Software",
            },
            "all_metadata": {
                "Make": "Test Camera",
                "Model": "ForensicCam",
                "Software": "Test Software",
            },
        },
    }

    report_path = generate_pdf_report(
        result_with_metadata,
    )

    assert report_path.exists()
    assert report_path.stat().st_size > 0
