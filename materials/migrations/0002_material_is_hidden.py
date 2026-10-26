from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("materials", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="material",
            name="is_hidden",
            field=models.BooleanField(default=False, db_index=True, verbose_name="Скрыт"),
        ),
    ]
