from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home_root"),      # /
    path("home/", views.home, name="home"),      # /home/
    path("consent/", views.consent, name="consent"),  # /consent/
    path("questionnaire/", views.questionnaire, name="questionnaire"),  # /questionnaire/
    path("questionnaire/results/<int:pk>/", views.questionnaire_results, name="questionnaire_results"),  # /questionnaire/results/
    path("daily-checkin/", views.daily_checkin, name="daily_checkin"),  # /daily-checkin/
    path("medication/", views.medication, name="medication"),  # /medication/
    path("history/", views.history, name="history"),  # /history/
    path("chat/", views.chat, name="chat"),  # /chat/
]