from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, NotFound

from users.utils import validate_username
from users.constants import (
    LENGTH_CHARFIELDS, LENGTH_EMAIL, UNIQUE_EMAIL, UNIQUE_USERNAME
)


User = get_user_model()


class UsersListSerializer(serializers.ModelSerializer):
    """Сериализатор для выдачи всех пользователей всем
    по api/users.
    """
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed', 'avatar'
        )
        read_only_fields = fields


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=LENGTH_CHARFIELDS,
        validators=[validate_username]
    )
    email = serializers.EmailField(max_length=LENGTH_EMAIL)

    class Meta:
        model = User
        fields = (
            'username', 'email',
            'first_name', 'last_name',
            'bio', 'role'
        )
        read_only_fields = ('confirmation_code',)

    def validate_role(self, value):
        creator = self.context['creator']
        if not creator.is_anonymous:
            if creator.user_is_admin:
                return value
        raise serializers.ValidationError('У вас нет прав изменять вашу роль')

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        user = User.objects.filter(
            username=username,
            email=email,
        )
        if user.exists():
            return data
        if User.objects.filter(username=username).exists():
            raise ValidationError(UNIQUE_USERNAME)
        if User.objects.filter(email=email).exists():
            raise ValidationError(UNIQUE_EMAIL)
        return data


class UserTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=LENGTH_CHARFIELDS,
    )
    confirmation_code = serializers.IntegerField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')

    def validate(self, data):
        user = User.objects.filter(username=data['username'])
        if not user.exists():
            raise NotFound('Такого пользователя не существует')
        elif user.get().confirmation_code == data['confirmation_code']:
            return data
        raise ValidationError('Неверный confirmation_code')
