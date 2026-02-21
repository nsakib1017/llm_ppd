from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home_root"),      # /
    path("home/", views.home, name="home"),      # /home/
    path("consent/", views.consent, name="consent"),  # /consent/
    path("questionnaire/", views.questionnaire, name="questionnaire"),  # /questioneer/
    path("medication/", views.medication, name="medication"),  # /daily-meds/
    path("history/", views.history, name="history"),  # /mood-statistics/
    path("chat/", views.chat, name="chat"),  # /materna-ai/
]