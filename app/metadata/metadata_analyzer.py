from pathlib import Path
from typing import Any

from PIL import ExifTags, Image, UnidentifiedImageError


def extract_exif_metadata(
    file_path: str | Path,
) -> dict[str, Any]:
    """
    Extract EXIF metadata from an image.

    Returns a dictionary of human-readable EXIF fields.
    If no EXIF metadata exists, an empty dictionary is returned.
    """

    path = Path(file_path)

    if not path.exists():
        raise ValueError("Evidence file does not exist.")

    if not path.is_file():
        raise ValueError("Evidence path is not a file.")

    try:
        with Image.open(path) as image:
            exif_data = image.getexif()

    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError(
            "The evidence file is not a readable image."
        ) from exc

    if not exif_data:
        return {}

    metadata = {}

    for tag_id, value in exif_data.items():
        tag_name = ExifTags.TAGS.get(
            tag_id,
            str(tag_id),
        )

        metadata[tag_name] = value

    return metadata


def summarize_metadata(
    metadata: dict[str, Any],
) -> dict[str, Any]:
    """
    Return a focused subset of EXIF fields commonly useful
    during basic forensic review.
    """

    fields_of_interest = [
        "Make",
        "Model",
        "Software",
        "DateTime",
        "DateTimeOriginal",
        "DateTimeDigitized",
        "Artist",
        "Copyright",
        "Orientation",
        "GPSInfo",
    ]

    summary = {}

    for field in fields_of_interest:
        if field in metadata:
            summary[field] = metadata[field]

    return summary


def analyze_metadata(
    file_path: str | Path,
) -> dict[str, Any]:
    """
    Extract EXIF metadata and return both the full metadata
    collection and a focused forensic summary.
    """

    metadata = extract_exif_metadata(
        file_path,
    )

    summary = summarize_metadata(
        metadata,
    )

    return {
        "metadata_present": bool(metadata),
        "metadata_count": len(metadata),
        "summary": summary,
        "all_metadata": metadata,
    }
