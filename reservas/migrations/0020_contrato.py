# Generated by Django 4.2.3 on 2023-07-19 18:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0019_remove_orcamento_img_contrato_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contrato',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aviso_contrato', models.TextField(blank=True, null=True)),
                ('info_adic_contrato', models.TextField(blank=True, null=True)),
                ('conta_deposito', models.TextField(blank=True, null=True)),
                ('cond_pag_contrato', models.TextField(blank=True, null=True)),
                ('orcamento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservas.orcamento')),
            ],
        ),
    ]
