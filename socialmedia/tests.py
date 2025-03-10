from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth.models import Permission
from django.utils import timezone

from newsroom.models import Article, Category
from .models import Tweet, TwitterHandle

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

#     def test_tweet(self):
#         num_published = Article.objects.published().count()
#         self.assertEquals(num_published, 1)
#         num_tweets = Tweet.objects.all().count()
#         self.assertEqual(num_tweets, 1)
#         from .management.commands import sendtweets
#         result = sendtweets.process(1, 1)
#         self.assertEqual(result["successes"], 1)
#         self.assertEqual(result["failures"], 0)
#         t = Tweet.objects.all()[0]
#         self.assertEqual(t.characters_left, 152)
#         self.assertEqual(t.status, "sent")

    def test_handle(self):
        handle = TwitterHandle.objects.all()[0]
        client = Client()
        response = client.get(reverse('socialmedia:twitterhandle.add'))
        self.assertEqual(response.status_code, 302)
        response = client.get(reverse('socialmedia:twitterhandle.update', args=([handle.pk])))
        self.assertEqual(response.status_code, 302)
        response = client.get(reverse('socialmedia:twitterhandle.detail', args=([handle.pk])))
        self.assertEqual(response.status_code, 302)

        user = User.objects.create_user('staff', 'staff@example.com', 'abcde')
        user.is_staff = True
        user.is_active = True
        permission1 = Permission.objects.get(codename='add_twitterhandle')
        user.user_permissions.add(permission1)
        permission2 = Permission.objects.get(codename='change_twitterhandle')
        user.user_permissions.add(permission2)
        user.save()

        staff = Client()
        staff.login(username='staff', password='abcde')
        response = staff.get(reverse('socialmedia:twitterhandle.add'))
        self.assertEqual(response.status_code, 200)
        response = staff.get(reverse('socialmedia:twitterhandle.update', args=([handle.pk])))
        self.assertEqual(response.status_code, 200)
        response = staff.get(reverse('socialmedia:twitterhandle.detail', args=([handle.pk])))
        self.assertEqual(response.status_code, 200)

class TweetTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test article 
        category = Category.objects.create(name="News", slug="news")
        cls.article = Article.objects.create(
            title="Test Article",
            slug="test-article",
            category=category
        )
        cls.article.publish_now()

        # Create test tweet
        cls.tweet = Tweet(
            article=cls.article,
            tweet_text="Test tweet text",
            status='p'  # Pending
        )
        cls.tweet.save()

    def test_tweet_str(self):
        """Test Tweet string representation
        
        Expected output:
        - Tweet string should match format "{article.title}: {wait_time}"
        """
        self.assertEqual(
            str(self.tweet),
            f"{self.article.title}: {self.tweet.wait_time}",
            "Tweet string representation should match expected format"
        )

    def test_tweet_status(self):
        """Test Tweet status changes
        
        Expected output:
        - Initial status should be 'p' (pending)
        - Status should update to 'd' (done) after change
        """
        self.assertEqual(self.tweet.status, 'p', "Initial status should be pending")
        self.tweet.status = 'd'
        self.tweet.save()
        self.assertEqual(self.tweet.status, 'd', "Status should update to done")

    def test_tweet_length(self):
        """Test Tweet length validation
        
        Expected output:
        - Should raise exception for tweets > 280 characters
        """
        long_tweet = Tweet(
            article=self.article,
            tweet_text="x" * 281
        )
        with self.assertRaises(Exception, msg="Should reject tweets > 280 chars"):
            long_tweet.full_clean()
