# Generated by Django 2.2 on 2019-05-06 20:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_tasker_account', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='oauth',
            name='refresh_token',
        ),
    ]
