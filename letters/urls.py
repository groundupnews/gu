from django.conf.urls import url
from .views import get_letter


urlpatterns = [
    url(r'^letter/([0-9]+)/$', get_letter, name='letter_to_editor'),
]
