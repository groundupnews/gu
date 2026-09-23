import datetime
import json
import re
from decimal import *

from bs4 import BeautifulSoup as bs
from django.db import IntegrityError
from django.test import Client, TestCase, override_settings
from django.utils import timezone
from letters.models import Letter
from newsroom import utils
from newsroom.models import (
    Article,
    Category,
    Topic,
    Author,
    Correction,
    MostPopular,
    MostDeeplyRead,
    Video,
    VideoCategory,
    VideoChapter,
    VideoContributor,
    extract_youtube_id,
)
from blocks.models import Block, BlockGroup
from blocks.models import Group as BlockGroup_Group
from republisher.models import Republisher, RepublisherArticle
import republisher.management.commands.emailrepublishers as emailrepublishers
import newsroom.management.commands.notifycorrections as notifycorrections
from pgsearch.utils import searchArticlesAndPhotos
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from django.contrib.flatpages.models import FlatPage
from django.urls import reverse


# The video form and the admin both carry a contributors inline, so a post that
# leaves the credits alone still has to send its management form.
NO_CONTRIBUTORS = {
    "contributors-TOTAL_FORMS": "0",
    "contributors-INITIAL_FORMS": "0",
    "contributors-MIN_NUM_FORMS": "0",
    "contributors-MAX_NUM_FORMS": "1000",
}


def main_markup(response):
    """Just the page body. base.html inlines every stylesheet, so asserting an
    id or class against the whole response matches the CSS, not the markup."""
    html = response.content.decode()
    start = html.index('<main id="main-content">')
    return html[start : html.index("</main>", start)]


class HtmlCleanUp(TestCase):
    def test_html_cleaners(self):
        """HTML is correctly cleaned"""

        html = "<p class='plod'></p><p>Hello</p><p class=''> &nbsp; </p><p class='test'> Good bye </p>"
        self.assertEqual(
            utils.remove_unnecessary_white_space(html),
            "<p>Hello</p><p class='test'> Good bye </p>",
        )

        html = bs(
            '<p><img alt="" src="/media/uploads/church-SiyavuyaKhaya-20150128.jpg" style="width: 1382px; height: 1037px;" /></p><p class="caption">This is the caption.</p>',
            "html.parser",
        )
        self.assertEqual(
            str(utils.replaceImgHeightWidthWithClass(html)),
            '<p><img alt="" src="/media/uploads/church-SiyavuyaKhaya-20150128.jpg"/></p><p class="caption">This is the caption.</p>',
            "html.parser",
        )

        html = bs(
            '<p><img alt="" src="/media/uploads/church-SiyavuyaKhaya-20150128.jpg" style="width: 1382px; height: 1037px;" /></p><p class="caption">This is the caption.</p>',
            "html.parser",
        )
        # self.assertEqual(str(utils.replacePImgWithFigureImg(html)),
        #                 '<figure><img alt="" src="/media/uploads/church-SiyavuyaKhaya-20150128.jpg" style="width: 1382px; height: 1037px;"/><figcaption>This is the caption.</figcaption></figure>')
        html = '<p><img alt="" src="/media/uploads/church-SiyavuyaKhaya-20150128.jpg" style="width: 1382px; height: 1037px;" /></p><p class="caption">This is the caption.</p>'
        self.assertEqual(
            utils.replaceBadHtmlWithGood(html),
            '<p><img alt="" src="/media/uploads/church-SiyavuyaKhaya-20150128.jpg"/></p><p class="caption">This is the caption.</p>',
        )
        html1 = (
            "<p>The dog ran away.</p>"
            "<p>The dog -- ran away.</p>"
            "<p>The dog --- ran away.</p>"
            "<p>The dog--ran away.</p>"
            "<p>The dog---ran away.</p>"
        )
        html2 = (
            "<p>The dog ran away.</p>"
            "<p>The dog – ran away.</p>"
            "<p>The dog — ran away.</p>"
            "<p>The dog--ran away.</p>"
            "<p>The dog---ran away.</p>"
        )
        html3 = str(utils.processDashes(bs(html1, "html.parser")))
        self.assertEqual(html2, html3)


class ArticleTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

        topic = Topic()
        topic.name = "government"
        topic.slug = "government"
        topic.save()

        category = Category()
        category.name = "Feature"
        category.slug = "feature"
        category.save()

        category = Category()
        category.name = "Photo essay"
        category.slug = "photo-essay"
        category.save()

        category = Category()
        category.name = "Opinion"
        category.slug = "opinion"
        category.save()

        category = Category()
        category.name = "Photo"
        category.slug = "photo"
        category.save()

        category = Category()
        category.name = "News"
        category.slug = "news"
        category.save()

        a = Article()
        a.title = "Test article 1"
        a.body = "<p>The quick brown fox jumps over the lazy dog.</p>"
        a.slug = "test-article-1"
        a.category = Category.objects.get(name="News")
        a.external_primary_image = "http://www.w3schools.com/html/pic_mountain.jpg"
        a.save()
        a.publish_now()

        a = Article()
        a.title = "Test article 2"
        a.subtitle = "Dogs and things"
        a.body = "<p>How now brown cow.</p>"
        a.slug = "test-article-2"
        a.category = Category.objects.get(slug="opinion")
        a.save()
        a.publish_now()

        author = Author()
        author.first_names = "Joe"
        author.last_name = "Bloggs"
        author.email = "joebloggs@example.com"
        author.save()
        a.author_01 = author
        a.save()

    def test_articles(self):
        articles = Article.objects.all()
        self.assertEqual(len(articles), 2)
        articles = Article.objects.published()
        self.assertEqual(len(articles), 2)
        article = Article.objects.published()[1]
        self.assertEqual(article.title, "Test article 1")
        self.assertEqual(
            article.cached_primary_image,
            "http://www.w3schools.com/html/pic_mountain.jpg",
        )
        article = Article.objects.published()[0]
        self.assertEqual(article.title, "Test article 2")

    def test_pages(self):
        client = Client()
        response = client.get("/article/test-article-1/")
        self.assertEqual(response.status_code, 200)
        client = Client()
        response = client.get("/article/test-article-2/")
        self.assertEqual(response.status_code, 200)
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        response = client.get("/article/no-exist/")
        self.assertEqual(response.status_code, 404)
        response = client.get("/content/test-article-1/")
        self.assertEqual(response.status_code, 302)
        response = client.get("/category/")
        self.assertEqual(response.status_code, 200)
        response = client.get("/category/News/")
        self.assertEqual(response.status_code, 200)
        response = client.get("/category/news/")
        self.assertEqual(response.status_code, 200)
        response = client.get("/category/Opinion/")
        self.assertEqual(response.status_code, 200)
        response = client.get("/category/opinion/")
        self.assertEqual(response.status_code, 200)
        response = client.get("/topic/")
        self.assertEqual(response.status_code, 200)
        topic = Topic.objects.all()[0]
        url = reverse(
            "newsroom:topic.detail",
            args=[
                topic,
            ],
        )
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        response = client.get("/author/")
        self.assertEqual(response.status_code, 200)
        author = Author.objects.all()[0]
        url = "/author/" + str(author.pk) + "/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        url = reverse("newsroom:author.add")
        response = client.get(url)
        url = reverse("newsroom:topic_create")
        response = client.get(url)
        self.assertEqual(response.status_code, 302)
        reponse = client.get(url)
        self.assertEqual(response.status_code, 302)

        user = User.objects.create_user("staff", "staff@example.com", "abcde")
        user.is_staff = True
        user.is_active = True
        permission1 = Permission.objects.get(name="Can add author")
        user.user_permissions.add(permission1)
        permission2 = Permission.objects.get(name="Can change author")
        user.user_permissions.add(permission2)
        permission3 = Permission.objects.get(name="Can add topic")
        user.user_permissions.add(permission3)
        permission4 = Permission.objects.get(name="Can change topic")
        user.user_permissions.add(permission4)
        user.save()

        staff = Client()
        staff.login(username="staff", password="abcde")
        url = reverse(
            "newsroom:author.update",
            args=[
                author.pk,
            ],
        )
        response = staff.get(url)
        self.assertEqual(response.status_code, 200)

        response = staff.get(url)
        self.assertEqual(response.status_code, 200)
        url = reverse(
            "newsroom:topic_update",
            args=[
                topic.pk,
            ],
        )
        response = staff.get(url)
        self.assertEqual(response.status_code, 200)

    def test_duplicate_save(self):
        a = Article()
        a.title = "Test article 3"
        a.category = Category.objects.get(name__iexact="news")
        a.slug = "test-article-1"
        shouldHaveFailed = True
        try:
            a.save()
        except IntegrityError:
            shouldHaveFailed = False
        self.assertEqual(shouldHaveFailed, False)

    def test_published(self):
        num_published = Article.objects.published().count()
        a = Article()
        a.title = "Test article 3"
        a.slug = "test-article-3"
        a.category = Category.objects.get(name="News")
        a.published = timezone.now()
        a.save()
        num_published_now = Article.objects.published().count()
        self.assertEqual(num_published + 1, num_published_now)
        a = Article()
        a.title = "Test article 4"
        a.category = Category.objects.get(name="News")
        a.slug = "test-article-4"
        a.published = timezone.now() + datetime.timedelta(hours=10)
        a.save()
        num_published_now = Article.objects.published().count()
        self.assertEqual(num_published + 1, num_published_now)
        self.assertEqual(a.is_published(), False)

    def test_serialize(self):
        num_published = Article.objects.published().count()
        self.assertTrue(num_published > 0)
        from django.core import serializers

        data = serializers.serialize("xml", Article.objects.published())
        objs = serializers.deserialize("xml", data)
        self.assertTrue(len(list(objs)) == num_published)

    def test_letter(self):
        letter = Letter()
        article = Article.objects.published()[0]
        letter.article = article
        letter.byline = "John Doe"
        letter.email = "johndoe@example.com"
        letter.title = "Test"
        letter.text = "Dear sir. This is a test"
        letter.rejected = False
        letter.published = timezone.now()
        letter.save()
        count = Letter.objects.published().count()
        self.assertEqual(count, 1)
        letter = Letter.objects.published()[0]

        c = Client()
        url = reverse("letters:letter_thanks")
        response = c.get(url)
        self.assertEqual(response.status_code, 200)
        url = reverse("letters:letter_to_editor", args=(article.pk,))
        response = c.get(url)
        self.assertEqual(response.status_code, 200)

        letter = Letter()
        article = Article.objects.published()[0]
        letter.article = article
        letter.byline = "Jane Smith"
        letter.email = "janedoe@this_is_an_invalid_domain.com"
        letter.title = "Test"
        letter.text = "Dear Madam. This is a test"
        letter.rejected = True
        letter.save()

        from letters.management.commands import processletters

        processletters.process()
        letters = Letter.objects.all()
        for l in letters:
            self.assertEqual(l.notified_letter_writer, True)

    def test_preview(self):
        article = Article.objects.get(slug="test-article-1")
        client = Client()
        response = client.get("/prev_gen/" + str(article.pk))
        self.assertEqual(response.status_code, 302)
        response = client.get("/prev_gen/test-article-1/")
        self.assertEqual(response.status_code, 404)
        article = Article.objects.get(slug="test-article-1")
        self.assertTrue(len(article.secret_link) > 40)
        user = User.objects.create_user("admin", "admin@example.com", "abcde")
        user.is_staff = True
        user.is_active = True
        permission = Permission.objects.get(name="Can change article")
        user.user_permissions.add(permission)
        user.save()
        client.login(username="admin", password="abcde")
        response = client.get("/prev_gen/" + str(article.pk))
        self.assertEqual(response.status_code, 302)
        article = Article.objects.get(slug="test-article-1")
        self.assertTrue(len(article.secret_link) > 0)
        response = client.get("/preview/" + article.secret_link + "/")
        self.assertEqual(response.status_code, 302)
        article.published = None
        article.save()
        response = client.get("/preview/" + article.secret_link + "/")
        self.assertEqual(response.status_code, 200)

    def test_search(self):
        articles = searchArticlesAndPhotos("cow dog")
        self.assertEqual(len(articles), 1)

    def test_corrections(self):
        article = Article.objects.get(slug="test-article-1")
        client = Client()
        response = client.get(reverse("newsroom:correction.list"))
        self.assertEqual(response.status_code, 200)
        user = User.objects.create_user("admin", "admin@example.com", "abcde")
        user.is_staff = True
        user.is_active = True
        permission = Permission.objects.get(name="Can add correction")
        user.user_permissions.add(permission)
        permission = Permission.objects.get(name="Can change correction")
        user.user_permissions.add(permission)
        permission = Permission.objects.get(name="Can delete correction")
        user.user_permissions.add(permission)
        user.save()
        client.login(username="admin", password="abcde")
        response = client.get(
            reverse("newsroom:correction.create") + "?article_pk=" + str(article.pk)
        )
        self.assertEqual(response.status_code, 200)
        correction = Correction()
        correction.article = article
        correction.update_type = "C"
        correction.text = "This is a test of the corrections."
        correction.save()
        correction = Correction.objects.get(pk=correction.pk)
        response = client.get(
            reverse("newsroom:correction.update", args=[correction.pk])
            + "?article_pk="
            + str(correction.article.pk)
        )
        self.assertEqual(response.status_code, 200)
        response = client.get(
            reverse("newsroom:correction.delete", args=[correction.pk])
            + "?article_pk="
            + str(correction.article.pk)
        )
        self.assertEqual(response.status_code, 200)
        response = client.get(reverse("newsroom:article.add"))
        self.assertEqual(response.status_code, 200)

        client = Client()
        response = client.get(reverse("newsroom:correction.update", args=[1]))
        self.assertEqual(response.status_code, 302)
        response = client.get(reverse("newsroom:correction.delete", args=[1]))
        self.assertEqual(response.status_code, 302)
        response = client.get(
            reverse("newsroom:correction.create") + "?article_pk=" + str(article.pk)
        )
        self.assertEqual(response.status_code, 302)
        response = client.get(reverse("newsroom:article.add"))
        self.assertEqual(response.status_code, 302)

    def test_flatpages(self):
        f = FlatPage()
        f.url = "/about/"
        f.title = "About page"
        f.content = "<p>About</p>"
        f.save()
        s = Site.objects.all()[0]
        f.sites.add(s)
        f.save()
        client = Client()
        response = client.get("/about/")
        self.assertEqual(response.status_code, 200)

    def add_corrections(self, articles):
        j = 0
        for a in articles:
            if j % 2 == 0:
                notify_republishers = True
            else:
                notify_republishers = False
            j = j + 1
            for i in range(2):
                if i == 1:
                    update_type = "C"
                else:
                    update_type = "U"
                Correction.objects.create(
                    article=a,
                    update_type=update_type,
                    text="We corrected the spelling of John Bloggs",
                    notify_republishers=notify_republishers,
                )

    def test_correction_republisher_notification(self):
        for i in range(5):
            Republisher.objects.create(
                name="Name" + str(i),
                email_addresses="email"
                + str(i)
                + "a@example.com,"
                + "email"
                + str(i)
                + "b@example.com",
                message="Dear republisher " + str(i),
                slug="republisher" + str(i),
            )
        republishers = Republisher.objects.all()
        articles = Article.objects.published()
        for a in articles:
            for r in republishers:
                republisher_article = RepublisherArticle.objects.create(
                    article=a, republisher=r
                )
        res = emailrepublishers.process()
        self.assertEqual(res["failures"], 0)
        self.assertEqual(res["successes"], len(articles) * len(republishers))
        # We add a bunch of corrections, process them twice. Then repeat.
        self.add_corrections(articles)
        res = notifycorrections.process(1)
        self.assertEqual(res["failures"], 0)
        self.assertEqual(res["successes"], 10)
        # Repeat with nothing happening
        res = notifycorrections.process(1)
        self.assertEqual(res["failures"], 0)
        self.assertEqual(res["successes"], 0)
        # And repeat from the top
        self.add_corrections(articles)
        res = notifycorrections.process(1)
        self.assertEqual(res["failures"], 0)
        self.assertEqual(res["successes"], 10)
        # Repeat with nothing happening
        res = notifycorrections.process(1)
        self.assertEqual(res["failures"], 0)
        self.assertEqual(res["successes"], 0)


class ArticleDetailTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.topic = Topic.objects.create(name="Test Topic", slug="test-topic")
        cls.category = Category.objects.create(
            name="Test Category", slug="test-category"
        )
        cls.author = Author.objects.create(
            first_names="Test", last_name="Author", email="test@example.com"
        )
        cls.article = Article.objects.create(
            title="Test Article", slug="test-article", category=cls.category
        )
        cls.article.author_01 = cls.author
        cls.article.topics.add(cls.topic)
        cls.article.save()

    def test_article_absolute_url(self):
        self.assertEqual(
            self.article.get_absolute_url(), f"/article/{self.article.slug}/"
        )

    def test_article_str(self):
        self.assertEqual(str(self.article), f"{self.article.pk} {self.article.title}")

    def test_unpublished_article_not_visible(self):
        c = Client()
        response = c.get(self.article.get_absolute_url())
        self.assertEqual(response.status_code, 404)

    def test_published_article_visible(self):
        self.article.publish_now()
        c = Client()
        response = c.get(self.article.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article.title)

    def test_article_authors(self):
        self.assertEqual(self.article.author_01, self.author)
        self.assertEqual(self.article.author_02, None)

    def test_article_topics(self):
        self.assertIn(self.topic, self.article.topics.all())


class CategoryTest(TestCase):
    def test_category_creation(self):
        category = Category.objects.create(name="Test Category", slug="test-category")
        self.assertEqual(str(category), category.name)
        self.assertEqual(category.get_absolute_url(), f"/category/{category.slug}/")


####################################################################
# JSON API tests: /api/most-popular/ and /api/most-deeply-read/
#
# Add these imports to the top of newsroom/tests.py if not present:
#
#   from django.test import Client, TestCase, override_settings
#   from newsroom.models import MostPopular, MostDeeplyRead
#   import datetime
#   from django.urls import reverse
#   from django.utils import timezone
####################################################################


class MostReadApiMixin:
    """Shared tests for the two structurally identical endpoints.

    MostPopular and MostDeeplyRead store the same thing -- newline-separated
    "slug|title" rows in one TextField -- and differ only in the name of the
    accessor. So the API contract is identical and the tests can be too.

    Subclasses supply `model`, `url_name` and `get_list`. Deliberately not a
    TestCase subclass, so the runner doesn't collect it on its own.
    """

    model = None
    url_name = None

    def get_list(self):
        """Call the model's list accessor (named differently on each model)."""
        raise NotImplementedError

    # -- helpers ----------------------------------------------------

    def store(self, article_list):
        """Create a record holding the given raw article_list text."""
        obj = self.model()
        obj.article_list = article_list
        obj.save()
        return obj

    def get_json(self):
        response = self.client.get(reverse(self.url_name))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        return response.json()

    def setUp(self):
        self.client = Client()

    # -- accessors behave as the API assumes ------------------------

    def test_accessor_returns_none_when_no_record(self):
        """The model returns None, not [], when the cron has never run."""
        self.assertIsNone(self.get_list())

    def test_accessor_splits_rows_and_fields(self):
        self.store("slug-a|Title A\nslug-b|Title B")
        self.assertEqual(
            self.get_list(),
            [["slug-a", "Title A"], ["slug-b", "Title B"]],
        )

    # -- empty / missing data ---------------------------------------

    def test_no_record_returns_empty_list(self):
        """No MostPopular/MostDeeplyRead row at all -> 200 with an empty list.

        Note this is indistinguishable from a genuinely empty list. See the
        `generated` suggestion in the notes if consumers need to tell them
        apart.
        """
        data = self.get_json()
        self.assertEqual(data["count"], 0)
        self.assertEqual(data["articles"], [])

    def test_record_with_empty_article_list(self):
        """A saved-but-empty record.

        "".split("\\n") is [""], so the accessor returns [[""]] -- one row of
        one empty string, not []. This is what makes get_most_popular_html()
        fall into its bare `except` (MostPopular only; the MostDeeplyRead
        version guards with len(article) >= 2). The API must filter it.
        """
        self.store("")
        self.assertEqual(self.get_list(), [[""]])
        data = self.get_json()
        self.assertEqual(data["count"], 0)
        self.assertEqual(data["articles"], [])

    # -- happy path -------------------------------------------------

    def test_returns_stored_articles_in_order(self):
        """Rank order is the stored order and must be preserved."""
        self.store("slug-a|Title A\nslug-b|Title B\nslug-c|Title C")
        data = self.get_json()
        self.assertEqual(data["count"], 3)
        self.assertEqual(
            [a["slug"] for a in data["articles"]],
            ["slug-a", "slug-b", "slug-c"],
        )
        self.assertEqual(
            [a["title"] for a in data["articles"]],
            ["Title A", "Title B", "Title C"],
        )

    def test_urls_are_absolute_and_match_reverse(self):
        self.store("slug-a|Title A")
        article = self.get_json()["articles"][0]
        expected_path = reverse("newsroom:article.detail", args=["slug-a"])
        self.assertEqual(article["url"], "http://testserver" + expected_path)
        self.assertTrue(article["url"].startswith("http://"))

    def test_keys_are_exactly_as_documented(self):
        """Guard against accidentally widening or narrowing the payload."""
        self.store("slug-a|Title A")
        data = self.get_json()
        self.assertEqual(set(data.keys()), {"count", "articles"})
        self.assertEqual(set(data["articles"][0].keys()), {"slug", "title", "url"})

    # -- malformed rows ---------------------------------------------

    def test_trailing_newline_does_not_produce_empty_entry(self):
        """The management commands use "\\n".join, but a stray trailing
        newline (hand-edited via admin, say) yields a final [''] row."""
        self.store("slug-a|Title A\n")
        self.assertEqual(self.get_list(), [["slug-a", "Title A"], [""]])
        data = self.get_json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["articles"][0]["slug"], "slug-a")

    def test_row_without_pipe_is_skipped(self):
        """A row with no separator has no title; reverse() would still build
        a URL, so it must be dropped explicitly rather than emitted."""
        self.store("slug-a|Title A\nbroken-row-no-pipe\nslug-b|Title B")
        data = self.get_json()
        self.assertEqual(data["count"], 2)
        self.assertEqual([a["slug"] for a in data["articles"]], ["slug-a", "slug-b"])

    def test_blank_slug_is_skipped(self):
        self.store("|Title with no slug\nslug-b|Title B")
        data = self.get_json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["articles"][0]["slug"], "slug-b")

    def test_blank_title_is_skipped(self):
        self.store("slug-a|\nslug-b|Title B")
        data = self.get_json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["articles"][0]["slug"], "slug-b")

    def test_pipe_in_title_is_preserved(self):
        """item.split("|") splits on every pipe, so a title containing one
        arrives as 3+ parts. The API rejoins; get_*_html() truncates."""
        self.store("slug-a|Cape Town | Water crisis")
        self.assertEqual(self.get_list(), [["slug-a", "Cape Town ", " Water crisis"]])
        data = self.get_json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["articles"][0]["title"], "Cape Town | Water crisis")

    def test_whitespace_is_stripped(self):
        self.store("  slug-a  |  Title A  ")
        article = self.get_json()["articles"][0]
        self.assertEqual(article["slug"], "slug-a")
        self.assertEqual(article["title"], "Title A")

    def test_windows_line_endings_are_not_silently_accepted(self):
        r"""Documents current behaviour: the accessor splits on "\n" only, so
        a \r\n-delimited list leaves \r glued to the previous title. The strip()
        in the API removes it. If this ever regresses, titles will end in \r."""
        self.store("slug-a|Title A\r\nslug-b|Title B")
        data = self.get_json()
        self.assertEqual(data["count"], 2)
        self.assertEqual(data["articles"][0]["title"], "Title A")

    # -- which record is served -------------------------------------

    def test_latest_record_wins(self):
        """Both accessors use .latest("modified"). Every cron run inserts a
        new row rather than updating, so the table grows and only the newest
        row should ever be served."""
        old = self.store("old-slug|Old title")
        new = self.store("new-slug|New title")

        # `modified` is auto_now=True, so save() would overwrite whatever we
        # set. QuerySet.update() bypasses field pre_save and lets us force an
        # unambiguous gap rather than relying on clock resolution.
        self.model.objects.filter(pk=old.pk).update(
            modified=timezone.now() - datetime.timedelta(days=2)
        )
        self.model.objects.filter(pk=new.pk).update(modified=timezone.now())

        data = self.get_json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["articles"][0]["slug"], "new-slug")

    def test_older_records_are_not_merged_in(self):
        old = self.store("a|A\nb|B\nc|C")
        new = self.store("d|D")
        self.model.objects.filter(pk=old.pk).update(
            modified=timezone.now() - datetime.timedelta(days=2)
        )
        self.assertEqual(self.model.objects.count(), 2)
        self.assertEqual(self.get_json()["count"], 1)

    # -- access control ---------------------------------------------

    def test_anonymous_access_is_allowed(self):
        """The point of the endpoint: no auth, no redirect to a login page."""
        self.store("slug-a|Title A")
        response = self.client.get(reverse(self.url_name))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Location", response)

    def test_authenticated_response_is_identical(self):
        """Nothing is user-specific, which is why plain cache_page is safe
        here instead of the site's cache_except_staff wrapper."""
        self.store("slug-a|Title A")
        anonymous = self.get_json()

        User.objects.create_user(
            username="staffer",
            password="pw",
            email="s@example.com",
            is_staff=True,
        )
        self.client.login(username="staffer", password="pw")
        self.assertEqual(self.get_json(), anonymous)

    def test_head_is_allowed(self):
        self.store("slug-a|Title A")
        response = self.client.head(reverse(self.url_name))
        self.assertEqual(response.status_code, 200)

    # -- staleness --------------------------------------------------

    def test_slug_of_deleted_article_is_still_returned(self):
        """Documents a real limitation rather than asserting desired
        behaviour: the stored list is a snapshot of slugs and titles, never
        re-validated against Article. If an article is deleted or unpublished
        after the cron ran, the endpoint keeps advertising it and the URL
        404s. Change this test if you add a published-articles filter.
        """
        self.store("no-such-article|Vanished")
        data = self.get_json()
        self.assertEqual(data["count"], 1)
        detail = self.client.get(data["articles"][0]["url"])
        self.assertEqual(detail.status_code, 404)


# `cache_page` is applied in urls.py, and the project's default cache is a
# FileBasedCache in /var/tmp/django_cache with KEY_PREFIX "gu" -- a real
# directory that persists between test runs. Without this override, a response
# cached by one test is served to the next (and to tomorrow's run), and every
# test above that changes the stored list then re-requests the URL fails
# confusingly. DummyCache makes cache_page a no-op.
DISABLE_CACHE = override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
)


@DISABLE_CACHE
class MostPopularApiTest(MostReadApiMixin, TestCase):
    model = MostPopular
    url_name = "newsroom:api.most_popular"

    def get_list(self):
        return MostPopular.get_most_popular_list()

    def test_endpoint_path(self):
        self.assertEqual(reverse(self.url_name), "/api/most-popular/")


@DISABLE_CACHE
class MostDeeplyReadApiTest(MostReadApiMixin, TestCase):
    model = MostDeeplyRead
    url_name = "newsroom:api.most_deeply_read"

    def get_list(self):
        # Note the shorter, inconsistent accessor name on this model.
        return MostDeeplyRead.get_list()

    def test_endpoint_path(self):
        self.assertEqual(reverse(self.url_name), "/api/most-deeply-read/")


@DISABLE_CACHE
class MostReadApiIntegrationTest(TestCase):
    """One end-to-end check that a URL built by the API actually resolves to a
    live article page, and that the two endpoints stay independent."""

    @classmethod
    def setUpTestData(cls):
        category = Category()
        category.name = "News"
        category.slug = "news"
        category.save()

        article = Article()
        article.title = "Cape Town water crisis deepens"
        article.body = "<p>Test body.</p>"
        article.slug = "cape-town-water-crisis_9999"
        article.category = category
        article.save()
        article.publish_now()
        cls.article = article

    def setUp(self):
        self.client = Client()

    def test_url_resolves_to_the_real_article(self):
        popular = MostPopular()
        popular.article_list = self.article.slug + "|" + self.article.title
        popular.save()

        data = self.client.get(reverse("newsroom:api.most_popular")).json()
        self.assertEqual(data["count"], 1)

        entry = data["articles"][0]
        self.assertEqual(entry["slug"], self.article.slug)
        self.assertEqual(entry["title"], self.article.title)

        detail = self.client.get(entry["url"])
        self.assertEqual(detail.status_code, 200)

    def test_endpoints_read_separate_tables(self):
        popular = MostPopular()
        popular.article_list = "popular-slug|Popular"
        popular.save()

        deeply = MostDeeplyRead()
        deeply.article_list = "deep-slug|Deep"
        deeply.save()

        popular_data = self.client.get(reverse("newsroom:api.most_popular")).json()
        deep_data = self.client.get(reverse("newsroom:api.most_deeply_read")).json()

        self.assertEqual(popular_data["articles"][0]["slug"], "popular-slug")
        self.assertEqual(deep_data["articles"][0]["slug"], "deep-slug")

    def test_populating_one_does_not_populate_the_other(self):
        popular = MostPopular()
        popular.article_list = "popular-slug|Popular"
        popular.save()

        deep_data = self.client.get(reverse("newsroom:api.most_deeply_read")).json()
        self.assertEqual(deep_data["count"], 0)


class YouTubeIdTest(TestCase):
    def test_extract_from_the_urls_editors_paste(self):
        cases = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/watch?app=desktop&v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ?t=42", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/live/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("  dQw4w9WgXcQ  ", "dQw4w9WgXcQ"),
        ]
        for value, expected in cases:
            self.assertEqual(extract_youtube_id(value), expected, value)

    def test_rejects_what_is_not_a_video(self):
        for value in ["", None, "https://www.youtube.com/@GroundUpNews", "abc"]:
            self.assertIsNone(extract_youtube_id(value))

    def test_save_normalises_a_pasted_url(self):
        video = Video.objects.create(
            title="Pasted URL",
            slug="pasted-url",
            youtube_id="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        )
        video.refresh_from_db()
        self.assertEqual(video.youtube_id, "dQw4w9WgXcQ")


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
)
class VideoTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # The categories in the design ship as a data migration.
        cls.explainers = VideoCategory.objects.get(slug="explainer")
        cls.documentaries = VideoCategory.objects.get(slug="feature")
        cls.topic = Topic.objects.create(name="Pyramid schemes", slug="pyramid-schemes")

        cls.newest = Video.objects.create(
            title="How to avoid pyramid schemes",
            slug="how-to-avoid-pyramid-schemes",
            youtube_id="dQw4w9WgXcQ",
            category=cls.explainers,
            summary="Thousands of South Africans have lost money.",
            duration="9:42",
            byline="GroundUp Video Team",
            published=timezone.now() - datetime.timedelta(days=1),
        )
        cls.newest.topics.add(cls.topic)
        VideoChapter.objects.create(
            video=cls.newest, timecode="2:41", description="How the payouts work"
        )

        cls.older = Video.objects.create(
            title="Municipal debt explained",
            slug="municipal-debt-explained",
            youtube_id="5RI7cF6A-8Q",
            category=cls.documentaries,
            duration="7:15",
            published=timezone.now() - datetime.timedelta(days=30),
        )

        cls.middle = Video.objects.create(
            title="What the grant increase buys",
            slug="what-the-grant-increase-buys",
            youtube_id="KXsqwgXEifE",
            published=timezone.now() - datetime.timedelta(days=2),
        )

        cls.unpublished = Video.objects.create(
            title="Not ready yet",
            slug="not-ready-yet",
            youtube_id="aaaaaaaaaaa",
        )

    def test_the_grid_holds_every_published_video(self):
        listed = Video.objects.list_view()
        self.assertIn(self.newest, listed)
        self.assertIn(self.middle, listed)
        self.assertIn(self.older, listed)
        self.assertNotIn(self.unpublished, listed)

    def test_duration_conversions(self):
        self.assertEqual(self.newest.duration_seconds(), 582)
        self.assertEqual(self.newest.duration_iso(), "PT0H9M42S")
        self.assertEqual(self.newest.watch_time(), "10 min watch")
        self.assertIsNone(self.unpublished.duration_seconds())
        self.assertEqual(self.unpublished.duration_iso(), "")
        self.assertEqual(self.unpublished.watch_time(), "")

    def test_chapter_seconds(self):
        self.assertEqual(self.newest.chapters.first().seconds(), 161)

    def test_urls_and_thumbnails(self):
        self.assertEqual(
            self.newest.watch_url(), "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )
        # A video uploaded as a Short is still just a video.
        self.assertEqual(
            self.middle.watch_url(), "https://www.youtube.com/watch?v=KXsqwgXEifE"
        )
        self.assertIn("maxresdefault", self.newest.thumbnail_url())
        self.assertIn("maxresdefault", self.middle.thumbnail_url())
        self.assertIn("hqdefault", self.newest.fallback_thumbnail_url())

    def test_byline_falls_back_to_the_authors_then_the_video_team(self):
        self.assertEqual(self.older.get_byline(), "GroundUp Video Team")
        first = Author.objects.create(
            first_names="Barbara", last_name="Maregele", email="b@example.com"
        )
        second = Author.objects.create(
            first_names="Ashraf", last_name="Nkosi", email="a@example.com"
        )
        self.older.authors.set([first, second])
        self.assertEqual(
            self.older.get_byline(), "{}, {}".format(first, second)
        )
        self.older.byline = "GroundUp Video Team"
        self.assertEqual(self.older.get_byline(), "GroundUp Video Team")

    def test_list_page(self):
        response = self.client.get(reverse("newsroom:video.list"))
        self.assertEqual(response.status_code, 200)
        # The newest video is the hero; the rest fill the grid.
        self.assertEqual(response.context["hero"], self.newest)
        self.assertEqual(
            list(response.context["videos"]), [self.middle, self.older]
        )
        self.assertContains(response, "What the grant increase buys")
        self.assertContains(response, "Municipal debt explained")
        self.assertNotContains(response, "Not ready yet")

    def test_promoted_video_becomes_the_hero(self):
        self.older.promote = True
        self.older.save()
        response = self.client.get(reverse("newsroom:video.list"))
        self.assertEqual(response.context["hero"], self.older)

    def test_category_page_filters(self):
        response = self.client.get(
            reverse("newsroom:video.category", args=["feature"])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["hero"], self.older)
        self.assertEqual(list(response.context["videos"]), [])
        self.assertContains(response, "Feature")

    def test_detail_page(self):
        response = self.client.get(self.newest.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "How to avoid pyramid schemes")
        self.assertContains(response, "GroundUp Video Team")
        self.assertContains(response, "How the payouts work")
        self.assertContains(response, "Pyramid schemes")
        # Nothing is requested from YouTube until a reader clicks play.
        self.assertNotContains(response, "<iframe")
        self.assertContains(response, "youtube-nocookie.com/embed/dQw4w9WgXcQ")

    def test_unpublished_video_is_hidden_from_readers(self):
        response = self.client.get(self.unpublished.get_absolute_url())
        self.assertEqual(response.status_code, 404)

    def test_structured_data_and_meta(self):
        response = self.client.get(self.newest.get_absolute_url())
        html = response.content.decode()
        self.assertIn('"@type": "VideoObject"', html)
        self.assertIn('"duration": "PT0H9M42S"', html)
        self.assertIn('"embedUrl": "https://www.youtube-nocookie.com/embed/', html)
        self.assertIn('"contentUrl": "https://www.youtube.com/watch?v=', html)
        self.assertIn('"publisher"', html)
        # Chapters become Clips, which is what Google reads for key moments.
        self.assertIn('"@type": "Clip"', html)
        self.assertIn('"startOffset": 161', html)
        # The licence is stated in the structured data as well as on the page.
        self.assertIn('"license": "https://groundup.org.za/licencing/detail/2/"',
                      html)
        self.assertContains(response, 'name="twitter:card" content="player"')
        self.assertContains(response, 'property="og:type" content="video.other"')
        summary = "Thousands of South Africans have lost money."
        # base.html breaks the plain description tag over two lines.
        self.assertRegex(html, r'name="description"\s+content="' + re.escape(summary))
        self.assertIn('property="og:description" content="' + summary + '"', html)
        self.assertIn('name="twitter:description" content="' + summary + '"', html)
        self.assertIn('"description": "' + summary + '"', html)

    def test_list_page_structured_data_and_feed(self):
        response = self.client.get(reverse("newsroom:video.list"))
        html = response.content.decode()
        self.assertIn('"@type": "ItemList"', html)
        # Hero first, then the grid.
        self.assertLess(
            html.index("how-to-avoid-pyramid-schemes"),
            html.index("municipal-debt-explained"),
        )
        self.assertContains(response, reverse("newsroom:video.rss"))

    def test_rss_feed(self):
        response = self.client.get(reverse("newsroom:video.rss"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "How to avoid pyramid schemes")
        self.assertNotContains(response, "Not ready yet")

    def test_videos_are_searchable(self):
        response = self.client.get(
            reverse("newsroom:advanced.search"),
            {"adv_search": "pyramid", "search_type": "video"},
        )
        self.assertEqual(response.status_code, 200)
        results = list(response.context["page"].object_list)
        self.assertEqual([video.pk for video in results], [self.newest.pk])
        self.assertContains(response, "VIDEO")
        self.assertContains(response, self.newest.get_absolute_url())

    def test_search_finds_videos_by_chapter_and_topic(self):
        for term in ["payouts", "Pyramid schemes"]:
            response = self.client.get(
                reverse("newsroom:advanced.search"),
                {"adv_search": term, "search_type": "video"},
            )
            results = list(response.context["page"].object_list)
            self.assertEqual([v.pk for v in results], [self.newest.pk], term)

    def test_search_skips_unpublished_videos(self):
        response = self.client.get(
            reverse("newsroom:advanced.search"),
            {"adv_search": "ready", "search_type": "video"},
        )
        self.assertEqual(list(response.context["page"].object_list), [])

    def test_search_everything_includes_videos_and_articles(self):
        news = Category.objects.create(name="News", slug="news")
        Article.objects.create(
            title="Pyramid scheme collapse leaves hundreds out of pocket",
            slug="pyramid-scheme-collapse",
            category=news,
            published=timezone.now(),
        )
        response = self.client.get(
            reverse("newsroom:advanced.search"),
            {"adv_search": "pyramid", "search_type": "both"},
        )
        types = {
            item.obj_type if hasattr(item, "obj_type") else item["obj_type"]
            for item in response.context["page"].object_list
        }
        self.assertEqual(types, {0, 2})

    def add_home_articles(self):
        Category.objects.create(name="News", slug="news")
        for number in range(6):
            Article.objects.create(
                title="Article {}".format(number),
                slug="article-{}".format(number),
                category=Category.objects.get(name="News"),
                published=timezone.now() - datetime.timedelta(days=number),
            )

    def test_the_home_page_has_no_videos_block_until_one_is_placed(self):
        self.add_home_articles()
        response = self.client.get(reverse("newsroom:home"))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("home_videos", response.context)
        self.assertNotIn('class="gu-video-block"', main_markup(response))

    def test_a_videos_block_placed_in_a_home_group_renders(self):
        # _Videos is an ordinary block: an editor adds it to a Home group in the
        # admin, like _Featured_Photos or _Popular.
        self.add_home_articles()
        block = Block.objects.create(name="_Videos")
        group = BlockGroup_Group.objects.create(name="Home_2")
        BlockGroup.objects.create(block=block, group=group, position=1)

        response = self.client.get(reverse("newsroom:home"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["home_videos"]),
            [self.newest, self.middle, self.older],
        )
        markup = main_markup(response)
        self.assertIn('class="gu-video-block"', markup)
        self.assertIn("All videos", markup)
        # It sits in the same wrapper as every other block.
        self.assertIn('class="home__article__block"', markup)
        self.assertIn('class="sidebar-block"', markup)

    def test_video_blocks_have_independent_titles_counts_and_positions(self):
        self.add_home_articles()
        for group_name, title, count in [
            ("Home_Top", "Watch the latest", 1),
            ("Home_2", "More from GroundUp", 2),
            ("Home_Bottom", "At the end", 1),
        ]:
            block = Block.objects.create(
                name=title, block_type="videos", custom_title=title,
                num_articles=count,
            )
            group = BlockGroup_Group.objects.create(name=group_name)
            BlockGroup.objects.create(block=block, group=group, position=1)
        response = self.client.get(reverse("newsroom:home"))
        markup = main_markup(response)
        self.assertLess(markup.index("Watch the latest"), markup.index("Article 0"))
        self.assertLess(markup.index("Article 1"), markup.index("More from GroundUp"))
        self.assertLess(markup.index("More from GroundUp"), markup.index("Article 2"))
        self.assertLess(markup.index("Article 5"), markup.index("At the end"))
        for key, count in [("topblocks", 1), ("home_2", 2), ("bottomblocks", 1)]:
            self.assertEqual(len(response.context[key][0].videos), count)
        self.assertNotIn("Not ready yet", markup)

    def test_video_block_display_options(self):
        from django.template.loader import render_to_string
        block = Block.objects.create(name="Compact videos", block_type="videos")
        def markup():
            return render_to_string("newsroom/video_home_block.html", {
                "video_block": block, "home_videos": [self.newest, self.older],
            })
        html = markup()
        self.assertNotIn("GroundUp in focus", html)
        self.assertNotIn("gu-video-block__card--lead", html)
        self.assertNotIn("<time", html)
        self.assertNotIn("gu-video-block__summary", html)
        self.assertIn("gu-video-duration", html)
        self.assertIn("gu-video-block__category", html)
        block.video_featured = block.video_dates = block.video_summaries = True
        block.video_categories = block.video_durations = False
        block.save()
        block.refresh_from_db()
        html = markup()
        self.assertEqual(html.count("gu-video-block__card--lead"), 1)
        self.assertEqual(html.count("<time"), 2)
        self.assertIn("gu-video-block__summary", html)
        self.assertNotIn("gu-video-block__category", html)
        self.assertNotIn("gu-video-duration", html)

    def test_empty_video_block_has_no_heading_or_cards(self):
        from newsroom.views import get_blocks_in_context
        from django.template.loader import render_to_string
        block = Block.objects.create(name="Empty videos", block_type="videos", num_articles=0)
        group = BlockGroup_Group.objects.create(name="Home_Top")
        BlockGroup.objects.create(block=block, group=group, position=1)
        context = get_blocks_in_context({}, "Home_Top")
        markup = render_to_string("blocks/blocks.html", context)
        self.assertNotIn('class="gu-video-block"', markup)



@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
)
class VideoEditingTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = VideoCategory.objects.get(slug="explainer")
        cls.video = Video.objects.create(
            title="Municipal debt explained",
            slug="municipal-debt-explained",
            youtube_id="5RI7cF6A-8Q",
            published=timezone.now(),
        )
        editor = User.objects.create_user("editor", "editor@example.com", "abcde")
        editor.is_staff = True
        for name in ["Can add video", "Can change video", "Can delete video"]:
            editor.user_permissions.add(Permission.objects.get(name=name))
        editor.save()
        User.objects.create_user("reader", "reader@example.com", "abcde")

    def test_adding_a_video_needs_permission(self):
        url = reverse("newsroom:video.add")
        self.assertEqual(self.client.get(url).status_code, 302)

        # Signed in but without the permission: forbidden, not a login redirect.
        self.client.login(username="reader", password="abcde")
        self.assertEqual(self.client.get(url).status_code, 403)

        self.client.login(username="editor", password="abcde")
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_editing_and_managing_need_permission(self):
        for url in [
            reverse("newsroom:video.update", args=[self.video.slug]),
            reverse("newsroom:video.manage"),
        ]:
            self.assertEqual(self.client.get(url).status_code, 302)
            self.client.login(username="editor", password="abcde")
            self.assertEqual(self.client.get(url).status_code, 200)
            self.client.logout()

    def test_an_editor_can_add_a_video_with_chapters(self):
        self.client.login(username="editor", password="abcde")
        published = timezone.now().strftime("%Y-%m-%dT%H:%M")
        response = self.client.post(
            reverse("newsroom:video.add"),
            {
                "title": "How to avoid pyramid schemes",
                "slug": "how-to-avoid-pyramid-schemes",
                # Pasted straight from the browser's address bar.
                "youtube_id": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "duration": "9:42",
                "category": self.category.pk,
                "summary": "Thousands of South Africans have lost money.",
                "body": "",
                "credits": "",
                "byline": "GroundUp Video Team",
                "thumbnail": "",
                "thumbnail_alt": "",
                "published": published,
                "include_on_home": "on",
                "chapters-TOTAL_FORMS": "2",
                "chapters-INITIAL_FORMS": "0",
                "chapters-MIN_NUM_FORMS": "0",
                "chapters-MAX_NUM_FORMS": "1000",
                **NO_CONTRIBUTORS,
                "chapters-0-timecode": "0:00",
                "chapters-0-description": "Why the schemes spread so fast",
                "chapters-1-timecode": "2:41",
                "chapters-1-description": "How the payouts actually work",
            },
        )
        self.assertEqual(response.status_code, 302)
        video = Video.objects.get(slug="how-to-avoid-pyramid-schemes")
        self.assertEqual(video.youtube_id, "dQw4w9WgXcQ")
        self.assertEqual(video.duration, "9:42")
        self.assertEqual(
            [chapter.timecode for chapter in video.chapters.all()], ["0:00", "2:41"]
        )

    def test_failed_credit_save_rolls_back_video_and_chapters(self):
        from unittest.mock import patch
        self.client.login(username="editor", password="abcde")
        with patch("newsroom.forms.VideoContributorFormSet.save", side_effect=RuntimeError("Save failed")):
            with self.assertRaises(RuntimeError):
                self.client.post(reverse("newsroom:video.add"), {
                    "title": "Rolled back", "slug": "rolled-back",
                    "youtube_id": "dQw4w9WgXcQ",                    "chapters-TOTAL_FORMS": "1", "chapters-INITIAL_FORMS": "0",
                    "chapters-0-timecode": "0:00", "chapters-0-description": "Opening",
                    **NO_CONTRIBUTORS,
                })
        self.assertFalse(Video.objects.filter(slug="rolled-back").exists())
        self.assertFalse(VideoChapter.objects.filter(description="Opening").exists())

    def test_a_bad_url_or_duration_is_rejected(self):
        self.client.login(username="editor", password="abcde")
        response = self.client.post(
            reverse("newsroom:video.add"),
            {
                "title": "Nope",
                "slug": "nope",
                "youtube_id": "https://vimeo.com/12345",
                "duration": "nine minutes",
                "chapters-TOTAL_FORMS": "0",
                "chapters-INITIAL_FORMS": "0",
                "chapters-MIN_NUM_FORMS": "0",
                "chapters-MAX_NUM_FORMS": "1000",
                **NO_CONTRIBUTORS,
            },
        )
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIn("youtube_id", form.errors)
        self.assertIn("duration", form.errors)
        self.assertFalse(Video.objects.filter(slug="nope").exists())

    def test_an_editor_can_preview_an_unpublished_video(self):
        draft = Video.objects.create(
            title="Not ready yet", slug="not-ready-yet", youtube_id="aaaaaaaaaaa"
        )
        self.assertEqual(self.client.get(draft.get_absolute_url()).status_code, 404)
        self.client.login(username="editor", password="abcde")
        response = self.client.get(draft.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Not published")


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
)
class VideoContributorTest(TestCase):
    """Videos are made by teams, so the credits are rows rather than the five
    author slots an article gets."""

    @classmethod
    def setUpTestData(cls):
        cls.video = Video.objects.create(
            title="Municipal debt explained",
            slug="municipal-debt-explained",
            youtube_id="5RI7cF6A-8Q",
            published=timezone.now(),
        )
        cls.reporter = Author.objects.create(
            first_names="Barbara", last_name="Maregele", email="b@example.com"
        )
        cls.camera = Author.objects.create(
            first_names="Ashraf", last_name="Hendricks", email="a@example.com"
        )
        cls.second_camera = Author.objects.create(
            first_names="Masixole", last_name="Feni", email="m@example.com"
        )
        editor = User.objects.create_user("editor", "editor@example.com", "abcde")
        editor.is_staff = True
        for name in ["Can add video", "Can change video"]:
            editor.user_permissions.add(Permission.objects.get(name=name))
        editor.save()

    def add_credits(self):
        VideoContributor.objects.create(
            video=self.video, author=self.camera, roles="camera"
        )
        VideoContributor.objects.create(
            video=self.video, author=self.second_camera, roles="camera",
            note="second camera", position=110,
        )
        VideoContributor.objects.create(
            video=self.video, author=self.reporter, roles="reporting"
        )

    def test_credits_are_grouped_by_role_in_the_order_the_roles_are_declared(self):
        self.add_credits()
        self.assertEqual(
            self.video.credits_by_role(),
            [
                {"role": "Reporting", "people": ["Barbara Maregele"]},
                {"role": "Camera",
                 "people": ["Ashraf Hendricks", "Masixole Feni (second camera)"]},
            ],
        )

    def test_the_byline_falls_back_to_whoever_reported(self):
        self.add_credits()
        self.assertEqual(self.video.get_byline(), "Barbara Maregele")
        # An author or a typed byline still wins.
        self.video.authors.add(self.camera)
        self.assertEqual(self.video.get_byline(), "Ashraf Hendricks")
        self.video.byline = "GroundUp Video Team"
        self.assertEqual(self.video.get_byline(), "GroundUp Video Team")

    def test_the_credits_are_on_the_page(self):
        self.add_credits()
        markup = main_markup(self.client.get(self.video.get_absolute_url()))
        self.assertIn("gu-video-credits", markup)
        self.assertIn("<dt>Camera</dt>", markup)
        self.assertIn("Masixole Feni (second camera)", markup)
        self.assertIn("By Barbara Maregele", markup)

    def test_a_person_is_credited_once_on_a_video(self):
        VideoContributor.objects.create(
            video=self.video, author=self.camera, roles="camera"
        )
        with self.assertRaises(IntegrityError):
            VideoContributor.objects.create(
                video=self.video, author=self.camera, roles="editing"
            )

    def test_one_person_can_be_credited_with_several_jobs(self):
        credit = VideoContributor.objects.create(
            video=self.video, author=self.camera,
            # Out of order, and with a duplicate, as a form can hand it over.
            roles="editing,camera,editing",
        )
        credit.refresh_from_db()
        self.assertEqual(credit.role_list(), ["camera", "editing"])
        self.assertEqual(credit.roles_display(), "Camera, Video editing")
        VideoContributor.objects.create(
            video=self.video, author=self.reporter,
            roles="reporting,story_editing", position=90,
        )
        self.assertEqual(
            self.video.credits_by_role(),
            [
                {"role": "Reporting", "people": ["Barbara Maregele"]},
                {"role": "Story editing", "people": ["Barbara Maregele"]},
                {"role": "Camera", "people": ["Ashraf Hendricks"]},
                {"role": "Video editing", "people": ["Ashraf Hendricks"]},
            ],
        )

    def test_the_form_takes_several_jobs_for_one_person(self):
        self.client.login(username="editor", password="abcde")
        response = self.client.post(
            reverse("newsroom:video.update", args=[self.video.slug]),
            {
                "title": self.video.title,
                "slug": self.video.slug,
                "youtube_id": self.video.youtube_id,
                "chapters-TOTAL_FORMS": "0",
                "chapters-INITIAL_FORMS": "0",
                "chapters-MIN_NUM_FORMS": "0",
                "chapters-MAX_NUM_FORMS": "1000",
                "contributors-TOTAL_FORMS": "1",
                "contributors-INITIAL_FORMS": "0",
                "contributors-MIN_NUM_FORMS": "0",
                "contributors-MAX_NUM_FORMS": "1000",
                "contributors-0-author": str(self.camera.pk),
                "contributors-0-roles": ["editing", "camera"],
                "contributors-0-note": "",
                "contributors-0-position": "100",
            },
        )
        self.assertEqual(response.status_code, 302)
        credit = self.video.contributors.get()
        self.assertEqual(credit.role_list(), ["camera", "editing"])

    def test_an_editor_can_add_contributors_through_the_form(self):
        self.client.login(username="editor", password="abcde")
        response = self.client.post(
            reverse("newsroom:video.update", args=[self.video.slug]),
            {
                "title": self.video.title,
                "slug": self.video.slug,
                "youtube_id": self.video.youtube_id,
                "chapters-TOTAL_FORMS": "0",
                "chapters-INITIAL_FORMS": "0",
                "chapters-MIN_NUM_FORMS": "0",
                "chapters-MAX_NUM_FORMS": "1000",
                "contributors-TOTAL_FORMS": "3",
                "contributors-INITIAL_FORMS": "0",
                "contributors-MIN_NUM_FORMS": "0",
                "contributors-MAX_NUM_FORMS": "1000",
                "contributors-0-author": str(self.reporter.pk),
                "contributors-0-roles": ["reporting"],
                "contributors-0-note": "",
                "contributors-0-position": "100",
                "contributors-1-author": str(self.camera.pk),
                "contributors-1-roles": ["camera"],
                "contributors-1-note": "",
                "contributors-1-position": "100",
                # Left blank: an untouched row must not become a credit.
                "contributors-2-note": "",
                "contributors-2-position": "100",
            },
        )
        self.assertEqual(
            response.status_code, 302,
            response.context["contributor_formset"].errors
            if response.context else "")
        self.assertEqual(
            [(c.author.last_name, c.roles) for c in self.video.contributors.all()],
            [("Maregele", "reporting"), ("Hendricks", "camera")],
        )

    def test_a_contributor_without_a_job_is_an_error(self):
        self.client.login(username="editor", password="abcde")
        response = self.client.post(
            reverse("newsroom:video.update", args=[self.video.slug]),
            {
                "title": self.video.title,
                "slug": self.video.slug,
                "youtube_id": self.video.youtube_id,
                "chapters-TOTAL_FORMS": "0",
                "chapters-INITIAL_FORMS": "0",
                "chapters-MIN_NUM_FORMS": "0",
                "chapters-MAX_NUM_FORMS": "1000",
                "contributors-TOTAL_FORMS": "1",
                "contributors-INITIAL_FORMS": "0",
                "contributors-MIN_NUM_FORMS": "0",
                "contributors-MAX_NUM_FORMS": "1000",
                "contributors-0-author": str(self.camera.pk),
                "contributors-0-note": "",
                "contributors-0-position": "100",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("roles", response.context["contributor_formset"].errors[0])
        self.assertEqual(self.video.contributors.count(), 0)

    def test_a_contributor_without_a_name_is_an_error_and_saves_nothing(self):
        self.client.login(username="editor", password="abcde")
        response = self.client.post(
            reverse("newsroom:video.update", args=[self.video.slug]),
            {
                "title": "A new title that must not be saved",
                "slug": self.video.slug,
                "youtube_id": self.video.youtube_id,
                "chapters-TOTAL_FORMS": "0",
                "chapters-INITIAL_FORMS": "0",
                "chapters-MIN_NUM_FORMS": "0",
                "chapters-MAX_NUM_FORMS": "1000",
                "contributors-TOTAL_FORMS": "1",
                "contributors-INITIAL_FORMS": "0",
                "contributors-MIN_NUM_FORMS": "0",
                "contributors-MAX_NUM_FORMS": "1000",
                "contributors-0-author": "",
                "contributors-0-roles": ["camera"],
                "contributors-0-note": "",
                "contributors-0-position": "100",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("author", response.context["contributor_formset"].errors[0])
        self.video.refresh_from_db()
        self.assertEqual(self.video.title, "Municipal debt explained")
        self.assertEqual(self.video.contributors.count(), 0)

    def test_a_contributor_can_be_excluded_from_payment(self):
        self.client.login(username="editor", password="abcde")
        response = self.client.post(
            reverse("newsroom:video.update", args=[self.video.slug]),
            {
                "title": self.video.title,
                "slug": self.video.slug,
                "youtube_id": self.video.youtube_id,
                "chapters-TOTAL_FORMS": "0",
                "chapters-INITIAL_FORMS": "0",
                "chapters-MIN_NUM_FORMS": "0",
                "chapters-MAX_NUM_FORMS": "1000",
                "contributors-TOTAL_FORMS": "2",
                "contributors-INITIAL_FORMS": "0",
                "contributors-MIN_NUM_FORMS": "0",
                "contributors-MAX_NUM_FORMS": "1000",
                "contributors-0-author": str(self.reporter.pk),
                "contributors-0-roles": ["reporting"],
                "contributors-0-note": "",
                "contributors-0-position": "100",
                "contributors-1-author": str(self.camera.pk),
                "contributors-1-roles": ["camera"],
                "contributors-1-note": "",
                "contributors-1-position": "100",
                "contributors-1-no_payment": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            {c.author.last_name: c.no_payment
             for c in self.video.contributors.all()},
            {"Maregele": False, "Hendricks": True},
        )

    def test_the_body_is_written_with_ckeditor(self):
        self.client.login(username="editor", password="abcde")
        markup = self.client.get(reverse("newsroom:video.add")).content.decode()
        self.assertIn("cdn.ckeditor.com", markup)
        self.assertIn("ck_inline_config.js", markup)
        self.assertRegex(
            markup, r'<textarea[^>]*class="gu-ckeditor"[^>]*name="body"'
                    r'|<textarea[^>]*name="body"[^>]*class="gu-ckeditor"'
        )

    def test_the_form_and_the_manage_list_show_what_has_been_billed(self):
        freelancer = Author.objects.create(
            first_names="Liezl", last_name="Human", email="lh@example.com",
            freelancer="f",
        )
        # Publishing the video raised the payment item; see
        # payment.models.create_video_payments.
        VideoContributor.objects.create(
            video=self.video, author=freelancer, roles="camera"
        )
        editor = User.objects.get(username="editor")
        editor.user_permissions.add(
            Permission.objects.get(codename="change_commission")
        )
        editor.save()
        self.client.login(username="editor", password="abcde")

        form = self.client.get(
            reverse("newsroom:video.update", args=[self.video.slug])
        ).content.decode()
        self.assertIn("Liezl Human", form)
        self.assertIn("Video contributor - Camera", form)

        manage = self.client.get(reverse("newsroom:video.manage"))
        self.assertEqual(manage.context["videos"][0].credit_count, 1)
        self.assertEqual(manage.context["videos"][0].payment_count, 1)
        self.assertIn("1 billed", manage.content.decode())

    def test_the_form_offers_a_payment_link_for_a_saved_contributor(self):
        self.add_credits()
        editor = User.objects.get(username="editor")
        editor.user_permissions.add(
            Permission.objects.get(codename="change_commission")
        )
        editor.save()
        self.client.login(username="editor", password="abcde")
        markup = self.client.get(
            reverse("newsroom:video.update", args=[self.video.slug])
        ).content.decode()
        self.assertIn(
            "{}?author={}&amp;video={}".format(
                reverse("payments:commissions.detail.add"),
                self.reporter.pk,
                self.video.pk,
            ),
            markup,
        )


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
)
class VideoQATest(TestCase):
    """Covers the paths editors actually use, including the admin."""

    @classmethod
    def setUpTestData(cls):
        cls.category = VideoCategory.objects.get(slug="explainer")
        cls.topic = Topic.objects.create(name="Grants", slug="grants")
        cls.news = Category.objects.create(name="News", slug="news")
        cls.article = Article.objects.create(
            title="Pyramid scheme collapse leaves hundreds out of pocket",
            slug="pyramid-scheme-collapse",
            category=cls.news,
            published=timezone.now(),
        )
        cls.video = Video.objects.create(
            title="Municipal debt explained",
            slug="municipal-debt-explained",
            youtube_id="5RI7cF6A-8Q",
            category=cls.category,
            duration="7:15",
            credits="Filmed in Makhanda, July 2026.",
            published=timezone.now(),
        )
        VideoChapter.objects.create(
            video=cls.video, timecode="1:20", description="Where the money goes"
        )
        superuser = User.objects.create_superuser(
            "boss", "boss@example.com", "abcde"
        )
        cls.superuser = superuser

    def admin_post(self, url, extra):
        payload = {
            "chapters-TOTAL_FORMS": "0",
            "chapters-INITIAL_FORMS": "0",
            "chapters-MIN_NUM_FORMS": "0",
            "chapters-MAX_NUM_FORMS": "1000",
            **NO_CONTRIBUTORS,
        }
        payload.update(extra)
        return self.client.post(url, payload)

    def test_admin_accepts_a_pasted_watch_url(self):
        # The field used to be 20 characters, so the widget's maxlength cut a
        # pasted URL down to "https://www.youtube.".
        self.client.force_login(self.superuser)
        response = self.admin_post(
            "/admin/newsroom/video/add/",
            {
                "title": "Pasted watch URL",
                "slug": "pasted-watch-url",
                "youtube_id": "https://www.youtube.com/watch?v=lRQ1kJJNjko",
            },
        )
        self.assertEqual(response.status_code, 302, response.context["errors"]
                         if response.context else "")
        self.assertEqual(
            Video.objects.get(slug="pasted-watch-url").youtube_id, "lRQ1kJJNjko"
        )

    def test_admin_accepts_a_pasted_shorts_url(self):
        self.client.force_login(self.superuser)
        self.admin_post(
            "/admin/newsroom/video/add/",
            {
                "title": "Pasted short",
                "slug": "pasted-short",
                "youtube_id": "https://www.youtube.com/shorts/lRQ1kJJNjko?feature=share",
            },
        )
        self.assertEqual(
            Video.objects.get(slug="pasted-short").youtube_id, "lRQ1kJJNjko"
        )

    def test_admin_rejects_a_url_that_is_not_youtube(self):
        self.client.force_login(self.superuser)
        response = self.admin_post(
            "/admin/newsroom/video/add/",
            {
                "title": "Not YouTube",
                "slug": "not-youtube",
                "youtube_id": "https://vimeo.com/12345",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Video.objects.filter(slug="not-youtube").exists())
        self.assertContains(response, "not a YouTube URL")

    def test_field_widths_hold_a_pasted_url(self):
        field = Video._meta.get_field("youtube_id")
        self.assertGreaterEqual(field.max_length, 200)

    def test_the_admin_related_article_lookup_finds_articles(self):
        # Grappelli reads autocomplete_search_fields() off the model; without it
        # the "related articles" lookup silently returned nothing.
        self.assertTrue(hasattr(Article, "autocomplete_search_fields"))
        self.client.force_login(self.superuser)
        response = self.client.get(
            reverse("grp_autocomplete_lookup"),
            {"term": "pyramid", "app_label": "newsroom", "model_name": "article"},
        )
        self.assertEqual(response.status_code, 200)
        results = json.loads(response.content)
        self.assertIn(self.article.pk, [row["value"] for row in results])

    def test_the_admin_lookups_for_the_video_models_work(self):
        self.client.force_login(self.superuser)
        for model_name, term, expected in [
            ("video", "municipal", self.video.pk),
            ("videocategory", "explainer", self.category.pk),
            ("topic", "grants", self.topic.pk),
        ]:
            response = self.client.get(
                reverse("grp_autocomplete_lookup"),
                {"term": term, "app_label": "newsroom", "model_name": model_name},
            )
            results = json.loads(response.content)
            self.assertIn(
                expected, [row["value"] for row in results], model_name
            )

    def test_the_admin_saves_a_contributor_inline(self):
        author = Author.objects.create(
            first_names="Ashraf", last_name="Hendricks", email="a@example.com"
        )
        self.client.force_login(self.superuser)
        response = self.admin_post(
            "/admin/newsroom/video/add/",
            {
                "title": "With a camera credit",
                "slug": "with-a-camera-credit",
                "youtube_id": "lRQ1kJJNjko",
                "contributors-TOTAL_FORMS": "1",
                "contributors-INITIAL_FORMS": "0",
                "contributors-0-author": str(author.pk),
                "contributors-0-roles": ["camera"],
                "contributors-0-position": "100",
            },
        )
        self.assertEqual(response.status_code, 302)
        video = Video.objects.get(slug="with-a-camera-credit")
        self.assertEqual(
            [str(c) for c in video.contributors.all()],
            ["Ashraf Hendricks - Camera"],
        )

    def test_the_admin_edits_the_body_with_ckeditor(self):
        self.client.force_login(self.superuser)
        markup = self.client.get(
            "/admin/newsroom/video/{}/change/".format(self.video.pk)
        ).content.decode()
        self.assertIn("cdn.ckeditor.com", markup)
        self.assertIn("ck_init_admin.js", markup)
        self.assertIn("gu-ckeditor", markup)

    def test_the_admin_inline_carries_the_payment_column(self):
        author = Author.objects.create(
            first_names="Ashraf", last_name="Hendricks", email="a@example.com",
            freelancer="f",
        )
        VideoContributor.objects.create(
            video=self.video, author=author, roles="camera"
        )
        self.client.force_login(self.superuser)
        markup = self.client.get(
            "/admin/newsroom/video/{}/change/".format(self.video.pk)
        ).content.decode()
        self.assertIn("no_payment", markup)
        # Publishing raised the item, so the column links to the invoice
        # rather than offering to raise one.
        self.assertIn(
            reverse("payments:invoice.detail", args=[author.pk, 1]), markup
        )

    def test_the_admin_raises_payments_when_it_publishes(self):
        from payment.models import Commission

        author = Author.objects.create(
            first_names="Masixole", last_name="Feni", email="m@example.com",
            freelancer="f",
        )
        self.client.force_login(self.superuser)
        response = self.admin_post(
            "/admin/newsroom/video/add/",
            {
                "title": "Published from the admin",
                "slug": "published-from-the-admin",
                "youtube_id": "lRQ1kJJNjko",
                "published_0": timezone.now().strftime("%Y-%m-%d"),
                "published_1": timezone.now().strftime("%H:%M:%S"),
                "contributors-TOTAL_FORMS": "1",
                "contributors-INITIAL_FORMS": "0",
                "contributors-0-author": str(author.pk),
                "contributors-0-roles": ["camera"],
                "contributors-0-position": "100",
            },
        )
        self.assertEqual(response.status_code, 302)
        video = Video.objects.get(slug="published-from-the-admin")
        item = Commission.objects.get(video=video)
        self.assertEqual(item.invoice.author, author)
        self.assertEqual(item.notes, "Camera")

    def test_the_form_video_lookup_finds_videos_including_drafts(self):
        # The payments form uses it, and a video is often paid for before it
        # is published.
        draft = Video.objects.create(
            title="Municipal debt, part two", slug="municipal-debt-two",
            youtube_id="lRQ1kJJNjko",
        )
        self.client.force_login(self.superuser)
        response = self.client.get(
            "/ajax_select/ajax_lookup/videos", {"term": "municipal"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, draft.title)
        self.assertContains(response, self.video.title)

    def test_the_form_article_lookup_finds_articles(self):
        self.client.force_login(self.superuser)
        response = self.client.get(
            "/ajax_select/ajax_lookup/articles", {"term": "pyramid"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pyramid scheme collapse")

    def test_the_form_accepts_a_pasted_watch_url(self):
        editor = User.objects.create_user("ed", "ed@example.com", "abcde")
        editor.is_staff = True
        for name in ["Can add video", "Can change video"]:
            editor.user_permissions.add(Permission.objects.get(name=name))
        editor.save()
        self.client.login(username="ed", password="abcde")
        response = self.client.post(
            reverse("newsroom:video.add"),
            {
                "title": "Pasted through the form",
                "slug": "pasted-through-the-form",
                "youtube_id": "https://www.youtube.com/watch?v=lRQ1kJJNjko",
                "related_articles": [str(self.article.pk)],
                "chapters-TOTAL_FORMS": "0",
                "chapters-INITIAL_FORMS": "0",
                "chapters-MIN_NUM_FORMS": "0",
                "chapters-MAX_NUM_FORMS": "1000",
                **NO_CONTRIBUTORS,
            },
        )
        self.assertEqual(response.status_code, 302)
        video = Video.objects.get(slug="pasted-through-the-form")
        self.assertEqual(video.youtube_id, "lRQ1kJJNjko")
        self.assertEqual(list(video.related_articles.all()), [self.article])

    def test_the_form_input_has_no_truncating_maxlength(self):
        editor = User.objects.create_user("ed2", "ed2@example.com", "abcde")
        editor.is_staff = True
        editor.user_permissions.add(Permission.objects.get(name="Can add video"))
        editor.save()
        self.client.login(username="ed2", password="abcde")
        response = self.client.get(reverse("newsroom:video.add"))
        widget = re.search(r'<input[^>]*name="youtube_id"[^>]*>', response.content.decode())
        self.assertIsNotNone(widget)
        maxlength = re.search(r'maxlength="(\d+)"', widget.group(0))
        if maxlength:
            self.assertGreaterEqual(int(maxlength.group(1)), 200)

    def test_the_timecode_and_duration_labels_carry_the_format(self):
        # Grappelli renders help_text as a tooltip icon that needs its JS, so
        # the format has to be visible in the label itself.
        self.assertEqual(
            str(VideoChapter._meta.get_field("timecode").verbose_name), "time (m:ss)"
        )
        self.assertEqual(
            str(Video._meta.get_field("duration").verbose_name), "length (m:ss)"
        )

    def test_the_embed_sends_a_referer(self):
        # Without one YouTube blocks playback with error 153, and the site sends
        # Referrer-Policy: same-origin.
        response = self.client.get(self.video.get_absolute_url())
        self.assertContains(response, "strict-origin-when-cross-origin")
        self.assertEqual(response.headers.get("Referrer-Policy"), "same-origin")

    def test_every_video_url_resolves(self):
        self.client.force_login(self.superuser)
        cases = [
            (reverse("newsroom:video.list"), 200),
            (reverse("newsroom:video.category", args=["explainer"]), 200),
            (reverse("newsroom:video.rss"), 200),
            (reverse("newsroom:video.atom"), 200),
            (reverse("newsroom:video.manage"), 200),
            (reverse("newsroom:video.add"), 200),
            (reverse("newsroom:video.update", args=[self.video.slug]), 200),
            (reverse("newsroom:video.delete", args=[self.video.slug]), 200),
            (self.video.get_absolute_url(), 200),
            ("/videos/category/nope/", 404),
            ("/videos/nope/", 404),
        ]
        for url, expected in cases:
            self.assertEqual(self.client.get(url).status_code, expected, url)

    def test_the_page_furniture_is_in_the_order_editorial_asked_for(self):
        self.video.related_articles.add(self.article)
        VideoContributor.objects.create(
            video=self.video,
            author=Author.objects.create(first_names="Ashraf",
                                         last_name="Hendricks"),
            roles="camera",
        )
        self.video.topics.add(self.topic)
        markup = main_markup(self.client.get(self.video.get_absolute_url()))
        order = [
            "gu-video-credits",
            "gu-video-section--readmore",
            "article__topics",
            "gu-video-support",
            "gu-follow",
            "gu-video-licence",
        ]
        positions = [markup.index(name) for name in order]
        self.assertEqual(positions, sorted(positions), order)

    def test_the_follow_row_says_what_it_is_for(self):
        markup = main_markup(self.client.get(self.video.get_absolute_url()))
        self.assertIn("Follow GroundUp for more videos", markup)
        self.assertNotIn("wherever you already are", markup)

    def test_the_videos_page_intro(self):
        response = self.client.get(reverse("newsroom:video.list"))
        self.assertContains(response, "Every GroundUp video is free to watch.")
        self.assertNotContains(response, "Explainers, investigations and")

    def test_the_categories_are_the_ones_editorial_asked_for(self):
        self.assertEqual(
            list(VideoCategory.objects.values_list("name", flat=True)),
            ["Explainer", "News reel", "Roundup", "Feature"],
        )

    def test_editing_keeps_and_changes_chapters(self):
        self.client.force_login(self.superuser)
        chapter = self.video.chapters.first()
        response = self.client.post(
            reverse("newsroom:video.update", args=[self.video.slug]),
            {
                "title": self.video.title,
                "slug": self.video.slug,
                "youtube_id": self.video.youtube_id,
                "duration": "7:15",
                "chapters-TOTAL_FORMS": "2",
                "chapters-INITIAL_FORMS": "1",
                "chapters-MIN_NUM_FORMS": "0",
                "chapters-MAX_NUM_FORMS": "1000",
                **NO_CONTRIBUTORS,
                "chapters-0-id": str(chapter.pk),
                "chapters-0-timecode": "1:20",
                "chapters-0-description": "Where the money really goes",
                "chapters-1-timecode": "4:05",
                "chapters-1-description": "Who ends up paying",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            [c.description for c in self.video.chapters.all()],
            ["Where the money really goes", "Who ends up paying"],
        )

    def test_deleting_a_video(self):
        self.client.force_login(self.superuser)
        response = self.client.post(
            reverse("newsroom:video.delete", args=[self.video.slug])
        )
        self.assertRedirects(response, reverse("newsroom:video.list"))
        self.assertFalse(Video.objects.filter(slug="municipal-debt-explained").exists())

    def test_a_video_with_nothing_but_a_title_renders_everywhere(self):
        bare = Video.objects.create(
            title="Bare minimum", slug="bare-minimum", youtube_id="lRQ1kJJNjko",
            published=timezone.now(),
        )
        for url in [
            bare.get_absolute_url(),
            reverse("newsroom:video.list"),
            reverse("newsroom:home"),
            reverse("newsroom:video.rss"),
        ]:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_a_video_uploaded_as_a_short_is_an_ordinary_landscape_page(self):
        short = Video.objects.create(
            title="A short", slug="a-short", youtube_id="lRQ1kJJNjko",
            published=timezone.now(),
        )
        response = self.client.get(short.get_absolute_url())
        self.assertNotContains(response, "gu-video-player--short")
        self.assertNotContains(response, "youtube.com/shorts/lRQ1kJJNjko")
        self.assertContains(response, "youtube.com/watch?v=lRQ1kJJNjko")

    def test_the_video_page_reuses_the_site_article_markup(self):
        markup = main_markup(self.client.get(self.video.get_absolute_url()))
        for css_class in [
            'class="article__title"',
            'class="article__details__date-by"',
            'class="article__image__caption"',
            'class="article__copyright gu-video-licence"',
        ]:
            self.assertIn(css_class, markup)

    def test_the_page_shares_the_way_an_article_does(self):
        markup = main_markup(self.client.get(self.video.get_absolute_url()))
        # One button that hands over to the reader's own share sheet, as on an
        # article, rather than the old row of per-network links.
        self.assertIn('class="gu-share-btn"', markup)
        self.assertIn('data-title="Municipal debt explained"', markup)
        for gone in ["facebook-share", "twitter-share", "whatsapp-share",
                     "email-share", "icon-share"]:
            self.assertNotIn(gone, markup)

    def test_the_page_is_full_width_with_no_sidebar(self):
        markup = main_markup(self.client.get(self.video.get_absolute_url()))
        self.assertIn('class="article gu-video-detail"', markup)
        self.assertNotIn("<aside", markup)
        self.assertNotIn("gu-video-aside", markup)
        self.assertNotIn("col-md-4", markup)

    def test_the_follow_row_is_below_everything(self):
        markup = main_markup(self.client.get(self.video.get_absolute_url()))
        self.assertIn('class="gu-follow"', markup)
        for url in ["youtube.com/@GroundUpNews", "tiktok.com/@groundup_news",
                    "instagram.com/groundup_news", "facebook.com/GroundUpNews"]:
            self.assertIn(url, markup)
        # Nothing comes after it.
        self.assertLess(markup.index("gu-video-player"), markup.index("gu-follow"))
        self.assertLess(markup.index("gu-video-support"), markup.index("gu-follow"))
        for icon in ["icon-tiktok", "icon-instagram", "icon-bluesky"]:
            self.assertIn(icon, self.client.get("/").content.decode())

    def test_the_page_states_the_republication_licence(self):
        markup = main_markup(self.client.get(self.video.get_absolute_url()))
        self.assertIn("GroundUp Republication Licence Version 1.0", markup)
        self.assertIn("licencing/detail/2/", markup)
        # A video is not Creative Commons licensed, and the page must not read
        # as though it is: the only mention of it is the denial.
        self.assertIn("<b>not</b> available under a Creative Commons", markup)
        self.assertEqual(markup.count("Creative Commons"), 1)

    def test_the_index_uses_the_video_desk_markup(self):
        markup = main_markup(self.client.get(reverse("newsroom:video.list")))
        # The dark panel for the newest report, and the runtime in its CTA.
        self.assertIn('class="gu-videos-hero"', markup)
        self.assertIn("gu-videos-hero__watch", markup)
        self.assertIn("Watch · 7:15", markup)
        self.assertIn("Latest video", markup)
        # The pills are still the site's own topic-chip component.
        self.assertIn('class="article__topic article__topic--selected"', markup)
        # The heading is the page name, not the featured video's.
        self.assertIn('class="gu-videos__title">Videos</h1>', markup)
        # The old centred-list-page treatment is gone.
        self.assertNotIn("summary-list-heading", markup)
        self.assertNotIn("home__articles__article__text__title", markup)

    def test_the_featured_video_is_flagged_when_promoted(self):
        self.video.promote = True
        self.video.save()
        markup = main_markup(self.client.get(reverse("newsroom:video.list")))
        self.assertIn("Featured", markup)
        self.assertNotIn("Latest video", markup)

    def test_the_index_hero_falls_back_without_a_duration_or_summary(self):
        Video.objects.all().delete()
        bare = Video.objects.create(
            title="No frills", slug="no-frills", youtube_id="lRQ1kJJNjko",
            published=timezone.now(),
        )
        markup = main_markup(self.client.get(reverse("newsroom:video.list")))
        self.assertIn("gu-videos-hero", markup)
        self.assertIn(bare.get_absolute_url(), markup)
        # The CTA drops the runtime rather than printing a bare separator.
        self.assertIn("Watch", markup)
        self.assertNotIn("Watch ·", markup)
        self.assertNotIn("gu-video-duration", markup)
