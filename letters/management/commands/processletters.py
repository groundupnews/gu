from smtplib import SMTPException
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

from letters import settings
from letters.models import Letter


def process():
    base_url = "http://" + Site.objects.all()[0].domain
    # Published letters
    published_letters = Letter.objects.published().\
        filter(notified_letter_writer=False)
    for letter in published_letters:
        subject = "Your letter has been published: " + letter.title
        message = render_to_string('letters/published_letter.txt',
                                   {'letter': letter,
                                    'base_url': base_url})
        try:
            send_mail(
                subject,
                message,
                settings.EDITOR,
                [letter.email]
            )
        except SMTPException as err:
            print("Error sending email: {0}".format(err))
        letter.notified_letter_writer = True
        letter.save()

    # Rejected letters
    rejected_letters = Letter.objects.filter(rejected=True).\
        filter(notified_letter_writer=False)
    for letter in rejected_letters:
        subject = "Regarding your letter: " + letter.title
        message = render_to_string('letters/rejected_letter.txt',
                                   {'letter': letter,
                                    'base_url': base_url})
        try:
            send_mail(
                subject,
                message,
                settings.EDITOR,
                [letter.email]
            )
        except SMTPException as err:
            print("Error sending email: {0}".format(err))

        letter.notified_letter_writer = True
        letter.save()

    # Notify editors of new letters
    new_letters = Letter.objects.filter(notified_editors=False)
    if len(new_letters) > 0:
        subject = "New letters received on " + Site.objects.all()[0].name
        message = render_to_string('letters/new_letter.txt',
                                   {'letters': new_letters,
                                    'base_url': base_url})
        send_mail(
            subject,
            message,
            settings.EDITOR,
            [settings.EDITOR]
        )
        for letter in new_letters:
            letter.notified_editors = True
            letter.save()

    return {'Published': len(published_letters),
            'Rejects': len(rejected_letters),
            'New': len(new_letters)}


class Command(BaseCommand):
    help = 'Notify editors of new letters and letter writers '
    'of rejections or publications.'

    def handle(self, *args, **options):
        success_dict = process()
        print("Letterprocessing: Published: {0}. Rejects: {1}. New: {2}".
              format(success_dict["Published"],
                     success_dict["Rejects"],
                     success_dict["New"]))
