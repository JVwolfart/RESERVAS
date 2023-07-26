from django.contrib import admin
from .models import Cliente, Empreendimento, Acomodacao, TipoObservacao, Observacao, DadosCliente, Orcamento, Periodo, Horario, ObsOrcamento, Contrato, Lancamentos
# Register your models here.

class AdmCliente(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'obs',)
    list_per_page = 10
    search_fields = ['nome', "telefone"]
    list_filter = ('obs',)

class AdmEmpreendimento(admin.ModelAdmin):
    list_display = ("nome",)
    list_per_page = 10
    search_fields = ['nome',]
    list_filter = ('nome',)

class AdmAcomodacao(admin.ModelAdmin):
    list_display = ("nome", "empreendimento", "tipo", "quartos", "limite_ideal", "limite_adicional",)
    list_per_page = 10
    search_fields = ['nome', "empreendimento", "tipo", "quartos"]
    list_filter = ('nome', "empreendimento", "tipo", "quartos", "limite_ideal", "limite_adicional",)

class AdmTipoObservacao(admin.ModelAdmin):
    list_display = ("tipo",)
    list_per_page = 10
    search_fields = ["tipo"]
    list_filter = ("tipo",)


class AdmObservacao(admin.ModelAdmin):
    list_display = ("tipo", "identificacao",)
    list_per_page = 10
    search_fields = ["tipo", "identificacao"]
    list_filter = ("tipo", "identificacao")

class AdmDadosCliente(admin.ModelAdmin):
    list_display = ("cliente", "nome_completo", "cpf",)
    list_per_page = 10
    search_fields = ["nome_completo", "cpf",]
    list_filter = ("cidade", "estado", "cep")

class AdmOrcamento(admin.ModelAdmin):
    list_display = ("cliente", "acomodacao", "data_entrada", "data_saida", "n_dias")
    list_per_page = 10
    search_fields = ["cliente", "acomodacao", "data_entrada", "data_saida"]
    list_filter = ("cliente", "acomodacao", "data_entrada", "data_saida")

class AdmPeriodo(admin.ModelAdmin):
    list_display = ("periodo",)
    list_per_page = 10
    search_fields = ["periodo"]
    list_filter = ("periodo",)

class AdmHorario(admin.ModelAdmin):
    list_display = ("hora", "checkin")
    list_per_page = 10
    search_fields = ["hora"]
    list_filter = ("hora", "checkin")

class AdmObsOrcamento(admin.ModelAdmin):
    list_display = ("orcamento",)
    list_per_page = 10
    search_fields = ["orcamento"]
    list_filter = ("orcamento",)

class AdmContrato(admin.ModelAdmin):
    list_display = ("orcamento",)
    list_per_page = 10
    search_fields = ["orcamento"]
    list_filter = ("orcamento",)

class AdmLancamento(admin.ModelAdmin):
    list_display = ("orcamento", "descricao", "data_lancamento", "valor", "tipo")
    list_per_page = 10
    search_fields = ["orcamento", "descricao", "data_lancamento", "tipo"]
    list_filter = ("orcamento", "tipo",)

admin.site.register(Cliente, AdmCliente)
admin.site.register(Empreendimento, AdmEmpreendimento)
admin.site.register(Acomodacao, AdmAcomodacao)
admin.site.register(Observacao, AdmObservacao)
admin.site.register(TipoObservacao, AdmTipoObservacao)
admin.site.register(DadosCliente, AdmDadosCliente)
admin.site.register(Orcamento, AdmOrcamento)
admin.site.register(Periodo, AdmPeriodo)
admin.site.register(Horario, AdmHorario)
admin.site.register(ObsOrcamento, AdmObsOrcamento)
admin.site.register(Contrato, AdmContrato)
admin.site.register(Lancamentos, AdmLancamento)