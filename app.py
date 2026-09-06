import os
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    request,
    send_file,
)
from werkzeug.utils import secure_filename

from app.analyzer.ai_explainer import explain_evidence
from app.analyzer.file_analyzer import analyze_file
from app.analyzer.image_analyzer import analyze_image
from app.detector.detector import detect_media_signals
from app.metadata.metadata_analyzer import analyze_metadata
from app.reporting.pdf_report import generate_pdf_report


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "uploads"

UPLOAD_FOLDER.mkdir(
    parents=True,
    exist_ok=True,
)


app = Flask(
    __name__,
    template_folder="app/templates",
    static_folder="app/static",
)

app.secret_key = os.getenv(
    "SECRET_KEY",
    "development-secret-key",
)

max_file_size_mb = int(
    os.getenv(
        "MAX_FILE_SIZE_MB",
        "25",
    )
)

app.config["MAX_CONTENT_LENGTH"] = (
    max_file_size_mb
    * 1024
    * 1024
)


ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
}


latest_analysis = {
    "result": None,
}


def allowed_file(
    filename: str,
) -> bool:
    """
    Check whether the uploaded filename uses a supported
    image extension.
    """

    return (
        Path(filename).suffix.lower()
        in ALLOWED_EXTENSIONS
    )


@app.route("/")
def dashboard():
    """
    Display the media-forensics upload dashboard.
    """

    return render_template(
        "dashboard.html",
        result=None,
        error=None,
    )


@app.route(
    "/analyze",
    methods=["POST"],
)
def analyze():
    """
    Receive an uploaded image and execute the forensic
    analysis pipeline.

    Uploaded filenames are sanitized and randomized before
    storage to avoid trusting user-controlled filenames.
    """

    uploaded_file = request.files.get(
        "evidence_file",
    )

    if uploaded_file is None:
        return render_template(
            "dashboard.html",
            result=None,
            error="No evidence file was provided.",
        )

    if not uploaded_file.filename:
        return render_template(
            "dashboard.html",
            result=None,
            error="Please select an image to analyze.",
        )

    if not allowed_file(
        uploaded_file.filename,
    ):
        return render_template(
            "dashboard.html",
            result=None,
            error=(
                "Unsupported file type. "
                "Upload a JPG, JPEG, or PNG image."
            ),
        )

    original_filename = secure_filename(
        uploaded_file.filename,
    )

    extension = Path(
        original_filename
    ).suffix.lower()

    stored_filename = (
        f"{uuid4().hex}{extension}"
    )

    evidence_path = (
        UPLOAD_FOLDER
        / stored_filename
    )

    try:
        uploaded_file.save(
            evidence_path,
        )

        file_information = analyze_file(
            evidence_path,
        )

        metadata = analyze_metadata(
            evidence_path,
        )

        image_analysis = analyze_image(
            evidence_path,
        )

        detection = detect_media_signals(
            evidence_path,
        )

        explanation = explain_evidence(
            detection,
        )

        result = {
            "original_filename": original_filename,
            "file_information": file_information,
            "metadata": metadata,
            "image_analysis": image_analysis,
            "detection": detection,
            "explanation": explanation,
        }

        latest_analysis["result"] = result

        return render_template(
            "dashboard.html",
            result=result,
            error=None,
        )

    except ValueError as exc:
        return render_template(
            "dashboard.html",
            result=None,
            error=str(exc),
        )

    finally:
        if evidence_path.exists():
            evidence_path.unlink()


@app.route("/download-report")
def download_report():
    """
    Generate a PDF report from the most recent completed
    analysis without rerunning the forensic pipeline.
    """

    result = latest_analysis["result"]

    if result is None:
        return (
            "No completed analysis is available. "
            "Analyze an image first.",
            400,
        )

    report_path = generate_pdf_report(
        result,
    )

    return send_file(
        report_path.resolve(),
        as_attachment=True,
        download_name=report_path.name,
        mimetype="application/pdf",
    )


if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000,
    )
