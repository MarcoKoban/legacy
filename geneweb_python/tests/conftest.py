"""Test configuration and fixtures."""

import warnings

import pytest

warnings.filterwarnings(
    "ignore",
    message="'crypt' is deprecated and slated for removal in Python 3.13",
    category=DeprecationWarning,
    module=r"passlib\.utils.*",
)

collect_ignore = [
    "tests/unit/api/test_privacy_search_service.py",
    "tests/integration/test_search_endpoints.py",
    "tests/security/test_privacy_rgpd_compliance.py",
]


@pytest.fixture
def sample_test_data():
    """Sample test data for TDD development."""
    return {
        "test_string": "foo bar",
        "test_numbers": [1, 10, 100, 1000],
        "test_places": ["[foo-bar] - boobar (baz)", "simple place"],
    }
