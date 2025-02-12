import csv
import json

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    def handle(self, *args, **options):
        file_path = settings.BASE_DIR / 'data/tags.csv'

        tags_to_create = []

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for name, slug in reader:
                tags_to_create.append(Tag(name=name, slug=slug))
            Tag.objects.bulk_create(tags_to_create)
        self.stdout.write(self.style.SUCCESS(
            'Successfully loaded tags'))
        with open('data/ingredients.json') as f:
            ingredients_data = json.load(f)
            ingredients_to_create = [
                Ingredient(name=ingredient['name'],
                           measurement_unit=ingredient['measurement_unit'])
                for ingredient in ingredients_data
            ]
            Ingredient.objects.bulk_create(ingredients_to_create)
        self.stdout.write(self.style.SUCCESS(
            'Successfully loaded ingredients'))
