from django.contrib import admin

from .models import Material, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ["title", "subject", "teacher", "course", "year", "created_at"]
    list_filter = ["subject", "course", "year"]
    search_fields = ["title", "teacher"]
    filter_horizontal = ["tags"]
