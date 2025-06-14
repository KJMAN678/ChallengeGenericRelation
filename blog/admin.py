from django.contrib import admin
from .models import Blog, Comment, Favorite


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'blog', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at', 'blog']
    search_fields = ['content', 'blog__title']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'content_type', 'object_id', 'created_at']
    list_filter = ['content_type', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
