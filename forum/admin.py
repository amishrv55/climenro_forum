from django.contrib import admin
from .models import Subreddit, Post, Comment, Vote, CommentVote

# Register your models here.

admin.site.register(Subreddit)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Vote)
admin.site.register(CommentVote)
