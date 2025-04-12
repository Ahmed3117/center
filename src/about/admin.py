from django.contrib import admin
from .models import AboutPage, Feature, News
class NewsAdmin(admin.ModelAdmin):
    list_display = ('id', 'content_preview', 'is_active', 'from_date', 'to_date', 'created_at', 'updated_at')
    list_filter = ('is_active', 'from_date', 'to_date')
    search_fields = ('content',)
    readonly_fields = ('created_at', 'updated_at')

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'

admin.site.register(News, NewsAdmin)
# Register your models here.
admin.site.register(AboutPage)
admin.site.register(Feature)
