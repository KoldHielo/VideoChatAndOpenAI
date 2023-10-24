from django.shortcuts import render
from django.conf import settings

# Create your views here.
def home(request):
    if request.META['HTTP_HOST'] == '16.170.98.35':
        settings.DEBUG = True
    return render(request, 'home.html')
