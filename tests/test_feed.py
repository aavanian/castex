"""Tests for feed merge/dedupe module."""

from datetime import date

from castex.feed import merge_feed_items
from castex.models import FeedItem


def test_merge_empty_feeds() -> None:
    """Test merging two empty feeds."""
    result = merge_feed_items([], [])

    assert result == []


def test_merge_with_one_empty() -> None:
    """Test merging when one feed is empty."""
    items = [
        FeedItem(
            guid="guid1",
            title="Episode 1",
            published=date(2020, 1, 1),
            link="https://example.com/ep1",
            description="Description 1",
        )
    ]

    result = merge_feed_items(items, [])

    assert len(result) == 1
    assert result[0].guid == "guid1"


def test_merge_without_duplicates() -> None:
    """Test merging feeds with no duplicates."""
    current = [
        FeedItem(
            guid="guid1",
            title="Episode 1",
            published=date(2020, 1, 1),
            link="https://example.com/ep1",
            description="Description 1",
        )
    ]
    historic = [
        FeedItem(
            guid="guid2",
            title="Episode 2",
            published=date(2019, 1, 1),
            link="https://example.com/ep2",
            description="Description 2",
        )
    ]

    result = merge_feed_items(current, historic)

    assert len(result) == 2


def test_merge_deduplicates_by_guid() -> None:
    """Test that merge deduplicates by guid, preferring current feed."""
    current = [
        FeedItem(
            guid="guid1",
            title="Current Title",
            published=date(2020, 1, 1),
            link="https://example.com/ep1-current",
            description="Current description",
        )
    ]
    historic = [
        FeedItem(
            guid="guid1",
            title="Historic Title",
            published=date(2020, 1, 1),
            link="https://example.com/ep1-historic",
            description="Historic description",
        )
    ]

    result = merge_feed_items(current, historic)

    assert len(result) == 1
    assert result[0].title == "Current Title"
    assert result[0].link == "https://example.com/ep1-current"


def test_merge_sorts_by_date_descending() -> None:
    """Test that merged items are sorted by published date descending."""
    items1 = [
        FeedItem(
            guid="guid1",
            title="Episode 1",
            published=date(2020, 3, 1),
            link="https://example.com/ep1",
            description=None,
        )
    ]
    items2 = [
        FeedItem(
            guid="guid2",
            title="Episode 2",
            published=date(2020, 1, 1),
            link="https://example.com/ep2",
            description=None,
        ),
        FeedItem(
            guid="guid3",
            title="Episode 3",
            published=date(2020, 5, 1),
            link="https://example.com/ep3",
            description=None,
        ),
    ]

    result = merge_feed_items(items1, items2)

    assert len(result) == 3
    assert result[0].guid == "guid3"
    assert result[1].guid == "guid1"
    assert result[2].guid == "guid2"


def test_merge_handles_multiple_duplicates() -> None:
    """Test merging with multiple duplicates."""
    current = [
        FeedItem(
            guid="guid1",
            title="Title 1 (current)",
            published=date(2020, 1, 1),
            link="https://example.com/ep1",
            description=None,
        ),
        FeedItem(
            guid="guid2",
            title="Title 2",
            published=date(2020, 2, 1),
            link="https://example.com/ep2",
            description=None,
        ),
    ]
    historic = [
        FeedItem(
            guid="guid1",
            title="Title 1 (historic)",
            published=date(2020, 1, 1),
            link="https://example.com/ep1-old",
            description=None,
        ),
        FeedItem(
            guid="guid3",
            title="Title 3",
            published=date(2019, 1, 1),
            link="https://example.com/ep3",
            description=None,
        ),
    ]

    result = merge_feed_items(current, historic)

    assert len(result) == 3
    guids = {item.guid for item in result}
    assert guids == {"guid1", "guid2", "guid3"}

    guid1_item = next(item for item in result if item.guid == "guid1")
    assert guid1_item.title == "Title 1 (current)"
