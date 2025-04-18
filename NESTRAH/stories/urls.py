from django.urls import path
from . import views

urlpatterns = [
    path('', views.story_list, name='story_list'),
    path('new/', views.new_story, name='new_story'),
    path('category/new/', views.create_category, name='create_category'),
    path('clear-notification/', views.clear_notification, name='clear_notification'),
    path('ajax/like/<int:story_id>/', views.ajax_like_story, name='ajax_like_story'),
    path('ajax/dislike/<int:story_id>/', views.ajax_dislike_story, name='ajax_dislike_story'),
    path('<int:story_id>/comments/', views.story_comments, name='story_comments'),
    path('<int:story_id>/add_comment/', views.add_comment, name='add_comment'),
    path('<int:story_id>/media/', views.story_media, name='story_media'),
    path('<int:story_id>/like/', views.like_story, name='like_story'),
    path('<int:story_id>/dislike/', views.dislike_story, name='dislike_story'),
    path('<int:story_id>/', views.story_detail, name='story_detail'),
]