"""Tests for In Our Time RSS feed parser."""

from datetime import date

from castex.podcasts.in_our_time.feed import InOurTimeFeedProvider, parse_rss_xml

SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" version="2.0">
  <channel>
    <title>In Our Time</title>
    <link>http://www.bbc.co.uk/programmes/b006qykl</link>
    <item>
      <title>The Siege of Malta (1565)</title>
      <link>https://www.bbc.co.uk/programmes/b09xyz123</link>
      <guid isPermaLink="false">urn:bbc:podcast:b09xyz123</guid>
      <pubDate>Thu, 21 Sep 2017 09:00:00 +0000</pubDate>
      <description>Melvyn Bragg discusses the Ottoman siege of Malta.</description>
    </item>
    <item>
      <title>Plato's Symposium</title>
      <link>https://www.bbc.co.uk/programmes/p00abc123</link>
      <guid isPermaLink="false">urn:bbc:podcast:p00abc123</guid>
      <pubDate>Thu, 06 Jan 2005 09:00:00 +0000</pubDate>
      <description>A discussion about Plato's famous dialogue.</description>
    </item>
  </channel>
</rss>
"""


def test_parse_rss_xml() -> None:
    """Test parsing RSS XML into FeedItems."""
    items = parse_rss_xml(SAMPLE_RSS)

    assert len(items) == 2
    assert items[0].guid == "urn:bbc:podcast:b09xyz123"
    assert items[0].title == "The Siege of Malta (1565)"
    assert items[0].published == date(2017, 9, 21)
    assert items[0].link == "https://www.bbc.co.uk/programmes/b09xyz123"
    assert items[0].description == "Melvyn Bragg discusses the Ottoman siege of Malta."


def test_parse_rss_xml_second_item() -> None:
    """Test second item in RSS feed."""
    items = parse_rss_xml(SAMPLE_RSS)

    assert items[1].guid == "urn:bbc:podcast:p00abc123"
    assert items[1].title == "Plato's Symposium"
    assert items[1].published == date(2005, 1, 6)


def test_parse_rss_xml_empty() -> None:
    """Test parsing empty RSS feed."""
    empty_rss = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
      <channel>
        <title>Empty Feed</title>
      </channel>
    </rss>
    """

    items = parse_rss_xml(empty_rss)

    assert items == []


def test_parse_rss_xml_no_description() -> None:
    """Test parsing RSS item without description."""
    rss_no_desc = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
      <channel>
        <item>
          <title>Episode Without Description</title>
          <link>https://example.com/ep</link>
          <guid>guid1</guid>
          <pubDate>Mon, 01 Jan 2024 09:00:00 +0000</pubDate>
        </item>
      </channel>
    </rss>
    """

    items = parse_rss_xml(rss_no_desc)

    assert len(items) == 1
    assert items[0].description is None


def test_feed_provider_is_feed_complete() -> None:
    """Test that In Our Time feed reports as complete."""
    provider = InOurTimeFeedProvider()

    assert provider.is_feed_complete() is True


def test_feed_provider_fetch_historic_feed() -> None:
    """Test that historic feed returns empty (not needed for IOT)."""
    provider = InOurTimeFeedProvider()

    items = provider.fetch_historic_feed()

    assert items == []
