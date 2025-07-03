from django.urls import path
from . import views

urlpatterns = [
    path('', views.news_feed, name='news_feed'),
    path('<int:article_id>/', views.news_detail, name='news_detail'),
]
