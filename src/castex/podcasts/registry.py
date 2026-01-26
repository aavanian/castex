"""Registry for podcast providers and enrichers."""

from castex.podcasts.base import EpisodeEnricher, FeedProvider
from castex.podcasts.in_our_time.enricher import InOurTimeEnricher
from castex.podcasts.in_our_time.feed import InOurTimeFeedProvider

_FEED_PROVIDERS: dict[str, type[FeedProvider]] = {
    "in_our_time": InOurTimeFeedProvider,
}

_ENRICHERS: dict[str, type[EpisodeEnricher]] = {
    "in_our_time": InOurTimeEnricher,
}


def list_podcasts() -> list[str]:
    """Return list of available podcast IDs."""
    return list(_FEED_PROVIDERS.keys())


def get_feed_provider(podcast_id: str) -> FeedProvider | None:
    """Get the feed provider for a podcast, or None if not found."""
    provider_class = _FEED_PROVIDERS.get(podcast_id)
    if provider_class is None:
        return None
    return provider_class()


def get_enricher(podcast_id: str) -> EpisodeEnricher | None:
    """Get the episode enricher for a podcast, or None if not found."""
    enricher_class = _ENRICHERS.get(podcast_id)
    if enricher_class is None:
        return None
    return enricher_class()
