from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("tickets", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="TicketProgress",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("unknown", "Не знаю"), ("bad", "Плохо"), ("learned", "Выучил")], default="unknown", max_length=10, verbose_name="Оценка")),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("ticket", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="progress", to="tickets.ticket")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="ticket_progress", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "Прогресс билета", "verbose_name_plural": "Прогресс билетов"},
        ),
        migrations.AddConstraint(
            model_name="ticketprogress",
            constraint=models.UniqueConstraint(fields=("user", "ticket"), name="unique_ticket_progress_per_user"),
        ),
    ]
