from django.http import JsonResponse
from django.shortcuts import render
from django.templatetags.static import static
from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import MenuItem, Restaurant
from .serializers import GetMenuSerializer

# Create your views here.


def home(request):
    return render(request, "pages/home.html")


def menu(request):
    return render(request, "pages/menu.html")


class GetMenuView(generics.ListAPIView):
    serializer_class = GetMenuSerializer

    def get_queryset(self):
        return MenuItem.objects.filter(is_menu=True)
