import json
import os
from typing import Any

from openai import OpenAI


def build_explanation_prompt(
    evidence: dict[str, Any],
) -> str:
    """
    Build a structured prompt from forensic findings.

    The AI is instructed to explain existing evidence
    rather than create new forensic conclusions.
    """

    evidence_json = json.dumps(
        evidence,
        indent=2,
        default=str,
    )

    return f"""
You are assisting with an authorized digital media forensic review.

Your role is to explain the supplied forensic findings in clear,
investigator-friendly language.

Important rules:

1. Use only the evidence provided.
2. Do not invent forensic findings.
3. Do not claim the image is authentic.
4. Do not claim the image is AI-generated.
5. Treat the review score as a heuristic review score, not a probability.
6. Explain reasonable alternative causes for observed signals.
7. Clearly state that human verification and additional forensic analysis
   may be required.

Provide the explanation using these sections:

Assessment Summary
Observed Signals
Possible Explanations
Limitations
Recommended Next Steps

FORENSIC EVIDENCE:

{evidence_json}
""".strip()


def create_fallback_explanation(
    evidence: dict[str, Any],
) -> str:
    """
    Create a deterministic explanation when AI analysis
    is disabled or unavailable.
    """

    assessment = evidence.get(
        "assessment",
        "Unknown",
    )

    review_score = evidence.get(
        "review_score",
        0,
    )

    signal_count = evidence.get(
        "signal_count",
        0,
    )

    return (
        "Assessment Summary\n"
        f"The forensic workflow produced the assessment: {assessment}. "
        f"The heuristic review score is {review_score}/100, with "
        f"{signal_count} configured forensic signal(s) observed.\n\n"
        "Observed Signals\n"
        "The application identified measurable metadata or image-structure "
        "signals that may warrant investigator review.\n\n"
        "Possible Explanations\n"
        "Observed signals may result from legitimate editing, compression, "
        "metadata removal, image processing, capture conditions, or other "
        "non-malicious causes.\n\n"
        "Limitations\n"
        "The review score is not a probability that the image was "
        "AI-generated and does not establish authenticity or manipulation.\n\n"
        "Recommended Next Steps\n"
        "Review the original evidence, preserve file integrity, compare "
        "metadata and visual findings, and use additional forensic methods "
        "before reaching a final conclusion."
    )


def explain_evidence(
    evidence: dict[str, Any],
) -> dict[str, Any]:
    """
    Explain forensic findings using either deterministic
    fallback mode or an authorized OpenAI API request.

    AI output is explanatory only and does not replace
    the underlying forensic evidence.
    """

    mode = os.getenv(
        "AI_EXPLAINER_MODE",
        "mock",
    ).lower()

    model = os.getenv(
        "AI_EXPLAINER_MODEL",
        "gpt-5.6-luna",
    )

    prompt = build_explanation_prompt(
        evidence,
    )

    if mode == "mock":
        return {
            "mode": "mock",
            "model": "deterministic-fallback",
            "explanation": create_fallback_explanation(
                evidence,
            ),
            "prompt": prompt,
        }

    if mode != "api":
        raise ValueError(
            "AI_EXPLAINER_MODE must be 'mock' or 'api'."
        )

    api_key = os.getenv(
        "OPENAI_API_KEY",
    )

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is required when "
            "AI_EXPLAINER_MODE is 'api'."
        )

    client = OpenAI(
        api_key=api_key,
    )

    response = client.responses.create(
        model=model,
        input=prompt,
    )

    return {
        "mode": "api",
        "model": model,
        "explanation": response.output_text,
        "prompt": prompt,
    }
