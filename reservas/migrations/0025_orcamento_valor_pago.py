# Generated by Django 4.2.3 on 2023-07-25 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0024_depositos'),
    ]

    operations = [
        migrations.AddField(
            model_name='orcamento',
            name='valor_pago',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7),
        ),
    ]
