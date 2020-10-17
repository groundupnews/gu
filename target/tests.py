from django.contrib.auth.models import User
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from target import models
from django.utils import timezone

# Create your tests here.

class URLSWork(TestCase):

    @classmethod
    def setUpTestData(cls):
        target = models.Target()
        target.letters = 'practical'
        target.words = 'practical'
        target.published = timezone.now()
        target.number = 1
        target.save()

    def test_urls(self):
        user = User.objects.create_user('admin', 'admin@example.com', 'abcde')
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save()
        c = Client()
        response = c.login(username='admin', password='abcde')
        self.assertEqual(response, True)
        url = reverse('target:list')
        response = c.get(url)
        self.assertEqual(response.status_code, 200)
        target = models.Target.objects.all()[0]
        url = reverse('target:detail', args=(target.number,))
        response = c.get(url)
        self.assertEqual(response.status_code, 200)
        url = reverse('target:create')
        response = c.post(url)
        self.assertEqual(response.status_code, 200)
        url = reverse('target:create_letters', args=('practical',))
        response = c.post(url)
        self.assertEqual(response.status_code, 200)
        url = reverse('target:delete', args=(1,))
        response = c.get(url)
        self.assertEqual(response.status_code, 200)
