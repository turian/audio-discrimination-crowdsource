# Generated by Django 4.1 on 2022-09-12 11:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0002_currentbatcheval_currentbatchgold_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='reference',
            new_name='reference_url',
        ),
        migrations.RenameField(
            model_name='task',
            old_name='transform',
            new_name='transform_metadata',
        ),
    ]