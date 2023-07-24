from django.db import models
from django.utils import timezone

class Cliente(models.Model):
    nome = models.CharField(max_length=30)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    obs = models.CharField(max_length=100)
    dados_adicionais = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nome} - {self.telefone} - {self.obs}"
    
class Empreendimento(models.Model):
    nome = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.nome}"
    
class TipoObservacao(models.Model):
    tipo = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.tipo}'
    

class Observacao(models.Model):
    identificacao = models.CharField(max_length=50)
    tipo = models.ForeignKey(TipoObservacao, on_delete=models.CASCADE)
    descricao = models.TextField()

    def __str__(self):
        return f"{self.identificacao}"

class Acomodacao(models.Model):
    nome = models.CharField(max_length=50)
    empreendimento = models.ForeignKey(Empreendimento, on_delete=models.DO_NOTHING)
    tipo = models.CharField(max_length=15)
    quartos = models.IntegerField(blank=True, null=True)
    valor_base = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    descricao = models.TextField()
    limite_ideal = models.IntegerField(blank=True, null=True)
    limite_adicional = models.IntegerField(blank=True, null=True)
    aceita_pet = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nome}"    


class DadosCliente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    nome_completo = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14)
    rua = models.CharField(max_length=100)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    cep = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.cliente} -> {self.nome_completo}"


class Orcamento(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    acomodacao = models.ForeignKey(Acomodacao, on_delete=models.CASCADE)
    data_entrada = models.DateField()
    dia_entrada = models.CharField(max_length=20)
    checkin = models.CharField(max_length=100)
    data_saida = models.DateField()
    dia_saida = models.CharField(max_length=20)
    checkout = models.CharField(max_length=100)
    data_orcamento = models.DateField(default=timezone.now)
    n_ocupantes = models.IntegerField(default=0)
    obs_n_ocupantes = models.CharField(max_length=150, blank=True, null=True)
    n_dias = models.IntegerField()
    valor_diaria = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    taxa_limpeza = models.DecimalField(default=0, max_digits=6, decimal_places=2)
    descontos = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    acrescimos = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    valor_pacote = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    dias_pacote = models.IntegerField(default=0)
    diaria_cheia = models.BooleanField(default=False)
    periodo = models.CharField(max_length=100)
    #aberto = models.BooleanField()
    #contrato_gerado = models.BooleanField(default=False)
    #finalizado = models.BooleanField(default=False)
    modificado = models.BooleanField(default=False)
    obs_modificacao = models.CharField(max_length=200, blank=True, null=True)
    eliminado = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=(("em digitação", "em digitação"), ("digitação concluída", "digitação concluída"), ("orçamento gerado", "orçamento gerado"), ("contrato gerado", "contrato gerado"),))
    total_valor_reserva = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    

    def __str__(self):
        return f"{self.acomodacao} - {self.cliente} - {self.data_entrada}"
    
class Periodo(models.Model):
    periodo = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.periodo}"
    
class Horario(models.Model):
    hora = models.CharField(max_length=100)
    checkin = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.hora}"
    
class ObsOrcamento(models.Model):
    orcamento = models.ForeignKey(Orcamento, on_delete=models.CASCADE)
    obs = models.TextField()
    condicoes_pagamento = models.TextField()
    informacoes_adicionais = models.TextField()

    def __str__(self):
        return f"{self.orcamento}"
    
class Contrato(models.Model):
    orcamento = models.ForeignKey(Orcamento, on_delete=models.CASCADE)
    data_contrato = models.DateField(default=timezone.now)
    aviso_contrato = models.TextField(blank=True, null=True)
    info_adic_contrato = models.TextField(blank=True, null=True)
    conta_deposito = models.TextField(blank=True, null=True)
    cond_pag_contrato = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Contrato {self.orcamento.id} de {self.orcamento.cliente} {self.orcamento.acomodacao}"