from django.contrib import admin
from .models import Professor, Comment

@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'department', 'created_at']
    search_fields = ['name', 'subject']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['professor', 'student_name', 'sentiment_label', 'created_at']
    list_filter = ['sentiment_label', 'created_at']
    search_fields = ['comment_text', 'student_name']