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

REMOTE = {
    "puzzles": {
        "crossword": {
            "available": True,
            "url": "https://puzzles.groundup.org.za/crossword/7/solve/",
            "archive_url": "https://puzzles.groundup.org.za/crossword/",
            "title": "Cryptic-ish #7",
            "short_description": "A fun puzzle that doesn't take itself too seriously.",
            "description": "A fun puzzle that doesn't take itself too seriously. An irreverent mix of puns, general knowledge and newsy clues.",
            "published": "2026-10-08T10:00:00+02:00",
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
        "target": {
            "available": True,
            "url": "https://puzzles.groundup.org.za/target/12",
            "archive_url": "https://puzzles.groundup.org.za/target/",
            "title": "Target #12",
            "number": 12,
            "cells": [
                {"char": char, "centre": index == 4}
                for index, char in enumerate("qmazealni")
            ],
        },
        "groupup": {
            "available": True,
            "url": "https://puzzles.groundup.org.za/groupup/3/",
            "archive_url": "https://puzzles.groundup.org.za/groupup/",
            "title": "GroupUp #3",
            "description": "",
        },
        "quiz": {
            "available": True,
            "url": "https://puzzles.groundup.org.za/quizzes/5/solve/",
            "archive_url": "https://puzzles.groundup.org.za/quizzes/",
            "title": "News Quiz",
            "description": "",
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

    def test_every_tile_opens_the_newest_puzzle_of_its_game(self):
        with patch("blocks.puzzles.requests.get", return_value=FakeResponse(REMOTE)):
            context = puzzles_block.puzzles_block_context()
        for name, path in [
            ("crossword", "/crossword/"),
            ("groupup", "/groupup/"),
            ("quiz", "/quizzes/"),
            ("sudoku", "/sudoku/"),
            ("target", "/target/"),
        ]:
            self.assertEqual(
                context[name]["url"], "https://puzzles.groundup.org.za" + path, name
            )

    def test_target_is_played_on_the_puzzles_site(self):
        with patch("blocks.puzzles.requests.get", return_value=FakeResponse(REMOTE)):
            html = render_to_string(
                "blocks/puzzles_block.html", puzzles_block.puzzles_block_context()
            )
        self.assertIn('href="https://puzzles.groundup.org.za/target/"', html)
        self.assertNotIn('href="%s"' % reverse("target:latest"), html)
        self.assertIn("Target #12", html)
        self.assertIn('<span class="is-centre">E</span>', html)

    def test_the_hero_is_split_between_the_crossword_and_groupup(self):
        with patch("blocks.puzzles.requests.get", return_value=FakeResponse(REMOTE)):
            html = render_to_string(
                "blocks/puzzles_block.html", puzzles_block.puzzles_block_context()
            )
        self.assertEqual(html.count('class="gup-card gup-hero '), 2)
        self.assertIn("GroupUp #3", html)
        self.assertIn("Play GroupUp", html)
        self.assertLess(html.index("gup-heroes"), html.index("gup-tiles"))

    def test_the_crossword_shows_the_day_it_came_out(self):
        with patch("blocks.puzzles.requests.get", return_value=FakeResponse(REMOTE)):
            html = render_to_string(
                "blocks/puzzles_block.html", puzzles_block.puzzles_block_context()
            )
        self.assertIn(">8 Oct<", html)

    def test_an_unreachable_puzzles_site_falls_back_to_placeholders(self):
        with patch("blocks.puzzles.requests.get", side_effect=requests.Timeout):
            context = puzzles_block.puzzles_block_context()
        for name in ("crossword", "groupup", "quiz", "sudoku", "target"):
            self.assertTrue(context[name]["placeholder"], name)
        html = render_to_string("blocks/puzzles_block.html", context)
        self.assertIn("Puzzles", html)

    def test_placeholders_link_to_the_games_too(self):
        with patch("blocks.puzzles.requests.get", side_effect=requests.Timeout):
            context = puzzles_block.puzzles_block_context()
        self.assertEqual(
            context["crossword"]["url"], "https://puzzles.groundup.org.za/crossword/"
        )
        self.assertEqual(
            context["sudoku"]["url"], "https://puzzles.groundup.org.za/sudoku/"
        )
        self.assertEqual(
            context["target"]["url"], "https://puzzles.groundup.org.za/target/"
        )
        self.assertEqual(
            context["groupup"]["url"], "https://puzzles.groundup.org.za/groupup/"
        )
        self.assertEqual(
            context["quiz"]["url"], "https://puzzles.groundup.org.za/quizzes/"
        )

    def test_a_placeholder_claims_nothing_about_todays_puzzle(self):
        """A reader clicking through lands on the archive, so nothing on
        the tile may promise them a particular puzzle."""
        with patch("blocks.puzzles.requests.get", side_effect=requests.Timeout):
            context = puzzles_block.puzzles_block_context()
            html = render_to_string("blocks/puzzles_block.html", context)
        for name in ("crossword", "groupup", "quiz", "sudoku"):
            for claim in ("title", "number", "difficulty", "published"):
                self.assertNotIn(claim, context[name], (name, claim))
        crossword = html[html.index("gup-hero gup-t-crossword"):html.index("gup-hero gup-t-groupup")]
        self.assertNotIn("gup-badge--solid", crossword)
        self.assertIn("Cryptic(ish)", crossword)
        self.assertNotIn("Browse", html)
        # The artwork still has to be there; an empty tile reads broken.
        self.assertEqual(len(context["sudoku"]["cells"]), 81)
        self.assertEqual(len(context["crossword"]["grid"]), 9)

    def test_a_day_with_no_new_puzzle_falls_back_the_same_way(self):
        payload = {"puzzles": {name: {"available": False} for name in REMOTE["puzzles"]}}
        with patch("blocks.puzzles.requests.get", return_value=FakeResponse(payload)):
            context = puzzles_block.puzzles_block_context()
        for name in ("crossword", "groupup", "quiz", "sudoku", "target"):
            self.assertTrue(context[name]["placeholder"], name)

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

    def test_the_blurb_is_the_short_description_not_the_long_one(self):
        with patch("blocks.puzzles.requests.get", return_value=FakeResponse(REMOTE)):
            html = render_to_string(
                "blocks/puzzles_block.html", puzzles_block.puzzles_block_context()
            )
        self.assertIn("too seriously.", html)
        self.assertNotIn("irreverent mix", html)

    def test_the_quiz_is_live_and_links_to_the_quizzes(self):
        with patch("blocks.puzzles.requests.get", return_value=FakeResponse(REMOTE)):
            html = render_to_string(
                "blocks/puzzles_block.html", puzzles_block.puzzles_block_context()
            )
        self.assertNotIn("Coming soon", html)
        self.assertIn(
            '<a class="gup-card gup-tile gup-t-quiz" '
            'href="https://puzzles.groundup.org.za/quizzes/">',
            html,
        )


class DynamicBlockTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from newsroom.models import Article, Category, Topic

        cls.news = Category.objects.create(name="News", slug="news")
        cls.charts = Category.objects.create(name="Charts", slug="charts")
        cls.topic = Topic.objects.create(name="Housing", slug="housing")
        for number in range(3):
            article = Article.objects.create(
                title="Housing story {}".format(number),
                slug="housing-story-{}".format(number),
                category=cls.news,
                published=timezone.now() - timezone.timedelta(days=number),
            )
            article.topics.add(cls.topic)
        Article.objects.create(
            title="A chart", slug="a-chart", category=cls.charts,
            published=timezone.now(),
        )

    def render(self, **fields):
        from newsroom.views import parse_shortcodes

        block = Block.objects.create(name=fields.pop("name", "Dynamic"), **fields)
        return parse_shortcodes(block.html)

    def test_topic_block_renders_as_a_rail(self):
        html = self.render(block_type="topic", selected_topic=self.topic, num_articles=3)
        self.assertIn('class="gu-dynamic-block"', html)
        self.assertIn("data-rail-block", html)
        self.assertIn("data-rail-controls", html)
        self.assertEqual(html.count('class="gu-dynamic-block__card'), 3)
        self.assertEqual(html.count("gu-dynamic-block__card--lead"), 1)
        self.assertIn("<h2>Housing</h2>", html)
        self.assertIn(self.topic.get_absolute_url(), html)

    def test_display_options_apply_to_the_lead_and_the_rest(self):
        html = self.render(
            block_type="category", selected_category=self.news, num_articles=2,
            custom_title="Latest news", show_date_featured=False,
            show_category_standard=False,
        )
        self.assertIn("<h2>Latest news</h2>", html)
        self.assertEqual(html.count("<time"), 1)
        self.assertEqual(html.count("gu-dynamic-block__category"), 1)

    def test_no_lead_card_when_first_article_is_not_featured(self):
        html = self.render(
            block_type="topic", selected_topic=self.topic, num_articles=3,
            feature_first_article=False,
        )
        self.assertNotIn("gu-dynamic-block__card--lead", html)

    def test_columns_wrap_instead_of_scrolling(self):
        html = self.render(
            block_type="topic", selected_topic=self.topic, num_articles=3,
            display_in_columns=True,
        )
        self.assertIn("gu-dynamic-block--columns", html)
        self.assertNotIn("data-rail-controls", html)

    def test_chart_of_the_week_uses_the_same_block_in_columns(self):
        html = self.render(block_type="chart_of_the_week", num_articles=1)
        self.assertIn("gu-dynamic-block--columns", html)
        self.assertIn("All charts", html)
        self.assertIn("<h2>Charts</h2>", html)
