"""Tests for scraper modules."""

from datetime import date
from pathlib import Path

from castex.scraper.bbc import parse_bbc_html, parse_rss_description_html
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
    """Test parsing episode data from BBC episode page."""
    html = (fixtures_dir / "bbc_episode_sample.html").read_text()

    result = parse_bbc_html(html)

    expected_text = (
        "Melvyn Bragg explores ideas that have influenced 20th century human rights and warfare."
    )
    assert result["short_description"] == expected_text
    assert result["description"] == expected_text
    assert result["contributors"] == []
    assert result["reading_list"] == []


def test_parse_bbc_html_no_description() -> None:
    """Test parsing handles missing description gracefully."""
    html = "<html><head><title>Test</title></head><body></body></html>"

    result = parse_bbc_html(html)

    assert result["short_description"] is None
    assert result["description"] is None
    assert result["contributors"] == []
    assert result["reading_list"] == []


def test_parse_bbc_html_new_format(fixtures_dir: Path) -> None:
    """Test parsing new format with structured paragraphs."""
    html = (fixtures_dir / "bbc_episode_new_format.html").read_text()

    result = parse_bbc_html(html)

    assert result["short_description"] == (
        "Melvyn Bragg and guests discuss Emily Dickinson (1830-1886), celebrated American poet."
    )
    assert result["description"] == (
        "Emily Dickinson was arguably the most startling and original poet in America in the C19th."
    )
    assert result["contributors"] == [
        "Fiona Green Senior Lecturer in English at Cambridge",
        "Linda Freedman Lecturer at University College London",
        "Paraic Finnerty Reader at the University of Portsmouth",
    ]
    assert result["reading_list"] == [
        "Christopher Benfey, A Summer of Hummingbirds (Penguin Books, 2009)",
        "Judith Farr, The Gardens of Emily Dickinson (Harvard University Press, 2005)",
    ]


def test_parse_rss_description_html_new_format() -> None:
    """Test parsing RSS description HTML with structured paragraphs."""
    html = """
    <p>Melvyn Bragg discusses Emily Dickinson.</p>
    <p>With </p>
    <p>Fiona Green Senior Lecturer at Cambridge</p>
    <p>and</p>
    <p>Linda Freedman Lecturer at UCL</p>
    <p>Reading list:</p>
    <p>A Summer of Hummingbirds (Penguin, 2009)</p>
    """

    result = parse_rss_description_html(html)

    assert result["description"] == "Melvyn Bragg discusses Emily Dickinson."
    assert result["contributors"] == [
        "Fiona Green Senior Lecturer at Cambridge",
        "Linda Freedman Lecturer at UCL",
    ]
    assert result["reading_list"] == ["A Summer of Hummingbirds (Penguin, 2009)"]


def test_parse_rss_description_html_old_format() -> None:
    """Test parsing RSS description HTML with old flat format."""
    html = """
    <p>Melvyn Bragg discusses the philosophy of mind.
    With John Smith, Professor at Oxford; Jane Doe, Reader at Cambridge.</p>
    """

    result = parse_rss_description_html(html)

    assert result["description"] == "Melvyn Bragg discusses the philosophy of mind."
    assert result["contributors"] == [
        "John Smith, Professor at Oxford",
        "Jane Doe, Reader at Cambridge",
    ]
    assert result["reading_list"] == []


def test_parse_rss_description_html_plain_text() -> None:
    """Test parsing RSS description HTML that is just plain text without p tags."""
    html = "Simple episode description without any HTML tags."

    result = parse_rss_description_html(html)

    assert result["description"] == "Simple episode description without any HTML tags."
    assert result["contributors"] == []
    assert result["reading_list"] == []


def test_parse_rss_description_html_empty() -> None:
    """Test parsing empty RSS description."""
    result = parse_rss_description_html("")

    assert result["description"] == ""
    assert result["contributors"] == []
    assert result["reading_list"] == []
