# Generated by Django 4.1.1 on 2023-03-04 17:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("polls", "0014_alter_experimenttypeannotation_experiment_type_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="experimenttypeannotation",
            name="experiment_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="polls.experimenttype"
            ),
        ),
    ]
