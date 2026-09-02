from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from .models import Group, Block, BlockGroup

class BlockTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.group = Group.objects.create(
            name="Test Group",
            pages_include="page1",
            pages_exclude="page2"
        )
        
        cls.block1 = Block.objects.create(
            name="Test Block 1",
            html="This is test block 1 content"
        )

        cls.block2 = Block.objects.create(
            name="Test Block 2", 
            html="This is test block 2 content"
        )

        # Connect blocks to group through BlockGroup
        BlockGroup.objects.create(
            block=cls.block1,
            group=cls.group
        )

        BlockGroup.objects.create(
            block=cls.block2,
            group=cls.group
        )

    def test_block_str(self):
        """Test Block string representation
        
        Expected output:
        - Block string should match its name
        """
        self.assertEqual(str(self.block1), self.block1.name)

    def test_group_str(self):
        """Test Group string representation
        
        Expected output:
        - Group string should match its name
        """
        self.assertEqual(str(self.group), self.group.name)

    def test_group_block_list(self):
        """Test block_list() method
        
        Expected output:
        - Should return comma-separated list of block names
        - Should include all blocks in correct order
        """
        expected = f"{self.block1.name}, {self.block2.name}"
        self.assertEqual(self.group.block_list(), expected)

    def test_get_blocks(self):
        """Test get_blocks() method
        
        Expected output:
        - Should return QuerySet of 2 blocks
        - Should contain both test blocks
        - Blocks should be ordered by link_to_group
        """
        blocks = self.group.get_blocks()
        self.assertEqual(len(blocks), 2, "Expected exactly 2 blocks")
        self.assertIn(self.block1, blocks, "First block should be in result")
        self.assertIn(self.block2, blocks, "Second block should be in result")


# --------------------------------------------------------------------------
# The GroundUp Puzzles block. Its teasers arrive over HTTP from another
# site, so what's worth testing is surviving that site being slow, broken
# or absent -- plus where each tile points.

from unittest.mock import patch

import requests
from django.core.cache import cache
from django.template.loader import render_to_string
from django.test import override_settings

from blocks import puzzles as puzzles_block
from target.models import Target

REMOTE = {
    "puzzles": {
        "crossword": {
            "available": True,
            "url": "https://puzzles.groundup.org.za/crossword/7/solve/",
            "archive_url": "https://puzzles.groundup.org.za/crossword/",
            "title": "Cryptic-ish #7",
            "description": "",
            "num_rows": 3,
            "num_cols": 3,
            "grid": [[{"block": False, "number": 1}] * 3] * 3,
        },
        "sudoku": {
            "available": True,
            "url": "https://puzzles.groundup.org.za/sudoku/9/",
            "archive_url": "https://puzzles.groundup.org.za/sudoku/",
            "title": "Sudoku #9",
            "number": 9,
            "difficulty": "Medium",
            "cells": [""] * 81,
        },
    }
}


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
    PUZZLES_SITE_URL="https://puzzles.groundup.org.za",
    PUZZLES_API_URL="https://puzzles.groundup.org.za/api/puzzles/",
    PUZZLES_API_TIMEOUT=2.5,
    PUZZLES_API_CACHE_SECONDS=300,
)
class PuzzlesBlockTests(TestCase):

    def setUp(self):
        cache.clear()
        Target.objects.create(
            letters="EQMAZALNI", words="MAZE", published=timezone.now()
        )

    def test_crossword_and_sudoku_keep_the_puzzles_site_links(self):
        with patch("blocks.puzzles.requests.get", return_value=FakeResponse(REMOTE)):
            context = puzzles_block.puzzles_block_context()
        self.assertEqual(
            context["crossword"]["url"],
            "https://puzzles.groundup.org.za/crossword/7/solve/",
        )
        self.assertEqual(
            context["sudoku"]["url"], "https://puzzles.groundup.org.za/sudoku/9/"
        )

    def test_target_is_played_here_and_links_here(self):
        with patch("blocks.puzzles.requests.get", return_value=FakeResponse(REMOTE)):
            context = puzzles_block.puzzles_block_context()
        self.assertEqual(context["target"]["url"], reverse("target:latest"))
        # Centre letter first in the model, middle of the tile on screen.
        self.assertEqual(
            [cell["char"] for cell in context["target"]["cells"]],
            list("QMAZEALNI"),
        )
        self.assertTrue(context["target"]["cells"][4]["centre"])

    def test_target_from_the_api_wins_once_it_moves_over(self):
        payload = {"puzzles": dict(REMOTE["puzzles"], target={"available": True, "url": "x"})}
        with patch("blocks.puzzles.requests.get", return_value=FakeResponse(payload)):
            context = puzzles_block.puzzles_block_context()
        self.assertEqual(context["target"]["url"], "x")

    def test_an_unreachable_puzzles_site_falls_back_to_placeholders(self):
        with patch("blocks.puzzles.requests.get", side_effect=requests.Timeout):
            context = puzzles_block.puzzles_block_context()
        for name in ("crossword", "sudoku"):
            self.assertTrue(context[name]["placeholder"], name)
        # Target is ours, so the outage can't touch it.
        self.assertNotIn("placeholder", context["target"])
        html = render_to_string("blocks/puzzles_block.html", context)
        self.assertIn("Puzzles", html)
        self.assertIn("Coming soon", html)

    def test_placeholders_point_at_the_archives_not_at_a_puzzle(self):
        with patch("blocks.puzzles.requests.get", side_effect=requests.Timeout):
            context = puzzles_block.puzzles_block_context()
        self.assertEqual(
            context["crossword"]["url"], "https://puzzles.groundup.org.za/crossword/"
        )
        self.assertEqual(
            context["sudoku"]["url"], "https://puzzles.groundup.org.za/sudoku/"
        )

    def test_a_placeholder_claims_nothing_about_todays_puzzle(self):
        """A reader clicking through lands on the archive, so nothing on
        the tile may promise them a particular puzzle."""
        with patch("blocks.puzzles.requests.get", side_effect=requests.Timeout):
            context = puzzles_block.puzzles_block_context()
            html = render_to_string("blocks/puzzles_block.html", context)
        for name in ("crossword", "sudoku"):
            for claim in ("title", "number", "difficulty", "published"):
                self.assertNotIn(claim, context[name], (name, claim))
        self.assertNotIn(">New<", html)
        self.assertIn("Browse the crosswords", html)
        # The artwork still has to be there; an empty tile reads broken.
        self.assertEqual(len(context["sudoku"]["cells"]), 81)
        self.assertEqual(len(context["crossword"]["grid"]), 9)

    def test_a_day_with_no_new_puzzle_falls_back_the_same_way(self):
        payload = {"puzzles": {"crossword": {"available": False}, "sudoku": {"available": False}}}
        Target.objects.all().delete()
        with patch("blocks.puzzles.requests.get", return_value=FakeResponse(payload)):
            context = puzzles_block.puzzles_block_context()
        for name in ("crossword", "sudoku", "target"):
            self.assertTrue(context[name]["placeholder"], name)
        self.assertEqual(context["target"]["url"], reverse("target:list"))

    def test_the_last_good_answer_covers_a_later_outage(self):
        with patch("blocks.puzzles.requests.get", return_value=FakeResponse(REMOTE)):
            puzzles_block.puzzles_block_context()
        cache.delete(puzzles_block.CACHE_KEY)
        with patch("blocks.puzzles.requests.get", side_effect=requests.Timeout):
            context = puzzles_block.puzzles_block_context()
        self.assertEqual(context["crossword"]["title"], "Cryptic-ish #7")

    def test_a_failed_fetch_is_not_retried_on_every_page_view(self):
        with patch(
            "blocks.puzzles.requests.get", side_effect=requests.Timeout
        ) as get:
            puzzles_block.puzzles_block_context()
            puzzles_block.puzzles_block_context()
        self.assertEqual(get.call_count, 1)

    def test_nonsense_from_the_api_is_treated_as_no_answer(self):
        with patch(
            "blocks.puzzles.requests.get", return_value=FakeResponse({"puzzles": "oops"})
        ):
            context = puzzles_block.puzzles_block_context()
        self.assertTrue(context["crossword"]["placeholder"])


    def test_the_block_is_named_for_puzzles_not_games(self):
        with patch("blocks.puzzles.requests.get", return_value=FakeResponse(REMOTE)):
            html = render_to_string(
                "blocks/puzzles_block.html", puzzles_block.puzzles_block_context()
            )
        self.assertIn("GroundUp Puzzles", html)
        self.assertIn("All puzzles", html)
        self.assertNotIn("game", html.lower())

    def test_the_quiz_is_marked_coming_soon_and_is_not_a_link(self):
        with patch("blocks.puzzles.requests.get", return_value=FakeResponse(REMOTE)):
            html = render_to_string(
                "blocks/puzzles_block.html", puzzles_block.puzzles_block_context()
            )
        self.assertIn("Coming soon", html)
        self.assertNotIn("quiz_solve", html)
        # A div, not an anchor: there's nothing to play yet.
        self.assertRegex(html, r'<div class="[^"]*gup-tile--soon')
        self.assertNotRegex(html, r'<a class="[^"]*gup-tile--soon')
