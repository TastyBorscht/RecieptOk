import json
from django.core.management.base import BaseCommand

from api.users.serializers import User
from recipes.models import Tag, Ingredient


class Command(BaseCommand):
    help = 'Load data from recipe.json and tags.json'

    def handle(self, *args, **kwargs):
        # Загрузка тегов
        with open('data/tags.json') as f:
            tags_data = json.load(f)
            for tag in tags_data:
                Tag.objects.get_or_create(
                    name=tag['name'],
                    slug=tag['slug']
                )
        self.stdout.write(self.style.SUCCESS('Successfully loaded tags'))

        with open('data/ingredients.json') as f:
            recipes_data = json.load(f)
            for ingredient in recipes_data:
                Ingredient.objects.get_or_create(
                    name=ingredient['name'],
                    measurement_unit=ingredient['measurement_unit']
                )
        self.stdout.write(self.style.SUCCESS(
            'Successfully loaded ingredients'))

        with open('data/users.json') as f:
            users_data = json.load(f)
            for user_ in users_data:
                User.objects.get_or_create(
                    username=user_['username'],
                    email=user_['email'],
                    first_name=user_['first_name'],
                    last_name=user_['last_name'],
                    role=user_['role'],
                    password=user_['password'],
                )
        self.stdout.write(self.style.SUCCESS('Successfully loaded users'))
