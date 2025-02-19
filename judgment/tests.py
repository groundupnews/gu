"""
    Commented out as judgments are currently disabled.
    Enable them by uncommenting the URL in urls.py, and uncommenting the app in settings.py.
"""

# from django.test import TestCase, Client
# from django.utils import timezone
# from django.urls import reverse
# from judgment.models import Court, Event


# class JudgmentTest(TestCase):

#     @classmethod
#     def setUpTestData(cls):
#         court = Court()
#         court.name = "Constitutional Court"
#         court.save()

#         court = Court()
#         court.name = "Western Cape High Court"
#         court.save()

#         event = Event()
#         event.case_id = "A` 123 / 45 6"
#         event.email_address = "john@example.com"
#         event.case_name = "`A test case`"
#         event.court = court
#         event.judges = """`Judge 1.
#                         'Judge 2'`"""
#         event.event_type = "R"
#         event.event_date = timezone.now()
#         event.document_url = "http://www.example.com/`hello`"
#         event.notes = """`Some notes`
#                             More notes"""
#         event.save()

#         event = Event()
#         event.case_id =  "A` 123 / 45 6"
#         event.email_address = "john@example.com"
#         event.event_type = "H"
#         event.save()

#         event = Event()
#         event.case_id = "B 123/456"
#         event.email_address = "john@example.com"
#         event.event_type = "R"
#         event.save()


#     def test_judgment(self):
#         c = Court.objects.all()
#         self.assertEqual(len(c), 2)
#         e = Event.objects.all()
#         self.assertEqual(len(e), 3)
#         self.assertEqual(e[0].case_id, "A'123/456")

#         c = Client()
#         url = reverse('judgment:list')
#         response = c.get(url)
#         self.assertEqual(response.status_code, 200)
#         url = reverse('judgment:event_add')
#         response = c.get(url)
#         self.assertEqual(response.status_code, 200)
#         url = reverse('judgment:event_add')
#         response = c.post(url)
#         self.assertEqual(response.status_code, 200)
#         e = Event.objects.all()
#         self.assertEqual(len(e), 3)
#         response = c.post(url, {
#                 'case_id': ' 123/654 ',
#                 'email_address': 'jane@example.com',
#                 'event_type': 'R'
#             })
#         self.assertEqual(response.status_code, 302)
#         e = Event.objects.all()
#         self.assertEqual(len(e), 4)
