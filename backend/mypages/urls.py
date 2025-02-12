from django.urls import path

from mypages import views

app_name = 'mypages'

urlpatterns = [
    path('', views.About.as_view(), name='about'),
]
