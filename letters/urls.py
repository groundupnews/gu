from django.conf.urls import url
from django.views.generic.base import TemplateView
from .views import write_letter

app_name = 'letters'

urlpatterns = [
    url(r'^letter/([0-9]+)/$', write_letter, name='letter_to_editor'),
    url(r'^thanks/$', TemplateView.as_view(
        template_name='letters/letter_thanks.html'),
        name='letter_thanks'),
]
