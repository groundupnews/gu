from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.utils import timezone


class Command(BaseCommand):
    help = 'Log out all users by removing their active sessions'

    def handle(self, *args, **options):
        deleted_session_details = Session.objects.filter(
            expire_date__gte=timezone.now()
        ).delete()
        print(f"Remove {deleted_session_details[0]} active sessions")
