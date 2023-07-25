# Generated by Django 4.2.3 on 2023-07-25 18:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0023_orcamento_confirmado'),
    ]

    operations = [
        migrations.CreateModel(
            name='Depositos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descricao', models.CharField(max_length=100)),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10)),
                ('orcamento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservas.orcamento')),
            ],
        ),
    ]
