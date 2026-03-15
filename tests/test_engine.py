import pytest

from speakeasy import get_engine
from speakeasy.engines.macos import MacOSSayEngine


class TestGetEngine:
    """Tests for the engine factory function."""

    def test_returns_macos_engine(self):
        engine = get_engine("say")
        assert isinstance(engine, MacOSSayEngine)

    def test_passes_voice_kwarg(self):
        engine = get_engine("say", voice="Samantha")
        assert engine.voice == "Samantha"

    def test_passes_rate_kwarg(self):
        engine = get_engine("say", rate=200)
        assert engine.rate == 200

    def test_unknown_engine_raises(self):
        with pytest.raises(ValueError, match="Unknown engine"):
            get_engine("nonexistent")
