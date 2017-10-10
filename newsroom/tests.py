from django.test import TestCase
from django.test import Client
from django.core import mail
from django.db import IntegrityError
from django.utils import timezone
import datetime
from newsroom.models import Article, Topic, Category, Author
from newsroom import utils
from bs4 import BeautifulSoup as bs
from letters.models import Letter
from decimal import *
from django.contrib.auth.models import User
from pgsearch.utils import searchPostgresDB

class HtmlCleanUp(TestCase):

    def test_html_cleaners(self):
        """HTML is correctly cleaned"""

        html = "<p class='plod'></p><p>Hello</p><p class=''> &nbsp; </p><p class='test'> Good bye </p>"
        self.assertEqual(utils.remove_unnecessary_white_space(html),
                         "<p>Hello</p><p class='test'> Good bye </p>")

        html = bs('<p><img alt="" src="/media/uploads/church-SiyavuyaKhaya-20150128.jpg" style="width: 1382px; height: 1037px;" /></p><p class="caption">This is the caption.</p>', "html.parser")
        self.assertEqual(str(utils.replaceImgHeightWidthWithClass(html)),
                         '<p><img alt="" src="/media/uploads/church-SiyavuyaKhaya-20150128.jpg"/></p><p class="caption">This is the caption.</p>', "html.parser")

        html = bs('<p><img alt="" src="/media/uploads/church-SiyavuyaKhaya-20150128.jpg" style="width: 1382px; height: 1037px;" /></p><p class="caption">This is the caption.</p>', "html.parser")
        self.assertEqual(str(utils.replacePImgWithFigureImg(html)),
                         '<figure><img alt="" src="/media/uploads/church-SiyavuyaKhaya-20150128.jpg" style="width: 1382px; height: 1037px;"/><figcaption>This is the caption.</figcaption></figure>')
        html = '<p><img alt="" src="/media/uploads/church-SiyavuyaKhaya-20150128.jpg" style="width: 1382px; height: 1037px;" /></p><p class="caption">This is the caption.</p>'
        self.assertEqual(utils.replaceBadHtmlWithGood(html),
                         '<figure><img alt="" src="/media/uploads/church-SiyavuyaKhaya-20150128.jpg"/><figcaption>This is the caption.</figcaption></figure>')
        html1 = "<p>The dog ran away.</p>" \
                "<p>The dog -- ran away.</p>" \
                "<p>The dog --- ran away.</p>" \
                "<p>The dog--ran away.</p>" \
                "<p>The dog---ran away.</p>"
        html2 = "<p>The dog ran away.</p>" \
                "<p>The dog – ran away.</p>" \
                "<p>The dog — ran away.</p>" \
                "<p>The dog--ran away.</p>" \
                "<p>The dog---ran away.</p>"
        html3 = str(utils.processDashes(bs(html1)))
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
        a.external_primary_image = \
            "http://www.w3schools.com/html/pic_mountain.jpg"
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

    def test_articles(self):
        articles = Article.objects.all()
        self.assertEqual(len(articles), 2)
        articles = Article.objects.published()
        self.assertEqual(len(articles), 2)
        article = Article.objects.published()[1]
        self.assertEqual(article.title, "Test article 1")
        self.assertEqual(article.cached_primary_image,
            "http://www.w3schools.com/html/pic_mountain.jpg")
        article = Article.objects.published()[0]
        self.assertEqual(article.title, "Test article 2")

    def test_pages(self):
        client = Client()
        response = client.get('/article/test-article-1/')
        self.assertEqual(response.status_code, 200)
        client = Client()
        response = client.get('/article/test-article-2/')
        self.assertEqual(response.status_code, 200)
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        response = client.get('/article/no-exist/')
        self.assertEqual(response.status_code, 404)
        response = client.get('/content/test-article-1/')
        self.assertEqual(response.status_code, 302)
        response = client.get('/category/News/')
        self.assertEqual(response.status_code, 200)
        response = client.get('/category/news/')
        self.assertEqual(response.status_code, 200)
        response = client.get('/category/Opinion/')
        self.assertEqual(response.status_code, 200)
        response = client.get('/category/opinion/')
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

    def test_facebook(self):
        article = Article.objects.published()[1]
        self.assertEqual(article.cached_primary_image,
            "http://www.w3schools.com/html/pic_mountain.jpg")
        self.assertEqual(article.facebook_send_status, "paused")
        article.facebook_send_status = "scheduled"
        article.save()
        from .management.commands import posttofacebook
        results = posttofacebook.process(1, 1)
        self.assertEqual(results["successes"], 1)
        self.assertEqual(results["failures"], 0)
        article = Article.objects.published()[1]
        self.assertEqual(article.facebook_send_status, "sent")

        article = Article.objects.published()[0]
        self.assertEqual(article.facebook_send_status, "paused")
        article.facebook_send_status = "scheduled"
        article.save()
        from .management.commands import posttofacebook
        results = posttofacebook.process(1, 1)
        self.assertEqual(results["successes"], 1)
        self.assertEqual(results["failures"], 0)
        article = Article.objects.published()[0]
        self.assertEqual(article.facebook_send_status, "sent")

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

    def test_search(self):
        articles = searchPostgresDB("cow dog", Article, 'english', False,
                                    "title", "subtitle", "body")
        self.assertEqual(len(articles), 1)
