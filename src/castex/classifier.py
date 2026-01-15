"""LLM-based episode classification."""

import json
import logging

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

CLASSIFICATION_PROMPT = """Classify this podcast episode into categories.

Title: {title}
Description: {description}
Contributors: {contributors}

Assign 3-7 tags from these options:

Discipline: History, Philosophy, Science, Mathematics, Literature, Poetry, Religion, Theology, Art, Architecture, Music, Politics, Economics, Law, Medicine, Technology, Archaeology, Linguistics, Psychology

Era: Ancient, Classical, Medieval, Renaissance, Early Modern, Enlightenment, 19th Century, 20th Century, Contemporary

Region: Britain, Ireland, France, Germany, Italy, Greece, Rome, Spain, Netherlands, Scandinavia, Eastern Europe, Russia, Middle East, Persia, India, China, Japan, Africa, Americas

Return only a JSON array of tag strings, e.g. ["History", "Medieval", "France"]"""


async def classify_episode(
    title: str,
    description: str | None,
    contributors: list[str],
    base_url: str,
    api_key: str,
    model: str,
) -> list[str]:
    """Classify an episode using an LLM.

    Returns a list of category tags, or empty list on failure.
    """
    client = AsyncOpenAI(base_url=base_url, api_key=api_key or "dummy")

    prompt = CLASSIFICATION_PROMPT.format(
        title=title,
        description=description or "(No description available)",
        contributors=", ".join(contributors) if contributors else "(No contributors listed)",
    )

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        content = response.choices[0].message.content
        if not content:
            logger.warning("Empty response from LLM for episode: %s", title)
            return []

        categories = json.loads(content)
        if not isinstance(categories, list):
            logger.warning("LLM response is not a list for episode: %s", title)
            return []

        return [str(cat) for cat in categories]

    except json.JSONDecodeError:
        logger.warning("Invalid JSON from LLM for episode: %s", title)
        return []
    except Exception as e:
        logger.error("Error classifying episode %s: %s", title, e)
        return []
