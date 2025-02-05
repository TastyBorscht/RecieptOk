from django.urls import include, path
from rest_framework import routers

from .views import UserViewSet, UpdatePasswordView

# from .views import RegistrationAuthViewSet, UserViewSet


user_router = routers.DefaultRouter()
# user_router.register('list', UsersListForAll)
user_router.register('', UserViewSet)
# user_router.register(
#     'auth', RegistrationAuthViewSet, basename='registration_for_user'
# )
urlpatterns = [
    path('set_password/', UpdatePasswordView.as_view(), name='set_password'),
    path('me/', UserViewSet.as_view({'get': 'retrieve'}), name='user-me'),
    path('', include(user_router.urls)),
]
