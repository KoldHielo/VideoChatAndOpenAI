from django.urls import path, include
from . import views
import debug_toolbar

urlpatterns = [
    path('VideoChat/', views.home, name='home'),
    path('__debug__/', include(debug_toolbar.urls)),
]
