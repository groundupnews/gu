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

class PhotoTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.album = models.Album.objects.create(name="Test Album")
        cls.photo = models.Photograph.objects.create(
            suggested_caption="Test Photo",
            alt="Test Alt Text"
        )
        cls.album.photograph_set.add(cls.photo)

    def test_photo_str(self):
        self.assertEqual(str(self.photo), f"{self.photo.pk}, , None")

    def test_photo_in_album(self):
        self.assertIn(self.photo, self.album.photograph_set.all())

    def test_photo_detail_view(self):
        user = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        c = Client()
        c.login(username='admin', password='password')
        response = c.get(reverse('gallery:photo.detail', 
                                args=[self.photo.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.photo.suggested_caption)

    def test_photo_list_view(self):
        user = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        c = Client()
        c.login(username='admin', password='password')
        response = c.get(reverse('gallery:photo.list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.photo.suggested_caption)
