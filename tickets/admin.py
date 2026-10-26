from django.contrib import admin

from .models import Subject, Ticket, TicketStatus


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ["subject", "number", "short_text"]
    list_filter = ["subject"]
    search_fields = ["text"]

    @admin.display(description="Текст вопроса")
    def short_text(self, obj):
        return obj.text[:80]


@admin.register(TicketStatus)
class TicketStatusAdmin(admin.ModelAdmin):
    list_display = ["user", "ticket", "status", "updated_at"]
    list_filter = ["status", "ticket__subject"]
