import os

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Loads data into database for stagging and local"

    def handle(self, *args, **options):
        directory = settings.BASE_DIR
        fixtures = []
        for filename in os.listdir(os.path.join(directory, "dummydata")):
            if filename.endswith(".json") or filename.endswith(".yaml"):
                fixtures.append(filename)

        for fixture in range(len(fixtures) + 1):
            self.stdout.write(f"loading fixtures in {fixture}")

            call_command("loaddata", os.path.join(directory, "dummydata/", fixtures[fixture]))
