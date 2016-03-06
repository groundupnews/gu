from django.test import TestCase
from django.test import Client
from django.db import IntegrityError
from django.utils import timezone
import datetime
from newsroom.models import Article, Topic, Category
from newsroom import utils
from bs4 import BeautifulSoup as bs


class HtmlCleanUp(TestCase):

    def test_html_cleaners(self):
        """HTML is correctly cleaned"""

        html = "<p class='plod'></p><p>Hello</p><p class=''> &nbsp; </p><p class='test'> Good bye </p>"
        self.assertEqual(utils.remove_blank_paras(html),
                         "<p>Hello</p><p class='test'> Good bye </p>")

        html = bs('<p><img alt="" src="/media/uploads/church-SiyavuyaKhaya-20150128.jpg" style="width: 1382px; height: 1037px;" /></p><p class="caption">This is the caption.</p>', "html.parser")
        print("BS: ", str(bs))
        self.assertEqual(str(utils.replaceImgHeightWidthWithClass(html)),
                         '<p><img alt="" src="/media/uploads/church-SiyavuyaKhaya-20150128.jpg"/></p><p class="caption">This is the caption.</p>', "html.parser")

        html = bs('<p><img alt="" src="/media/uploads/church-SiyavuyaKhaya-20150128.jpg" style="width: 1382px; height: 1037px;" /></p><p class="caption">This is the caption.</p>', "html.parser")
        self.assertEqual(str(utils.replacePImgWithFigureImg(html)),
                         '<figure><img alt="" src="/media/uploads/church-SiyavuyaKhaya-20150128.jpg" style="width: 1382px; height: 1037px;"/><figcaption>This is the caption.</figcaption></figure>')
        html = '<p><img alt="" src="/media/uploads/church-SiyavuyaKhaya-20150128.jpg" style="width: 1382px; height: 1037px;" /></p><p class="caption">This is the caption.</p>'
        self.assertEqual(utils.replaceBadHtmlWithGood(html),
                         '<figure><img alt="" src="/media/uploads/church-SiyavuyaKhaya-20150128.jpg"/><figcaption>This is the caption.</figcaption></figure>')


class ArticleTest(TestCase):

    def setUp(self):
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
        a.slug = "test-article-1"
        a.category = Category.objects.get(name="News")
        a.save()
        a.publish_now()
        a = Article()
        a.title = "Test article 2"
        a.slug = "test-article-2"
        a.category = Category.objects.get(slug="opinion")
        a.save()
        a.publish_now()

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
