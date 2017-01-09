from django.test import TestCase
from django.test import Client
from newsroom.models import Article, Category
from .models import Tweet, TwitterHandle
from django.contrib.auth.models import User

class TwitterTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

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

        h = TwitterHandle()
        h.name = "groundup_news"
        h.slug = "groundup_news"
        h.save()

        t = Tweet()
        t.article = a
        t.wait_time = 0
        t.status = "scheduled"
        t.tweet_text = "Test tweet " + str(a.published)
        t.save()
        t.tag_accounts.add(h)
        t.save()

    def test_tweet(self):
        num_published = Article.objects.published().count()
        self.assertEquals(num_published, 1)
        num_tweets = Tweet.objects.all().count()
        self.assertEqual(num_tweets, 1)
        from .management.commands import sendtweets
        result = sendtweets.process(1, 1)
        self.assertEqual(result["successes"], 1)
        self.assertEqual(result["failures"], 0)
        t = Tweet.objects.all()[0]
        self.assertEqual(t.characters_left, 58)
        self.assertEqual(t.status, "sent")
