# this_file: tests/test_package.py
"""Test suite for claif_gem."""

import claif_gem


def test_version():
    """Verify package exposes version."""
    assert claif_gem.__version__
