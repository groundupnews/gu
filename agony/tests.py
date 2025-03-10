from django.test import TestCase
from django.test import Client
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

from newsroom.models import Topic
from agony.models import QandA

class QandaTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

        t1 = Topic()
        t1.name = "Social grants"
        t1.slug = "social-grants"
        t1.save()

        t2 = Topic()
        t2.name = "Housing"
        t2.slug = "housing"
        t2.save()

        q = QandA()
        q.short_question = "Test question 1"
        q.short_answer = "Test answer 1"
        q.published = timezone.now()
        q.save()
        q.topics.add(t1, t2)
        q.save()

        q = QandA()
        q.short_question = "Test question 2"
        q.short_answer = "Test answer 2"
        q.save()

    def test_qanda(self):
        """Test Q&A functionality
        
        Expected output:
        - Should have 2 total Q&As
        - Should have 1 published Q&A
        - Q&A list view should be accessible
        - Q&A detail view should be accessible
        - All views should return 200 status
        """
        qandas = QandA.objects.all()
        self.assertEqual(len(qandas), 2, "Should have 2 total Q&As")
        qandas = QandA.objects.published()
        self.assertEqual(len(qandas), 1, "Should have 1 published Q&A")
        
        client = Client()
        url = reverse('agony:list')
        response = client.get(url)
        self.assertEqual(response.status_code, 200, "List view should be accessible")

        url = reverse('agony:detail', args=[1, ])
        response = client.get(url)
        self.assertEqual(response.status_code, 200, "Detail view should be accessible")
