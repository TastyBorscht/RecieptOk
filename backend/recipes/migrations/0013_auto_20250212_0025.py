# Generated by Django 3.2.3 on 2025-02-12 00:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0012_auto_20250211_0153'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favorite',
            options={'default_related_name': 'favoriting', 'verbose_name': 'Избранное', 'verbose_name_plural': 'Избранное'},
        ),
        migrations.AlterModelOptions(
            name='shoppingcart',
            options={'default_related_name': 'shopping_cart', 'verbose_name': 'Список покупок', 'verbose_name_plural': 'Списки покупок'},
        ),
    ]
