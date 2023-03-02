# Generated by Django 4.1.1 on 2023-02-25 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("polls", "0006_experimenttype_experimenttypetaskpresentation_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="experimenttypetaskpresentation",
            name="experiment_type",
        ),
        migrations.AlterField(
            model_name="experimenttype",
            name="type",
            field=models.CharField(max_length=100),
        ),
        migrations.DeleteModel(
            name="ExperimentTypeAnnotation",
        ),
        migrations.DeleteModel(
            name="ExperimentTypeTaskPresentation",
        ),
    ]