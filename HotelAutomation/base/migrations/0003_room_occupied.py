# Generated by Django 3.2 on 2021-05-26 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_auto_20210526_1829'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='occupied',
            field=models.BooleanField(default=False),
        ),
    ]
