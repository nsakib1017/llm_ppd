from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home_root"),      # /
    path("home/", views.home, name="home"),      # /home/
    path("consent/", views.consent, name="consent"),  # /consent/
    path("questioneer/", views.questioneer, name="questioneer"),  # /questioneer/
    path("daily-meds/", views.daily_meds, name="daily_meds"),  # /daily-meds/
    path("mood-statistics/", views.mood_statistics, name="mood_statistics"),  # /mood-statistics/
    path("materna-ai/", views.materna_ai, name="materna_ai"),  # /materna-ai/
]