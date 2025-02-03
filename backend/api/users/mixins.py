from rest_framework import viewsets
from rest_framework.mixins import CreateModelMixin


class RegistrationAuthMixin(CreateModelMixin, viewsets.GenericViewSet):
    pass
