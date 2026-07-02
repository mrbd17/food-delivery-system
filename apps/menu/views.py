from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import MenuItem
from .serializers import GetMenuSerializer

# Create your views here.


def home(request):
    return render(request, "pages/home.html")


def menu(request):
    return render(request, "pages/menu.html")


def health_check(request):
    return HttpResponse("ok")


class GetMenuView(generics.ListAPIView):
    serializer_class = GetMenuSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return MenuItem.objects.filter(is_menu=True)
