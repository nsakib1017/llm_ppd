from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home_root"),      # /
    path("home/", views.home, name="home"),      # /home/
    path("consent/", views.consent, name="consent"),  # /consent/
    path("questionnaire/", views.questionnaire, name="questionnaire"),  # /questionnaire/
    path("history/", views.history, name="history"),  # /history/
    path("chat/", views.chat, name="chat"),  # /chat/
    path("medication/", views.medication, name="medication"),  # /medication/
]