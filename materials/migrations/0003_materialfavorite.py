from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [('materials','0002_material_is_hidden'), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(name='MaterialFavorite',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('material',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='favorites',to='materials.material')),
            ('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='material_favorites',to=settings.AUTH_USER_MODEL))],
            options={'verbose_name':'Избранное','verbose_name_plural':'Избранные материалы'}),
        migrations.AddConstraint(model_name='materialfavorite',constraint=models.UniqueConstraint(fields=('user','material'),name='unique_material_favorite')),
    ]
