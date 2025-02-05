from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField

from users.utils import validate_username
from users.constants import (
    LENGTH_CHARFIELDS, LENGTH_EMAIL, UNIQUE_EMAIL, UNIQUE_USERNAME
)


User = get_user_model()


class UsersListSerializer(serializers.ModelSerializer):
    """Сериализатор для выдачи всех пользователей всем
    по api/users.
    """
    avatar = Base64ImageField()
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed', 'avatar'
        )
        read_only_fields = fields


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления нового пользователя
    по POST-запросу на api/users .
    """
    username = serializers.CharField(
        max_length=LENGTH_CHARFIELDS,
        validators=[validate_username]
    )
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(max_length=LENGTH_EMAIL)
    class Meta:
        model = User
        fields = (
            'email', 'username',
            'first_name', 'last_name',
            'password',
        )

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        user = User.objects.filter(
            username=username,
            email=email,
        )
        if data.get('username') == 'me':
            raise serializers.ValidationError(
                'Использовать имя me запрещено'
            )
        if user.exists():
            return data
        if User.objects.filter(username=username).exists():
            raise ValidationError(UNIQUE_USERNAME)
        if User.objects.filter(email=email).exists():
            raise ValidationError(UNIQUE_EMAIL)
        return data

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class PasswordChangeSerializer(serializers.ModelSerializer):
    password =