import csv

from django.core.management import BaseCommand
from django.db import transaction

from common.models import Album


class Command(BaseCommand):
    def handle(self, *args, **options):
        albums_to_create = []
        with open('albums.csv', "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                albums_to_create.append(
                    Album(
                        title=row['Album Title'],
                        artist=row['Artist'],
                        submitted_by=row['Submitted By'],
                        genre=row['Genre'],
                    )
                )
        with transaction.atomic():
            Album.objects.bulk_create(albums_to_create)
        return
