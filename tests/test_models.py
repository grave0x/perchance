"""Unit tests for perchance domain models."""
from perchance_toolkit.models.generation import ExportFormat, Generation

from perchance_toolkit.models.generator import Generator

from perchance_toolkit.models.user import AccountStatus, User

def test_generation_export_text() -> None:
    gen = Generation(
        id="test-1",
        generator_id="gen-123",
        generator_title="Test Gen",
        prompt="hello",
        output="world",
    )
    assert gen.to_export(ExportFormat.text) == "world"


def test_generation_export_json() -> None:
    gen = Generation(
        id="test-1",
        generator_id="gen-123",
        generator_title="Test Gen",
        prompt="hello",
        output="world",
    )
    result = gen.to_export(ExportFormat.json)
    assert '"id": "test-1"' in result
    assert '"output": "world"' in result


def test_user_default_anonymous() -> None:
    user = User()
    assert user.status == AccountStatus.anonymous
    assert user.username is None


def test_generator_defaults() -> None:
    gen = Generator(id="g-1", title="My Gen", author="me")
    assert gen.source == ""
    assert gen.version == 1
    assert gen.power_ups == []
