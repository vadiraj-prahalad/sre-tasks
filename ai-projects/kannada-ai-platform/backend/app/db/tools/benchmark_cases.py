"""
Retrieval benchmark case definitions.

Contains benchmark data only.
Evaluation logic belongs in evaluate_retrieval_baseline.py.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievalCase:
    question: str
    acceptable_title_terms: tuple[str, ...]


# ==========================================================
# Canonical Entity Retrieval
# ==========================================================

CANONICAL_CASES = [
    RetrievalCase(
        question="ಕುವೆಂಪು ಯಾರು?",
        acceptable_title_terms=(
            "ಕುವೆಂಪು",
        ),
    ),
    RetrievalCase(
        question="ಕುವೆಂಪು ಕನ್ನಡ ಸಾಹಿತ್ಯಕ್ಕೆ ನೀಡಿದ ಕೊಡುಗೆ",
        acceptable_title_terms=(
            "Kuvempu",
            "ಕುವೆಂಪು",
        ),
    ),
    RetrievalCase(
        question="ಪುರಂದರ ದಾಸರು ಯಾರು?",
        acceptable_title_terms=(
            "ಪುರಂದರ ದಾಸರು",
        ),
    ),
    RetrievalCase(
        question="ಪುರಂದರ ದಾಸರ ಕೊಡುಗೆ",
        acceptable_title_terms=(
            "ಪುರಂದರ ದಾಸರ ಕೊಡುಗೆ",
        ),
    ),
    RetrievalCase(
        question="ಮಧ್ವಾಚಾರ್ಯರು ಯಾರು?",
        acceptable_title_terms=(
            "ಮಧ್ವಾಚಾರ್ಯರು",
            "Madhwacharya",
        ),
    ),
    RetrievalCase(
        question="ವಿಷ್ಣುವರ್ಧನ್ ಯಾರು?",
        acceptable_title_terms=(
            "ವಿಷ್ಣುವರ್ಧನ್",
            "Vishnuvardhan",
        ),
    ),
    RetrievalCase(
        question="ಮೈಸೂರು ಅರಮನೆ ಬಗ್ಗೆ ಹೇಳಿ",
        acceptable_title_terms=(
            "ಮೈಸೂರು ಅರಮನೆ",
            "Mysore Palace",
        ),
    ),
]


# ==========================================================
# Alias Resolution Retrieval
# ==========================================================

ALIAS_CASES = [
    RetrievalCase(
        question="ಡಾ ವಿಷ್ಣುವರ್ಧನ್ ಬಗ್ಗೆ ಹೇಳಿ",
        acceptable_title_terms=(
            "ಡಾ ವಿಷ್ಣುವರ್ಧನ್",
            "ವಿಷ್ಣುವರ್ಧನ್",
            "Dr Vishnuvardhan",
        ),
    ),
    RetrievalCase(
        question="ಡಾ ರಾಜಕುಮಾರ್ ಯಾರು?",
        acceptable_title_terms=(
            "Dr Rajkumar",
            "ರಾಜಕುಮಾರ್",
            "ರಾಜ್‌ಕುಮಾರ್",
        ),
    ),
]


# ==========================================================
# Relationship Retrieval
# ==========================================================

RELATIONSHIP_CASES = [
    RetrievalCase(
        question="ಉಡುಪಿ ಮಠದ ಜೊತೆ ಮಧ್ವರ ಸಂಬಂಧ ಏನು",
        acceptable_title_terms=(
            "Madhwacharya",
            "ಮಧ್ವಾಚಾರ್ಯ",
        ),
    ),
]


# ==========================================================
# Mixed Language Retrieval
# (Will be expanded in future milestones)
# ==========================================================

MIXED_LANGUAGE_CASES = []


# ==========================================================
# Negative Retrieval
# (Will be expanded in future milestones)
# ==========================================================

NEGATIVE_CASES = []


# ==========================================================
# Complete Benchmark Suite
#
# The evaluator imports only TEST_CASES.
# Category-wise metrics can later iterate over the individual
# category lists without modifying the evaluator.
# ==========================================================

TEST_CASES = (
    CANONICAL_CASES
    + ALIAS_CASES
    + RELATIONSHIP_CASES
    + MIXED_LANGUAGE_CASES
    + NEGATIVE_CASES
)
