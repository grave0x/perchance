"""Unit tests for search functionality."""
from datetime import datetime

from perchance_toolkit.models.search_result import GeneratorSearchResult


def test_from_api_parses_full_response() -> None:
    raw = {
        "name": "name-generator",
        "views": 42_000,
        "lastEditTime": 1_700_000_000_000,
        "lastEditTime_ago": 12345,
        "metaData": {
            "title": "🚀 Name Generator",
            "description": "Generate awesome names for your characters",
            "image": "https://example.com/img.png",
            "tags": ["fantasy", "names"],
            "header": {},
        },
    }
    result = GeneratorSearchResult.from_api(raw)
    assert result.name == "name-generator"
    assert result.title == "🚀 Name Generator"
    assert "awesome names" in result.description
    assert result.views == 42_000
    assert result.tags == ["fantasy", "names"]
    assert result.image_url == "https://example.com/img.png"
    assert isinstance(result.last_edit, datetime)
    assert result.last_edit.tzinfo is not None


def test_from_api_handles_minimal() -> None:
    raw = {"name": "minimal"}
    result = GeneratorSearchResult.from_api(raw)
    assert result.name == "minimal"
    assert result.title == ""
    assert result.description == ""
    assert result.views == 0
    assert result.last_edit is None
    assert result.tags == []
    assert result.image_url is None


def test_from_api_handles_null_metadata() -> None:
    raw = {"name": "test", "metaData": None, "views": 99}
    result = GeneratorSearchResult.from_api(raw)
    assert result.name == "test"
    assert result.title == ""
    assert result.views == 99
