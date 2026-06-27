"""Tests for DupeClean summary generator module."""

from __future__ import annotations

from dupeclean.summary_gen import (
    CleanupSummaryGenerator,
    format_summary,
    generate_cleanup_summary,
)


class TestCleanupSummaryGenerator:
    def test_add_section(self):
        gen = CleanupSummaryGenerator()
        gen.add_section("Test", "Content")
        assert len(gen.sections) == 1

    def test_render_empty(self):
        gen = CleanupSummaryGenerator()
        assert "No summary" in gen.render()

    def test_render_with_sections(self):
        gen = CleanupSummaryGenerator()
        gen.add_section("Section 1", "Content 1")
        gen.add_section("Section 2", "Content 2")
        text = gen.render()
        assert "Section 1" in text
        assert "Section 2" in text


class TestGenerateCleanupSummary:
    def test_basic(self):
        gen = generate_cleanup_summary(
            files_before=100,
            files_after=80,
            size_before=10000,
            size_after=8000,
            groups_cleaned=10,
            errors=2,
            duration=5.0,
        )
        text = gen.render()
        assert "100" in text
        assert "80" in text
        assert "2,000" in text or "2.0" in text

    def test_zero_duration(self):
        gen = generate_cleanup_summary(100, 80, 10000, 8000, 10, 0, 0.0)
        text = gen.render()
        assert "N/A" in text


class TestFormatSummary:
    def test_basic(self):
        gen = CleanupSummaryGenerator()
        gen.add_section("Test", "Content")
        text = format_summary(gen)
        assert "Test" in text
