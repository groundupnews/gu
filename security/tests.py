from django.contrib.auth.models import User
from django.test import TestCase
from django.test import Client
from django.urls import reverse

# Create your tests here.

class URLSWork(TestCase):

    def test_urls(self):
        user = User.objects.create_user('admin', 'admin@example.com', 'abcde')
        user.is_staff = True
        user.is_active = True
        user.save()
        c = Client()
        response = c.login(username='admin', password='abcde')
        self.assertEqual(response, True)
        url = reverse('security:account_change_password')
        response = c.get(url)
        self.assertEqual(response.status_code, 200)
