# Generated by Django 4.2.3 on 2023-07-13 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0010_obsorcamento'),
    ]

    operations = [
        migrations.AddField(
            model_name='orcamento',
            name='contrato_gerado',
            field=models.BooleanField(default=False),
        ),
    ]
