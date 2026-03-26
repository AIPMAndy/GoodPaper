"""Basic tests for GoodPaper."""

import pytest
from pathlib import Path

# Test imports
def test_import_core():
    """Test that core module can be imported."""
    from goodpaper_mvp.core import analyze_document, format_document
    assert callable(analyze_document)
    assert callable(format_document)


def test_import_templates():
    """Test that templates module can be imported."""
    from goodpaper_mvp.templates import (
        list_template_packages,
        get_default_template_package,
    )
    assert callable(list_template_packages)
    assert callable(get_default_template_package)


def test_import_server():
    """Test that server module can be imported."""
    from goodpaper_mvp.server import GoodPaperHandler, run_server
    assert GoodPaperHandler is not None


def test_list_templates():
    """Test listing template packages."""
    from goodpaper_mvp.templates import list_template_packages

    packages = list_template_packages()
    assert isinstance(packages, list)
    assert len(packages) > 0

    # Check that packages have required attributes
    for pkg in packages:
        assert hasattr(pkg, 'name')
        assert hasattr(pkg, 'version')


def test_default_template():
    """Test getting default template."""
    from goodpaper_mvp.templates import get_default_template_package

    default = get_default_template_package()
    assert default is not None
    assert hasattr(default, 'template_path')
