# Generated by Django 4.2.3 on 2023-07-17 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0016_orcamento_img_orcamento_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='orcamento',
            name='img_contrato',
            field=models.URLField(blank=True, null=True),
        ),
    ]
