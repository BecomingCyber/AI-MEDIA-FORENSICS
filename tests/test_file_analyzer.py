from pathlib import Path

import pytest
from PIL import Image

from app.analyzer.file_analyzer import (
    analyze_file,
    calculate_sha256,
    validate_image,
)


def create_test_image(file_path: Path) -> None:
    """
    Create a small valid PNG image for testing.
    """

    image = Image.new(
        "RGB",
        (100, 50),
        color="white",
    )

    image.save(file_path)


def test_calculate_sha256_returns_expected_hash(tmp_path):
    """
    SHA-256 should return a 64-character hexadecimal digest.
    """

    test_file = tmp_path / "evidence.txt"
    test_file.write_text(
        "forensic evidence",
        encoding="utf-8",
    )

    file_hash = calculate_sha256(test_file)

    assert len(file_hash) == 64
    assert all(
        character in "0123456789abcdef"
        for character in file_hash
    )


def test_same_file_produces_same_hash(tmp_path):
    """
    Hashing the same unchanged file twice should produce
    the same SHA-256 value.
    """

    test_file = tmp_path / "evidence.txt"
    test_file.write_text(
        "unchanged evidence",
        encoding="utf-8",
    )

    first_hash = calculate_sha256(test_file)
    second_hash = calculate_sha256(test_file)

    assert first_hash == second_hash


def test_changed_file_produces_different_hash(tmp_path):
    """
    Modifying file contents should change the SHA-256 hash.
    """

    test_file = tmp_path / "evidence.txt"

    test_file.write_text(
        "original evidence",
        encoding="utf-8",
    )

    original_hash = calculate_sha256(test_file)

    test_file.write_text(
        "modified evidence",
        encoding="utf-8",
    )

    modified_hash = calculate_sha256(test_file)

    assert original_hash != modified_hash


def test_validate_image_accepts_valid_png(tmp_path):
    """
    A legitimate PNG image should pass validation.
    """

    image_path = tmp_path / "evidence.png"

    create_test_image(image_path)

    validate_image(image_path)


def test_validate_image_rejects_unsupported_extension(tmp_path):
    """
    Unsupported extensions should be rejected.
    """

    file_path = tmp_path / "evidence.txt"

    file_path.write_text(
        "not an image",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Unsupported file type",
    ):
        validate_image(file_path)


def test_validate_image_rejects_fake_image(tmp_path):
    """
    A file renamed with an image extension should still fail
    if its contents are not a valid image.
    """

    fake_image = tmp_path / "fake.jpg"

    fake_image.write_text(
        "this is not really an image",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="not a valid readable image",
    ):
        validate_image(fake_image)


def test_analyze_file_returns_expected_evidence_information(
    tmp_path,
):
    """
    analyze_file should return basic forensic information
    about a valid image.
    """

    image_path = tmp_path / "sample.png"

    create_test_image(image_path)

    result = analyze_file(image_path)

    assert result["file_name"] == "sample.png"
    assert result["extension"] == ".png"
    assert result["image_format"] == "PNG"
    assert result["width"] == 100
    assert result["height"] == 50
    assert result["color_mode"] == "RGB"
    assert result["file_size_bytes"] > 0
    assert len(result["sha256"]) == 64
