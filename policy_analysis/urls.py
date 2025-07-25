# policy_analysis/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.policy_home, name='policy_home'),
    path('upload/', views.upload_metadata, name='upload_metadata'),
    path('explore/', views.explore_metadata, name='explore_metadata'),
    path('explore/<str:policy_id>/', views.policy_detail, name='policy_detail'),
    path('graph/', views.policy_graph_view, name='policy_graph'),
    path('policy_graph/', views.policy_graph_home, name='policy_graph_home'),
]