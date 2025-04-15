from django.contrib import admin
from django.utils.html import format_html
from .models import AboutPage, Feature, News

@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('title', 'image_preview', 'created_at', 'updated_at')
    search_fields = ('title', 'description')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    list_per_page = 25

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 100px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image Preview'

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('short_content', 'image_preview', 'is_active', 'from_date', 'to_date', 'created_at', 'updated_at')
    list_filter = ('is_active', 'from_date', 'to_date', 'created_at')
    search_fields = ('content',)
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    list_editable = ('is_active',)
    date_hierarchy = 'created_at'
    list_per_page = 25

    def short_content(self, obj):
        return obj.content[:75] + '...' if len(obj.content) > 75 else obj.content
    short_content.short_description = 'Content Snippet'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 100px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image Preview'