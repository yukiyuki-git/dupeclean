"""Tests for DupeClean feedback module."""

from __future__ import annotations

from dupeclean.feedback import (
    CleanupFeedback,
    FeedbackItem,
    generate_feedback,
)


class TestCleanupFeedback:
    def test_success(self):
        fb = CleanupFeedback()
        fb.success("Done")
        assert len(fb.items) == 1
        assert fb.items[0].category == "success"

    def test_warning(self):
        fb = CleanupFeedback()
        fb.warning("Watch out")
        assert len(fb.items) == 1

    def test_error(self):
        fb = CleanupFeedback()
        fb.error("Failed")
        assert fb.has_errors is True
        assert fb.error_count == 1

    def test_warning_count(self):
        fb = CleanupFeedback()
        fb.warning("a")
        fb.warning("b")
        assert fb.warning_count == 2

    def test_render(self):
        fb = CleanupFeedback()
        fb.success("Done")
        fb.warning("Watch")
        text = fb.render()
        assert "Done" in text
        assert "Watch" in text


class TestGenerateFeedback:
    def test_with_deletions(self):
        fb = generate_feedback(10, 5, 1000, [])
        assert fb.has_errors is False

    def test_with_errors(self):
        fb = generate_feedback(10, 5, 1000, ["Error 1", "Error 2"])
        assert fb.has_errors is True
        assert fb.error_count == 2

    def test_no_files(self):
        fb = generate_feedback(0, 0, 0, [])
        assert any(i.category == "info" for i in fb.items)


class TestFeedbackItem:
    def test_defaults(self):
        item = FeedbackItem(category="test", message="msg")
        assert item.details == ""
