# Generated by Django 4.1.1 on 2022-09-26 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("polls", "0004_task_transform_url"),
    ]

    operations = [
        migrations.AlterField(
            model_name="batch",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
