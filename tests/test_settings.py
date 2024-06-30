""".. include:: README.md

A unique pytest example...
"""

import pytest

from core.settings.settings import Settings


def test_settings_singleton() -> None:
    """Test the singleton pattern"""
    config1 = Settings()
    config2 = Settings()
    # instantiation of a second object must yield the same object
    assert id(config1) == id(config2)  # noqa: S101


if __name__ == "__main__":  # pragma: no cover
    pytest.main()
