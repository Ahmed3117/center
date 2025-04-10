from django.contrib import admin
from accounts.models import Year, TypeEducation

@admin.register(Year)
class YearAdmin(admin.ModelAdmin):
    list_display = ('name', 'created', 'updated')
    search_fields = ('name',)
    list_filter = ('created', 'updated')

@admin.register(TypeEducation)
class TypeEducationAdmin(admin.ModelAdmin):
    list_display = ('name', 'created', 'updated')
    search_fields = ('name',)
    list_filter = ('created', 'updated')
