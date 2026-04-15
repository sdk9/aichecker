"""
Unit tests for ai_detector.py heuristic signal functions.

Run with:
    cd backend && python -m pytest tests/test_ai_detector.py -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from app.services.ai_detector import (
    _text_burstiness,
    _vocabulary_richness,
    _transition_phrases,
    _paragraph_homogeneity,
    _sentence_self_similarity,
    _template_placeholder_check,
    _professional_buzzwords,
    _split_into_units,
)


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

AI_CV_TEXT = """
Results-driven and detail-oriented professional with a proven track record of
delivering innovative solutions. Passionate about continuous improvement and
leveraging cutting-edge technologies to streamline workflows.

Strong communication skills and excellent analytical thinking. Committed to
excellence and dedicated to driving results in a fast-paced environment.
Highly motivated team player with demonstrated ability to collaborate across
cross-functional teams. Seeking to leverage my comprehensive understanding of
data-driven best practices to empower stakeholders.

Results-driven professional with a holistic approach to problem-solving.
Adept at spearheading transformative initiatives that deliver actionable
insights. Committed to best practices and continuous improvement throughout
the entire software development lifecycle.
"""

HUMAN_TEXT = """
I started programming in 2018 when I picked up an old laptop from a garage
sale. It had Linux on it, which was annoying at first.

After failing to get Wi-Fi working for three weeks, I gave up and just started
learning Python offline using a PDF I'd found before the trip.

The first thing I built was a script that renamed all my music files. It was
terrible but it worked, mostly. Sometimes it renamed the wrong files. I lost
about forty songs.

Later I got a job writing automation scripts for a small manufacturing company.
The boss wanted reports but didn't want to pay for software, so I made something
in Excel first and then moved it to Python when that got too slow.
"""

AI_CV_WITH_PLACEHOLDERS = """
[Your Full Name]
[Your Email] | [Your Phone] | City, Country

PROFESSIONAL SUMMARY
Results-driven software developer with proven track record.
Company Name - Job Title - (Year - Present)
University Name - Degree - University

SKILLS
Strong communication skills, attention to detail, team player.
"""

TEMPLATE_TEXT = """
Dear Hiring Manager,

My name is [Your Full Name] and I am applying for the [Job Title] position at Company Name.
I graduated from University Name with a degree in Computer Science.
I worked at Company Name from (Year - Present).

Please contact me at [Your Email].
"""


# ─────────────────────────────────────────────────────────────────────────────
# _split_into_units
# ─────────────────────────────────────────────────────────────────────────────

class TestSplitIntoUnits:
    def test_splits_on_sentence_endings(self):
        text = "Hello world. This is a test. Another sentence here."
        units = _split_into_units(text)
        assert len(units) >= 2

    def test_splits_on_newlines(self):
        text = "First bullet point here\nSecond bullet item there\nThird entry listed"
        units = _split_into_units(text)
        assert len(units) >= 2

    def test_filters_too_short(self):
        text = "Hi.\nHello.\nOne two three four five six seven eight."
        units = _split_into_units(text)
        # Only the last one has >= 2 words and satisfies the filter
        assert all(len(u.split()) >= 2 for u in units)

    def test_filters_too_long(self):
        long_unit = " ".join(["word"] * 90)
        text = f"{long_unit}\nNormal sentence here today."
        units = _split_into_units(text)
        # The 90-word unit should be filtered out
        assert all(len(u.split()) <= 80 for u in units)

    def test_empty_text(self):
        assert _split_into_units("") == []


# ─────────────────────────────────────────────────────────────────────────────
# _text_burstiness
# ─────────────────────────────────────────────────────────────────────────────

class TestTextBurstiness:
    def test_uniform_ai_text_scores_high(self):
        # Uniform bullet points — AI-like
        uniform = "\n".join([
            "Managed software development projects efficiently",
            "Coordinated cross-functional team collaboration",
            "Delivered innovative solutions on schedule",
            "Optimised database performance significantly",
            "Implemented automated testing procedures",
            "Reviewed code for quality assurance",
        ])
        score, sig = _text_burstiness(uniform)
        assert score >= 0.45, f"Expected high AI score for uniform text, got {score}"

    def test_varied_human_text_scores_lower(self):
        score, sig = _text_burstiness(HUMAN_TEXT)
        assert score <= 0.55, f"Expected lower score for human text, got {score}"

    def test_too_few_units_returns_default(self):
        score, sig = _text_burstiness("Short text.")
        assert score == 0.3
        assert "Too few" in sig.description

    def test_returns_signal_with_cv_in_details(self):
        score, sig = _text_burstiness(HUMAN_TEXT)
        assert "CV=" in sig.details


# ─────────────────────────────────────────────────────────────────────────────
# _vocabulary_richness
# ─────────────────────────────────────────────────────────────────────────────

class TestVocabularyRichness:
    def test_repetitive_text_scores_higher(self):
        repetitive = " ".join(["the quick brown fox jumps over the lazy dog"] * 20)
        score, _ = _vocabulary_richness(repetitive)
        assert score >= 0.3

    def test_diverse_text_scores_lower(self):
        score, _ = _vocabulary_richness(HUMAN_TEXT)
        assert score <= 0.50

    def test_short_text_returns_default(self):
        score, sig = _vocabulary_richness("Too short")
        assert score == 0.3
        assert "Insufficient" in sig.description

    def test_ttr_in_details(self):
        score, sig = _vocabulary_richness(HUMAN_TEXT)
        assert "TTR=" in sig.details


# ─────────────────────────────────────────────────────────────────────────────
# _transition_phrases
# ─────────────────────────────────────────────────────────────────────────────

class TestTransitionPhrases:
    def test_ai_text_high_density(self):
        score, sig = _transition_phrases(AI_CV_TEXT)
        assert score >= 0.48, f"Expected high phrase score for AI CV, got {score}"

    def test_human_text_low_density(self):
        score, sig = _transition_phrases(HUMAN_TEXT)
        assert score <= 0.48, f"Expected lower phrase score for human text, got {score}"

    def test_specific_phrases_detected(self):
        text = "Furthermore, it is important to note that in conclusion this is key."
        score, sig = _transition_phrases(text)
        assert score >= 0.48

    def test_density_in_details(self):
        _, sig = _transition_phrases(AI_CV_TEXT)
        assert "Density=" in sig.details


# ─────────────────────────────────────────────────────────────────────────────
# _paragraph_homogeneity
# ─────────────────────────────────────────────────────────────────────────────

class TestParagraphHomogeneity:
    def test_double_newline_paragraphs(self):
        text = (
            "This is paragraph one with enough words to count for analysis purposes here.\n\n"
            "This is paragraph two with enough words to count for analysis purposes here.\n\n"
            "This is paragraph three with enough words to count for analysis purposes here."
        )
        score, sig = _paragraph_homogeneity(text)
        assert score > 0.3, "Should detect homogeneity in paragraphs"

    def test_single_newline_fallback(self):
        # CV-style text with single newlines — should NOT return the fallback 0.3
        cv_lines = "\n".join([
            "Managed software projects delivering innovative results on schedule regularly",
            "Coordinated team collaboration across cross-functional departments effectively",
            "Implemented automated testing ensuring comprehensive quality assurance",
            "Optimised database performance reducing query execution time significantly",
        ])
        score, sig = _paragraph_homogeneity(cv_lines)
        # Should use single-newline fallback and find homogeneity
        assert "Too few paragraphs" not in sig.description

    def test_too_few_paragraphs(self):
        score, sig = _paragraph_homogeneity("One line.")
        assert score == 0.3
        assert "Too few" in sig.description


# ─────────────────────────────────────────────────────────────────────────────
# _sentence_self_similarity
# ─────────────────────────────────────────────────────────────────────────────

class TestSentenceSelfSimilarity:
    def test_repetitive_vocab_scores_high(self):
        # Repeating the same vocabulary in every sentence
        text = "\n".join([
            "The team delivers results through innovative collaborative approaches",
            "The team achieves results via innovative cross-functional collaboration",
            "The team produces results using innovative strategic methodologies",
            "The team drives results with innovative data-driven insights",
            "The team creates results from innovative comprehensive solutions",
        ])
        score, _ = _sentence_self_similarity(text)
        assert score >= 0.30

    def test_diverse_text_scores_lower(self):
        score, _ = _sentence_self_similarity(HUMAN_TEXT)
        assert score <= 0.50

    def test_too_few_sentences(self):
        score, sig = _sentence_self_similarity("Short text only.")
        assert score == 0.3
        assert "Too few" in sig.description


# ─────────────────────────────────────────────────────────────────────────────
# _template_placeholder_check
# ─────────────────────────────────────────────────────────────────────────────

class TestTemplatePlaceholderCheck:
    def test_multiple_placeholders_score_very_high(self):
        score, sig = _template_placeholder_check(TEMPLATE_TEXT)
        assert score >= 0.82, f"Expected high score with placeholders, got {score}"
        assert sig.severity.value in ("high",)

    def test_cv_placeholders_detected(self):
        score, sig = _template_placeholder_check(AI_CV_WITH_PLACEHOLDERS)
        assert score >= 0.82

    def test_no_placeholders_score_low(self):
        score, sig = _template_placeholder_check(HUMAN_TEXT)
        assert score <= 0.10, f"Expected low score for human text, got {score}"

    def test_bracket_placeholder_detected(self):
        text = "Please send your CV to [Your Email] by Friday."
        score, _ = _template_placeholder_check(text)
        assert score >= 0.82

    def test_count_in_details(self):
        _, sig = _template_placeholder_check(TEMPLATE_TEXT)
        assert "Placeholders found:" in sig.details


# ─────────────────────────────────────────────────────────────────────────────
# _professional_buzzwords
# ─────────────────────────────────────────────────────────────────────────────

class TestProfessionalBuzzwords:
    def test_ai_cv_scores_high(self):
        score, sig = _professional_buzzwords(AI_CV_TEXT)
        assert score >= 0.65, f"Expected high buzzword score for AI CV, got {score}"

    def test_human_text_scores_low(self):
        score, sig = _professional_buzzwords(HUMAN_TEXT)
        assert score <= 0.35, f"Expected low buzzword score for human text, got {score}"

    def test_density_in_details(self):
        _, sig = _professional_buzzwords(AI_CV_TEXT)
        assert "Density=" in sig.details

    def test_no_buzzwords(self):
        score, sig = _professional_buzzwords("The cat sat on the mat. It was sunny outside.")
        assert score <= 0.10


# ─────────────────────────────────────────────────────────────────────────────
# Integration: combined signals on known AI CV text
# ─────────────────────────────────────────────────────────────────────────────

class TestCombinedSignalsOnAICV:
    """
    Sanity check: all heuristic signals together should lean toward AI
    for text that is clearly AI-generated.
    """

    def test_ai_cv_has_high_phrase_score(self):
        score, _ = _transition_phrases(AI_CV_TEXT)
        assert score >= 0.48

    def test_ai_cv_has_high_buzzword_score(self):
        score, _ = _professional_buzzwords(AI_CV_TEXT)
        assert score >= 0.65

    def test_human_story_has_low_phrase_score(self):
        score, _ = _transition_phrases(HUMAN_TEXT)
        assert score <= 0.48

    def test_template_cv_triggers_placeholder_floor(self):
        # When placeholders found, floor logic in analyze_document would set >= 0.72
        tmpl_score, _ = _template_placeholder_check(AI_CV_WITH_PLACEHOLDERS)
        assert tmpl_score >= 0.80, "Template score must be >= 0.80 to trigger floor"
