import csv

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.db.models import Q

from recipes.models import Tag


class Command(BaseCommand):
    def handle(self, *args, **options):
        file_path = settings.BASE_DIR / 'data/tags.csv'

        tags_to_create = []
        existing_tags = set()

        for tag in Tag.objects.all():
            existing_tags.add(tag.name)
            existing_tags.add(tag.slug)

        with open(file_path, 'r', encoding='utf-8') as f:
            for row in csv.reader(f):
                name, slug = row[0], row[1]
                if name in existing_tags or slug in existing_tags:
                    self.stdout.write(
                        self.style.ERROR(f'Cannot add {name!r}: already exists!')
                    )
                    continue

                tags_to_create.append(Tag(name=name, slug=slug))
        try:
            if tags_to_create:
                Tag.objects.bulk_create(tags_to_create)
                for tag in tags_to_create:
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully added {tag.name!r}')
                    )
        except(IntegrityError, Exception):
            pass

        # with open('data/ingredients.json') as f:
        #     ingredients_data = json.load(f)
        #     ingredients_to_create = [
        #         Ingredient(name=ingredient['name'],
        #                    measurement_unit=ingredient['measurement_unit'])
        #         for ingredient in ingredients_data
        #     ]
        #     Ingredient.objects.bulk_create(
        #         ingredients_to_create, ignore_conflicts=True)
        #
        # self.stdout.write(self.style.SUCCESS(
        #     'Successfully loaded ingredients'))
