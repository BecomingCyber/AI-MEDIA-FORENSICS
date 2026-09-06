from pathlib import Path
from typing import Any

import cv2
import numpy as np


def load_image(
    file_path: str | Path,
) -> np.ndarray:
    """
    Load an image with OpenCV.

    Raises ValueError if the image cannot be decoded.
    """

    path = Path(file_path)

    if not path.exists():
        raise ValueError("Evidence file does not exist.")

    if not path.is_file():
        raise ValueError("Evidence path is not a file.")

    image = cv2.imread(str(path))

    if image is None:
        raise ValueError(
            "The evidence file could not be decoded as an image."
        )

    return image


def analyze_dimensions(
    image: np.ndarray,
) -> dict[str, Any]:
    """
    Return basic dimensional characteristics of an image.
    """

    height, width = image.shape[:2]

    channels = (
        image.shape[2]
        if len(image.shape) == 3
        else 1
    )

    return {
        "width": width,
        "height": height,
        "channels": channels,
        "aspect_ratio": round(
            width / height,
            4,
        ),
    }


def analyze_brightness(
    image: np.ndarray,
) -> dict[str, float]:
    """
    Measure grayscale brightness statistics.
    """

    grayscale = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY,
    )

    return {
        "mean_brightness": round(
            float(np.mean(grayscale)),
            2,
        ),
        "brightness_std": round(
            float(np.std(grayscale)),
            2,
        ),
    }


def analyze_edges(
    image: np.ndarray,
) -> dict[str, float]:
    """
    Estimate edge density using Canny edge detection.

    Edge density is an observation about image structure,
    not proof of manipulation or synthetic generation.
    """

    grayscale = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY,
    )

    edges = cv2.Canny(
        grayscale,
        100,
        200,
    )

    edge_pixels = np.count_nonzero(edges)
    total_pixels = edges.size

    edge_density = (
        edge_pixels / total_pixels
        if total_pixels
        else 0.0
    )

    return {
        "edge_density": round(
            float(edge_density),
            4,
        ),
    }


def analyze_sharpness(
    image: np.ndarray,
) -> dict[str, float]:
    """
    Estimate image sharpness using the variance of the
    Laplacian.

    This provides a measurable forensic signal but should
    not be interpreted as authenticity proof.
    """

    grayscale = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY,
    )

    laplacian = cv2.Laplacian(
        grayscale,
        cv2.CV_64F,
    )

    return {
        "laplacian_variance": round(
            float(laplacian.var()),
            2,
        ),
    }


def analyze_image(
    file_path: str | Path,
) -> dict[str, Any]:
    """
    Run the initial forensic image-analysis pipeline.

    The returned measurements are forensic observations.
    They do not independently establish whether an image
    is authentic, manipulated, or AI-generated.
    """

    image = load_image(
        file_path,
    )

    return {
        "dimensions": analyze_dimensions(image),
        "brightness": analyze_brightness(image),
        "edges": analyze_edges(image),
        "sharpness": analyze_sharpness(image),
    }
