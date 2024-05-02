# Generated by Django 3.2.25 on 2024-05-02 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_product_stripe_price_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='cancellation_policy',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='duration',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='recurrence',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
