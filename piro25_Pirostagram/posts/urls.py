from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.feed, name='feed'),
    path('create/', views.post_create, name='post_create'),
    path('update/<int:pk>/', views.post_update, name='post_update'),
    path('delete/<int:pk>/', views.post_delete, name='post_delete'),
    path('like/<int:pk>/', views.post_like, name='post_like'),
    path('<int:post_pk>/comments/create/', views.comment_create, name='comment_create'),
    path('comments/update/<int:pk>/', views.comment_update, name='comment_update'),
    path('comments/delete/<int:pk>/', views.comment_delete, name='comment_delete'),
    path('stories/create/', views.story_create, name='story_create'),
    path('stories/<int:pk>/', views.story_detail, name='story_detail'),
    path('stories/delete/<int:pk>/', views.story_delete, name='story_delete'),
    path('search/', views.post_search, name='post_search'),
]