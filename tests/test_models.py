"""Tests for the Episode data model."""

from datetime import date

from castex.models import Episode, make_braggoscope_url, make_episode_id


def test_episode_creation() -> None:
    """Test that Episode can be created with valid data."""
    episode = Episode(
        id="the-siege-of-malta-1565",
        title="The Siege of Malta, 1565",
        broadcast_date=date(2017, 9, 21),
        contributors=["Anne Smith (Oxford)", "John Doe (Cambridge)"],
        description="A discussion about the siege of Malta.",
        source_url="https://www.bbc.co.uk/programmes/b0xyz123",
        categories=["History", "Military", "Medieval", "Mediterranean"],
        braggoscope_url="https://www.braggoscope.com/2017/09/21/the-siege-of-malta-1565.html",
    )

    assert episode.id == "the-siege-of-malta-1565"
    assert episode.title == "The Siege of Malta, 1565"
    assert episode.broadcast_date == date(2017, 9, 21)
    assert episode.contributors == ["Anne Smith (Oxford)", "John Doe (Cambridge)"]
    assert episode.description == "A discussion about the siege of Malta."
    assert episode.source_url == "https://www.bbc.co.uk/programmes/b0xyz123"
    assert episode.categories == ["History", "Military", "Medieval", "Mediterranean"]
    assert (
        episode.braggoscope_url
        == "https://www.braggoscope.com/2017/09/21/the-siege-of-malta-1565.html"
    )


def test_episode_with_optional_fields_none() -> None:
    """Test Episode with optional fields set to None."""
    episode = Episode(
        id="plato-symposium",
        title="Plato's Symposium",
        broadcast_date=date(2005, 1, 6),
        contributors=["Professor A", "Professor B"],
        description=None,
        source_url="https://www.bbc.co.uk/programmes/p00abc123",
        categories=["Philosophy", "Ancient", "Greece"],
        braggoscope_url=None,
    )

    assert episode.description is None
    assert episode.braggoscope_url is None


def test_make_episode_id_basic() -> None:
    """Test basic slug generation from title."""
    assert make_episode_id("The Siege of Malta, 1565") == "the-siege-of-malta-1565"


def test_make_episode_id_apostrophe() -> None:
    """Test slug generation with apostrophes."""
    assert make_episode_id("Plato's Symposium") == "platos-symposium"


def test_make_episode_id_special_chars() -> None:
    """Test slug generation with various special characters."""
    assert make_episode_id("E=mc2: Einstein's Equation") == "emc2-einsteins-equation"


def test_make_episode_id_multiple_spaces() -> None:
    """Test slug generation with multiple spaces."""
    assert make_episode_id("The   Great    Fire") == "the-great-fire"


def test_make_braggoscope_url() -> None:
    """Test braggoscope URL generation with date path."""
    url = make_braggoscope_url("the-siege-of-malta-1565", date(2017, 9, 21))
    assert url == "https://www.braggoscope.com/2017/09/21/the-siege-of-malta-1565.html"


def test_make_braggoscope_url_single_digit_date() -> None:
    """Test braggoscope URL with single-digit month and day are zero-padded."""
    url = make_braggoscope_url("platos-symposium", date(2005, 1, 6))
    assert url == "https://www.braggoscope.com/2005/01/06/platos-symposium.html"


def test_episode_with_reading_list() -> None:
    """Test Episode with reading_list field."""
    reading_list = [
        "Christopher Benfey, A Summer of Hummingbirds (Penguin Books, 2009)",
        "Judith Farr, The Gardens of Emily Dickinson (Harvard University Press, 2005)",
    ]
    episode = Episode(
        id="emily-dickinson",
        title="Emily Dickinson",
        broadcast_date=date(2017, 5, 4),
        contributors=["Fiona Green", "Linda Freedman"],
        description="Emily Dickinson was a startling poet.",
        source_url="https://www.bbc.co.uk/programmes/b08p3jlw",
        categories=["Literature", "Poetry", "American"],
        braggoscope_url=None,
        reading_list=reading_list,
    )

    assert episode.reading_list == reading_list
