from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home_root"),      # /
    path("home/", views.home, name="home"),      # /home/
    path("consent/", views.consent, name="consent"),  # /consent/
]