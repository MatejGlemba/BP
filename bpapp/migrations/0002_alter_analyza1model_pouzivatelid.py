# Generated by Django 3.2.1 on 2021-05-14 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bpapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analyza1model',
            name='pouzivatelId',
            field=models.CharField(max_length=150),
        ),
    ]