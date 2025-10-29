"""First TDD test to verify setup works."""

import pytest


class TestSetup:
    """Test that our TDD environment is properly configured."""

    @pytest.mark.unit
    def test_python_environment_works(self):
        """Test that Python environment is working."""
        assert True

    @pytest.mark.unit
    def test_pytest_marks_work(self):
        """Test that pytest markers work correctly."""
        assert True

    @pytest.mark.tdd
    def test_first_tdd_cycle(self):
        """Our first TDD test - should pass to verify setup."""
        # This is our first GREEN test in the TDD cycle
        expected = "Hello TDD"
        actual = "Hello TDD"
        assert actual == expected
