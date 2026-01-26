"""In Our Time RSS feed parser."""

import xml.etree.ElementTree as ET
from datetime import date
from email.utils import parsedate_to_datetime

import httpx

from castex.models import FeedItem

RSS_FEED_URL = "https://podcasts.files.bbci.co.uk/b006qykl.rss"


def parse_rss_xml(xml_content: str) -> list[FeedItem]:
    """Parse RSS XML content into FeedItems."""
    root = ET.fromstring(xml_content)
    channel = root.find("channel")

    if channel is None:
        return []

    items: list[FeedItem] = []

    for item in channel.findall("item"):
        guid = _get_text(item, "guid")
        title = _get_text(item, "title")
        link = _get_text(item, "link")
        pub_date_str = _get_text(item, "pubDate")
        description = _get_text(item, "description")

        if not guid or not title or not link or not pub_date_str:
            continue

        published = _parse_rfc822_date(pub_date_str)
        if published is None:
            continue

        items.append(
            FeedItem(
                guid=guid,
                title=title,
                published=published,
                link=link,
                description=description,
            )
        )

    return items


def _get_text(element: ET.Element, tag: str) -> str | None:
    """Get text content of a child element."""
    child = element.find(tag)
    return child.text if child is not None else None


def _parse_rfc822_date(date_str: str) -> date | None:
    """Parse RFC 822 date format used in RSS."""
    try:
        dt = parsedate_to_datetime(date_str)
        return dt.date()
    except (ValueError, TypeError):
        return None


class InOurTimeFeedProvider:
    """Feed provider for BBC's In Our Time podcast."""

    def fetch_current_feed(self) -> list[FeedItem]:
        """Fetch and parse the current RSS feed."""
        response = httpx.get(RSS_FEED_URL, timeout=30.0)
        response.raise_for_status()
        return parse_rss_xml(response.text)

    def fetch_historic_feed(self) -> list[FeedItem]:
        """Return empty list - RSS feed contains full history."""
        return []

    def is_feed_complete(self) -> bool:
        """The BBC RSS feed contains the complete history since 1998."""
        return True
