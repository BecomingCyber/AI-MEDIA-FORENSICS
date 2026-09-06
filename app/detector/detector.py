from pathlib import Path
from typing import Any

from app.analyzer.image_analyzer import analyze_image
from app.metadata.metadata_analyzer import analyze_metadata


def evaluate_metadata_signals(
    metadata_result: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Evaluate metadata for signals that may warrant
    additional forensic review.

    These signals are observations and are not proof
    that media is synthetic or manipulated.
    """

    signals = []

    if not metadata_result["metadata_present"]:
        signals.append(
            {
                "signal": "No EXIF metadata detected",
                "category": "metadata",
                "weight": 1,
                "description": (
                    "The image does not contain readable EXIF "
                    "metadata. Metadata may be absent for many "
                    "legitimate reasons."
                ),
            }
        )

    summary = metadata_result["summary"]

    software = str(
        summary.get(
            "Software",
            "",
        )
    ).lower()

    editing_terms = [
        "photoshop",
        "gimp",
        "lightroom",
        "editor",
        "editing",
    ]

    if any(
        term in software
        for term in editing_terms
    ):
        signals.append(
            {
                "signal": "Image-editing software metadata detected",
                "category": "metadata",
                "weight": 2,
                "description": (
                    "The Software EXIF field references image-editing "
                    "software. This indicates processing history but "
                    "does not establish malicious manipulation."
                ),
            }
        )

    return signals


def evaluate_image_signals(
    image_result: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Evaluate measurable image characteristics for values
    that may warrant closer inspection.
    """

    signals = []

    edge_density = image_result["edges"]["edge_density"]

    sharpness = image_result["sharpness"][
        "laplacian_variance"
    ]

    if edge_density < 0.005:
        signals.append(
            {
                "signal": "Very low edge density",
                "category": "image_structure",
                "weight": 1,
                "description": (
                    "The image contains unusually little detected "
                    "edge structure under the configured thresholds."
                ),
            }
        )

    if sharpness < 20:
        signals.append(
            {
                "signal": "Low measured sharpness",
                "category": "image_structure",
                "weight": 1,
                "description": (
                    "The image has low Laplacian variance, which may "
                    "indicate blur, smoothing, compression, or other "
                    "image characteristics requiring review."
                ),
            }
        )

    return signals


def calculate_confidence(
    signals: list[dict[str, Any]],
) -> int:
    """
    Convert the combined signal weights into a bounded
    review score from 0 to 100.

    This is a heuristic review score, not a probability
    that the image is AI-generated.
    """

    total_weight = sum(
        signal["weight"]
        for signal in signals
    )

    return min(
        total_weight * 20,
        100,
    )


def classify_assessment(
    review_score: int,
) -> str:
    """
    Convert the review score into an investigator-friendly
    assessment category.
    """

    if review_score >= 60:
        return "Further Analysis Recommended"

    if review_score >= 20:
        return "Review Recommended"

    return "No Significant Signals Detected"


def detect_media_signals(
    file_path: str | Path,
) -> dict[str, Any]:
    """
    Run the initial synthetic-media forensic detection
    workflow.

    The result identifies forensic signals requiring
    review. It does not determine authenticity by itself.
    """

    metadata_result = analyze_metadata(
        file_path,
    )

    image_result = analyze_image(
        file_path,
    )

    metadata_signals = evaluate_metadata_signals(
        metadata_result,
    )

    image_signals = evaluate_image_signals(
        image_result,
    )

    signals = (
        metadata_signals
        + image_signals
    )

    review_score = calculate_confidence(
        signals,
    )

    assessment = classify_assessment(
        review_score,
    )

    return {
        "assessment": assessment,
        "review_score": review_score,
        "signal_count": len(signals),
        "signals": signals,
        "disclaimer": (
            "The review score is a heuristic indicator based on "
            "configured forensic signals. It is not a probability "
            "of AI generation and does not establish authenticity."
        ),
    }
