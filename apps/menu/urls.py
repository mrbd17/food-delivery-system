from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("api/menu/", views.GetMenuView.as_view(), name="menu_api"),
    path("menu/", views.menu, name="menu"),
    path("api/health/", views.health_check, name="health")
]
