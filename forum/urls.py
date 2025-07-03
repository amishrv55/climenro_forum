from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('r/<str:subreddit_name>/', views.subreddit, name='subreddit'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('create_post/', views.create_post, name='create_post'),
    path('vote/<int:post_id>/<str:direction>/', views.vote_post, name='vote_post'),
    path('comment/add/<int:post_id>/', views.add_comment, name='add_comment'),
    path('post/edit/<int:post_id>/', views.edit_post, name='edit_post'),
    path('comment/edit/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('post/delete/<int:post_id>/', views.delete_post, name='delete_post'),
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('create_subreddit/', views.create_subreddit, name='create_subreddit'),
    path('user/<str:username>/', views.user_profile, name='user_profile'),
    path('search/', views.search, name='search'),
    path('register/', views.register, name='register'),
    path('comment/vote/<int:comment_id>/<str:direction>/', views.vote_comment, name='vote_comment'),

]
