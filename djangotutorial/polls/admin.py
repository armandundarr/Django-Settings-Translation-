from django.contrib import admin

from .models import Choice, Question, Category, Comment, VoterIP

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["question_text", "category"]}),
        ("Date information", {"fields": ["pub_date", "end_date"], "classes": ["collapse"]}),
    ]
    inlines = [ChoiceInline, CommentInline]
    list_display = ["question_text", "category", "pub_date", "end_date", "was_published_recently", "is_active"]
    list_filter = ["pub_date", "category"]
    search_fields = ["question_text"]

admin.site.register(Question, QuestionAdmin)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(VoterIP)
