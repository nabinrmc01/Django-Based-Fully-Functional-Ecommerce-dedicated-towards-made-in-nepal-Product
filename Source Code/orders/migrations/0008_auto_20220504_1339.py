# Generated by Django 3.1 on 2022-05-04 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_auto_20220504_1047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Canclelld', 'Cancelled'), ('Completed', 'Completed'), ('Accepted', 'Accepted'), ('New', 'New')], default='New', max_length=10),
        ),
    ]
