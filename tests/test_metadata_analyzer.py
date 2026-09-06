from pathlib import Path

import pytest
from PIL import Image

from app.metadata.metadata_analyzer import (
    analyze_metadata,
    extract_exif_metadata,
    summarize_metadata,
)


def create_test_image_without_exif(
    file_path: Path,
) -> None:
    """
    Create a valid PNG image with no EXIF metadata.
    """

    image = Image.new(
        "RGB",
        (80, 60),
        color="white",
    )

    image.save(file_path)


def create_test_image_with_exif(
    file_path: Path,
) -> None:
    """
    Create a JPEG image containing a small controlled
    EXIF metadata set for testing.
    """

    image = Image.new(
        "RGB",
        (120, 90),
        color="white",
    )

    exif = Image.Exif()

    exif[271] = "Test Camera Company"
    exif[272] = "ForensicCam 1000"
    exif[305] = "Test Editing Software"
    exif[306] = "2026:09:06 12:00:00"

    image.save(
        file_path,
        exif=exif,
    )


def test_extract_exif_metadata_returns_empty_for_no_exif(
    tmp_path,
):
    """
    An image without EXIF metadata should return
    an empty dictionary.
    """

    image_path = tmp_path / "no_exif.png"

    create_test_image_without_exif(
        image_path,
    )

    metadata = extract_exif_metadata(
        image_path,
    )

    assert metadata == {}


def test_extract_exif_metadata_reads_expected_fields(
    tmp_path,
):
    """
    Controlled EXIF values should be extracted using
    human-readable field names.
    """

    image_path = tmp_path / "with_exif.jpg"

    create_test_image_with_exif(
        image_path,
    )

    metadata = extract_exif_metadata(
        image_path,
    )

    assert metadata["Make"] == "Test Camera Company"
    assert metadata["Model"] == "ForensicCam 1000"
    assert metadata["Software"] == "Test Editing Software"
    assert metadata["DateTime"] == "2026:09:06 12:00:00"


def test_summarize_metadata_returns_forensic_fields():
    """
    summarize_metadata should retain only selected
    forensic fields.
    """

    metadata = {
        "Make": "Example Camera",
        "Model": "Example Model",
        "Software": "Example Editor",
        "DateTime": "2026:09:06 12:00:00",
        "UnrelatedField": "ignore this",
    }

    summary = summarize_metadata(
        metadata,
    )

    assert summary["Make"] == "Example Camera"
    assert summary["Model"] == "Example Model"
    assert summary["Software"] == "Example Editor"
    assert summary["DateTime"] == "2026:09:06 12:00:00"
    assert "UnrelatedField" not in summary


def test_analyze_metadata_reports_metadata_present(
    tmp_path,
):
    """
    analyze_metadata should correctly report when
    EXIF metadata is present.
    """

    image_path = tmp_path / "with_exif.jpg"

    create_test_image_with_exif(
        image_path,
    )

    result = analyze_metadata(
        image_path,
    )

    assert result["metadata_present"] is True
    assert result["metadata_count"] >= 4
    assert result["summary"]["Make"] == "Test Camera Company"


def test_analyze_metadata_reports_no_metadata(
    tmp_path,
):
    """
    analyze_metadata should correctly report when
    EXIF metadata is absent.
    """

    image_path = tmp_path / "no_exif.png"

    create_test_image_without_exif(
        image_path,
    )

    result = analyze_metadata(
        image_path,
    )

    assert result["metadata_present"] is False
    assert result["metadata_count"] == 0
    assert result["summary"] == {}
    assert result["all_metadata"] == {}


def test_extract_exif_metadata_rejects_missing_file(
    tmp_path,
):
    """
    Missing evidence files should raise ValueError.
    """

    missing_file = tmp_path / "missing.jpg"

    with pytest.raises(
        ValueError,
        match="Evidence file does not exist",
    ):
        extract_exif_metadata(
            missing_file,
        )


def test_extract_exif_metadata_rejects_invalid_image(
    tmp_path,
):
    """
    A fake image file should be rejected even when it
    has an image extension.
    """

    fake_image = tmp_path / "fake.jpg"

    fake_image.write_text(
        "not really an image",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="not a readable image",
    ):
        extract_exif_metadata(
            fake_image,
        )
