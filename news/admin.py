# Register your models here.
from django.contrib import admin
from .models import NewsArticle
from .models import Announcement

admin.site.register(Announcement)
admin.site.register(NewsArticle)
