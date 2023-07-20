from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('clientes/', views.cadastrar_cliente, name="clientes"),
    path('manut_cliente', views.manut_clientes, name="manut_cliente"),
    path('alterar_cliente/<int:id>', views.alterar_cliente, name="alterar_cliente"),
    path('lista_empreendimentos/', views.lista_empreendimentos, name="lista_empreendimentos"),
    path("dados_cliente/<int:id>", views.dados_cliente, name="dados_cliente"),
    path("alterar_dados_cliente/<int:id>", views.alterar_dados_cliente, name="alterar_dados_cliente"),
    path("gerar_orcamento/<int:id>", views.gerar_orcamento, name="gerar_orcamento"),
    path("lista_orcamentos_digitados/", views.lista_orcamentos_digitados, name="lista_orcamentos_digitados"),
    path("finalizar_digitacao/<int:id>", views.finalizar_digitacao, name="finalizar_digitacao"),
    path("lista_gera_pdf_orcamento/", views.lista_gera_pdf_orcamento, name="lista_gera_pdf_orcamento"),
    path("gera_pdf_orc/<int:id>", views.gera_pdf_orc, name="gera_pdf_orc"),
    path('lista_orçamentos_concluidos/', views.lista_orçamentos_concluidos, name="lista_orçamentos_concluidos"),
    path('vizualizar_pdf/<int:id>', views.vizualizar_pdf, name="vizualizar_pdf"),
    path('gerar_contrato/<int:id>', views.gerar_contrato, name="gerar_contrato"),
]