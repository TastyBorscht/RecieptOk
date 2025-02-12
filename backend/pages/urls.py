from django.urls import path

from pages import views

app_name = 'pages'

urlpatterns = [
    path('', views.About.as_view(), name='about'),
]
