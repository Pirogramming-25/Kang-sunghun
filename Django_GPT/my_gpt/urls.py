from django.urls import path

from . import views

app_name = "my_gpt"

urlpatterns = [
    path("sentiment/", views.sentiment_page, name="sentiment"),
    path("sentiment/run/", views.sentiment_run, name="sentiment_run"),
    path("summarize/", views.summarize_page, name="summarize"),
    path("summarize/run/", views.summarize_run, name="summarize_run"),
    path("moderate/", views.moderate_page, name="moderate"),
    path("moderate/run/", views.moderate_run, name="moderate_run"),
    path("combo/", views.combo_page, name="combo"),
    path("combo/run/", views.combo_run, name="combo_run"),
]