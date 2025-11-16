"""Test package initialization."""

import veloxdf


def test_package_imports():
    """Test that main classes can be imported from package."""
    assert hasattr(veloxdf, "DataFrame")
    assert hasattr(veloxdf, "Optimizer")


def test_version():
    """Test package version."""
    assert hasattr(veloxdf, "__version__")
    assert veloxdf.__version__ == "0.1.0"
