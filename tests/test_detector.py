from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from app.detector.detector import (
    calculate_confidence,
    classify_assessment,
    detect_media_signals,
    evaluate_image_signals,
    evaluate_metadata_signals,
)


def create_plain_image(
    file_path: Path,
    width: int = 120,
    height: int = 80,
) -> None:
    """
    Create a simple PNG image with minimal structure.
    """

    image = np.zeros(
        (height, width, 3),
        dtype=np.uint8,
    )

    cv2.imwrite(
        str(file_path),
        image,
    )


def create_image_with_editing_metadata(
    file_path: Path,
) -> None:
    """
    Create a JPEG with controlled EXIF metadata that
    references editing software.
    """

    image = Image.new(
        "RGB",
        (120, 80),
        color="white",
    )

    exif = Image.Exif()

    exif[271] = "Test Camera Company"
    exif[272] = "ForensicCam 1000"
    exif[305] = "Adobe Photoshop"

    image.save(
        file_path,
        exif=exif,
    )


def test_evaluate_metadata_signals_flags_missing_metadata():
    """
    Missing metadata should produce a review signal.
    """

    metadata_result = {
        "metadata_present": False,
        "summary": {},
    }

    signals = evaluate_metadata_signals(
        metadata_result,
    )

    assert len(signals) == 1
    assert signals[0]["signal"] == "No EXIF metadata detected"
    assert signals[0]["weight"] == 1


def test_evaluate_metadata_signals_flags_editing_software():
    """
    Editing software metadata should produce a review signal.
    """

    metadata_result = {
        "metadata_present": True,
        "summary": {
            "Software": "Adobe Photoshop",
        },
    }

    signals = evaluate_metadata_signals(
        metadata_result,
    )

    assert len(signals) == 1
    assert (
        signals[0]["signal"]
        == "Image-editing software metadata detected"
    )
    assert signals[0]["weight"] == 2


def test_evaluate_image_signals_flags_low_edge_density():
    """
    Very low edge density should generate a signal.
    """

    image_result = {
        "edges": {
            "edge_density": 0.001,
        },
        "sharpness": {
            "laplacian_variance": 100.0,
        },
    }

    signals = evaluate_image_signals(
        image_result,
    )

    assert any(
        signal["signal"] == "Very low edge density"
        for signal in signals
    )


def test_evaluate_image_signals_flags_low_sharpness():
    """
    Low sharpness should generate a signal.
    """

    image_result = {
        "edges": {
            "edge_density": 0.05,
        },
        "sharpness": {
            "laplacian_variance": 5.0,
        },
    }

    signals = evaluate_image_signals(
        image_result,
    )

    assert any(
        signal["signal"] == "Low measured sharpness"
        for signal in signals
    )


def test_calculate_confidence_sums_signal_weights():
    """
    Review score should reflect combined signal weights.
    """

    signals = [
        {
            "weight": 1,
        },
        {
            "weight": 2,
        },
    ]

    score = calculate_confidence(
        signals,
    )

    assert score == 60


def test_calculate_confidence_caps_at_100():
    """
    Review score should never exceed 100.
    """

    signals = [
        {
            "weight": 3,
        },
        {
            "weight": 3,
        },
    ]

    score = calculate_confidence(
        signals,
    )

    assert score == 100


def test_classify_assessment_no_significant_signals():
    """
    A score below 20 should indicate no significant signals.
    """

    result = classify_assessment(
        0,
    )

    assert result == "No Significant Signals Detected"


def test_classify_assessment_review_recommended():
    """
    Scores from 20 through 59 should recommend review.
    """

    result = classify_assessment(
        40,
    )

    assert result == "Review Recommended"


def test_classify_assessment_further_analysis_recommended():
    """
    Scores of 60 or more should recommend further analysis.
    """

    result = classify_assessment(
        60,
    )

    assert result == "Further Analysis Recommended"


def test_detect_media_signals_returns_complete_result(
    tmp_path,
):
    """
    The detector should return a complete review structure.
    """

    image_path = tmp_path / "plain.png"

    create_plain_image(
        image_path,
    )

    result = detect_media_signals(
        image_path,
    )

    assert "assessment" in result
    assert "review_score" in result
    assert "signal_count" in result
    assert "signals" in result
    assert "disclaimer" in result

    assert isinstance(
        result["review_score"],
        int,
    )

    assert 0 <= result["review_score"] <= 100


def test_detect_media_signals_detects_editing_metadata(
    tmp_path,
):
    """
    Controlled editing metadata should be surfaced as
    a forensic review signal.
    """

    image_path = tmp_path / "edited.jpg"

    create_image_with_editing_metadata(
        image_path,
    )

    result = detect_media_signals(
        image_path,
    )

    signal_names = [
        signal["signal"]
        for signal in result["signals"]
    ]

    assert (
        "Image-editing software metadata detected"
        in signal_names
    )
