from django.urls import path
from . import views

urlpatterns = [
    path('VideoChat/', views.home, name='home'),
]
