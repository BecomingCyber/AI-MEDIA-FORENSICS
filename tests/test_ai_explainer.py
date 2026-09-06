import os

import pytest

from app.analyzer.ai_explainer import (
    build_explanation_prompt,
    create_fallback_explanation,
    explain_evidence,
)


SAMPLE_EVIDENCE = {
    "assessment": "Review Recommended",
    "review_score": 40,
    "signal_count": 2,
    "signals": [
        {
            "signal": "No EXIF metadata detected",
            "category": "metadata",
            "weight": 1,
            "description": (
                "The image does not contain readable EXIF metadata."
            ),
        },
        {
            "signal": "Low measured sharpness",
            "category": "image_structure",
            "weight": 1,
            "description": (
                "The image has low Laplacian variance."
            ),
        },
    ],
    "disclaimer": (
        "The review score is a heuristic indicator."
    ),
}


def test_build_explanation_prompt_contains_evidence():
    """
    The AI prompt should include the supplied forensic evidence.
    """

    prompt = build_explanation_prompt(
        SAMPLE_EVIDENCE,
    )

    assert "Review Recommended" in prompt
    assert "No EXIF metadata detected" in prompt
    assert "Low measured sharpness" in prompt
    assert "review score as a heuristic review score" in prompt


def test_build_explanation_prompt_contains_safety_limits():
    """
    The prompt should explicitly prevent unsupported conclusions.
    """

    prompt = build_explanation_prompt(
        SAMPLE_EVIDENCE,
    )

    assert "Do not claim the image is authentic." in prompt
    assert "Do not claim the image is AI-generated." in prompt
    assert "Do not invent forensic findings." in prompt


def test_create_fallback_explanation_contains_assessment():
    """
    The deterministic fallback should summarize the assessment.
    """

    explanation = create_fallback_explanation(
        SAMPLE_EVIDENCE,
    )

    assert "Assessment Summary" in explanation
    assert "Review Recommended" in explanation
    assert "40/100" in explanation
    assert "2 configured forensic signal(s)" in explanation


def test_create_fallback_explanation_contains_limitations():
    """
    The fallback explanation should clearly state limitations.
    """

    explanation = create_fallback_explanation(
        SAMPLE_EVIDENCE,
    )

    assert "Limitations" in explanation
    assert "not a probability" in explanation
    assert "does not establish authenticity" in explanation


def test_explain_evidence_mock_mode(
    monkeypatch,
):
    """
    Mock mode should return a deterministic explanation
    without making an external API request.
    """

    monkeypatch.setenv(
        "AI_EXPLAINER_MODE",
        "mock",
    )

    result = explain_evidence(
        SAMPLE_EVIDENCE,
    )

    assert result["mode"] == "mock"
    assert result["model"] == "deterministic-fallback"
    assert "Assessment Summary" in result["explanation"]
    assert "FORENSIC EVIDENCE" in result["prompt"]


def test_explain_evidence_defaults_to_mock_mode(
    monkeypatch,
):
    """
    If no explainer mode is configured, the application
    should default safely to mock mode.
    """

    monkeypatch.delenv(
        "AI_EXPLAINER_MODE",
        raising=False,
    )

    result = explain_evidence(
        SAMPLE_EVIDENCE,
    )

    assert result["mode"] == "mock"


def test_explain_evidence_rejects_invalid_mode(
    monkeypatch,
):
    """
    Unsupported explainer modes should raise ValueError.
    """

    monkeypatch.setenv(
        "AI_EXPLAINER_MODE",
        "unsupported",
    )

    with pytest.raises(
        ValueError,
        match="AI_EXPLAINER_MODE must be 'mock' or 'api'",
    ):
        explain_evidence(
            SAMPLE_EVIDENCE,
        )


def test_explain_evidence_api_mode_requires_key(
    monkeypatch,
):
    """
    API mode should not run without an API key.
    """

    monkeypatch.setenv(
        "AI_EXPLAINER_MODE",
        "api",
    )

    monkeypatch.delenv(
        "OPENAI_API_KEY",
        raising=False,
    )

    with pytest.raises(
        ValueError,
        match="OPENAI_API_KEY is required",
    ):
        explain_evidence(
            SAMPLE_EVIDENCE,
        )
