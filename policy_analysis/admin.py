# Register your models here.

from django.contrib import admin
from .models import Policy, PolicySection

@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ('title', 'year', 'country', 'document_type', 'num_sections', 'is_fundamental')
    search_fields = ('title', 'country', 'document_type')
    list_filter = ('country', 'document_type', 'year', 'is_fundamental')
    ordering = ('-year',)

@admin.register(PolicySection)
class PolicySectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'policy', 'sector')
    search_fields = ('title', 'policy__title', 'sector')
    list_filter = ('sector', 'policy__title')
