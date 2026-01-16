"""Feed operations: merge, deduplicate, and transform."""

from castex.models import FeedItem


def merge_feed_items(
    current_feed: list[FeedItem],
    historic_feed: list[FeedItem],
) -> list[FeedItem]:
    """Merge two feeds, deduplicating by guid.

    Current feed items take precedence over historic items.
    Result is sorted by published date descending.
    """
    items_by_guid: dict[str, FeedItem] = {}

    for item in historic_feed:
        items_by_guid[item.guid] = item

    for item in current_feed:
        items_by_guid[item.guid] = item

    merged = list(items_by_guid.values())
    merged.sort(key=lambda item: item.published, reverse=True)

    return merged
