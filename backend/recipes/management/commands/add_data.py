import csv

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q

from recipes.models import Tag


class Command(BaseCommand):
    def handle(self, *args, **options):
        file_path = settings.BASE_DIR / 'data/tags.csv'
        with open(file_path, 'r', encoding='utf-8') as f:
            for row in csv.reader(f):
                if Tag.objects.filter(
                    Q(name=row[0]) | Q(slug=row[1])
                ).exists():
                    self.stdout.write(
                        self.style.ERROR(f'{row[0]!r} already exists!')
                    )
                    continue
                Tag.objects.create(name=row[0], slug=row[1])
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully added {row[0]!r}')
                )

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
