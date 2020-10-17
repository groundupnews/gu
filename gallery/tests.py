from django.contrib.auth.models import User
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from filebrowser.fields import FileBrowseField
from gallery import models

# Create your tests here.

class URLSWork(TestCase):

    @classmethod
    def setUpTestData(cls):
        album = models.Album()
        album.name = "album1"
        album.save()
        photo = models.Photograph()
        photo.suggested_caption = "caption1"
        photo.alt = "alt1"
        photo.save()
        album.photograph_set.add(photo)
        album.save()
        photo = models.Photograph()
        photo.suggested_caption = "caption2"
        photo.alt = "alt2"
        photo.save()
        album.photograph_set.add(photo)
        album.save()

    def test_urls(self):
        user = User.objects.create_user('admin', 'admin@example.com', 'abcde')
        user.is_staff = True
        user.is_active = True
        user.save()
        c = Client()
        response = c.login(username='admin', password='abcde')
        self.assertEqual(response, True)
        url = reverse('gallery:gallery.front')
        response = c.get(url)
        self.assertEqual(response.status_code, 200)
        url = reverse('gallery:album.list')
        response = c.get(url)
        self.assertEqual(response.status_code, 200)
        album = models.Album.objects.all()[0]
        url = reverse('gallery:album.detail', args = (album.pk, ))
        response = c.get(url)
        self.assertEqual(response.status_code, 200)
        url = reverse('gallery:photo.list')
        response = c.get(url)
        self.assertEqual(response.status_code, 200)
        url = reverse('gallery:photo.detail',
                      args=(album.photograph_set.all()[0].pk,))
        response = c.get(url)
        self.assertEqual(response.status_code, 200)
