# Generated by Django 3.1 on 2022-04-17 09:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='is_avaliable',
            new_name='is_available',
        ),
    ]