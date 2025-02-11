import csv
from django.core.management.base import BaseCommand
from django.db import IntegrityError

from foodgram_backend import settings
from recipes.models import Ingredient


class Inrgredient:
    pass


#  не смотря на bulk_create на удаленном сервере эта команда выбрасывает ошибку
#  django.***.utils.DataError: value too long for type character varying(50)
# 2025/02/11 02:26:27 Process exited with status 1
class Command(BaseCommand):
    help = 'Load data from recipe.csv and tags.csv'

    def handle(self, *args, **options):
        file_path = settings.BASE_DIR / 'data/ingredients.csv'
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                Ingredient.objects.bulk_create(
                    Ingredient(name=row[0], measurement_unit=row[1])
                    for row in csv.reader(f)
                )
                self.stdout.write(
                    self.style.SUCCESS('Successfully added ingredients!')
                )
            except IntegrityError:
                self.stdout.write(
                    self.style.ERROR('Ingredients already exists!')
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
