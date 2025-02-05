from django.urls import include, path
from rest_framework import routers

from .views import UserViewSet
# from .views import RegistrationAuthViewSet, UserViewSet


user_router = routers.DefaultRouter()
# user_router.register('list', UsersListForAll)
user_router.register('', UserViewSet)
# user_router.register(
#     'auth', RegistrationAuthViewSet, basename='registration_for_user'
# )
urlpatterns = [
    path('', include(user_router.urls)),
    path('users/me/', UserViewSet.as_view({'get': 'retrieve'}), name='user-me'),
    # path('', UsersListForAll.as_view()),
]
