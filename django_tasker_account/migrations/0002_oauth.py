# Generated by Django 2.2 on 2019-05-03 22:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('django_tasker_account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Oauth',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('oauth_id', models.CharField(max_length=255, verbose_name='Oauth ID')),
                ('server', models.IntegerField(choices=[(1, 'Google'), (2, 'Yandex'), (3, 'Mail.ru'), (4, 'VK.com'), (5, 'Facebook')], verbose_name='Server')),
                ('access_token', models.CharField(max_length=255, verbose_name='Access token')),
                ('refresh_token', models.CharField(max_length=255, verbose_name='Refresh token')),
                ('expires_in', models.DateTimeField(verbose_name='Expires date')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name_plural': 'Oauth',
                'unique_together': {('oauth_id', 'server')},
            },
        ),
    ]