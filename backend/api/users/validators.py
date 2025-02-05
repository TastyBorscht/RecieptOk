# from rest_framework import serializers
#
#
# def validate_password(password, username, email, new_password):
#     """Проверяем, что пароль не схож с другими данными пользователя."""
#     if password.lower() == username.lower():
#         raise serializers.ValidationError(
#             "Пароль не должен совпадать с именем пользователя."
#         )
#     if password.lower() == new_password.lower():
#         raise serializers.ValidationError(
#             "Новый пароль не должен совпадать с адресом электронной почты."
#         )
#     if password.lower() == email.lower():
#         raise serializers.ValidationError(
#             "Пароль не должен совпадать с адресом электронной почты."
#         )
#     if username in password.lower() or email.split('@')[0] in password.lower():
#         raise serializers.ValidationError(
#             "Пароль не должен быть слишком схож с именем пользователя "
#             "или адресом электронной почты."
#         )
#
#     if len(password) < 8:
#         raise serializers.ValidationError(
#             "Пароль должен содержать не менее 8 символов."
#         )
