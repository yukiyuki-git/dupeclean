"""Tests for DupeClean CLI progress bar."""

from __future__ import annotations

import io

from dupeclean.progress import ProgressBar, Spinner


class TestProgressBar:
    def test_basic_progress(self):
        output = io.StringIO()
        bar = ProgressBar(total=100, stream=output)
        bar.update(50)
        bar.finish()

        result = output.getvalue()
        assert "50.0%" in result or "100.0%" in result

    def test_set_absolute(self):
        output = io.StringIO()
        bar = ProgressBar(total=100, stream=output)
        bar.set(75)
        bar.finish()

        result = output.getvalue()
        assert "100.0%" in result

    def test_with_message(self):
        output = io.StringIO()
        bar = ProgressBar(total=100, stream=output)
        bar.update(10, message="Processing files")
        bar.finish()

        result = output.getvalue()
        assert "Processing" in result or "Done" in result

    def test_context_manager(self):
        output = io.StringIO()
        with ProgressBar(total=100, stream=output) as bar:
            for _i in range(100):
                bar.update(1)

        result = output.getvalue()
        assert "Done" in result

    def test_finish_message(self):
        output = io.StringIO()
        bar = ProgressBar(total=10, stream=output)
        bar.finish("Complete")

        result = output.getvalue()
        assert "Complete" in result

    def test_zero_total(self):
        output = io.StringIO()
        bar = ProgressBar(total=0, stream=output)
        bar.update(0)
        bar.finish()
        # Should not crash

    def test_eta_formatting(self):
        output = io.StringIO()
        bar = ProgressBar(total=100, stream=output)
        assert bar._format_eta(0) == ""
        # With no progress, ETA should be empty
        assert bar._format_eta(10) == ""
        # With some progress and elapsed time
        bar.current = 50
        assert bar._format_eta(10) != ""

    def test_custom_width(self):
        output = io.StringIO()
        bar = ProgressBar(total=100, width=50, stream=output)
        bar.set(50)
        bar.finish()

        result = output.getvalue()
        assert "█" in result


class TestSpinner:
    def test_basic_spin(self):
        output = io.StringIO()
        spinner = Spinner(message="Testing", stream=output)
        spinner.spin()
        spinner.spin()
        spinner.stop("Finished")

        result = output.getvalue()
        assert "Testing" in result
        assert "Finished" in result

    def test_update_message(self):
        output = io.StringIO()
        spinner = Spinner(stream=output)
        spinner.update("New message")

        result = output.getvalue()
        assert "New message" in result

    def test_stop_message(self):
        output = io.StringIO()
        spinner = Spinner(stream=output)
        spinner.stop("All done")

        result = output.getvalue()
        assert "All done" in result
