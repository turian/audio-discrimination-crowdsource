# Generated by Django 4.1 on 2022-09-12 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0003_rename_reference_task_reference_url_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='transform_url',
            field=models.URLField(default='www.example.com'),
            preserve_default=False,
        ),
    ]
