from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [migrations.CreateModel(name='PomodoroSession',fields=[
        ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
        ('subject_name',models.CharField(max_length=200,verbose_name='Предмет')),
        ('duration_minutes',models.PositiveSmallIntegerField(default=25,verbose_name='Минут')),
        ('client_token',models.CharField(max_length=100,verbose_name='Идентификатор цикла')),
        ('created_at',models.DateTimeField(auto_now_add=True,verbose_name='Завершено')),
        ('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='pomodoro_sessions',to=settings.AUTH_USER_MODEL))],
        options={'ordering':['-created_at'],'verbose_name':'Помодоро-сессия','verbose_name_plural':'Помодоро-сессии'}),
        migrations.AddConstraint(model_name='pomodorosession',constraint=models.UniqueConstraint(fields=('user','client_token'),name='unique_pomodoro_session_per_user'))]
