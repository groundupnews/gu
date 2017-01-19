from django.test import TestCase
from django.core import management
from newsroom.models import Article, Topic, Category, Author
from republisher.models import Republisher, RepublisherArticle

# Create your tests here.

class RepublishTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        republisher = Republisher()
        republisher.name = "NYT"
        republisher.email_addresses = "editor@example.com,news@example.com"
        republisher.message = "Hi. Please republish this."
        republisher.save()

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

        article = Article()
        article.title = "Test article 1"
        article.body = "<p>The quick brown fox jumps over the lazy dog.</p>"
        article.slug = "test-article-1"
        article.category = Category.objects.get(name="News")
        article.external_primary_image = \
            "http://www.w3schools.com/html/pic_mountain.jpg"
        article.save()
        article.publish_now()

        republisherArticle  = RepublisherArticle()
        republisherArticle.article = article
        republisherArticle.republisher = republisher
        republisherArticle.save()

    def test_republisher(self):
        r = RepublisherArticle.objects.all()
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0].status, "scheduled")
        management.call_command('emailrepublishers')
        r = RepublisherArticle.objects.all()
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0].status, "sent")
