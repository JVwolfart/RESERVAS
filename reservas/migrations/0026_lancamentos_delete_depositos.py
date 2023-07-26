# Generated by Django 4.2.3 on 2023-07-26 17:07

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0025_orcamento_valor_pago'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lancamentos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descricao', models.CharField(max_length=100)),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10)),
                ('data_lancamento', models.DateField(default=django.utils.timezone.now)),
                ('tipo_lancamento', models.CharField(choices=[('pagamento', 'pagamento'), ('acréscimo', 'acréscimo')], max_length=10)),
                ('orcamento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservas.orcamento')),
            ],
        ),
        migrations.DeleteModel(
            name='Depositos',
        ),
    ]
