"""Tests for scraper modules."""

from datetime import date
from pathlib import Path

from castex.scraper.bbc import parse_bbc_html
from castex.scraper.wikipedia import parse_wikipedia_html


def test_parse_wikipedia_html(fixtures_dir: Path) -> None:
    """Test parsing episode data from Wikipedia HTML."""
    html = (fixtures_dir / "wikipedia_sample.html").read_text()

    episodes = parse_wikipedia_html(html)

    assert len(episodes) == 4

    # Check first episode
    ep1 = episodes[0]
    assert ep1["title"] == "War in the 20th Century"
    assert ep1["broadcast_date"] == date(1998, 10, 15)
    assert ep1["source_url"] == "https://www.bbc.co.uk/programmes/p0054578"
    assert len(ep1["contributors"]) == 2
    assert "Michael Ignatieff, writer and broadcaster" in ep1["contributors"]

    # Check third episode (from 2023)
    ep3 = episodes[2]
    assert ep3["title"] == "The Siege of Malta, 1565"
    assert ep3["broadcast_date"] == date(2023, 9, 21)


def test_parse_wikipedia_html_preserves_spaces_around_links(fixtures_dir: Path) -> None:
    """Test that text around links is properly spaced."""
    html = (fixtures_dir / "wikipedia_sample.html").read_text()

    episodes = parse_wikipedia_html(html)

    # Find the Aristocracy episode which has linked institution names
    aristocracy = next(ep for ep in episodes if ep["title"] == "The Aristocracy")

    # Check that spaces are preserved around linked text
    contributor = aristocracy["contributors"][0]
    assert "the University of London" in contributor, (
        f"Missing space before 'University': {contributor}"
    )
    assert "London's Institute" in contributor, f"Missing space after 's: {contributor}"
    assert "Research and author" in contributor, f"Missing space before 'and': {contributor}"
    assert "of The Decline" in contributor, f"Missing space before 'The': {contributor}"


def test_parse_wikipedia_html_malformed() -> None:
    """Test parsing handles malformed HTML gracefully."""
    # Empty table
    html = '<table class="wikitable"><tbody></tbody></table>'
    assert parse_wikipedia_html(html) == []

    # No wikitable
    html = "<html><body><p>No table here</p></body></html>"
    assert parse_wikipedia_html(html) == []

    # Row without link
    html = """
    <table class="wikitable">
    <tr><th>Date</th><th>Title</th><th>Contributors</th></tr>
    <tr><td>No link</td><td>Title</td><td>Someone</td></tr>
    </table>
    """
    assert parse_wikipedia_html(html) == []


def test_parse_bbc_html(fixtures_dir: Path) -> None:
    """Test parsing description from BBC episode page."""
    html = (fixtures_dir / "bbc_episode_sample.html").read_text()

    description = parse_bbc_html(html)

    assert description == (
        "Melvyn Bragg explores ideas that have influenced 20th century human rights and warfare."
    )


def test_parse_bbc_html_no_description() -> None:
    """Test parsing handles missing description gracefully."""
    html = "<html><head><title>Test</title></head><body></body></html>"

    description = parse_bbc_html(html)

    assert description is None
