# Generated by Django 3.2 on 2021-05-28 18:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_auto_20210528_2246'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catering',
            name='token',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.guest'),
        ),
        migrations.AlterField(
            model_name='room',
            name='book_when',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='room',
            name='occupied_when',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='room',
            name='token',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.guest'),
        ),
    ]
