# Generated by Django 3.2 on 2021-05-29 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_alter_room_bed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='discount',
            name='id',
        ),
        migrations.AddField(
            model_name='discount',
            name='identification',
            field=models.CharField(max_length=16, null=True),
        ),
    ]
