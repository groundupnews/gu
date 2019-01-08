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
        qandas = QandA.objects.all()
        self.assertEqual(len(qandas), 2)
        qandas = QandA.objects.published()
        self.assertEqual(len(qandas), 1)
        client = Client()
        url = reverse('agony:list')
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        client = Client()
        url = reverse('agony:detail', args=[1, ])
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
