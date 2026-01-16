"""Tests for podcast registry."""

from castex.podcasts.registry import get_enricher, get_feed_provider, list_podcasts


def test_list_podcasts() -> None:
    """Test listing available podcasts."""
    podcasts = list_podcasts()

    assert "in_our_time" in podcasts


def test_get_feed_provider() -> None:
    """Test getting feed provider for In Our Time."""
    provider = get_feed_provider("in_our_time")

    assert provider is not None
    assert provider.is_feed_complete() is True


def test_get_feed_provider_unknown() -> None:
    """Test getting feed provider for unknown podcast returns None."""
    provider = get_feed_provider("unknown_podcast")

    assert provider is None


def test_get_enricher() -> None:
    """Test getting enricher for In Our Time."""
    enricher = get_enricher("in_our_time")

    assert enricher is not None


def test_get_enricher_unknown() -> None:
    """Test getting enricher for unknown podcast returns None."""
    enricher = get_enricher("unknown_podcast")

    assert enricher is None
