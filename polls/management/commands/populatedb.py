from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import os


class Command(BaseCommand):
    help = "Loads data into database for stagging and local"

    def handle(self, *args, **options):
        directory = settings.BASE_DIR
        fixtures = []
        for filename in os.listdir(os.path.join(directory, "dummydata")):
            if filename.endswith(".json") or filename.endswith(".yaml"):
                fixtures.append(filename)

        for fixture in fixtures:
            self.stdout.write(f"loading fixtures in {fixture}")
            call_command("loaddata", os.path.join(directory, "dummydata/", fixture))
