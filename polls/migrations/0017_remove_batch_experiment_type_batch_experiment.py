# Generated by Django 4.1.1 on 2023-03-06 18:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("polls", "0016_alter_experimenttypetaskpresentation_experiment_type"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="batch",
            name="experiment_type",
        ),
        migrations.AddField(
            model_name="batch",
            name="experiment",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="batches",
                to="polls.experiment",
            ),
        ),
    ]