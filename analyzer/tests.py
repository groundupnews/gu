from django.contrib.auth.models import User
from django.test import TestCase
from django.test import Client
from django.urls import reverse

# Create your tests here.

class URLSWork(TestCase):


    def test_urls(self):
        """Test analyzer URLs and permissions
        
        Expected output:
        - Staff user should be created successfully 
        - Login should succeed with correct credentials
        - Should access top URLs page successfully
        - All requests should return 200 status
        """
        user = User.objects.create_user('admin', 'admin@example.com', 'abcde')
        user.is_staff = True
        user.is_active = True
        user.save()
        c = Client()
        response = c.login(username='admin', password='abcde')
        self.assertEqual(response, True, "Login should succeed")
        url = reverse('analyzer:top_urls')
        response = c.get(url)
        self.assertEqual(response.status_code, 200, 
                        "Top URLs should be accessible")
