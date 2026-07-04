from django.urls import path
from . import views

urlpatterns = [
    path('devtools/', views.develop_list, name='develop_list'),
    path('devtools/register/', views.develop_register, name='develop_register'),
    path('devtools/<int:id>/', views.develop_detail, name='develop_detail'),
    path('devtools/<int:id>/modify/', views.develop_modify, name='develop_modify'),
    path('devtools/<int:id>/delete/', views.develop_delete, name='develop_delete'),
    path('ideas/', views.idea_list, name='idea_list'),
    path('ideas/register/', views.idea_register, name='idea_register'),
    path('ideas/<int:id>/', views.idea_detail, name='idea_detail'),
    path('ideas/<int:id>/modify/', views.idea_modify, name='idea_modify'),
    path('ideas/<int:id>/delete/', views.idea_delete, name='idea_delete'),
    path('ideas/<int:id>/interest/up/', views.idea_interest_up, name='idea_interest_up'),
    path('ideas/<int:id>/interest/down/', views.idea_interest_down, name='idea_interest_down'),
    path('ideas/<int:id>/star/', views.idea_star, name='idea_star'),
]