from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.http import Http404
from django.urls import reverse
from . import settings
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.contrib import messages
from django.template.loader import render_to_string
from time import time

from .forms import LetterForm
from .models import Letter
from newsroom.models import Article


def write_letter(request, pk):
    problem = False

    # Check the article exists
    article = get_object_or_404(Article, pk=pk)
    if article.letters_on is False:
        raise Http404

    try:
        # Check there aren't too many letters to process.
        # This offers some protection against a massive
        # number of malicious automated letter submissions.
        if Letter.objects.unprocessed().count() > 200:
            messages.add_message(request, messages.ERROR,
                                 "Sorry, we have more letters "
                                 "than we can handle "
                                 "at the moment. Please try again tomorrow "
                                 "or on the next workday.")
            problem = True
            raise ValidationError("Too many letters for GroundUp to process")

        # Check that the writer hasn't recently submitted
        # a letter for the same article.
        dupkey = 'dup_' + str(article.pk)
        try:
            last_accessed = float(request.session.get(dupkey))
        except:
            last_accessed = 0
        if time() - last_accessed < 3600:
            problem = True
            messages.add_message(request, messages.ERROR,
                                 "You submitted a letter for this "
                                 "article very recently. "
                                 "Please wait a few hours "
                                 "before sending another one.")
            raise ValidationError("Already submitted a letter on this article")

        if request.method == 'POST':
            form = LetterForm(request.POST)
            if form.is_valid():

                # Check that the letter wasn't written suspiciously
                # quickly such that it was likely written by a bot
                startkey = 'time_' + str(article.pk)
                try:
                    start = float(request.session.get(startkey))
                except:
                    start = 0
                if time() - start < 20:
                    messages.add_message(request, messages.ERROR,
                                         "You submitted this letter "
                                         "so quickly "
                                         "that our system "
                                         "suspects you are a spambot. "
                                         "If you are human, "
                                         "our apologies, take it easy, "
                                         "and resubmit in about 30 seconds.")
                    raise ValidationError("Letter submitted too quickly")
                request.session[dupkey] = str(time())
                letter = Letter()
                letter.article = article
                letter.title = form.cleaned_data['title']
                letter.byline = form.cleaned_data['byline']
                letter.text = form.cleaned_data['text']
                letter.email = form.cleaned_data['email']
                letter.save()
                subject = "Thank you for submitting a letter to GroundUp"
                html_message = render_to_string(
                    'letters/acknowledge_letter.html',
                    {'letter': letter})
                message = strip_tags(html_message)
                send_mail(
                    subject,
                    message,
                    settings.EDITOR,
                    [letter.email],
                    html_message=html_message
                )
                return HttpResponseRedirect(reverse("letters:letter_thanks"))
            else:
                messages.add_message(request, messages.ERROR,
                                     "Please fix the problems below.")
    except ValidationError:
        pass

    startkey = 'time_' + str(article.pk)
    request.session[startkey] = str(time())
    form = LetterForm()
    return render(request, 'letters/letter_form.html',
                  {'form': form,
                   'article': article,
                   'problem': problem})
