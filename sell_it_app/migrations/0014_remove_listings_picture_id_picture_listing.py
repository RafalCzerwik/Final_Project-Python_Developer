# Generated by Django 4.2.11 on 2024-03-13 13:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sell_it_app', '0013_remove_address_listings_remove_picture_listing_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listings',
            name='picture_id',
        ),
        migrations.AddField(
            model_name='picture',
            name='listing',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='sell_it_app.listings'),
            preserve_default=False,
        ),
    ]