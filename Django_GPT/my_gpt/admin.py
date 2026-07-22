from django.contrib import admin

from .models import InferenceHistory


@admin.register(InferenceHistory)
class InferenceHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "task", "created_at")
    list_filter = ("task", "user")
    search_fields = ("input_text", "output_text")