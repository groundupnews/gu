from smtplib import SMTPException
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from agony import settings
from agony.models import QandA


def process():
    responses_to_send = QandA.objects.filter(notify_sender=True). \
                        filter(sender_notified=False)
    for response in responses_to_send:
        subject = "Response to your question to GroundUp"
        html_message = render_to_string('agony/response.html',
                                        {'response': response})
        message = strip_tags(html_message)
        try:
            send_mail(
                subject,
                message,
                settings.AGONY_EMAIL,
                [response.sender_email] + settings.AGONY_EMAIL_RECIPIENTS,
                html_message=html_message
            )
            print("Response sent to: ", response.sender_email)
        except SMTPException as err:
            print("Error sending response to agony writer {0}: {1}".
                  format(response.sender_email, err))

        response.sender_notified = True
        response.save()

    return len(responses_to_send)


class Command(BaseCommand):
    help = 'Send responses to people who write to agony aunt.'

    def handle(self, *args, **options):
        response_count = process()
        print("Agony aunt responses: ", response_count)
