# Generated by Django 3.2.3 on 2025-02-10 16:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_auto_20250208_2116'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tag',
            options={},
        ),
        migrations.RemoveConstraint(
            model_name='tag',
            name='unique_tags',
        ),
    ]
