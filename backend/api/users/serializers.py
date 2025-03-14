from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from recipes.models import Recipe
from users.models import Subscription


User = get_user_model()


class UserProfileMeSerializer(UserSerializer):
    """Сериализатор для модели User."""

    avatar = Base64ImageField()
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        )

    def get_is_subscribed(self, object):
        """Проверяет, подписан ли текущий пользователь на автора аккаунта."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return object.author.filter(subscriber=request.user).exists()


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления аватара."""
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class SubscribeRecipeMiniSerializer(serializers.ModelSerializer):
    """Сериализатор предназначен для вывода рецептом в FollowSerializer."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image',)


class UserRecipieSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения полей ApiUser при создании рецепта."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscriber'
        )

    def get_is_subscribed(self, object):
        """Проверяет, подписан ли текущий пользователь на автора аккаунта."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return object.author.filter(subscriber=request.user).exists()


class SubscribeSerializer(serializers.ModelSerializer):
    """Serializer для модели Subscription."""
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes',
                  'recipes_count', 'avatar')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return (Subscription.objects.filter(
                subscriber=obj.subscriber,
                author=obj.author
            ).exists())
        return False

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj.author)
        if limit and limit.isdigit():
            recipes = recipes[:int(limit)]
        return SubscribeRecipeMiniSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def get_avatar(self, obj):
        if obj.author.avatar:
            return obj.author.avatar.url
        return None

    def validate(self, data):
        author = self.context.get('author')
        user = self.context.get('request').user
        request_method = self.context.get('request').method

        if request_method == 'POST':
            if Subscription.objects.filter(
                    author=author, subscriber=user).exists():
                raise ValidationError(
                    detail='Вы уже подписаны на этого пользователя!',
                    code=status.HTTP_400_BAD_REQUEST
                )
            if user == author:
                raise ValidationError(
                    detail='Невозможно подписаться на себя!',
                    code=status.HTTP_400_BAD_REQUEST
                )

        if request_method == 'DELETE':
            if not Subscription.objects.filter(
                    author=author, subscriber=user).exists():
                raise ValidationError(
                    detail='Вы не подписаны на этого пользователя!',
                    code=status.HTTP_400_BAD_REQUEST
                )

        return data
