from hashlib import sha256
from pathlib import Path
from typing import Any

from PIL import Image, UnidentifiedImageError


ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def calculate_sha256(file_path: Path) -> str:
    """
    Calculate the SHA-256 hash of a file.

    The file is read in chunks so large evidence files do not
    need to be loaded completely into memory.
    """

    digest = sha256()

    with file_path.open("rb") as evidence_file:
        for chunk in iter(lambda: evidence_file.read(65536), b""):
            digest.update(chunk)

    return digest.hexdigest()


def validate_image(file_path: Path) -> None:
    """
    Validate that the supplied path represents a supported,
    readable image file.

    Raises ValueError when validation fails.
    """

    if not file_path.exists():
        raise ValueError("Evidence file does not exist.")

    if not file_path.is_file():
        raise ValueError("Evidence path is not a file.")

    if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {file_path.suffix or 'unknown'}"
        )

    try:
        with Image.open(file_path) as image:
            image.verify()

    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError(
            "The uploaded file is not a valid readable image."
        ) from exc


def analyze_file(file_path: str | Path) -> dict[str, Any]:
    """
    Validate an evidence image and return basic forensic
    information about the file.
    """

    path = Path(file_path)

    validate_image(path)

    file_size = path.stat().st_size
    file_hash = calculate_sha256(path)

    with Image.open(path) as image:
        width, height = image.size
        image_format = image.format or "Unknown"
        image_mode = image.mode

    return {
        "file_name": path.name,
        "extension": path.suffix.lower(),
        "file_size_bytes": file_size,
        "image_format": image_format,
        "width": width,
        "height": height,
        "color_mode": image_mode,
        "sha256": file_hash,
    }
