# Generated by Django 3.2.1 on 2021-05-16 01:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bpapp', '0003_alter_analyza1model_pouzivatelid'),
    ]

    operations = [
        migrations.CreateModel(
            name='Images',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nazov', models.TextField()),
                ('url', models.ImageField(upload_to='graphs/')),
            ],
        ),
        migrations.DeleteModel(
            name='Katalog',
        ),
    ]
