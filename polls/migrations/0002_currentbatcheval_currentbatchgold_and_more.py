# Generated by Django 4.1 on 2022-09-05 14:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("polls", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CurrentBatchEval",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "current_batch_eval",
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to={"is_gold": False},
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="current_batch_eval",
                        to="polls.batch",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="CurrentBatchGold",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "current_batch_gold",
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to={"is_gold": True},
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="current_batch_gold",
                        to="polls.batch",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.DeleteModel(
            name="CurrentBatch",
        ),
    ]
