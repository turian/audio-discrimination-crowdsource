# Generated by Django 4.1.1 on 2023-03-04 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("polls", "0013_alter_annotatorprofile_hourly_rate"),
    ]

    operations = [
        migrations.AlterField(
            model_name="experimenttype",
            name="type",
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
