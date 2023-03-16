import os

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Loads data into database for stagging and local"

    def handle(self, *args, **options):
        directory = settings.BASE_DIR
        call_command("loaddata", os.path.join(directory, "dummydata/all_fixtures.json"))
