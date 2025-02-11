import json
from django.core.management.base import BaseCommand
from recipes.models import Tag, Ingredient


class Inrgredient:
    pass


#  не смотря на bulk_create на удаленном сервере эта команда выбрасывает ошибку
#  django.***.utils.DataError: value too long for type character varying(50)
# 2025/02/11 02:26:27 Process exited with status 1
class Command(BaseCommand):
    help = 'Load data from recipe.json and tags.json'

    def handle(self, *args, **kwargs):
        with open('data/tags.json') as f:
            tags_data = json.load(f)
            tags_to_create = [
                Tag(name=tag['name'], slug=tag['slug'])
                for tag in tags_data
            ]

            Tag.objects.bulk_create(tags_to_create, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS('Successfully loaded tags'))

        with open('data/ingredients.json') as f:
            ingredients_data = json.load(f)
            ingredients_to_create = [
                Ingredient(name=ingredient['name'],
                           measurement_unit=ingredient['measurement_unit'])
                for ingredient in ingredients_data
            ]
            Ingredient.objects.bulk_create(ingredients_to_create, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS('Successfully loaded ingredients'))
