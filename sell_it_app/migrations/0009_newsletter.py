# Generated by Django 4.2.11 on 2024-03-11 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sell_it_app', '0008_alter_messages_date_sent'),
    ]

    operations = [
        migrations.CreateModel(
            name='Newsletter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
    ]