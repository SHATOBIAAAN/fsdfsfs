# Generated by Django 5.1.7 on 2025-04-01 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_profile_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='crypto_token',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Токен для криптовалюты'),
        ),
    ]
