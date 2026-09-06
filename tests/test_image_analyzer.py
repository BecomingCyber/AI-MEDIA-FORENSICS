from pathlib import Path

import cv2
import numpy as np
import pytest

from app.analyzer.image_analyzer import (
    analyze_brightness,
    analyze_dimensions,
    analyze_edges,
    analyze_image,
    analyze_sharpness,
    load_image,
)


def create_test_image(
    file_path: Path,
    width: int = 120,
    height: int = 80,
) -> None:
    """
    Create a simple valid test image with a white rectangle
    on a black background.
    """

    image = np.zeros(
        (height, width, 3),
        dtype=np.uint8,
    )

    cv2.rectangle(
        image,
        (20, 20),
        (width - 20, height - 20),
        (255, 255, 255),
        -1,
    )

    cv2.imwrite(
        str(file_path),
        image,
    )


def test_load_image_returns_numpy_array(
    tmp_path,
):
    """
    A valid image should load as a NumPy array.
    """

    image_path = tmp_path / "sample.png"

    create_test_image(
        image_path,
    )

    image = load_image(
        image_path,
    )

    assert isinstance(
        image,
        np.ndarray,
    )


def test_load_image_rejects_missing_file(
    tmp_path,
):
    """
    Missing files should raise ValueError.
    """

    missing_file = tmp_path / "missing.png"

    with pytest.raises(
        ValueError,
        match="Evidence file does not exist",
    ):
        load_image(
            missing_file,
        )


def test_load_image_rejects_invalid_image(
    tmp_path,
):
    """
    A fake image file should fail OpenCV decoding.
    """

    fake_image = tmp_path / "fake.png"

    fake_image.write_text(
        "not really an image",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="could not be decoded as an image",
    ):
        load_image(
            fake_image,
        )


def test_analyze_dimensions_returns_expected_values(
    tmp_path,
):
    """
    Image dimensions should match the generated test image.
    """

    image_path = tmp_path / "sample.png"

    create_test_image(
        image_path,
        width=120,
        height=80,
    )

    image = load_image(
        image_path,
    )

    result = analyze_dimensions(
        image,
    )

    assert result["width"] == 120
    assert result["height"] == 80
    assert result["channels"] == 3
    assert result["aspect_ratio"] == 1.5


def test_analyze_brightness_returns_numeric_values(
    tmp_path,
):
    """
    Brightness analysis should return non-negative values.
    """

    image_path = tmp_path / "sample.png"

    create_test_image(
        image_path,
    )

    image = load_image(
        image_path,
    )

    result = analyze_brightness(
        image,
    )

    assert result["mean_brightness"] >= 0
    assert result["brightness_std"] >= 0


def test_analyze_edges_returns_valid_density(
    tmp_path,
):
    """
    Edge density should remain between 0 and 1.
    """

    image_path = tmp_path / "sample.png"

    create_test_image(
        image_path,
    )

    image = load_image(
        image_path,
    )

    result = analyze_edges(
        image,
    )

    assert 0 <= result["edge_density"] <= 1


def test_analyze_sharpness_returns_nonnegative_variance(
    tmp_path,
):
    """
    Laplacian variance should be non-negative.
    """

    image_path = tmp_path / "sample.png"

    create_test_image(
        image_path,
    )

    image = load_image(
        image_path,
    )

    result = analyze_sharpness(
        image,
    )

    assert result["laplacian_variance"] >= 0


def test_analyze_image_returns_complete_signal_set(
    tmp_path,
):
    """
    analyze_image should return every initial forensic
    signal category.
    """

    image_path = tmp_path / "sample.png"

    create_test_image(
        image_path,
    )

    result = analyze_image(
        image_path,
    )

    assert "dimensions" in result
    assert "brightness" in result
    assert "edges" in result
    assert "sharpness" in result

    assert result["dimensions"]["width"] == 120
    assert result["dimensions"]["height"] == 80
