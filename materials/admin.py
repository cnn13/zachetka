from django.contrib import admin
from .models import Material, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ["title", "subject", "teacher", "course", "year", "is_hidden", "created_at"]
    list_display_links = ["title"]
    list_editable = ["is_hidden"]
    list_filter = ["is_hidden", "subject", "course", "year"]
    search_fields = ["title", "teacher"]
    filter_horizontal = ["tags"]
    fields = ["title", "subject", "teacher", "course", "year", "file", "tags", "is_hidden"]
    actions = ["hide_selected", "show_selected"]

    @admin.action(description="Скрыть выбранные материалы")
    def hide_selected(self, request, queryset):
        self.message_user(request, f"Скрыто материалов: {queryset.update(is_hidden=True)}")

    @admin.action(description="Показать выбранные материалы")
    def show_selected(self, request, queryset):
        self.message_user(request, f"Открыто материалов: {queryset.update(is_hidden=False)}")
