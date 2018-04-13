from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.http import Http404
from django.urls import reverse
from . import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.template.loader import render_to_string
from time import time

from .forms import LetterForm
from .models import Letter
from newsroom.models import Article


def write_letter(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if article.letters_on is False:
        raise Http404
    dupkey = 'dup_' + str(article.pk)
    duplicate = False
    try:
        last_accessed = float(request.session.get(dupkey))
    except:
        last_accessed = 0
    if time() - last_accessed < 3600:
        duplicate = True
        messages.add_message(request, messages.ERROR,
                             "You submitted a letter for this "
                             "article very recently. "
                             "Please wait a few hours "
                             "before sending another one.")
    if request.method == 'POST' and duplicate is False:
        form = LetterForm(request.POST)
        if form.is_valid():
            request.session[dupkey] = str(time())
            letter = Letter()
            letter.article = article
            letter.title = form.cleaned_data['title']
            letter.byline = form.cleaned_data['byline']
            letter.text = form.cleaned_data['text']
            letter.email = form.cleaned_data['email']
            letter.save()
            subject = "Thank you for submitting a letter to GroundUp"
            message = render_to_string('letters/acknowledge_letter.txt',
                                       {'letter': letter})
            send_mail(
                subject,
                message,
                settings.EDITOR,
                [letter.email]
            )
            return HttpResponseRedirect(reverse("letter_thanks"))
        else:
            messages.add_message(request, messages.ERROR,
                                 "Please fix the problems below.")
    else:
        form = LetterForm()
    return render(request, 'letters/letter_form.html', {'form': form,
                                                        'article': article})
