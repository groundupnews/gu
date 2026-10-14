"""Data for the GroundUp Puzzles block."""

import logging

import requests
from django.conf import settings
from django.core.cache import cache
from django.utils.dateparse import parse_datetime

logger = logging.getLogger("django")

CACHE_KEY = "puzzles_block:puzzles"
# The last answer that worked (we chache)
STALE_KEY = "puzzles_block:puzzles:last_good"
STALE_SECONDS = 24 * 60 * 60
RETRY_SECONDS = 60


def _fetch():
    """The puzzles site's puzzles, or None"""
    url = settings.PUZZLES_API_URL
    try:
        response = requests.get(
            url,
            timeout=settings.PUZZLES_API_TIMEOUT,
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        puzzles = response.json()["puzzles"]
    except (requests.RequestException, ValueError, KeyError, TypeError):
        logger.warning("Puzzles block: could not read %s", url, exc_info=True)
        return None
    if not isinstance(puzzles, dict):
        logger.warning("Puzzles block: unexpected payload from %s", url)
        return None
    return puzzles


def remote_puzzles():
    """Cached puzzles from the puzzles site."""
    puzzles = cache.get(CACHE_KEY)
    if puzzles is not None:
        return puzzles
    puzzles = _fetch()
    if puzzles is None:
        puzzles = cache.get(STALE_KEY) or {}
        cache.set(CACHE_KEY, puzzles, RETRY_SECONDS)
        return puzzles
    cache.set(CACHE_KEY, puzzles, settings.PUZZLES_API_CACHE_SECONDS)
    cache.set(STALE_KEY, puzzles, STALE_SECONDS)
    return puzzles


GAME_PATHS = {
    "crossword": "/crossword/",
    "groupup": "/groupup/",
    "quiz": "/quizzes/",
    "sudoku": "/sudoku/",
    "target": "/target/",
}

# Placeholders (when the puzzles server is burning)
PLACEHOLDER_SIZE = 9

PLACEHOLDER_BLOCKS = (
    "...#....."
    "...#..#.."
    "......#.."
    "##...#..."
    "...###..."
    "...#...##"
    "..#......"
    "..#..#..."
    ".....#..."
)

PLACEHOLDER_GIVENS = (
    "4...6...."
    "..9.3...6"
    "...3..7.8"
    ".8..2..7."
    "..36.51.."
    ".2..7..5."
    "1.7..4..."
    "5...1.2.."
    "....8...9"
)


def _puzzles_site_url(path):
    return settings.PUZZLES_SITE_URL.rstrip("/") + path


def _crossword_placeholder():
    """A 9x9 grid, unnumbered"""
    grid = [
        [
            {
                "block": PLACEHOLDER_BLOCKS[row * PLACEHOLDER_SIZE + col] == "#",
                "number": None,
            }
            for col in range(PLACEHOLDER_SIZE)
        ]
        for row in range(PLACEHOLDER_SIZE)
    ]
    return {
        "placeholder": True,
        "num_rows": PLACEHOLDER_SIZE,
        "num_cols": PLACEHOLDER_SIZE,
        "grid": grid,
    }


def _sudoku_placeholder():
    return {
        "placeholder": True,
        "cells": [c if c != "." else "" for c in PLACEHOLDER_GIVENS],
    }


def _target_placeholder():
    return {
        "placeholder": True,
        "title": "Target",
        "cells": [
            {"char": char, "centre": index == 4}
            for index, char in enumerate("GROUNDUPS")
        ],
    }


def _resolve(name, teaser, placeholder):
    """The real teaser if we have one; generic if we don't."""
    if teaser and teaser.get("available"):
        teaser = dict(teaser)
        teaser["published"] = parse_datetime(teaser.get("published") or "")
    else:
        teaser = placeholder
    teaser["url"] = _puzzles_site_url(GAME_PATHS[name])
    return teaser


def puzzles_block_context():
    """Everything the GroundUp Puzzles block template renders."""
    puzzles = remote_puzzles()
    return {
        "crossword": _resolve(
            "crossword", puzzles.get("crossword"), _crossword_placeholder()
        ),
        "groupup": _resolve("groupup", puzzles.get("groupup"), {"placeholder": True}),
        "quiz": _resolve("quiz", puzzles.get("quiz"), {"placeholder": True}),
        "sudoku": _resolve("sudoku", puzzles.get("sudoku"), _sudoku_placeholder()),
        "target": _resolve("target", puzzles.get("target"), _target_placeholder()),
        "puzzles_url": settings.PUZZLES_SITE_URL,
    }
