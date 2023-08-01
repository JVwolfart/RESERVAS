from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cliente, Empreendimento, DadosCliente, Acomodacao, Periodo, Horario, Orcamento, ObsOrcamento, Observacao, Contrato, TipoObservacao, Lancamentos
from django.db.models import Q
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from django.contrib.auth.models import User
#from reservas.utils.gera_pdf_orcamento import gera_pdf_orcamento

import io
from django.http import FileResponse
from reportlab.pdfgen import canvas

from reportlab.lib.pagesizes import A4
#from reportlab.lib      import colors
from reportlab.platypus import Paragraph
from pathlib import Path




@login_required(login_url="login")
def index(request):
    return render(request, "index.html")

@login_required(login_url="login")
def cadastrar_cliente(request):
    if request.method != 'POST':
        return render(request, "form_cliente.html")
    else:
        nome = request.POST.get('nome').strip().title()
        celular = request.POST.get('celular')
        obs = request.POST.get("obs").strip().title()
        if celular == "":
            celular = "Não informado"
        if not nome or not obs:
            messages.add_message(request, messages.ERROR, 'Nome e observação de identificação não podem ser vazios')
            return render(request, "form_cliente.html")
        if celular != "Não informado":
            clientes = Cliente.objects.all().filter(telefone=celular)
            if len(clientes) != 0:
                messages.add_message(request, messages.ERROR, f'Esse telefone já está cadastrado para o cliente {clientes[0]}')
                return render(request, "form_cliente.html")
        novo_cliente = Cliente.objects.create(nome=nome, telefone=celular, obs=obs)
        novo_cliente.save()
        messages.add_message(request, messages.SUCCESS, f'Cliente {novo_cliente} cadastrado com sucesso')
        return redirect("manut_cliente")

@login_required(login_url="login")
def manut_clientes(request):
    termo_cliente = request.GET.get("termo_cliente")
    if termo_cliente:
        termo_cliente = termo_cliente.strip()
        clientes = Cliente.objects.all().filter(
            Q(nome__icontains=termo_cliente) | Q(telefone__icontains=termo_cliente) | Q(obs__icontains=termo_cliente)
        ).order_by("nome")
    else:
        clientes = Cliente.objects.all().order_by("nome")
    if len(clientes) == 0:
        messages.add_message(request, messages.WARNING, f"Nenhum cliente encontrado com o termo {termo_cliente}")
    paginator = Paginator(clientes, 10)
    page = request.GET.get('p')
    clientes = paginator.get_page(page)

    return render(request, "manut_cliente.html", {"clientes": clientes})

@login_required(login_url="login")
def gera_orcamento(request):
    termo_cliente = request.GET.get("termo_cliente")
    if termo_cliente:
        termo_cliente = termo_cliente.strip()
        clientes = Cliente.objects.all().filter(
            Q(nome__icontains=termo_cliente) | Q(telefone__icontains=termo_cliente) | Q(obs__icontains=termo_cliente)
        ).order_by("nome")
    else:
        clientes = Cliente.objects.all().order_by("nome")
    if len(clientes) == 0:
        messages.add_message(request, messages.WARNING, f"Nenhum cliente encontrado com o termo {termo_cliente}")
    paginator = Paginator(clientes, 10)
    page = request.GET.get('p')
    clientes = paginator.get_page(page)

    return render(request, "manut_cliente.html", {"clientes": clientes})

@login_required(login_url="login")
def alterar_cliente(request, id):
    cliente = Cliente.objects.get(id=id)
    if request.method != "POST":
        return render(request, "alterar_cliente.html", {"cliente": cliente})
    else:
        nome = request.POST.get('nome').strip().title()
        celular = request.POST.get('celular')
        obs = request.POST.get("obs").strip().title()
        if celular == "":
            celular = "Não informado"
        if not nome or not obs:
            messages.add_message(request, messages.ERROR, 'Nome e observação de identificação não podem ser vazios')
            return render(request, "alterar_cliente.html", {"cliente": cliente})
        if celular != cliente.telefone:
            clientes = Cliente.objects.all().filter(telefone=celular)
            if len(clientes) != 0:
                messages.add_message(request, messages.ERROR, f'Esse telefone já está cadastrado para o cliente {clientes[0]}')
                return render(request, "alterar_cliente.html", {"cliente": cliente})
        cliente.nome = nome
        cliente.telefone = celular
        cliente.obs = obs
        cliente.save()
        messages.add_message(request, messages.SUCCESS, f'Cliente {cliente} alterado com sucesso')
        return redirect("manut_cliente")
    
@login_required(login_url="login")
def lista_empreendimentos(request):
    empreendimentos = Empreendimento.objects.all()
    return render(request, "lista_empreendimentos.html", {"empreendimentos":empreendimentos})

@login_required(login_url="login")
def dados_cliente(request, id):
    cliente = Cliente.objects.get(id=id)
    if request.method != "POST":
        return render(request, 'form_dados_cliente.html', {"cliente": cliente})
    else:
        nome_completo = request.POST.get('nome_completo').strip().title()
        cpf = request.POST.get('cpf')
        cep = request.POST.get('cep')
        rua = request.POST.get('rua').strip().title()
        bairro = request.POST.get('bairro').strip().title()
        cidade = request.POST.get('cidade').strip().title()
        estado = request.POST.get('estado')
        if not nome_completo or not cpf or not cep or not rua or not bairro or not cidade or not estado:
            messages.add_message(request, messages.ERROR, "Nenhum campo pode ficar em branco. Por favor verifique")
            return render(request, 'form_dados_cliente.html', {"cliente": cliente})
        if len(cpf) != 14:
            messages.add_message(request, messages.ERROR, "CPF precisa ter 14 caracteres. Por favor verifique")
            return render(request, 'form_dados_cliente.html', {"cliente": cliente})
        if len(cep) != 10:
            messages.add_message(request, messages.ERROR, "CEP precisa ter 10 caracteres. Por favor verifique")
            return render(request, 'form_dados_cliente.html', {"cliente": cliente})
        cpf_existe = DadosCliente.objects.all().filter(cpf=cpf)
        if len(cpf_existe) != 0:
            messages.add_message(request, messages.ERROR, f"CPF {cpf} já foi cadastrado para o cliente {cpf_existe[0].cliente}. Por favor verifique")
            return render(request, 'form_dados_cliente.html', {"cliente": cliente})
        dados = DadosCliente(cliente=cliente, nome_completo=nome_completo, cpf=cpf, cep=cep, rua=rua, bairro=bairro, cidade=cidade, estado=estado)
        cliente.dados_adicionais = True
        dados.save()
        cliente.save()
        messages.add_message(request, messages.SUCCESS, f"Dados cadastrados com sucesso para o cliente {cliente}")
        return redirect("manut_cliente")

@login_required(login_url="login")
def alterar_dados_cliente(request, id):
    cliente = Cliente.objects.get(id=id)
    dados_cliente = DadosCliente.objects.get(cliente=cliente)
    if request.method != "POST":
        return render(request, 'alterar_dados_cliente.html', {"cliente": cliente, "dados_cliente": dados_cliente})
    else:
        nome_completo = request.POST.get('nome_completo').strip().title()
        cpf = request.POST.get('cpf')
        cep = request.POST.get('cep')
        rua = request.POST.get('rua').strip().title()
        bairro = request.POST.get('bairro').strip().title()
        cidade = request.POST.get('cidade').strip().title()
        estado = request.POST.get('estado')
        if not nome_completo or not cpf or not cep or not rua or not bairro or not cidade or not estado:
            messages.add_message(request, messages.ERROR, "Nenhum campo pode ficar em branco. Por favor verifique")
            return render(request, 'alterar_dados_cliente.html', {"cliente": cliente, "dados_cliente": dados_cliente})
        if len(cpf) != 14:
            messages.add_message(request, messages.ERROR, "CPF precisa ter 14 caracteres. Por favor verifique")
            return render(request, 'alterar_dados_cliente.html', {"cliente": cliente, "dados_cliente": dados_cliente})
        if len(cep) != 10:
            messages.add_message(request, messages.ERROR, "CEP precisa ter 10 caracteres. Por favor verifique")
            return render(request, 'alterar_dados_cliente.html', {"cliente": cliente, "dados_cliente": dados_cliente})
        cpf_existe = DadosCliente.objects.all().filter(cpf=cpf)
        if len(cpf_existe) != 0 and cpf_existe[0].cliente != cliente:
            messages.add_message(request, messages.ERROR, f"CPF {cpf} já foi cadastrado para o cliente {cpf_existe[0].cliente}. Por favor verifique")
            return render(request, 'alterar_dados_cliente.html', {"cliente": cliente, "dados_cliente": dados_cliente})
        dados_cliente.nome_completo = nome_completo
        dados_cliente.cpf = cpf
        dados_cliente.cep = cep
        dados_cliente.rua = rua
        dados_cliente.bairro = bairro
        dados_cliente.cidade = cidade
        dados_cliente.estado = estado
        dados_cliente.save()
        messages.add_message(request, messages.SUCCESS, f"Dados do cliente {cliente} alterados com sucesso")
        return redirect('manut_cliente')
    
@login_required(login_url="login")
def gerar_orcamento(request, id):
    cliente = Cliente.objects.get(id=id)
    acomodacoes = Acomodacao.objects.all()
    periodos = Periodo.objects.all()
    horas = Horario.objects.all()
    if request.method != "POST":
        return render(request, "form_orc.html", {"cliente": cliente, "acomodacoes": acomodacoes, "periodos": periodos, "horas": horas})
    else:
        n_ocupantes = int(request.POST.get("n_ocupantes"))
        obs_n_ocupantes = request.POST.get("obs_n_ocupantes")
        acomodacao_id = int(request.POST.get("acomodacao"))
        cheia = bool(request.POST.get("cheia"))
        n_dias = request.POST.get("n_dias")
        entrada = request.POST.get("entrada")
        dia_entrada = request.POST.get("dia_entrada")
        checkin = request.POST.get("checkin")
        saida = request.POST.get("saida")
        dia_saida = request.POST.get("dia_saida")
        checkout = request.POST.get("checkout")
        periodo = request.POST.get("periodo")
        entrada = datetime.strptime(entrada, "%Y-%m-%d")
        saida = datetime.strptime(saida, "%Y-%m-%d")
        hoje = datetime.today()
        hoje = hoje-timedelta(days=1)
        acomodacao = Acomodacao.objects.get(id=acomodacao_id)
        """print(n_ocupantes, type(n_ocupantes))
        print(obs_n_ocupantes, type(obs_n_ocupantes))
        print(acomodacao, type(acomodacao))
        print(cheia, type(cheia))
        print(n_dias, type(n_dias))
        print(entrada, type(entrada))
        print(dia_entrada, type(dia_entrada))
        print(checkin, type(checkin))
        print(saida, type(saida))
        print(dia_saida, type(dia_saida))
        print(checkout, type(checkout))
        print(periodo, type(periodo))"""
        if not acomodacao or not n_dias or not entrada or not dia_entrada or not checkin or not saida or not dia_saida or not checkout or not periodo:
            messages.add_message(request, messages.ERROR, "Nenhum campo pode ficar em branco. Por favor verifique")
            return render(request, "form_orc.html", {"cliente": cliente, "acomodacoes": acomodacoes, "periodos": periodos, "horas": horas})
        if n_ocupantes < 1:
            messages.add_message(request, messages.ERROR, "Número mínimo de ocupantes é 1. Por favor verifique")
            return render(request, "form_orc.html", {"cliente": cliente, "acomodacoes": acomodacoes, "periodos": periodos, "horas": horas})
        n_dias = int(n_dias)
        if entrada >= saida:
            messages.add_message(request, messages.ERROR, "Data de entrada deve ser anterior a data de saída. Por favor verifique")
            return render(request, "form_orc.html", {"cliente": cliente, "acomodacoes": acomodacoes, "periodos": periodos, "horas": horas})
        print(entrada, hoje)
        if entrada < hoje:
            messages.add_message(request, messages.ERROR, "Data de entrada não pode ser anterior a atual. Por favor verifique")
            return render(request, "form_orc.html", {"cliente": cliente, "acomodacoes": acomodacoes, "periodos": periodos, "horas": horas})
        orcamento = Orcamento(cliente=cliente, acomodacao=acomodacao, n_ocupantes=n_ocupantes, obs_n_ocupantes=obs_n_ocupantes, diaria_cheia=cheia, data_entrada=entrada, dia_entrada=dia_entrada, checkin=checkin, data_saida=saida, dia_saida=dia_saida, checkout=checkout, periodo=periodo, n_dias=n_dias, status="em digitação")
        orcamento.save()
        messages.add_message(request, messages.SUCCESS, f"Orçamento de {orcamento} gerado com sucesso.")
        return redirect("lista_orcamentos_digitados")
    
@login_required(login_url="login")
def lista_orcamentos_digitados(request):
    orcamentos = Orcamento.objects.all().filter(
        status="em digitação"
    ).exclude(eliminado=True)
    if len(orcamentos) == 0:
        messages.add_message(request, messages.WARNING, "Não existem orçamentos pendentes em digitação")
    return render(request, "orc_em_digitacao.html", {"orcamentos": orcamentos})

@login_required(login_url="login")
def finalizar_digitacao(request, id):
    orcamento = Orcamento.objects.get(id=id)
    info_adic = Observacao.objects.all().filter(
        tipo__tipo="Informações adicionais orçamento"
    )
    obs_orc = Observacao.objects.all().filter(
        tipo__tipo="Observações orçamento"
    )
    cond_pag_orc = Observacao.objects.all().filter(
        tipo__tipo="Condições de pagamento orçamento"
    )
    valor = str(orcamento.acomodacao.valor_base)
    if request.method != "POST":
        return render(request, "form_orc2.html", {"orcamento": orcamento, "valor":valor, "info_adic":info_adic, "obs_orc":obs_orc, "cond_pag_orc": cond_pag_orc})
    else:
        tot_diarias = request.POST.get("valor_diaria").replace("R$ ", "")
        tot_pacote = request.POST.get("tot_pacote").replace("R$ ", "")
        tot_taxa_limpeza = request.POST.get("tot_taxa_limpeza").replace("R$ ", "")
        tot_descontos = request.POST.get("tot_descontos").replace("R$ ", "")
        tot_acrescimos = request.POST.get("tot_acrescimos").replace("R$ ", "")
        dias_pacote = request.POST.get("dias_pacote")
        tot_reserva = request.POST.get("tot_reserva").replace("R$ ", "")
        cond_pag = request.POST.get("cond_pag")
        obs = request.POST.get("obs")
        info_adicionais = request.POST.get("info_adicionais")
        """print(tot_diarias)
        print(tot_pacote)
        print(tot_taxa_limpeza)
        print(tot_descontos)
        print(tot_acrescimos)
        print(dias_pacote)
        print(tot_reserva)"""
        if not tot_diarias or not tot_pacote or not tot_taxa_limpeza or not tot_descontos or not tot_acrescimos or not dias_pacote or not tot_reserva or not cond_pag or not obs or not info_adicionais:
            messages.add_message(request, messages.ERROR, "Nenhum campo pode ficar em branco. Por favor verifique")
            return render(request, "form_orc2.html", {"orcamento": orcamento, "valor":valor, "info_adic":info_adic, "obs_orc":obs_orc, "cond_pag_orc": cond_pag_orc})
        tot_diarias = float(tot_diarias)
        tot_pacote = float(tot_pacote)
        tot_taxa_limpeza = float(tot_taxa_limpeza)
        tot_descontos = float(tot_descontos)
        tot_acrescimos = float(tot_acrescimos)
        dias_pacote = int(dias_pacote)
        tot_reserva = float(tot_reserva)
        if tot_reserva == 0.0:
            messages.add_message(request, messages.ERROR, "Total da reserva não pode ser zero. Por favor verifique")
            return render(request, "form_orc2.html", {"orcamento": orcamento, "valor":valor, "info_adic":info_adic, "obs_orc":obs_orc, "cond_pag_orc": cond_pag_orc})
        orcamento.valor_diaria = tot_diarias
        orcamento.taxa_limpeza = tot_taxa_limpeza
        orcamento.descontos = tot_descontos
        orcamento.acrescimos = tot_acrescimos
        orcamento.valor_pacote = tot_pacote
        orcamento.dias_pacote = dias_pacote
        orcamento.total_valor_reserva = tot_reserva
        orcamento.status = "digitação concluída"
        orcamento.save()
        obs_orcamento = ObsOrcamento(orcamento=orcamento, obs=obs, condicoes_pagamento=cond_pag, informacoes_adicionais=info_adicionais)
        obs_orcamento.save()
        messages.add_message(request, messages.SUCCESS, f"Orçamento {orcamento.id} do cliente {orcamento.cliente} para a acomodação {orcamento.acomodacao} gerado com sucesso. Você já pode gerar o PDF e enviar para o cliente")
        return redirect("lista_gera_pdf_orcamento")
    
@login_required(login_url="login")
def lista_gera_pdf_orcamento(request):
    orcamentos = Orcamento.objects.all().filter(
        status="digitação concluída"
    ).exclude(eliminado=True)
    if len(orcamentos) == 0:
        messages.add_message(request, messages.WARNING, "Todos os orçamentos pendentes já tiveram seu PDF gerado. Dúvidas, consulte a lista de orçamentos concluídos")
    return render(request, "orc_digitados.html", {"orcamentos": orcamentos})

@login_required(login_url="login")
def gera_pdf_orc(request, id):
    orc = Orcamento.objects.get(id=id)
    obs_orc = ObsOrcamento.objects.get(orcamento=orc)
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    ### variáveis do projeto
    if orc.modificado:
        modificado = "***Modificado"
        motivo = f"Motivo: {orc.obs_modificacao}"
    else:
        modificado = ""
        motivo = ""
    data_orçamento = f"{datetime.strftime(orc.data_orcamento, '%d de %b de %Y')}"
    n_orçamento=f"{orc.id}"
    hospede = f"{orc.cliente}"
    empreendimento= f"{orc.acomodacao.empreendimento}"
    acomodação = f"{orc.acomodacao}"
    entrada = f"{datetime.strftime(orc.data_entrada, '%d/%m/%Y')} - {orc.dia_entrada} - {orc.checkin}"
    saída =  f"{datetime.strftime(orc.data_saida, '%d/%m/%Y')} - {orc.dia_saida} - {orc.checkout}"
    tot_diárias =f"{orc.n_dias}"
    tot_ocupantes= f"{orc.n_ocupantes}"
    obs_ocupantes=f"{orc.obs_n_ocupantes}"
    perido = f"{orc.periodo}"
    if orc.diaria_cheia:
        tipo_diária="DIÁRIA CHEIA"
    else:
        tipo_diária="PERNOITE"
    valor_diaria=f"R$ {orc.valor_diaria:.2f}"
    tx_limpeza=  f"R$ {orc.taxa_limpeza:.2f}"
    valor_pacote=f"R$ {orc.valor_pacote:.2f}"
    dias_pacote=f"{orc.dias_pacote}"
    tot_valor_diarias = orc.valor_diaria*(orc.n_dias-orc.dias_pacote)
    tot_valor_diarias=f"{tot_valor_diarias:.2f}"
    tot_valor_pacote=f"{orc.valor_pacote:.2f}"
    tot_tx_limpeza=f"{orc.taxa_limpeza:.2f}"
    tot_acrescimo=f"{orc.acrescimos:.2f}"
    tot_desconto=f"{orc.descontos:.2f}"
    total_valor=f"{orc.total_valor_reserva:.2f}"

    ##observaçoes
    #condições de pagamento
    condiçao_pag =obs_orc.condicoes_pagamento
    #obs importantes
    obs_importante = obs_orc.obs

    #informações adicionias
    info = obs_orc.informacoes_adicionais
    #descrição da acomodação
    desc_acomod=orc.acomodacao.descricao

    ## fontes do report lab
    #Courier
    bold1 = "Courier-Bold"
    bold2 = "Courier-BoldOblique"
    #Courier-Oblique
    padr = "Helvetica" #padrão
    padr_bold = "Helvetica-Bold"   #padrão
    bold4 = "Helvetica-BoldOblique"
    #Helvetica-Oblique
    #Symbol
    bold5 = "Times-Bold"
    #Times-BoldItalic
    #Times-Italic
    #Times-Roman
    #ZapfDingbats

    ##### inicio do projeto ########

    #transforma mm em pontos
    def mm2p(mm):
        return mm/0.352777
    ## gera nome do arquivo personalizado para cada cliente
    cliente = hospede.replace("(","-").replace(")","-").replace("/","-")
    arquivo = f"orcamento-{n_orçamento}-{acomodação} {cliente}.pdf"
    #url_pdf = os.path.join(caminho, arquivo)
    cnv =  canvas.Canvas(buffer, pagesize=A4)

    #drawMyRuler(cnv)
    cnv.setTitle("Orçamento de "+ hospede + acomodação)

    #desenhar um retangulo informa x inicial, y inicial , largura e altura
    cnv.rect(mm2p(2),mm2p(2),mm2p(205),mm2p(293))

    ##### fazendo um cabeçalho ######
    #desenhar um retangulo para cabeçalho
    cnv.rect(mm2p(2),mm2p(250),mm2p(205),mm2p(45))
    #desenhar uma imagem
    cnv.drawImage("templates/static/img/LOGO.png",mm2p(3),mm2p(251),width=mm2p(30),height=mm2p(40))
    cnv.setFontSize(15)
    cnv.setFont(padr_bold,15)
    cnv.drawCentredString(320,810,"RESIDENCIAL SOL DE VERÃO & MORADAS PÉ NA AREIA")
    cnv.setFontSize(20)

    cnv.setFillColor("green")
    cnv.drawCentredString(320,780,"ORÇAMENTO DE RESERVA")
    cnv.setFillColor('red')
    cnv.setFont(padr_bold,14)
    cnv.drawCentredString(320,750, empreendimento)
    cnv.setFillColor('black')

    cnv.setFillColor('blue')
    cnv.setFont(padr_bold,10)
    #cnv.drawCentredString(320,750,"NÚMERO DO ORÇAMENTO: ")
    cnv.drawRightString(500,713,"NÚMERO DO ORÇAMENTO: ")
    cnv.setFillColor('black')
    cnv.setFont(padr,13)
    cnv.drawRightString(570,713, n_orçamento)
    cnv.setFillColor('black')
    cnv.setFillColor('blue')
    cnv.setFont(padr_bold,10)
    cnv.drawString(110,713,"DATA DO ORÇAMENTO: ")
    cnv.setFillColor('black')
    cnv.setFont(padr,13)
    cnv.drawString(230,713, data_orçamento)
    cnv.setFillColor('black')


    #linha 1
    linha=243
    desconto =  5
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha),"HÓSPEDE:")
    cnv.setFont(padr,12)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(24),mm2p(linha),hospede)

    #linha 2
    linha = linha-desconto
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha),"ACOMODAÇÃO:")
    cnv.setFont(padr,12)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(33),mm2p(linha),acomodação)

    #linha 3
    linha = linha-desconto
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha),"DATA DE ENTRADA(check in):")
    cnv.setFont(padr,12)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(60),mm2p(linha),entrada)

    #linha 4
    linha = linha-desconto
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha),"DATA DE SAÍDA(check out):")
    cnv.setFont(padr,12)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(60),mm2p(linha),saída)

    cnv.rect(mm2p(2),mm2p(linha-4),mm2p(205),mm2p(0))

    #linha 5  TOTAL DE  DIÁRIA, OCUPANTES E TIPO DE DIÁRIA
    linha = linha-desconto-6
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha),"TOTAL DE DIÁRIAS:")
    cnv.setFont(padr,18)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(39),mm2p(linha),tot_diárias)

    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(50),mm2p(linha),"TOTAL DE OCUPANTES:")
    cnv.setFont(padr,18)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(96),mm2p(linha),tot_ocupantes)
    cnv.setFont(padr,10)
    cnv.drawString(mm2p(105),mm2p(linha),obs_ocupantes)
    cnv.setFillColor("green")
    cnv.setFont(padr_bold,7)
    cnv.drawRightString(mm2p(205),mm2p(linha-1),tipo_diária)
    cnv.drawRightString(mm2p(205),mm2p(linha+4),perido)
    cnv.setFont(padr,10)

    cnv.rect(mm2p(2),mm2p(linha-4),mm2p(205),mm2p(0))

    # linha 6 - VALORES  INDIVIDUAIS
    linha = linha-desconto-6
    fonte_destaque=14      
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha),"VALOR DA DIÁRIA:")
    cnv.setFont(padr,fonte_destaque)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(39),mm2p(linha),valor_diaria)

    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(100),mm2p(linha),"TX DE LIMPEZA:")
    cnv.setFont(padr,fonte_destaque)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(150),mm2p(linha),tx_limpeza)
    cnv.setFont(padr,10)

    #LINHA7
    linha = linha-desconto-2

    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha),"VALOR DO PACOTE:")
    cnv.setFont(padr,fonte_destaque)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(39),mm2p(linha),valor_pacote)

    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(100),mm2p(linha)," QUANTIDADE DIAS DO PACOTE:")
    cnv.setFont(padr,fonte_destaque)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(160),mm2p(linha),dias_pacote)
    cnv.setFont(padr,10)

    cnv.rect(mm2p(2),mm2p(linha-4),mm2p(205),mm2p(0))

    ## grade do calculo do orçamento
    cnv.rect(mm2p(2),mm2p(linha-45),mm2p(80),mm2p(41))
    cnv.rect(mm2p(2),mm2p(linha-45),mm2p(205),mm2p(41))

    #coluna de CALCULO DO ORÇAMENTO
    size_calculo = 12
    linha_coluna_calculo = linha-desconto-4
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha_coluna_calculo),"CALCULO DO ORÇAMENTO:")
    cnv.setFont(padr,fonte_destaque)
    cnv.setFillColor("black")

    linha_coluna_calculo = linha_coluna_calculo-desconto-2
    cnv.setFont(padr_bold,8)
    cnv.setFillColor("blue")
    cnv.drawString(mm2p(3),mm2p(linha_coluna_calculo),"Total das diárias ==> ")
    cnv.setFont(padr,size_calculo)
    cnv.setFillColor("black")
    cnv.drawRightString(mm2p(65),mm2p(linha_coluna_calculo), tot_valor_diarias)

    linha_coluna_calculo = linha_coluna_calculo-desconto
    cnv.setFont(padr_bold,8)
    cnv.setFillColor("blue")
    cnv.drawString(mm2p(3),mm2p(linha_coluna_calculo),"Valor do Pacote  ==> ")
    cnv.setFont(padr,size_calculo)
    cnv.setFillColor("black")
    cnv.drawRightString(mm2p(65),mm2p(linha_coluna_calculo), tot_valor_pacote)

    linha_coluna_calculo = linha_coluna_calculo-desconto
    cnv.setFont(padr_bold,8)
    cnv.setFillColor("blue")
    cnv.drawString(mm2p(3),mm2p(linha_coluna_calculo),"Taxa de Limpeza ==> ")
    cnv.setFont(padr,size_calculo)
    cnv.setFillColor("black")
    cnv.drawRightString(mm2p(65),mm2p(linha_coluna_calculo), tot_tx_limpeza)

    linha_coluna_calculo = linha_coluna_calculo-desconto
    cnv.setFont(padr_bold,8)
    cnv.setFillColor("blue")
    cnv.drawString(mm2p(3),mm2p(linha_coluna_calculo),"Acréscimos ==> ")
    cnv.setFont(padr,size_calculo)
    cnv.setFillColor("black")
    cnv.drawRightString(mm2p(65),mm2p(linha_coluna_calculo), tot_acrescimo)

    linha_coluna_calculo = linha_coluna_calculo-desconto
    cnv.setFont(padr_bold,8)
    cnv.setFillColor("blue")
    cnv.drawString(mm2p(3),mm2p(linha_coluna_calculo),"Descontos ==> ")
    cnv.setFont(padr,size_calculo)
    cnv.setFillColor("red")
    cnv.drawRightString(mm2p(65),mm2p(linha_coluna_calculo), tot_desconto)
    cnv.setFillColor("black")

    linha_coluna_calculo = linha_coluna_calculo-desconto
    cnv.setFont(padr_bold,11)
    cnv.setFillColor("blue")
    cnv.drawString(mm2p(3),mm2p(linha_coluna_calculo),"TOTAL ==> ")
    cnv.setFont(padr_bold,size_calculo+3)
    cnv.setFillColor("black")
    cnv.drawRightString(mm2p(65),mm2p(linha_coluna_calculo), total_valor)
    cnv.setFillColor("black")

    #coluna observações

    size_calculo = 12
    linha_coluna_obs = linha-desconto-4
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(85),mm2p(linha_coluna_obs),"OBSERVAÇÕES IMPORTANTES :")
    cnv.setFont(padr,3)
    cnv.setFillColor("black")

    from reportlab.lib.styles import ParagraphStyle

    estilo_obs = ParagraphStyle('Body', fontName=padr_bold, fontSize=8, leading=10, spaceBefore=20, textColor="black",backColor="#f1f1f1")

    obs = obs_importante.replace("\n","<BR/>")
    p = Paragraph(obs,estilo_obs)

    p.wrapOn(cnv, 340, 100)
    p.drawOn(cnv, 240, 450)

    #condições de pagamento
    size_calculo = 12
    linha_f_pagto = linha_coluna_calculo-9
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha_f_pagto),"CONDIÇÕES DE PAGAMENTO:")
    cnv.setFont(padr,fonte_destaque)
    cnv.setFillColor("black")

    cnv.rect(mm2p(2),mm2p(linha_f_pagto-30),mm2p(205),mm2p(0))

    estilo_cond_pag = ParagraphStyle('Body', fontName=padr_bold, fontSize=8, leading=10, spaceBefore=20, textColor="green",backColor="#f1f1f1")
    cond_pag= condiçao_pag.replace("\n","<BR/>")
    p_cond_pag = Paragraph(cond_pag,estilo_cond_pag)

    p_cond_pag.wrapOn(cnv, 570, 100)
    p_cond_pag.drawOn(cnv, 10, 350)

    ####  coluna informações adicionias importante ######
    linha_info = linha_f_pagto-35
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha_info),"INFORMAÇÕES ADICIONAIS:  (ATENÇÃO IMPORTANTE)")
    cnv.setFont(padr,fonte_destaque)
    cnv.setFillColor("black")

    estilo_info = ParagraphStyle('Body', fontName=padr_bold, fontSize=8, leading=10, spaceBefore=20, textColor="blue",alignment=0,backColor="#f1f1f1")

    testeinfo=info.replace("\n","<BR/>")

    p_info = Paragraph(testeinfo,estilo_info)

    p_info.wrapOn(cnv, 270, 80)
    p_info.drawOn(cnv, 10, 50)


    ###### coluna descrição acomodação ####


    coluna = mm2p(105)
    cnv.rect(mm2p(102),mm2p(2),mm2p(105),mm2p(117))
    linha_info = linha_f_pagto-35
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(coluna,mm2p(linha_info),"BREVE DESCRIÇÃO DA ACOMODAÇÃO:")
    cnv.setFont(padr,fonte_destaque)
    cnv.setFillColor("black")

    estilo_desc_acomod = ParagraphStyle('Body', fontName=padr_bold, fontSize=8, leading=10, spaceBefore=20, textColor="black",alignment=0,backColor="#f1f1f1")

    acomod=desc_acomod.replace("\n","<BR/>")

    p_info = Paragraph(acomod,estilo_desc_acomod)

    p_info.wrapOn(cnv, 270, 80)
    p_info.drawOn(cnv, coluna+5, 50)

    cnv.setFont(padr, 7)
    cnv.drawRightString(mm2p(200), mm2p(7), modificado)
    cnv.drawRightString(mm2p(200), mm2p(5), motivo)
    cnv.showPage()
    cnv.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    orc.status = "orçamento gerado"
    orc.save()
    return FileResponse(buffer, as_attachment=False, filename=arquivo)
    
@login_required(login_url="login")
def lista_orçamentos_concluidos(request):
    termo_cliente = request.GET.get("termo_cliente")
    if termo_cliente:
        termo_cliente = termo_cliente.strip()
        orcamentos = Orcamento.objects.all().filter(
            Q(cliente__nome__icontains=termo_cliente) | Q(cliente__telefone__icontains=termo_cliente) | Q(cliente__obs__icontains=termo_cliente) | Q(acomodacao__nome__icontains=termo_cliente), Q(status="orçamento gerado") | Q(status="contrato gerado"), quitado=False
        ).exclude(eliminado=True).order_by("-id")
    else:
        orcamentos = Orcamento.objects.all().filter(
            Q(status="orçamento gerado") | Q(status="contrato gerado"), quitado=False
        ).exclude(eliminado=True).order_by("-id")
    if len(orcamentos) == 0:
        messages.add_message(request, messages.WARNING, f"Nenhum orçamento encontrado com o termo {termo_cliente}")
    paginator = Paginator(orcamentos, 10)
    page = request.GET.get('p')
    orcamentos = paginator.get_page(page)
    return render(request, "lista_orcamentos_concluidos.html", {"orcamentos": orcamentos})

@login_required(login_url="login")
def vizualizar_pdf(request, id):
    orc = Orcamento.objects.get(id=id)
    obs_orc = ObsOrcamento.objects.get(orcamento=orc)
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    ### variáveis do projeto
    if orc.modificado:
        modificado = "***Modificado"
        motivo = f"Motivo: {orc.obs_modificacao}"
    else:
        modificado = ""
        motivo = ""
    data_orçamento = f"{datetime.strftime(orc.data_orcamento, '%d de %b de %Y')}"
    n_orçamento=f"{orc.id}"
    hospede = f"{orc.cliente}"
    empreendimento= f"{orc.acomodacao.empreendimento}"
    acomodação = f"{orc.acomodacao}"
    entrada = f"{datetime.strftime(orc.data_entrada, '%d/%m/%Y')} - {orc.dia_entrada} - {orc.checkin}"
    saída =  f"{datetime.strftime(orc.data_saida, '%d/%m/%Y')} - {orc.dia_saida} - {orc.checkout}"
    tot_diárias =f"{orc.n_dias}"
    tot_ocupantes= f"{orc.n_ocupantes}"
    obs_ocupantes=f"{orc.obs_n_ocupantes}"
    perido = f"{orc.periodo}"
    if orc.diaria_cheia:
        tipo_diária="DIÁRIA CHEIA"
    else:
        tipo_diária="PERNOITE"
    valor_diaria=f"R$ {orc.valor_diaria:.2f}"
    tx_limpeza=  f"R$ {orc.taxa_limpeza:.2f}"
    valor_pacote=f"R$ {orc.valor_pacote:.2f}"
    dias_pacote=f"{orc.dias_pacote}"
    tot_valor_diarias = orc.valor_diaria*(orc.n_dias-orc.dias_pacote)
    tot_valor_diarias=f"{tot_valor_diarias:.2f}"
    tot_valor_pacote=f"{orc.valor_pacote:.2f}"
    tot_tx_limpeza=f"{orc.taxa_limpeza:.2f}"
    tot_acrescimo=f"{orc.acrescimos:.2f}"
    tot_desconto=f"{orc.descontos:.2f}"
    total_valor=f"{orc.total_valor_reserva:.2f}"

    ##observaçoes
    #condições de pagamento
    condiçao_pag =obs_orc.condicoes_pagamento
    #obs importantes
    obs_importante = obs_orc.obs

    #informações adicionias
    info = obs_orc.informacoes_adicionais
    #descrição da acomodação
    desc_acomod=orc.acomodacao.descricao

    ## fontes do report lab
    #Courier
    bold1 = "Courier-Bold"
    bold2 = "Courier-BoldOblique"
    #Courier-Oblique
    padr = "Helvetica" #padrão
    padr_bold = "Helvetica-Bold"   #padrão
    bold4 = "Helvetica-BoldOblique"
    #Helvetica-Oblique
    #Symbol
    bold5 = "Times-Bold"
    #Times-BoldItalic
    #Times-Italic
    #Times-Roman
    #ZapfDingbats

    ##### inicio do projeto ########

    #transforma mm em pontos
    def mm2p(mm):
        return mm/0.352777
    ## gera nome do arquivo personalizado para cada cliente
    cliente = hospede.replace("(","-").replace(")","-").replace("/","-")
    arquivo = f"orcamento-{n_orçamento}-{acomodação} {cliente}.pdf"
    #url_pdf = os.path.join(caminho, arquivo)
    cnv =  canvas.Canvas(buffer, pagesize=A4)

    #drawMyRuler(cnv)
    cnv.setTitle("Orçamento de "+ hospede + acomodação)

    #desenhar um retangulo informa x inicial, y inicial , largura e altura
    cnv.rect(mm2p(2),mm2p(2),mm2p(205),mm2p(293))

    ##### fazendo um cabeçalho ######
    #desenhar um retangulo para cabeçalho
    cnv.rect(mm2p(2),mm2p(250),mm2p(205),mm2p(45))
    #desenhar uma imagem
    cnv.drawImage("templates/static/img/LOGO.png",mm2p(3),mm2p(251),width=mm2p(30),height=mm2p(40))
    cnv.setFontSize(15)
    cnv.setFont(padr_bold,15)
    cnv.drawCentredString(320,810,"RESIDENCIAL SOL DE VERÃO & MORADAS PÉ NA AREIA")
    cnv.setFontSize(20)

    cnv.setFillColor("green")
    cnv.drawCentredString(320,780,"ORÇAMENTO DE RESERVA")
    cnv.setFillColor('red')
    cnv.setFont(padr_bold,14)
    cnv.drawCentredString(320,750, empreendimento)
    cnv.setFillColor('black')

    cnv.setFillColor('blue')
    cnv.setFont(padr_bold,10)
    #cnv.drawCentredString(320,750,"NÚMERO DO ORÇAMENTO: ")
    cnv.drawRightString(500,713,"NÚMERO DO ORÇAMENTO: ")
    cnv.setFillColor('black')
    cnv.setFont(padr,13)
    cnv.drawRightString(570,713, n_orçamento)
    cnv.setFillColor('black')
    cnv.setFillColor('blue')
    cnv.setFont(padr_bold,10)
    cnv.drawString(110,713,"DATA DO ORÇAMENTO: ")
    cnv.setFillColor('black')
    cnv.setFont(padr,13)
    cnv.drawString(230,713, data_orçamento)
    cnv.setFillColor('black')


    #linha 1
    linha=243
    desconto =  5
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha),"HÓSPEDE:")
    cnv.setFont(padr,12)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(24),mm2p(linha),hospede)

    #linha 2
    linha = linha-desconto
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha),"ACOMODAÇÃO:")
    cnv.setFont(padr,12)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(33),mm2p(linha),acomodação)

    #linha 3
    linha = linha-desconto
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha),"DATA DE ENTRADA(check in):")
    cnv.setFont(padr,12)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(60),mm2p(linha),entrada)

    #linha 4
    linha = linha-desconto
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha),"DATA DE SAÍDA(check out):")
    cnv.setFont(padr,12)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(60),mm2p(linha),saída)

    cnv.rect(mm2p(2),mm2p(linha-4),mm2p(205),mm2p(0))

    #linha 5  TOTAL DE  DIÁRIA, OCUPANTES E TIPO DE DIÁRIA
    linha = linha-desconto-6
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha),"TOTAL DE DIÁRIAS:")
    cnv.setFont(padr,18)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(39),mm2p(linha),tot_diárias)

    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(50),mm2p(linha),"TOTAL DE OCUPANTES:")
    cnv.setFont(padr,18)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(96),mm2p(linha),tot_ocupantes)
    cnv.setFont(padr,10)
    cnv.drawString(mm2p(105),mm2p(linha),obs_ocupantes)
    cnv.setFillColor("green")
    cnv.setFont(padr_bold,7)
    cnv.drawRightString(mm2p(205),mm2p(linha-1),tipo_diária)
    cnv.drawRightString(mm2p(205),mm2p(linha+4),perido)
    cnv.setFont(padr,10)

    cnv.rect(mm2p(2),mm2p(linha-4),mm2p(205),mm2p(0))

    # linha 6 - VALORES  INDIVIDUAIS
    linha = linha-desconto-6
    fonte_destaque=14      
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha),"VALOR DA DIÁRIA:")
    cnv.setFont(padr,fonte_destaque)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(39),mm2p(linha),valor_diaria)

    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(100),mm2p(linha),"TX DE LIMPEZA:")
    cnv.setFont(padr,fonte_destaque)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(150),mm2p(linha),tx_limpeza)
    cnv.setFont(padr,10)

    #LINHA7
    linha = linha-desconto-2

    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha),"VALOR DO PACOTE:")
    cnv.setFont(padr,fonte_destaque)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(39),mm2p(linha),valor_pacote)

    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(100),mm2p(linha)," QUANTIDADE DIAS DO PACOTE:")
    cnv.setFont(padr,fonte_destaque)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(160),mm2p(linha),dias_pacote)
    cnv.setFont(padr,10)

    cnv.rect(mm2p(2),mm2p(linha-4),mm2p(205),mm2p(0))

    ## grade do calculo do orçamento
    cnv.rect(mm2p(2),mm2p(linha-45),mm2p(80),mm2p(41))
    cnv.rect(mm2p(2),mm2p(linha-45),mm2p(205),mm2p(41))

    #coluna de CALCULO DO ORÇAMENTO
    size_calculo = 12
    linha_coluna_calculo = linha-desconto-4
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha_coluna_calculo),"CALCULO DO ORÇAMENTO:")
    cnv.setFont(padr,fonte_destaque)
    cnv.setFillColor("black")

    linha_coluna_calculo = linha_coluna_calculo-desconto-2
    cnv.setFont(padr_bold,8)
    cnv.setFillColor("blue")
    cnv.drawString(mm2p(3),mm2p(linha_coluna_calculo),"Total das diárias ==> ")
    cnv.setFont(padr,size_calculo)
    cnv.setFillColor("black")
    cnv.drawRightString(mm2p(65),mm2p(linha_coluna_calculo), tot_valor_diarias)

    linha_coluna_calculo = linha_coluna_calculo-desconto
    cnv.setFont(padr_bold,8)
    cnv.setFillColor("blue")
    cnv.drawString(mm2p(3),mm2p(linha_coluna_calculo),"Valor do Pacote  ==> ")
    cnv.setFont(padr,size_calculo)
    cnv.setFillColor("black")
    cnv.drawRightString(mm2p(65),mm2p(linha_coluna_calculo), tot_valor_pacote)

    linha_coluna_calculo = linha_coluna_calculo-desconto
    cnv.setFont(padr_bold,8)
    cnv.setFillColor("blue")
    cnv.drawString(mm2p(3),mm2p(linha_coluna_calculo),"Taxa de Limpeza ==> ")
    cnv.setFont(padr,size_calculo)
    cnv.setFillColor("black")
    cnv.drawRightString(mm2p(65),mm2p(linha_coluna_calculo), tot_tx_limpeza)

    linha_coluna_calculo = linha_coluna_calculo-desconto
    cnv.setFont(padr_bold,8)
    cnv.setFillColor("blue")
    cnv.drawString(mm2p(3),mm2p(linha_coluna_calculo),"Acréscimos ==> ")
    cnv.setFont(padr,size_calculo)
    cnv.setFillColor("black")
    cnv.drawRightString(mm2p(65),mm2p(linha_coluna_calculo), tot_acrescimo)

    linha_coluna_calculo = linha_coluna_calculo-desconto
    cnv.setFont(padr_bold,8)
    cnv.setFillColor("blue")
    cnv.drawString(mm2p(3),mm2p(linha_coluna_calculo),"Descontos ==> ")
    cnv.setFont(padr,size_calculo)
    cnv.setFillColor("red")
    cnv.drawRightString(mm2p(65),mm2p(linha_coluna_calculo), tot_desconto)
    cnv.setFillColor("black")

    linha_coluna_calculo = linha_coluna_calculo-desconto
    cnv.setFont(padr_bold,11)
    cnv.setFillColor("blue")
    cnv.drawString(mm2p(3),mm2p(linha_coluna_calculo),"TOTAL ==> ")
    cnv.setFont(padr_bold,size_calculo+3)
    cnv.setFillColor("black")
    cnv.drawRightString(mm2p(65),mm2p(linha_coluna_calculo), total_valor)
    cnv.setFillColor("black")

    #coluna observações

    size_calculo = 12
    linha_coluna_obs = linha-desconto-4
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(85),mm2p(linha_coluna_obs),"OBSERVAÇÕES IMPORTANTES :")
    cnv.setFont(padr,3)
    cnv.setFillColor("black")

    from reportlab.lib.styles import ParagraphStyle

    estilo_obs = ParagraphStyle('Body', fontName=padr_bold, fontSize=8, leading=10, spaceBefore=20, textColor="black",backColor="#f1f1f1")

    obs = obs_importante.replace("\n","<BR/>")
    p = Paragraph(obs,estilo_obs)

    p.wrapOn(cnv, 340, 100)
    p.drawOn(cnv, 240, 450)

    #condições de pagamento
    size_calculo = 12
    linha_f_pagto = linha_coluna_calculo-9
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha_f_pagto),"CONDIÇÕES DE PAGAMENTO:")
    cnv.setFont(padr,fonte_destaque)
    cnv.setFillColor("black")

    cnv.rect(mm2p(2),mm2p(linha_f_pagto-30),mm2p(205),mm2p(0))

    estilo_cond_pag = ParagraphStyle('Body', fontName=padr_bold, fontSize=8, leading=10, spaceBefore=20, textColor="green",backColor="#f1f1f1")
    cond_pag= condiçao_pag.replace("\n","<BR/>")
    p_cond_pag = Paragraph(cond_pag,estilo_cond_pag)

    p_cond_pag.wrapOn(cnv, 570, 100)
    p_cond_pag.drawOn(cnv, 10, 350)

    ####  coluna informações adicionias importante ######
    linha_info = linha_f_pagto-35
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha_info),"INFORMAÇÕES ADICIONAIS:  (ATENÇÃO IMPORTANTE)")
    cnv.setFont(padr,fonte_destaque)
    cnv.setFillColor("black")

    estilo_info = ParagraphStyle('Body', fontName=padr_bold, fontSize=8, leading=10, spaceBefore=20, textColor="blue",alignment=0,backColor="#f1f1f1")

    testeinfo=info.replace("\n","<BR/>")

    p_info = Paragraph(testeinfo,estilo_info)

    p_info.wrapOn(cnv, 270, 80)
    p_info.drawOn(cnv, 10, 50)


    ###### coluna descrição acomodação ####


    coluna = mm2p(105)
    cnv.rect(mm2p(102),mm2p(2),mm2p(105),mm2p(117))
    linha_info = linha_f_pagto-35
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(coluna,mm2p(linha_info),"BREVE DESCRIÇÃO DA ACOMODAÇÃO:")
    cnv.setFont(padr,fonte_destaque)
    cnv.setFillColor("black")

    estilo_desc_acomod = ParagraphStyle('Body', fontName=padr_bold, fontSize=8, leading=10, spaceBefore=20, textColor="black",alignment=0,backColor="#f1f1f1")

    acomod=desc_acomod.replace("\n","<BR/>")

    p_info = Paragraph(acomod,estilo_desc_acomod)

    p_info.wrapOn(cnv, 270, 80)
    p_info.drawOn(cnv, coluna+5, 50)

    cnv.setFont(padr, 7)
    cnv.drawRightString(mm2p(200), mm2p(7), modificado)
    cnv.drawRightString(mm2p(200), mm2p(5), motivo)
    cnv.showPage()
    cnv.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename=arquivo)

@login_required(login_url="login")
def gerar_contrato(request, id):
    orcamento = Orcamento.objects.get(id=id)
    total_diarias = orcamento.valor_diaria * (orcamento.n_dias-orcamento.dias_pacote)
    obs_orcamento = ObsOrcamento.objects.get(orcamento=orcamento)
    cond_pag = obs_orcamento.condicoes_pagamento
    info_adic_contrato = Observacao.objects.all().filter(
        tipo__tipo="Informações adicionais contrato"
    )
    aviso_contrato = Observacao.objects.all().filter(
        tipo__tipo="Aviso contrato"
    )
    cond_pag_contrato = Observacao.objects.all().filter(
        tipo__tipo="Condições de pagamento contrato"
    )
    contas_deposito = Observacao.objects.all().filter(
        tipo__tipo="Contas para depósito"
    )
    #print(total_diarias)
    if request.method != "POST":
        return render(request, "form_contrato.html", {"orcamento": orcamento, "total_diarias": total_diarias, "cond_pag": cond_pag, "info_adic_contrato": info_adic_contrato, "aviso_contrato":aviso_contrato, "cond_pag_contrato": cond_pag_contrato, "contas_deposito":contas_deposito})
    else:
        cond_pagamento = request.POST.get("cond_pag")
        conta_deposito = request.POST.get("conta_deposito")
        obs = request.POST.get("obs")
        informacoes_adicionais = request.POST.get("info_adicionais")
        if not cond_pagamento or not conta_deposito:
            messages.add_message(request, messages.ERROR, "Atenção! Conta para depósito e condição de pagamento não podem ficar em branco. Por favor verifique")            
        else:
            contrato = Contrato(orcamento=orcamento, aviso_contrato=obs, info_adic_contrato=informacoes_adicionais, conta_deposito=conta_deposito, cond_pag_contrato=cond_pagamento)
            orcamento.status = "contrato gerado"
            orcamento.save()
            contrato.save()
            messages.add_message(request, messages.SUCCESS, f"Contrato {contrato} gerado com sucesso. Você já pode gerar o PDF e enviar para o cliente")
            return redirect("lista_orçamentos_concluidos")
    return render(request, "form_contrato.html", {"orcamento": orcamento, "total_diarias": total_diarias, "cond_pag": cond_pag, "info_adic_contrato": info_adic_contrato, "aviso_contrato":aviso_contrato, "cond_pag_contrato": cond_pag_contrato, "contas_deposito":contas_deposito})

@login_required(login_url="login")
def visualizar_pdf_contrato(request, id):
    orc = Orcamento.objects.get(id=id)
    obs_contrato = Contrato.objects.get(orcamento=orc)
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()
    ## fontes do report lab
    #Courier
    bold1 = "Courier-Bold"
    bold2 = "Courier-BoldOblique"
    #Courier-Oblique
    padr = "Helvetica" #padrão
    padr_bold = "Helvetica-Bold"   #padrão
    bold4 = "Helvetica-BoldOblique"
    #Helvetica-Oblique
    #Symbol
    bold5 = "Times-Bold"
    #Times-BoldItalic
    #Times-Italic
    #Times-Roman
    #ZapfDingbats

    ### variáveis do projeto
    if orc.modificado:
        modificado = "***Modificado"
        motivo = f"Motivo: {orc.obs_modificacao}"
    else:
        modificado = ""
        motivo = ""
    
    data_contrato = f"{datetime.strftime(obs_contrato.data_contrato, '%d de %b de %Y')}"
    #print (data_contrato)
    n_orçamento=f"{orc.id}"
    hospede = f"{orc.cliente}"
    empreendimento= f"{orc.acomodacao.empreendimento}"
    acomodação = f"{orc.acomodacao}"
    entrada = f"{datetime.strftime(orc.data_entrada, '%d/%m/%Y')} - {orc.dia_entrada} - {orc.checkin}"
    saída =  f"{datetime.strftime(orc.data_saida, '%d/%m/%Y')} - {orc.dia_saida} - {orc.checkout}"
    tot_diárias =f"{orc.n_dias}"
    tot_ocupantes= f"{orc.n_ocupantes}"
    obs_ocupantes=f"{orc.obs_n_ocupantes}"
    perido = f"{orc.periodo}"
    if orc.diaria_cheia:
        tipo_diária="DIÁRIA CHEIA"
    else:
        tipo_diária="PERNOITE"
    valor_diaria=f"R$ {orc.valor_diaria:.2f}"
    tx_limpeza=  f"R$ {orc.taxa_limpeza:.2f}"
    valor_pacote=f"R$ {orc.valor_pacote}"
    dias_pacote=f"{orc.dias_pacote}"
    tot_valor_diarias = orc.valor_diaria*(orc.n_dias-orc.dias_pacote)
    tot_valor_diarias = f"{tot_valor_diarias:.2f}"
    tot_valor_pacote=f"{orc.valor_pacote}"
    tot_tx_limpeza=f"{orc.taxa_limpeza}"
    tot_acrescimo=f"{orc.acrescimos}"
    tot_desconto=f"{orc.descontos}"
    total_valor=f"{orc.total_valor_reserva}"

    ##observaçoes
    #condições de pagamento
    condiçao_pag =f"""{obs_contrato.cond_pag_contrato}"""
    #obs importantes
    dados_banco =f"""{obs_contrato.conta_deposito}"""
    #obs_importante = f'''{obs_contrato.aviso_contrato}'''

    #informações adicionias
    info_adicional_contrato=f"""{obs_contrato.info_adic_contrato}"""
    importante_contrato=f"""{obs_contrato.aviso_contrato}"""




    info = importante_contrato + "\n\n" + info_adicional_contrato


    #descrição da acomodação
    desc_acomod=f"""{orc.acomodacao.descricao}"""

    ##### inicio do projeto ########

    #transforma mm em pontos
    def mm2p(mm):
        return mm/0.352777
    ## gera nome do arquivo personalizado para cada cliente
    cliente = hospede.replace("(","-").replace(")","-").replace("/","-")
    arquivo = f"Dados de Reserva contrato-{n_orçamento}-{acomodação} {cliente}.pdf"
    cnv =  canvas.Canvas(buffer, pagesize=A4)

    cnv.setTitle(f"Dados de Reserva-contrato n-{n_orçamento} de {hospede} {acomodação}")

    #desenhar um retangulo informa x inicial, y inicial , largura e altura
    cnv.rect(mm2p(2),mm2p(2),mm2p(205),mm2p(293))

    ##### fazendo um cabeçalho ######
    #desenhar um retangulo para cabeçalho
    cnv.rect(mm2p(2),mm2p(250),mm2p(205),mm2p(45))
    #desenhar uma imagem
    cnv.drawImage("templates/static/img/LOGO.png",mm2p(3),mm2p(251),width=mm2p(30),height=mm2p(40))
    cnv.setFontSize(15)
    cnv.setFont(padr_bold,15)
    cnv.drawCentredString(320,810,"RESIDENCIAL SOL DE VERÃO & MORADAS PÉ NA AREIA")
    cnv.setFontSize(18)

    cnv.setFillColor("green")
    cnv.drawCentredString(320,780,"DADOS DA RESERVA/CONTRATO SIMPLIFICADO")
    cnv.setFillColor('red')
    cnv.setFont(padr_bold,14)
    cnv.drawCentredString(320,750, empreendimento)
    cnv.setFillColor('black')

    cnv.setFillColor('blue')
    cnv.setFont(padr_bold,10)
    #cnv.drawCentredString(320,750,"NÚMERO DO ORÇAMENTO: ")
    cnv.drawRightString(500,713,"CONTRATO Nº: ")
    cnv.setFillColor('black')
    cnv.setFont(padr,13)
    cnv.drawRightString(570,713, n_orçamento)
    cnv.setFillColor('black')
    
    cnv.setFillColor('blue')
    cnv.setFont(padr_bold,10)
    cnv.drawString(110,713,"DATA DO CONTRATO: ")
    cnv.setFillColor('black')
    cnv.setFont(padr,13)
    cnv.drawString(225,713, data_contrato)
    cnv.setFillColor('black')


    #linha 1
    linha=243
    desconto =  5
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha),"HÓSPEDE:")
    cnv.setFont(padr,12)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(24),mm2p(linha),hospede)

    #linha 2
    linha = linha-desconto
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha),"ACOMODAÇÃO:")
    cnv.setFont(padr,12)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(33),mm2p(linha),acomodação)

    #linha 3
    linha = linha-desconto
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha),"DATA DE ENTRADA(check in):")
    cnv.setFont(padr,12)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(60),mm2p(linha),entrada)

    #linha 4
    linha = linha-desconto
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha),"DATA DE SAÍDA(check out):")
    cnv.setFont(padr,12)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(60),mm2p(linha),saída)

    cnv.rect(mm2p(2),mm2p(linha-4),mm2p(205),mm2p(0))

    #linha 5  TOTAL DE  DIÁRIA, OCUPANTES E TIPO DE DIÁRIA
    linha = linha-desconto-6
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha),"TOTAL DE DIÁRIAS:")
    cnv.setFont(padr,18)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(39),mm2p(linha),tot_diárias)

    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(50),mm2p(linha),"TOTAL DE OCUPANTES:")
    cnv.setFont(padr,18)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(96),mm2p(linha),tot_ocupantes)
    cnv.setFont(padr,10)
    cnv.drawString(mm2p(105),mm2p(linha),obs_ocupantes)
    cnv.setFillColor("green")
    cnv.setFont(padr_bold,7)
    cnv.drawRightString(mm2p(205),mm2p(linha-1),tipo_diária)
    cnv.drawRightString(mm2p(205),mm2p(linha+4),perido)
    cnv.setFont(padr,10)

    cnv.rect(mm2p(2),mm2p(linha-4),mm2p(205),mm2p(0))

    # linha 6 - VALORES  INDIVIDUAIS
    linha = linha-desconto-6
    fonte_destaque=14      
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha),"VALOR DA DIÁRIA:")
    cnv.setFont(padr,fonte_destaque)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(39),mm2p(linha),valor_diaria)

    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(100),mm2p(linha),"TX DE LIMPEZA:")
    cnv.setFont(padr,fonte_destaque)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(150),mm2p(linha),tx_limpeza)
    cnv.setFont(padr,10)

    #LINHA7
    linha = linha-desconto-2

    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha),"VALOR DO PACOTE:")
    cnv.setFont(padr,fonte_destaque)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(39),mm2p(linha),valor_pacote)

    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(100),mm2p(linha)," QUANTIDADE DIAS DO PACOTE:")
    cnv.setFont(padr,fonte_destaque)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(160),mm2p(linha),dias_pacote)
    cnv.setFont(padr,10)

    cnv.rect(mm2p(2),mm2p(linha-4),mm2p(205),mm2p(0))

    ## grade do calculo do orçamento
    cnv.rect(mm2p(2),mm2p(linha-45),mm2p(80),mm2p(41))
    cnv.rect(mm2p(2),mm2p(linha-45),mm2p(205),mm2p(41))

    #coluna de CALCULO DO ORÇAMENTO
    size_calculo = 12
    linha_coluna_calculo = linha-desconto-4
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha_coluna_calculo),"CALCULO DO ORÇAMENTO:")
    cnv.setFont(padr,fonte_destaque)
    cnv.setFillColor("black")

    linha_coluna_calculo = linha_coluna_calculo-desconto-2
    cnv.setFont(padr_bold,8)
    cnv.setFillColor("blue")
    cnv.drawString(mm2p(3),mm2p(linha_coluna_calculo),"Total das diárias ==> ")
    cnv.setFont(padr,size_calculo)
    cnv.setFillColor("black")
    cnv.drawRightString(mm2p(65),mm2p(linha_coluna_calculo), tot_valor_diarias)

    linha_coluna_calculo = linha_coluna_calculo-desconto
    cnv.setFont(padr_bold,8)
    cnv.setFillColor("blue")
    cnv.drawString(mm2p(3),mm2p(linha_coluna_calculo),"Valor do Pacote  ==> ")
    cnv.setFont(padr,size_calculo)
    cnv.setFillColor("black")
    cnv.drawRightString(mm2p(65),mm2p(linha_coluna_calculo), tot_valor_pacote)

    linha_coluna_calculo = linha_coluna_calculo-desconto
    cnv.setFont(padr_bold,8)
    cnv.setFillColor("blue")
    cnv.drawString(mm2p(3),mm2p(linha_coluna_calculo),"Taxa de Limpeza ==> ")
    cnv.setFont(padr,size_calculo)
    cnv.setFillColor("black")
    cnv.drawRightString(mm2p(65),mm2p(linha_coluna_calculo), tot_tx_limpeza)

    linha_coluna_calculo = linha_coluna_calculo-desconto
    cnv.setFont(padr_bold,8)
    cnv.setFillColor("blue")
    cnv.drawString(mm2p(3),mm2p(linha_coluna_calculo),"Acréscimos ==> ")
    cnv.setFont(padr,size_calculo)
    cnv.setFillColor("black")
    cnv.drawRightString(mm2p(65),mm2p(linha_coluna_calculo), tot_acrescimo)

    linha_coluna_calculo = linha_coluna_calculo-desconto
    cnv.setFont(padr_bold,8)
    cnv.setFillColor("blue")
    cnv.drawString(mm2p(3),mm2p(linha_coluna_calculo),"Descontos ==> ")
    cnv.setFont(padr,size_calculo)
    cnv.setFillColor("red")
    cnv.drawRightString(mm2p(65),mm2p(linha_coluna_calculo), tot_desconto)
    cnv.setFillColor("black")

    linha_coluna_calculo = linha_coluna_calculo-desconto
    cnv.setFont(padr_bold,11)
    cnv.setFillColor("blue")
    cnv.drawString(mm2p(3),mm2p(linha_coluna_calculo),"TOTAL ==> ")
    cnv.setFont(padr_bold,size_calculo+3)
    cnv.setFillColor("black")
    cnv.drawRightString(mm2p(65),mm2p(linha_coluna_calculo), total_valor)
    cnv.setFillColor("black")

    #coluna observações

    size_calculo = 12
    linha_coluna_obs = linha-desconto-4
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(85),mm2p(linha_coluna_obs),"DADOS BANCÁRIOS PARA O PAGAMENTO :")
    cnv.setFont(padr,3)
    cnv.setFillColor("black")

    from reportlab.lib.styles import ParagraphStyle

    estilo_obs = ParagraphStyle('Body', fontName=bold1, fontSize=10, leading=12, spaceBefore=20, textColor="black",backColor="#f1f1f1")

    obs = dados_banco.replace("\n","<BR/>")
    p = Paragraph(obs,estilo_obs)

    p.wrapOn(cnv, 340, 100)
    p.drawOn(cnv, 240, 450)

    #condições de pagamento
    size_calculo = 12
    linha_f_pagto = linha_coluna_calculo-9
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha_f_pagto),"CONDIÇÕES DE PAGAMENTO:")
    cnv.setFont(padr,fonte_destaque)
    cnv.setFillColor("black")

    cnv.rect(mm2p(2),mm2p(linha_f_pagto-30),mm2p(205),mm2p(0))

    estilo_cond_pag = ParagraphStyle('Body', fontName=padr_bold, fontSize=8, leading=10, spaceBefore=20, textColor="green",backColor="#f1f1f1")
    cond_pag= condiçao_pag.replace("\n","<BR/>")
    p_cond_pag = Paragraph(cond_pag,estilo_cond_pag)

    p_cond_pag.wrapOn(cnv, 570, 100)
    p_cond_pag.drawOn(cnv, 10, 350)

    ####  coluna informações adicionias importante ######
    linha_info = linha_f_pagto-35
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha_info),"INFORMAÇÕES ADICIONAIS:  (ATENÇÃO IMPORTANTE)")
    cnv.setFont(padr,fonte_destaque)
    cnv.setFillColor("black")

    estilo_info = ParagraphStyle('Body', fontName=padr_bold, fontSize=7, leading=7, spaceBefore=10, textColor="blue",alignment=0,backColor="#f1f1f1")

    testeinfo=info.replace("\n","<BR/>")

    p_info = Paragraph(testeinfo,estilo_info)

    p_info.wrapOn(cnv, 270, 80)
    p_info.drawOn(cnv, 10, 50)


    ###### coluna descrição acomodação ####


    coluna = mm2p(105)
    cnv.rect(mm2p(102),mm2p(2),mm2p(105),mm2p(117))
    linha_info = linha_f_pagto-35
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(coluna,mm2p(linha_info),"BREVE DESCRIÇÃO DA ACOMODAÇÃO:")
    cnv.setFont(padr,fonte_destaque)
    cnv.setFillColor("black")

    estilo_desc_acomod = ParagraphStyle('Body', fontName=padr_bold, fontSize=8, leading=10, spaceBefore=20, textColor="black",alignment=0,backColor="#f1f1f1")

    acomod=desc_acomod.replace("\n","<BR/>")

    p_info = Paragraph(acomod,estilo_desc_acomod)

    p_info.wrapOn(cnv, 270, 80)
    p_info.drawOn(cnv, coluna+5, 50)

    cnv.setFont(padr, 7)
    cnv.drawRightString(mm2p(200), mm2p(7), modificado)
    cnv.drawRightString(mm2p(200), mm2p(5), motivo)
    

    #cnv.rect(mm2p(2),mm2p(linha-45),mm2p(205),mm2p(41))

    cnv.showPage()
    cnv.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename=arquivo)

@login_required(login_url="login")
def lista_orçamentos_geral(request):
    termo_cliente = request.GET.get("termo_cliente")
    if termo_cliente:
        termo_cliente = termo_cliente.strip()
        orcamentos = Orcamento.objects.all().filter(
            Q(cliente__nome__icontains=termo_cliente) | Q(cliente__telefone__icontains=termo_cliente) | Q(cliente__obs__icontains=termo_cliente) | Q(acomodacao__nome__icontains=termo_cliente), eliminado=False
        ).order_by("-id")
    else:
        orcamentos = Orcamento.objects.all().filter(
            eliminado=False
        ).order_by("-id")
    if len(orcamentos) == 0:
        messages.add_message(request, messages.WARNING, f"Nenhum orçamento encontrado com o termo {termo_cliente}")
    paginator = Paginator(orcamentos, 10)
    page = request.GET.get('p')
    orcamentos = paginator.get_page(page)
    return render(request, "lista_orcamentos_geral.html", {"orcamentos": orcamentos})


@login_required(login_url="login")
def lista_eliminar_orcamento(request):
    termo_cliente = request.GET.get("termo_cliente")
    if termo_cliente:
        termo_cliente = termo_cliente.strip()
        orcamentos = Orcamento.objects.all().filter(
            Q(cliente__nome__icontains=termo_cliente) | Q(cliente__telefone__icontains=termo_cliente) | Q(cliente__obs__icontains=termo_cliente) | Q(acomodacao__nome__icontains=termo_cliente),
        ).exclude(
            status="contrato gerado"
        ).order_by("-id")
    else:
        orcamentos = Orcamento.objects.all().exclude(
            status="contrato gerado"
        ).order_by("-id")
    if len(orcamentos) == 0:
        messages.add_message(request, messages.WARNING, f"Nenhum orçamento encontrado com o termo {termo_cliente}")
    paginator = Paginator(orcamentos, 10)
    page = request.GET.get('p')
    orcamentos = paginator.get_page(page)
    return render(request, "lista_eliminar_orcamento.html", {"orcamentos": orcamentos})

@login_required(login_url="login")
def eliminar_orcamento(request, id):
    orcamento = Orcamento.objects.get(id=id)
    if orcamento.eliminado:
        orcamento.eliminado = False
        messages.add_message(request, messages.INFO, f"Orçamento {orcamento.id} de {orcamento} reativado com sucesso")
    else:
        orcamento.eliminado = True
        messages.add_message(request, messages.INFO, f"Orçamento {orcamento.id} de {orcamento} eliminado com sucesso")
    orcamento.save()
    return redirect("lista_eliminar_orcamento")

@login_required(login_url="login")
def lista_eliminar_contrato(request):
    termo_cliente = request.GET.get("termo_cliente")
    if termo_cliente:
        termo_cliente = termo_cliente.strip()
        orcamentos = Orcamento.objects.all().filter(
            Q(cliente__nome__icontains=termo_cliente) | Q(cliente__telefone__icontains=termo_cliente) | Q(cliente__obs__icontains=termo_cliente) | Q(acomodacao__nome__icontains=termo_cliente), status="contrato gerado", quitado=False
        ).order_by("-id")
    else:
        orcamentos = Orcamento.objects.all().filter(
            status="contrato gerado", quitado=False
        ).order_by("-id")
    if len(orcamentos) == 0:
        messages.add_message(request, messages.WARNING, f"Nenhum orçamento encontrado com o termo {termo_cliente}")
    paginator = Paginator(orcamentos, 10)
    page = request.GET.get('p')
    orcamentos = paginator.get_page(page)
    return render(request, "lista_eliminar_contrato.html", {"orcamentos": orcamentos})

@login_required(login_url="login")
def eliminar_contrato(request, id):
    orcamento = Orcamento.objects.get(id=id)
    contrato = Contrato.objects.all().filter(orcamento=orcamento)
    orcamento.eliminado = True
    orcamento.status = "orçamento gerado"
    contrato.delete()
    messages.add_message(request, messages.INFO, f"Contrato {orcamento.id} de {orcamento} foi eliminado com sucesso, caso queira utilizar e alterar este orçamentro, deve primeiro reativar o orçamento, logo em seguida fazer as alterações necessárias e depois gerar novo orçamento e novo contrato")
    orcamento.save()
    return redirect("lista_eliminar_contrato")

@login_required(login_url="login")
def lista_alterar_orcamento(request):
    termo_cliente = request.GET.get("termo_cliente")
    if termo_cliente:
        termo_cliente = termo_cliente.strip()
        orcamentos = Orcamento.objects.all().filter(
            Q(cliente__nome__icontains=termo_cliente) | Q(cliente__telefone__icontains=termo_cliente) | Q(cliente__obs__icontains=termo_cliente) | Q(acomodacao__nome__icontains=termo_cliente), eliminado=False
        ).exclude(
            status="contrato gerado"
        ).exclude(
            eliminado=True
        ).order_by("-id")
    else:
        orcamentos = Orcamento.objects.all().exclude(
            status="contrato gerado", eliminado=False
        ).exclude(
            eliminado=True
        ).order_by("-id")
    if len(orcamentos) == 0:
        messages.add_message(request, messages.WARNING, f"Nenhum orçamento encontrado com o termo {termo_cliente}")
    paginator = Paginator(orcamentos, 10)
    page = request.GET.get('p')
    orcamentos = paginator.get_page(page)
    return render(request, "lista_alterar_orcamento.html", {"orcamentos": orcamentos})

@login_required(login_url="login")
def alterar_orcamento(request, id):
    orcamento = Orcamento.objects.get(id=id)
    acomodacoes = Acomodacao.objects.all()
    periodos = Periodo.objects.all()
    checkin = Horario.objects.all().filter(
        checkin=True
    )
    checkout = Horario.objects.all().filter(
        checkin=False
    )
    valor = str(orcamento.valor_diaria)
    taxa_limpeza = str(orcamento.taxa_limpeza)
    descontos = str(orcamento.descontos)
    acrescimos = str(orcamento.acrescimos)
    valor_pacote = str(orcamento.valor_pacote)
    dias_pacote = str(orcamento.dias_pacote)
    info_adic = Observacao.objects.all().filter(
        tipo__tipo="Informações adicionais orçamento"
    )
    obs_orc = Observacao.objects.all().filter(
        tipo__tipo="Observações orçamento"
    )
    cond_pag_orc = Observacao.objects.all().filter(
        tipo__tipo="Condições de pagamento orçamento"
    )
    data_entrada = datetime.strftime(orcamento.data_entrada, "%Y-%m-%d")
    data_saida = datetime.strftime(orcamento.data_saida, "%Y-%m-%d")
    obs_orcamento = ObsOrcamento.objects.get(orcamento=orcamento)
    if request.method != "POST":
        return render(request, "form_alterar_orcamento.html", {"orcamento": orcamento, "acomodacoes": acomodacoes, "periodos": periodos, "checkin": checkin, "checkout": checkout, "valor": valor, "taxa_limpeza": taxa_limpeza, "descontos": descontos, "acrescimos": acrescimos, "valor_pacote": valor_pacote, "dias_pacote": dias_pacote, "info_adic": info_adic, "obs_orc": obs_orc, "cond_pag_orc": cond_pag_orc, "data_entrada": data_entrada, "data_saida": data_saida, "obs_orcamento": obs_orcamento})
    else:
        tot_diarias = request.POST.get("valor_diaria").replace("R$ ", "")
        tot_pacote = request.POST.get("tot_pacote").replace("R$ ", "")
        tot_taxa_limpeza = request.POST.get("tot_taxa_limpeza").replace("R$ ", "")
        tot_descontos = request.POST.get("tot_descontos").replace("R$ ", "")
        tot_acrescimos = request.POST.get("tot_acrescimos").replace("R$ ", "")
        dias_pacote = request.POST.get("dias_pacote")
        tot_reserva = request.POST.get("tot_reserva").replace("R$ ", "")
        cond_pag = request.POST.get("cond_pag")
        obs = request.POST.get("obs")
        info_adicionais = request.POST.get("info_adicionais")
        acomodacao = Acomodacao.objects.get(id=int(request.POST.get("acomodacao")))
        periodo = request.POST.get("periodo")
        checkin_post = request.POST.get("checkin")
        checkout_post = request.POST.get("checkout")
        entrada = datetime.strptime(request.POST.get("entrada"), "%Y-%m-%d")
        saida = datetime.strptime(request.POST.get("saida"), "%Y-%m-%d")
        dia_entrada = request.POST.get("dia_entrada")
        dia_saida = request.POST.get("dia_saida")
        cheia = bool(request.POST.get("cheia"))
        n_ocupantes = request.POST.get("n_ocupantes")
        obs_n_ocupantes = request.POST.get("obs_n_ocupantes")
        n_dias = request.POST.get("n_dias")
        motivo = request.POST.get("motivo")
        valor_diaria = request.POST.get("valor_diaria")
        """print(tot_diarias)
        print(tot_pacote)
        print(tot_taxa_limpeza)
        print(tot_descontos)
        print(tot_acrescimos)
        print(dias_pacote)
        print(tot_reserva)
        print(cond_pag)
        print(obs)
        print(info_adicionais)
        print(acomodacao)
        print(periodo)
        print(checkin_post)
        print(checkout_post)
        print(entrada)
        print(saida)
        print(dia_entrada)
        print(dia_saida)
        print(cheia)
        print(n_ocupantes)
        print(obs_n_ocupantes)
        print(n_dias)
        print(valor_diaria)"""
        if not motivo:
            messages.add_message(request, messages.ERROR, "É obrigatório informar o motivo da alteração do orçamento")
            return render(request, "form_alterar_orcamento.html", {"orcamento": orcamento, "acomodacoes": acomodacoes, "periodos": periodos, "checkin": checkin, "checkout": checkout, "valor": valor, "taxa_limpeza": taxa_limpeza, "descontos": descontos, "acrescimos": acrescimos, "valor_pacote": valor_pacote, "dias_pacote": dias_pacote, "info_adic": info_adic, "obs_orc": obs_orc, "cond_pag_orc": cond_pag_orc, "data_entrada": data_entrada, "data_saida": data_saida, "obs_orcamento": obs_orcamento})
        if not tot_diarias or not tot_pacote or not tot_taxa_limpeza or not tot_descontos or not tot_acrescimos or not dias_pacote or not tot_reserva or not cond_pag or not obs or not info_adicionais or not acomodacao or not periodo or not checkin_post or not checkout_post or not entrada or not saida or not dia_entrada or not dia_saida or not n_ocupantes:
            messages.add_message(request, messages.ERROR, "Nenhum campo pode ficar em branco. Por favor verifique")
            return render(request, "form_alterar_orcamento.html", {"orcamento": orcamento, "acomodacoes": acomodacoes, "periodos": periodos, "checkin": checkin, "checkout": checkout, "valor": valor, "taxa_limpeza": taxa_limpeza, "descontos": descontos, "acrescimos": acrescimos, "valor_pacote": valor_pacote, "dias_pacote": dias_pacote, "info_adic": info_adic, "obs_orc": obs_orc, "cond_pag_orc": cond_pag_orc, "data_entrada": data_entrada, "data_saida": data_saida, "obs_orcamento": obs_orcamento})
        tot_diarias = float(tot_diarias)
        tot_pacote = float(tot_pacote)
        tot_taxa_limpeza = float(tot_taxa_limpeza)
        tot_descontos = float(tot_descontos)
        tot_acrescimos = float(tot_acrescimos)
        dias_pacote = int(dias_pacote)
        tot_reserva = float(tot_reserva)
        valor_diaria = float(valor_diaria)
        if tot_reserva == 0.0:
            messages.add_message(request, messages.ERROR, "Total da reserva não pode ser zero. Por favor verifique")
            return render(request, "form_alterar_orcamento.html", {"orcamento": orcamento, "acomodacoes": acomodacoes, "periodos": periodos, "checkin": checkin, "checkout": checkout, "valor": valor, "taxa_limpeza": taxa_limpeza, "descontos": descontos, "acrescimos": acrescimos, "valor_pacote": valor_pacote, "dias_pacote": dias_pacote, "info_adic": info_adic, "obs_orc": obs_orc, "cond_pag_orc": cond_pag_orc, "data_entrada": data_entrada, "data_saida": data_saida, "obs_orcamento": obs_orcamento})
        orcamento.status = "digitação concluída"
        orcamento.modificado = True
        orcamento.obs_modificacao = motivo
        orcamento.acomodacao = acomodacao
        orcamento.valor_diaria = valor_diaria
        orcamento.taxa_limpeza = tot_taxa_limpeza
        orcamento.descontos = tot_descontos
        orcamento.acrescimos = tot_acrescimos
        orcamento.valor_pacote = valor_pacote
        orcamento.dias_pacote = dias_pacote
        orcamento.total_valor_reserva = tot_reserva
        orcamento.periodo = periodo
        orcamento.checkin = checkin_post
        orcamento.checkout = checkout_post
        orcamento.data_entrada = entrada
        orcamento.data_saida = saida
        orcamento.dia_entrada = dia_entrada
        orcamento.dia_saida = dia_saida
        orcamento.diaria_cheia = cheia
        orcamento.n_dias = n_dias
        orcamento.n_ocupantes = n_ocupantes
        orcamento.obs_n_ocupantes = obs_n_ocupantes
        orcamento.data_orcamento = datetime.today()
        obs_orcamento.condicoes_pagamento = cond_pag
        obs_orcamento.obs = obs
        obs_orcamento.informacoes_adicionais = info_adicionais
        orcamento.save()
        obs_orcamento.save()
        messages.add_message(request, messages.SUCCESS, "Orçamento alterado com sucesso. Você já pode gerar o novo PDF do orçamento")
        return redirect("lista_gera_pdf_orcamento")
    
@login_required(login_url="login")
def lista_acomodacoes(request):
    acomodacoes = Acomodacao.objects.all().order_by("-id")
    return render(request, "lista_acomodacoes.html", {"acomodacoes": acomodacoes})

@login_required(login_url="login")
def cadastrar_acomodacao(request):
    empreendimentos = Empreendimento.objects.all()
    if request.method != "POST":
        return render(request, "form_acomodacao.html", {"empreendimentos": empreendimentos})
    else:
        nome = request.POST.get("nome")
        empreendimento = Empreendimento.objects.get(id=int(request.POST.get("empreendimento")))
        tipo = request.POST.get("tipo")
        quartos = int(request.POST.get("quartos"))
        valor_base = float(request.POST.get("valor_base"))
        limite_ideal = int(request.POST.get("limite_ideal"))
        limite_adicional = int(request.POST.get("limite_adicional"))
        pet = bool(request.POST.get("pet"))
        descricao = request.POST.get("descricao")
        if not nome or not empreendimento or not tipo or not descricao:
            messages.add_message(request, messages.ERROR, "Nenhum campo pode ficar vazio. Por favor verifique")
            return render(request, "form_acomodacao.html", {"empreendimentos": empreendimentos})
        else:
            acomodacao = Acomodacao(nome=nome, empreendimento=empreendimento, tipo=tipo, quartos=quartos, valor_base=valor_base, limite_ideal=limite_ideal, limite_adicional=limite_adicional, aceita_pet=pet, descricao=descricao)
            acomodacao.save()
            messages.add_message(request, messages.SUCCESS, f"Acomodação {acomodacao} cadastrada com sucesso")
            return redirect("lista_acomodacoes")
        
@login_required(login_url="login")
def alterar_acomodacao(request, id):
    acomodacao = Acomodacao.objects.get(id=id)
    empreendimentos = Empreendimento.objects.all()
    valor = str(acomodacao.valor_base)
    tipos = ["Apartamento", "Kitnet Simples", "Kitnet Casal", "Kit com sacada", "Sobrado", "Casa", "Flat", "Combo"]
    if request.method != "POST":
        return render(request, "form_alterar_acomodacao.html", {"acomodacao": acomodacao, "empreendimentos": empreendimentos, "tipos": tipos, "valor": valor})
    else:
        nome = request.POST.get("nome")
        empreendimento = Empreendimento.objects.get(id=int(request.POST.get("empreendimento")))
        tipo = request.POST.get("tipo")
        quartos = int(request.POST.get("quartos"))
        valor_base = float(request.POST.get("valor_base"))
        limite_ideal = int(request.POST.get("limite_ideal"))
        limite_adicional = int(request.POST.get("limite_adicional"))
        pet = bool(request.POST.get("pet"))
        descricao = request.POST.get("descricao")
        if not nome or not empreendimento or not tipo or not descricao:
            messages.add_message(request, messages.ERROR, "Nenhum campo pode ficar vazio. Por favor verifique")
            return render(request, "form_alterar_acomodacao.html", {"acomodacao": acomodacao, "empreendimentos": empreendimentos, "tipos": tipos, "valor": valor})
        else:
            acomodacao.nome = nome
            acomodacao.empreendimento = empreendimento
            acomodacao.tipo = tipo
            acomodacao.quartos = quartos
            acomodacao.valor_base = valor_base
            acomodacao.limite_ideal = limite_ideal
            acomodacao.limite_adicional = limite_adicional
            acomodacao.aceita_pet = pet
            acomodacao.descricao = descricao
            acomodacao.save()
            messages.add_message(request, messages.SUCCESS, f"Acomodação {acomodacao} alterada com sucesso")
            return redirect("lista_acomodacoes")
        
@login_required(login_url="login")
def lista_horarios(request):
    horarios = Horario.objects.all().order_by("-checkin")
    return render(request, "lista_horarios.html", {"horarios": horarios})

@login_required(login_url="login")
def cadastrar_horario(request):
    if request.method != "POST":
        return render(request, "form_horario.html")
    else:
        hora = request.POST.get("hora")
        tipo = request.POST.get("checkin")
        if tipo == "checkin":
            checkin = True
        else:
            checkin = False
        if not hora or not tipo:
            messages.add_message(request, messages.ERROR, "Atenção! É necessário descrever o horário, e escolher se será do tipo checkin ou checkout")
            return render(request, "form_horario.html")
        else:
            horario = Horario(hora=hora, checkin=checkin)
            horario.save()
            messages.add_message(request, messages.SUCCESS, f"Horário {horario} do tipo {tipo} cadastrado com sucesso")
            return redirect("lista_horarios")
        
@login_required(login_url="login")
def alterar_horario(request, id):
    horario = Horario.objects.get(id=id)
    if request.method != "POST":
        return render(request, "form_alterar_horario.html", {"horario": horario})
    else:
        hora = request.POST.get("hora")
        tipo = request.POST.get("checkin")
        if tipo == "checkin":
            checkin = True
        else:
            checkin = False
        if not hora or not tipo:
            messages.add_message(request, messages.ERROR, "Atenção! É necessário descrever o horário, e escolher se será do tipo checkin ou checkout")
            return render(request, "form_alterar_horario.html", {"horario": horario})
        else:
            horario.hora = hora
            horario.checkin = checkin
            horario.save()
            messages.add_message(request, messages.SUCCESS, f"Horário {horario} do tipo {tipo} alterado com sucesso")
            return redirect("lista_horarios")
        
@login_required(login_url="login")
def lista_obs(request):
    observacoes = Observacao.objects.all().order_by("tipo")
    return render(request, "lista_obs.html", {"observacoes": observacoes})

@login_required(login_url="login")
def cadastrar_obs(request):
    tipos = TipoObservacao.objects.all()
    if request.method != "POST":
        return render(request, "form_obs.html", {"tipos": tipos})
    else:
        identificacao = request.POST.get("identificacao")
        tipo = TipoObservacao.objects.get(id=int(request.POST.get("tipo")))
        descricao = request.POST.get("descricao")
        if not identificacao or not tipo or not descricao:
            messages.add_message(request, messages.ERROR, "Atenção! Nenhum campo pode ficar vazio")
            return render(request, "form_obs.html", {"tipos": tipos})
        else:
            obs = Observacao(identificacao=identificacao, tipo=tipo, descricao=descricao)
            obs.save()
            messages.add_message(request, messages.SUCCESS, f"Observação {obs.identificacao} cadastrada com sucesso")
            return redirect("lista_obs")
        
@login_required(login_url="login")
def alterar_obs(request, id):
    obs = Observacao.objects.get(id=id)
    tipos = TipoObservacao.objects.all()
    if request.method != "POST":
        return render(request, "form_alterar_obs.html", {"obs": obs, "tipos": tipos})
    else:
        identificacao = request.POST.get("identificacao")
        tipo = TipoObservacao.objects.get(id=int(request.POST.get("tipo")))
        descricao = request.POST.get("descricao")
        if not identificacao or not tipo or not descricao:
            messages.add_message(request, messages.ERROR, "Atenção! Nenhum campo pode ficar vazio")
            return render(request, "form_alterar_obs.html", {"obs": obs, "tipos": tipos})
        else:
            obs.identificacao = identificacao
            obs.tipo = tipo
            obs.descricao = descricao
            obs.save()
            messages.add_message(request, messages.SUCCESS, f"Observação {obs.identificacao} alterada com sucesso")
            return redirect("lista_obs")
        
@login_required(login_url="login")
def lista_confirmar_orcamento(request):
    termo_cliente = request.GET.get("termo_cliente")
    if termo_cliente:
        termo_cliente = termo_cliente.strip()
        orcamentos = Orcamento.objects.all().filter(
            Q(cliente__nome__icontains=termo_cliente) | Q(cliente__telefone__icontains=termo_cliente) | Q(cliente__obs__icontains=termo_cliente) | Q(acomodacao__nome__icontains=termo_cliente), status="contrato gerado", quitado=False
        ).exclude(
            eliminado=True
        ).order_by("-id")
    else:
        orcamentos = Orcamento.objects.all().filter(
        status="contrato gerado", quitado=False
        ).exclude(
            eliminado=True
        ).order_by("-id")
    saldos = []
    for o in orcamentos:
        saldo = o.total_valor_reserva + o.valor_extras - o.valor_pago
        saldos.append(saldo)
    if len(orcamentos) == 0:
        messages.add_message(request, messages.WARNING, f"Nenhum orçamento encontrado com o termo {termo_cliente}")
    paginator = Paginator(orcamentos, 10)
    page = request.GET.get('p')
    orcamentos = paginator.get_page(page)
    orcamentos_saldos = zip(orcamentos, saldos)
    return render(request, "lista_confirmar_orcamento.html", {"orcamentos": orcamentos,"orcamentos_saldos":orcamentos_saldos})

@login_required(login_url="login")
def registrar_pagamento(request, id):
    orcamento = Orcamento.objects.get(id=id)
    lancamentos = Lancamentos.objects.all().filter(
        orcamento=orcamento
    )
    if request.method != "POST":
        return render(request, "form_lancamento.html", {"orcamento": orcamento, "lancamentos": lancamentos})
    else:
        descricao = request.POST.get("descricao")
        data_lancamento = request.POST.get("data_lancamento")
        valor = request.POST.get("valor")
        if not descricao or not data_lancamento or not valor:
            messages.add_message(request, messages.ERROR, "Atenção! Nenhum campo pode ficar vazio. Por favor verifique")
            return render(request, "form_lancamento.html", {"orcamento": orcamento, "lancamentos": lancamentos})
        descricao = descricao.strip().title()
        valor = float(valor)
        data_lancamento = datetime.strptime(data_lancamento, "%Y-%m-%d")
        if valor <= 0:
            messages.add_message(request, messages.ERROR, "Atenção! Valor do lançamento deve ser maior que zero. Por favor verifique")
            return render(request, "form_lancamento.html", {"orcamento": orcamento, "lancamentos": lancamentos})
        orcamento.valor_pago = float(orcamento.valor_pago)+valor
        orcamento.confirmado = True
        lancamento = Lancamentos(orcamento=orcamento, descricao=descricao, data_lancamento=data_lancamento, valor=valor, tipo="pagamento")
        lancamento.save()
        orcamento.save()
        messages.add_message(request, messages.SUCCESS, f"Pagamento de R$ {valor:.2f} lançado com sucesso para o orçamento {orcamento.id}")
        return redirect("lista_confirmar_orcamento")
    
@login_required(login_url="login")
def alterar_pagamento(request, id):
    lancamento = Lancamentos.objects.get(id=id)
    data_lancamento = datetime.strftime(lancamento.data_lancamento, "%Y-%m-%d")
    valor = str(lancamento.valor)
    if request.method != "POST":
        return render(request, "form_alterar_lancamento.html", {"lancamento": lancamento, "data_lancamento": data_lancamento, "valor": valor})
    else:
        nova_descricao = request.POST.get("descricao")
        nova_data_lancamento = request.POST.get("data_lancamento")
        novo_valor = request.POST.get("valor")
        if not nova_descricao or not nova_data_lancamento or not novo_valor:
            messages.add_message(request, messages.ERROR, "Atenção! Nenhum campo pode ficar vazio. Por favor verifique")
            return render(request, "form_alterar_lancamento.html", {"lancamento": lancamento, "data_lancamento": data_lancamento, "valor": valor})
        lancamento.orcamento.valor_pago = float(lancamento.orcamento.valor_pago)-float(lancamento.valor)
        nova_descricao = nova_descricao.strip().title()
        novo_valor = float(novo_valor)
        nova_data_lancamento = datetime.strptime(nova_data_lancamento, "%Y-%m-%d")
        if novo_valor <= 0:
            messages.add_message(request, messages.ERROR, "Atenção! Valor do lançamento deve ser maior que zero. Por favor verifique")
            return render(request, "form_alterar_lancamento.html", {"lancamento": lancamento, "data_lancamento": data_lancamento, "valor": valor})
        lancamento.orcamento.valor_pago = float(lancamento.orcamento.valor_pago)+novo_valor
        lancamento.descricao = nova_descricao
        lancamento.data_lancamento = nova_data_lancamento
        lancamento.valor = novo_valor
        lancamento.save()
        lancamento.orcamento.save()
        messages.add_message(request, messages.SUCCESS, f"Pagamento alterado com sucesso para o orçamento {lancamento.orcamento.id}")
        return redirect("lista_confirmar_orcamento")

@login_required(login_url="login")
def excluir_pagamento(request, id):
    lancamento = Lancamentos.objects.get(id=id)
    lancamento.orcamento.valor_pago = float(lancamento.orcamento.valor_pago)-float(lancamento.valor)
    if lancamento.orcamento.valor_pago == 0:
        lancamento.orcamento.confirmado = False
    lancamento.orcamento.save()
    messages.add_message(request, messages.SUCCESS, f"Lançamento {lancamento.id} excluido com sucesso para o orçamento {lancamento.orcamento.id}")
    lancamento.delete()
    return redirect("lista_confirmar_orcamento")

@login_required(login_url="login")
def registrar_extra(request, id):
    orcamento = Orcamento.objects.get(id=id)
    lancamentos = Lancamentos.objects.all().filter(
        orcamento=orcamento
    )
    if request.method != "POST":
        return render(request, "form_extras.html", {"orcamento": orcamento, "lancamentos": lancamentos})
    else:
        descricao = request.POST.get("descricao")
        data_lancamento = request.POST.get("data_lancamento")
        valor = request.POST.get("valor")
        if not descricao or not data_lancamento or not valor:
            messages.add_message(request, messages.ERROR, "Atenção! Nenhum campo pode ficar vazio. Por favor verifique")
            return render(request, "form_extras.html", {"orcamento": orcamento, "lancamentos": lancamentos})
        descricao = descricao.strip().title()
        valor = float(valor)
        data_lancamento = datetime.strptime(data_lancamento, "%Y-%m-%d")
        if valor <= 0:
            messages.add_message(request, messages.ERROR, "Atenção! Valor do lançamento deve ser maior que zero. Por favor verifique")
            return render(request, "form_extras.html", {"orcamento": orcamento, "lancamentos": lancamentos})
        orcamento.valor_extras = float(orcamento.valor_extras)+valor
        lancamento = Lancamentos(orcamento=orcamento, descricao=descricao, data_lancamento=data_lancamento, valor=valor, tipo="acréscimo")
        lancamento.save()
        orcamento.save()
        messages.add_message(request, messages.SUCCESS, f"Cobrança extra de R$ {valor:.2f} lançada com sucesso para o orçamento {orcamento.id}")
        return redirect("lista_confirmar_orcamento")
    
@login_required(login_url="login")
def alterar_extra(request, id):
    lancamento = Lancamentos.objects.get(id=id)
    data_lancamento = datetime.strftime(lancamento.data_lancamento, "%Y-%m-%d")
    valor = str(lancamento.valor)
    if request.method != "POST":
        return render(request, "form_alterar_extra.html", {"lancamento": lancamento, "data_lancamento": data_lancamento, "valor": valor})
    else:
        nova_descricao = request.POST.get("descricao")
        nova_data_lancamento = request.POST.get("data_lancamento")
        novo_valor = request.POST.get("valor")
        if not nova_descricao or not nova_data_lancamento or not novo_valor:
            messages.add_message(request, messages.ERROR, "Atenção! Nenhum campo pode ficar vazio. Por favor verifique")
            return render(request, "form_alterar_extra.html", {"lancamento": lancamento, "data_lancamento": data_lancamento, "valor": valor})
        lancamento.orcamento.valor_extras = float(lancamento.orcamento.valor_extras)-float(lancamento.valor)
        nova_descricao = nova_descricao.strip().title()
        novo_valor = float(novo_valor)
        nova_data_lancamento = datetime.strptime(nova_data_lancamento, "%Y-%m-%d")
        if novo_valor <= 0:
            messages.add_message(request, messages.ERROR, "Atenção! Valor do lançamento deve ser maior que zero. Por favor verifique")
            return render(request, "form_alterar_extra.html", {"lancamento": lancamento, "data_lancamento": data_lancamento, "valor": valor})
        lancamento.orcamento.valor_extras = float(lancamento.orcamento.valor_extras)+novo_valor
        lancamento.descricao = nova_descricao
        lancamento.data_lancamento = nova_data_lancamento
        lancamento.valor = novo_valor
        lancamento.save()
        lancamento.orcamento.save()
        messages.add_message(request, messages.SUCCESS, f"Cobrança extra alterada com sucesso para o orçamento {lancamento.orcamento.id}")
        return redirect("lista_confirmar_orcamento")
    
@login_required(login_url="login")
def excluir_extra(request, id):
    lancamento = Lancamentos.objects.get(id=id)
    lancamento.orcamento.valor_extras = float(lancamento.orcamento.valor_extras)-float(lancamento.valor)
    lancamento.orcamento.save()
    messages.add_message(request, messages.SUCCESS, f"Lançamento {lancamento.id} excluido com sucesso para o orçamento {lancamento.orcamento.id}")
    lancamento.delete()
    return redirect("lista_confirmar_orcamento")

@login_required(login_url="login")
def lista_orcamentos_confirmados(request):
    termo_cliente = request.GET.get("termo_cliente")
    if termo_cliente:
        termo_cliente = termo_cliente.strip()
        orcamentos = Orcamento.objects.all().filter(
            Q(cliente__nome__icontains=termo_cliente) | Q(cliente__telefone__icontains=termo_cliente) | Q(cliente__obs__icontains=termo_cliente) | Q(acomodacao__nome__icontains=termo_cliente), status="contrato gerado", confirmado=True, quitado=False
        ).exclude(
            eliminado=True
        ).order_by("-id")
    else:
        orcamentos = Orcamento.objects.all().filter(
        status="contrato gerado", confirmado=True, quitado=False
        ).exclude(
            eliminado=True
        ).order_by("-id")
    saldos = []
    for o in orcamentos:
        saldo = o.total_valor_reserva + o.valor_extras - o.valor_pago
        saldos.append(saldo)
    if len(orcamentos) == 0:
        messages.add_message(request, messages.WARNING, f"Nenhum orçamento encontrado com o termo {termo_cliente}")
    paginator = Paginator(orcamentos, 10)
    page = request.GET.get('p')
    orcamentos = paginator.get_page(page)
    orcamentos_saldos = zip(orcamentos, saldos)
    return render(request, "lista_orcamentos_confirmados.html", {"orcamentos": orcamentos,"orcamentos_saldos":orcamentos_saldos})

@login_required(login_url="login")
def lista_orcamentos_pendentes(request):
    termo_cliente = request.GET.get("termo_cliente")
    if termo_cliente:
        termo_cliente = termo_cliente.strip()
        orcamentos = Orcamento.objects.all().filter(
            Q(cliente__nome__icontains=termo_cliente) | Q(cliente__telefone__icontains=termo_cliente) | Q(cliente__obs__icontains=termo_cliente) | Q(acomodacao__nome__icontains=termo_cliente), status="contrato gerado", confirmado=False, quitado=False
        ).exclude(
            eliminado=True
        ).order_by("-id")
    else:
        orcamentos = Orcamento.objects.all().filter(
        status="contrato gerado", confirmado=False, quitado=False
        ).exclude(
            eliminado=True
        ).order_by("-id")
    saldos = []
    for o in orcamentos:
        saldo = o.total_valor_reserva + o.valor_extras - o.valor_pago
        saldos.append(saldo)
    if len(orcamentos) == 0:
        messages.add_message(request, messages.WARNING, f"Nenhum orçamento encontrado com o termo {termo_cliente}")
    paginator = Paginator(orcamentos, 10)
    page = request.GET.get('p')
    orcamentos = paginator.get_page(page)
    orcamentos_saldos = zip(orcamentos, saldos)
    return render(request, "lista_orcamentos_pendentes.html", {"orcamentos": orcamentos,"orcamentos_saldos":orcamentos_saldos})

@login_required(login_url="login")
def lista_orcamentos_quitados(request):
    termo_cliente = request.GET.get("termo_cliente")
    if termo_cliente:
        termo_cliente = termo_cliente.strip()
        orcamentos = Orcamento.objects.all().filter(
            Q(cliente__nome__icontains=termo_cliente) | Q(cliente__telefone__icontains=termo_cliente) | Q(cliente__obs__icontains=termo_cliente) | Q(acomodacao__nome__icontains=termo_cliente), status="contrato gerado", confirmado=True, quitado=True
        ).exclude(
            eliminado=True
        ).order_by("-id")
    else:
        orcamentos = Orcamento.objects.all().filter(
        status="contrato gerado", confirmado=True, quitado=True
        ).exclude(
            eliminado=True
        ).order_by("-id")
    saldos = []
    for o in orcamentos:
        saldo = o.total_valor_reserva + o.valor_extras - o.valor_pago
        saldos.append(saldo)
    if len(orcamentos) == 0 and termo_cliente:
        messages.add_message(request, messages.WARNING, f"Nenhum orçamento encontrado com o termo {termo_cliente}")
    paginator = Paginator(orcamentos, 10)
    page = request.GET.get('p')
    orcamentos = paginator.get_page(page)
    orcamentos_saldos = zip(orcamentos, saldos)
    return render(request, "lista_orcamentos_quitados.html", {"orcamentos": orcamentos,"orcamentos_saldos":orcamentos_saldos})


@login_required(login_url="login")
def quitar_orcamento(request, id):
    orcamento = Orcamento.objects.get(id=id)
    if orcamento.quitado == False:
        orcamento.quitado = True
        messages.add_message(request, messages.SUCCESS, f"Orçamento Nº {orcamento.id} quitado com sucesso")
    else:
        orcamento.quitado = False
        messages.add_message(request, messages.SUCCESS, f"Quitação do orçamento Nº {orcamento.id} cancelada com sucesso. Você pode rever esse orçamento na lista de orçamentos confirmados")
    orcamento.save()
    return redirect("lista_orcamentos_quitados")


@login_required(login_url="login")
def lista_relatorio_reservas(request):
    termo_cliente = request.GET.get("termo_cliente")
    if termo_cliente:
        termo_cliente = termo_cliente.strip()
        orcamentos = Orcamento.objects.all().filter(
            Q(cliente__nome__icontains=termo_cliente) | Q(cliente__telefone__icontains=termo_cliente) | Q(cliente__obs__icontains=termo_cliente) | Q(acomodacao__nome__icontains=termo_cliente), status="contrato gerado", quitado=False
        ).exclude(
            eliminado=True
        ).order_by("-id")
    else:
        orcamentos = Orcamento.objects.all().filter(
        status="contrato gerado", quitado=False
        ).exclude(
            eliminado=True
        ).order_by("-id")
    saldos = []
    for o in orcamentos:
        saldo = o.total_valor_reserva + o.valor_extras - o.valor_pago
        saldos.append(saldo)
    if len(orcamentos) == 0:
        messages.add_message(request, messages.WARNING, f"Nenhum orçamento encontrado com o termo {termo_cliente}")
    paginator = Paginator(orcamentos, 10)
    page = request.GET.get('p')
    orcamentos = paginator.get_page(page)
    orcamentos_saldos = zip(orcamentos, saldos)
    return render(request, "lista_relatorio_reservas.html", {"orcamentos": orcamentos,"orcamentos_saldos":orcamentos_saldos})

@login_required(login_url="login")
def visualizar_relatorio_financeiro(request, id):
    orcamento = Orcamento.objects.get(id=id)
    pag = Lancamentos.objects.all().filter(
        orcamento=orcamento, tipo="pagamento"
    )
    extras = Lancamentos.objects.all().filter(
        orcamento=orcamento, tipo="acréscimo"
    )
    tot_pag = 0
    tot_extra = 0
    saldo = 0
    for p in pag:
        tot_pag += p.valor

    for e in extras: 
        tot_extra += e.valor
    saldo = orcamento.total_valor_reserva + tot_extra - tot_pag
    valor_diarias = (orcamento.n_dias-orcamento.dias_pacote)*orcamento.valor_diaria
    buffer = io.BytesIO()
    ## fontes do report lab
    #Courier
    bold1 = "Courier-Bold"
    bold2 = "Courier-BoldOblique"
    #Courier-Oblique
    padr = "Helvetica" #padrão
    padr_bold = "Helvetica-Bold"   #padrão
    bold4 = "Helvetica-BoldOblique"
    #Helvetica-Oblique
    #Symbol
    bold5 = "Times-Bold"
    #Times-BoldItalic
    #Times-Italic
    #Times-Roman
    #ZapfDingbats

    #Início código

    n_orçamento=f"{orcamento.id}"
    hospede = f"{orcamento.cliente}"
    empreendimento= f"{orcamento.acomodacao.empreendimento}"
    acomodação = f"{orcamento.acomodacao}"
    entrada = f"{datetime.strftime(orcamento.data_entrada, '%d/%m/%Y')} - {orcamento.dia_entrada} - {orcamento.checkin}"
    saída =  f"{datetime.strftime(orcamento.data_saida, '%d/%m/%Y')} - {orcamento.dia_saida} - {orcamento.checkout}"
    tot_diárias =f"{orcamento.n_dias}"
    tot_ocupantes= f"{orcamento.n_ocupantes}"
    obs_ocupantes=f"{orcamento.obs_n_ocupantes}"
    perido = f"{orcamento.periodo}"
    if orcamento.diaria_cheia:
        tipo_diária="DIÁRIA CHEIA"
    else:
        tipo_diária="PERNOITE"
    valor_diaria=f"R$ {orcamento.valor_diaria:.2f}"
    tx_limpeza=  f"R$ {orcamento.taxa_limpeza:.2f}"
    valor_pacote=f"R$ {orcamento.valor_pacote:.2f}"
    dias_pacote=f"{orcamento.dias_pacote}"
    tot_valor_diarias=f"{valor_diarias:.2f}"
    tot_valor_pacote=f"{orcamento.valor_pacote}"
    tot_tx_limpeza=f"{orcamento.taxa_limpeza}"
    tot_acrescimo=f"{orcamento.acrescimos}"
    tot_desconto=f"{orcamento.descontos}"
    total_valor=f"{orcamento.total_valor_reserva}"

    if orcamento.modificado:
        modificado = "***Modificado"
        motivo = f"Motivo: {orcamento.obs_modificacao}"
    else:
        modificado = ""
        motivo = ""
    #condições de pagamento
    ##### inicio do projeto ########

    #transforma mm em pontos
    def mm2p(mm):
        return mm/0.352777
    ## gera nome do arquivo personalizado para cada cliente
    cliente = hospede.replace("(","-").replace(")","-").replace("/","-")
    arquivo = f"{n_orçamento}-{acomodação} {cliente}.pdf"
    cnv =  canvas.Canvas(buffer, pagesize=A4)

    cnv.setTitle(f"Resumo financeiro do orçamento {orcamento.id} de {hospede} - {acomodação}")

    #desenhar um retangulo informa x inicial, y inicial , largura e altura
    cnv.rect(mm2p(2),mm2p(2),mm2p(205),mm2p(293))

    ##### fazendo um cabeçalho ######
    #desenhar um retangulo para cabeçalho
    cnv.rect(mm2p(2),mm2p(250),mm2p(205),mm2p(45))
    #desenhar uma imagem
    cnv.drawImage("templates/static/img/LOGO.png",mm2p(3),mm2p(251),width=mm2p(30),height=mm2p(40))
    cnv.setFontSize(15)
    cnv.setFont(padr_bold,15)
    cnv.drawCentredString(320,810,"RESIDENCIAL SOL DE VERÃO & MORADAS PÉ NA AREIA")
    cnv.setFontSize(18)

    cnv.setFillColor("green")
    cnv.drawCentredString(320,780,"DADOS FINANCEIROS DA RESERVA")
    cnv.setFillColor('red')
    cnv.setFont(padr_bold,14)
    cnv.drawCentredString(320,750, empreendimento)
    cnv.setFillColor('black')

    cnv.setFillColor('blue')
    cnv.setFont(padr_bold,10)
    #cnv.drawCentredString(320,750,"NÚMERO DO ORÇAMENTO: ")
    cnv.drawRightString(500,713,"CONTRATO Nº: ")
    cnv.setFillColor('black')
    cnv.setFont(padr,13)
    cnv.drawRightString(570,713, n_orçamento)
    cnv.setFillColor('black')


    #linha 1
    linha=243
    desconto =  5
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha),"HÓSPEDE:")
    cnv.setFont(padr,12)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(24),mm2p(linha),hospede)

    #linha 2
    linha = linha-desconto
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha),"ACOMODAÇÃO:")
    cnv.setFont(padr,12)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(33),mm2p(linha),acomodação)

    #linha 3
    linha = linha-desconto
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha),"DATA DE ENTRADA(check in):")
    cnv.setFont(padr,12)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(60),mm2p(linha),entrada)

    #linha 4
    linha = linha-desconto
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha),"DATA DE SAÍDA(check out):")
    cnv.setFont(padr,12)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(60),mm2p(linha),saída)

    cnv.rect(mm2p(2),mm2p(linha-4),mm2p(205),mm2p(0))

    #linha 5  TOTAL DE  DIÁRIA, OCUPANTES E TIPO DE DIÁRIA
    linha = linha-desconto-6
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha),"TOTAL DE DIÁRIAS:")
    cnv.setFont(padr,18)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(39),mm2p(linha),tot_diárias)

    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(50),mm2p(linha),"TOTAL DE OCUPANTES:")
    cnv.setFont(padr,18)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(96),mm2p(linha),tot_ocupantes)
    cnv.setFont(padr,10)
    cnv.drawString(mm2p(105),mm2p(linha),obs_ocupantes)
    cnv.setFillColor("green")
    cnv.setFont(padr_bold,7)
    cnv.drawRightString(mm2p(205),mm2p(linha-1),tipo_diária)
    cnv.drawRightString(mm2p(205),mm2p(linha+4),perido)
    cnv.setFont(padr,10)

    cnv.rect(mm2p(2),mm2p(linha-4),mm2p(205),mm2p(0))

    # linha 6 - VALORES  INDIVIDUAIS
    linha = linha-desconto-6
    fonte_destaque=14      
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha),"VALOR DA DIÁRIA:")
    cnv.setFont(padr,fonte_destaque)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(39),mm2p(linha),valor_diaria)

    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(100),mm2p(linha),"TX DE LIMPEZA:")
    cnv.setFont(padr,fonte_destaque)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(150),mm2p(linha),tx_limpeza)
    cnv.setFont(padr,10)

    #LINHA7
    linha = linha-desconto-2

    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha),"VALOR DO PACOTE:")
    cnv.setFont(padr,fonte_destaque)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(39),mm2p(linha),valor_pacote)

    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(100),mm2p(linha)," QUANTIDADE DIAS DO PACOTE:")
    cnv.setFont(padr,fonte_destaque)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(160),mm2p(linha),dias_pacote)
    cnv.setFont(padr,10)

    cnv.rect(mm2p(2),mm2p(linha-4),mm2p(205),mm2p(0))

    ## grade do calculo do orçamento
    cnv.rect(mm2p(2),mm2p(linha-45),mm2p(80),mm2p(41))
    cnv.rect(mm2p(2),mm2p(linha-45),mm2p(205),mm2p(41))

    #coluna de CALCULO DO ORÇAMENTO
    size_calculo = 12
    linha_coluna_calculo = linha-desconto-4
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha_coluna_calculo),"CALCULO DO ORÇAMENTO:")
    cnv.setFont(padr,fonte_destaque)
    cnv.setFillColor("black")

    linha_coluna_calculo = linha_coluna_calculo-desconto-2
    cnv.setFont(padr_bold,8)
    cnv.setFillColor("blue")
    cnv.drawString(mm2p(3),mm2p(linha_coluna_calculo),"Total das diárias ==> ")
    cnv.setFont(padr,size_calculo)
    cnv.setFillColor("black")
    cnv.drawRightString(mm2p(65),mm2p(linha_coluna_calculo), tot_valor_diarias)

    linha_coluna_calculo = linha_coluna_calculo-desconto
    cnv.setFont(padr_bold,8)
    cnv.setFillColor("blue")
    cnv.drawString(mm2p(3),mm2p(linha_coluna_calculo),"Valor do Pacote  ==> ")
    cnv.setFont(padr,size_calculo)
    cnv.setFillColor("black")
    cnv.drawRightString(mm2p(65),mm2p(linha_coluna_calculo), tot_valor_pacote)

    linha_coluna_calculo = linha_coluna_calculo-desconto
    cnv.setFont(padr_bold,8)
    cnv.setFillColor("blue")
    cnv.drawString(mm2p(3),mm2p(linha_coluna_calculo),"Taxa de Limpeza ==> ")
    cnv.setFont(padr,size_calculo)
    cnv.setFillColor("black")
    cnv.drawRightString(mm2p(65),mm2p(linha_coluna_calculo), tot_tx_limpeza)

    linha_coluna_calculo = linha_coluna_calculo-desconto
    cnv.setFont(padr_bold,8)
    cnv.setFillColor("blue")
    cnv.drawString(mm2p(3),mm2p(linha_coluna_calculo),"Acréscimos ==> ")
    cnv.setFont(padr,size_calculo)
    cnv.setFillColor("black")
    cnv.drawRightString(mm2p(65),mm2p(linha_coluna_calculo), tot_acrescimo)

    linha_coluna_calculo = linha_coluna_calculo-desconto
    cnv.setFont(padr_bold,8)
    cnv.setFillColor("blue")
    cnv.drawString(mm2p(3),mm2p(linha_coluna_calculo),"Descontos ==> ")
    cnv.setFont(padr,size_calculo)
    cnv.setFillColor("red")
    cnv.drawRightString(mm2p(65),mm2p(linha_coluna_calculo), tot_desconto)
    cnv.setFillColor("black")

    linha_coluna_calculo = linha_coluna_calculo-desconto
    cnv.setFont(padr_bold,11)
    cnv.setFillColor("blue")
    cnv.drawString(mm2p(3),mm2p(linha_coluna_calculo),"TOTAL ==> ")
    cnv.setFont(padr_bold,size_calculo+3)
    cnv.setFillColor("black")
    cnv.drawRightString(mm2p(65),mm2p(linha_coluna_calculo), total_valor)
    cnv.setFillColor("black")

    # total de lançamentos financeiros

    size_calculo = 12
    linha_lanc = linha-desconto-4
    col_lanc = mm2p(85)
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(col_lanc,mm2p(linha_lanc),"TOTAL DE LANÇAMENTOS FINANCEIROS :")
    cnv.setFont(padr,3)
    cnv.setFillColor("black")

    linha_lanc=linha_lanc-6
    cnv.setFont(padr_bold,8)
    cnv.setFillColor("black")
    cnv.drawString(col_lanc,mm2p(linha_lanc),"Total de Extras Registrados ==> ")
    cnv.setFont(padr,size_calculo)
    cnv.setFillColor("black")
    cnv.drawRightString(col_lanc+300,mm2p(linha_lanc), f"R$ {tot_extra:.2f}")

    linha_lanc=linha_lanc-6
    cnv.setFont(padr_bold,8)
    cnv.setFillColor("black")
    cnv.drawString(col_lanc,mm2p(linha_lanc),"Total de pagamentos Registrados ==> ")
    cnv.setFont(padr,size_calculo)
    cnv.setFillColor("black")
    cnv.drawRightString(col_lanc+300,mm2p(linha_lanc), f"R$ {tot_pag:.2f}")

    linha_lanc=linha_lanc-12
    cnv.setFont(padr_bold,12)
    cnv.setFillColor("black")
    cnv.drawString(col_lanc,mm2p(linha_lanc),"SALDO A PAGAR ==> ")
    cnv.setFont(padr_bold,20)
    cnv.setFillColor("red")
    cnv.drawRightString(col_lanc+300,mm2p(linha_lanc), f"R$ {saldo:.2f}")



    #lançamento de extras
    size_calculo = 12
    linha_f_pagto = linha_coluna_calculo-9
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha_f_pagto),"LANÇAMENTOS DE COBRANÇAS EXTRAS:")

    """extras = [
        {"data":"25/07/2023", "valor":30.00 , "descricao": "consumo ar condiconado 10 kw x R$ 3,00"},
        {"data":"24/07/2023", "valor":15.50 , "descricao": "1 bomboma de agua mineral"},
        {"data":"22/07/2023", "valor":54.50 , "descricao": "vaga extra no estacionamento"},
    ]"""
    linha_extras = linha_f_pagto - 6
    cnv.setFont(padr_bold,size_calculo-3)
    cnv.setFillColor("blue")
    cnv.drawString(mm2p(3),mm2p(linha_extras),"Data Lançamento")
    cnv.drawString(mm2p(33),mm2p(linha_extras),"Valor")
    cnv.drawString(mm2p(53),mm2p(linha_extras),"Descrição")

    #tot_extra = 0
    linha_pos = linha_extras-4
    cnv.setFont(padr,size_calculo-5)
    cnv.setFillColor("black")
    for e in extras:
        cnv.drawString(mm2p(3),mm2p(linha_pos),datetime.strftime(e.data_lancamento, "%d/%m/%Y"))
        cnv.drawString(mm2p(33),mm2p(linha_pos),f'R$ {e.valor:.2f}')
        cnv.drawString(mm2p(53),mm2p(linha_pos),e.descricao)
        linha_pos+= -3
    cnv.setFont(padr_bold,size_calculo)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(3),mm2p(linha_pos-4),"Total de cobrança de Extras ===>")
    cnv.drawString(mm2p(75),mm2p(linha_pos-4),f"R$ {tot_extra:.2f}")


    cnv.rect(mm2p(2),mm2p(linha_f_pagto-50),mm2p(205),mm2p(0))



    ####  pagamentos efetuados ######
    linha_info = linha_f_pagto-55
    cnv.setFont(padr_bold,10)
    cnv.setFillColor("red")
    cnv.drawString(mm2p(3),mm2p(linha_info),"LANÇAMENTOS DOS PAGAMENTOS EFETUADOS:")
    cnv.setFont(padr,fonte_destaque)
    cnv.setFillColor("black")

    linha_pag = linha_info - 6
    cnv.setFont(padr_bold,size_calculo-3)
    cnv.setFillColor("blue")
    cnv.drawString(mm2p(3),mm2p(linha_pag),"Data Lançamento")
    cnv.drawString(mm2p(33),mm2p(linha_pag),"Valor")
    cnv.drawString(mm2p(53),mm2p(linha_pag),"Descrição")

    """pagamentos = [
        {"data":"22/07/2023", "valor":1030.00 , "descricao": "deposito conta PJ inter"},
        {"data":"24/07/2023", "valor":150.00 , "descricao": "depósito conta brsdesco"},
        {"data":"27/07/2023", "valor":100.00 , "descricao": "pagamento em dinheiro"},
    ]"""

    linha_pos = linha_pag-4
    cnv.setFont(padr,size_calculo-5)
    cnv.setFillColor("black")
    #tot_pag = 0
    for e in pag:
        cnv.drawString(mm2p(3),mm2p(linha_pos),datetime.strftime(e.data_lancamento, "%d/%m/%Y"))
        cnv.drawString(mm2p(33),mm2p(linha_pos),f'R$ {e.valor:.2f}')
        cnv.drawString(mm2p(53),mm2p(linha_pos),e.descricao)
        linha_pos+= -3

    cnv.setFont(padr_bold,size_calculo)
    cnv.setFillColor("black")
    cnv.drawString(mm2p(3),mm2p(linha_pos-4),"Total de Pagamentos Registrados ===>")
    cnv.drawString(mm2p(90),mm2p(linha_pos-4),f"R$ {tot_pag:.2f}")

    cnv.setFont(padr, 7)
    cnv.drawRightString(mm2p(200), mm2p(7), modificado)
    cnv.drawRightString(mm2p(200), mm2p(5), motivo)
    cnv.showPage()
    cnv.save()
    #Fim código

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename=arquivo)

@login_required(login_url="login")
def lista_checkout(request):
    data_inicial = request.POST.get("data_inicial")
    data_final = request.POST.get("data_final")
    if not data_inicial or not data_final:
        messages.add_message(request, messages.INFO, "Informe uma data inicial e uma data final")
        return render(request, "lista_checkout.html")
    data_inicial = datetime.strptime(data_inicial, "%Y-%m-%d")
    data_final = datetime.strptime(data_final, "%Y-%m-%d")
    if data_final < data_inicial:
        messages.add_message(request, messages.ERROR, "Data final não pode ser menor que a data inicial")
        return render(request, "lista_checkout.html")
    else:
        orcamentos = Orcamento.objects.all().filter(
            data_saida__range=(data_inicial, data_final)
        ).filter(
            confirmado=True
        ).exclude(
            eliminado=True
        ).order_by("data_saida")
        datas = []
        for o in orcamentos:
            if o.data_saida not in datas:
                datas.append(o.data_saida)
        if len(orcamentos) == 0:
            messages.add_message(request, messages.INFO, "Não existe checkout previsto para este intervalo de datas até o momento")
            return render(request, "lista_checkout.html")
        else:
            return render(request, "lista_checkout.html", {"orcamentos": orcamentos, "datas": datas})
        
@login_required(login_url="login")
def pdf_checkout(request,):
    data_inicial = request.GET.get("data_inicial")
    data_final = request.GET.get("data_final")
    data_inicial = datetime.strptime(data_inicial, "%Y-%m-%d")
    data_final = datetime.strptime(data_final, "%Y-%m-%d")
    orcamentos = Orcamento.objects.all().filter(
        data_saida__range=(data_inicial, data_final)
    ).filter(
        confirmado=True
    ).exclude(
        eliminado=True
    ).order_by("data_saida")
    datas = []
    for o in orcamentos:
        if o.data_saida not in datas:
            datas.append(o.data_saida)
    buffer = io.BytesIO()
    ## fontes do report lab
    #Courier
    bold1 = "Courier-Bold"
    bold2 = "Courier-BoldOblique"
    #Courier-Oblique
    padr = "Helvetica" #padrão
    padr_bold = "Helvetica-Bold"   #padrão
    bold4 = "Helvetica-BoldOblique"
    #Helvetica-Oblique
    #Symbol
    bold5 = "Times-Bold"
    #Times-BoldItalic
    #Times-Italic
    #Times-Roman
    #ZapfDingbats


    ##### inicio do projeto ########

    #transforma mm em pontos
    def mm2p(mm):
        return mm/0.352777
    ## gera nome do arquivo personalizado para cada cliente
    arquivo = f"Programação de limpezas do dia {datetime.strftime(data_inicial, '%d/%m/%Y')} até o dia {datetime.strftime(data_final, '%d/%m/%Y')}.pdf"
    rel = f"Programação de limpezas do dia {datetime.strftime(data_inicial, '%d/%m/%Y')} até o dia {datetime.strftime(data_final, '%d/%m/%Y')}."
    cnv =  canvas.Canvas(buffer, pagesize=A4)
    hoje = datetime.now()
    hoje = datetime.strftime(hoje,'%d/%m/%Y %H:%M:%S')
    
    cnv.setTitle(f"Programação de limpezas do dia {datetime.strftime(data_inicial, '%d/%m/%Y')} até o dia {datetime.strftime(data_final, '%d/%m/%Y')}")

    #desenhar um retangulo informa x inicial, y inicial , largura e altura
    cnv.rect(mm2p(2),mm2p(2),mm2p(205),mm2p(293))

    ##### fazendo um cabeçalho ######
    #desenhar um retangulo para cabeçalho
    cnv.rect(mm2p(2),mm2p(250),mm2p(205),mm2p(45))
    pagina = 1
    #desenhar uma imagem
    cnv.drawImage("templates/static/img/LOGO.png",mm2p(3),mm2p(251),width=mm2p(30),height=mm2p(40))
    cnv.setFontSize(15)
    cnv.setFont(padr_bold,15)
    cnv.drawCentredString(320,810,"RESIDENCIAL SOL DE VERÃO & MORADAS PÉ NA AREIA")
    cnv.setFontSize(18)

    cnv.setFillColor("green")
    cnv.drawCentredString(320,780,"PROGRAMAÇÃO DE CHECKOUTS")
    cnv.setFillColor('red')
    cnv.setFont(padr_bold,14)

    cnv.setFillColor("red")
    cnv.setFont(padr_bold,10)
    cnv.drawCentredString(320,750,rel)
    cnv.setFillColor('black')
    cnv.setFont(bold4,10)
    cnv.drawCentredString(320,720,f"Relatório Gerado em {hoje}  ===> Pagina {pagina}")
    cnv.setFont(padr_bold,14)


    semana = ("Segunda Feira", "Terça Feira", "Quarta Feira", "Quinta Feira", "Sexta Feira", "Sábado", "Domingo")

    linha = mm2p(297-55)
    for d in datas:
        cnv.setFontSize(15)
        cnv.setFillColor("red")
        cnv.drawString(10,linha,f"Data: {datetime.strftime(d, '%d/%m/%Y')} {semana[d.weekday()]}")
        cnv.setFillColor("black")
        cab=True
        for o in orcamentos:
            if linha<100:
                pagina+=1
                cnv.setFont(padr,7)
                cnv.drawCentredString(320,20,f"Continua na Página {pagina}")
                cnv.showPage()
                linha = mm2p(297-55)
                cnv.rect(mm2p(2),mm2p(2),mm2p(205),mm2p(293))
                cnv.rect(mm2p(2),mm2p(250),mm2p(205),mm2p(45))
                #desenhar uma imagem
                cnv.drawImage("templates/static/img/LOGO.png",mm2p(3),mm2p(251),width=mm2p(30),height=mm2p(40))
                cnv.setFontSize(15)
                cnv.setFont(padr_bold,15)
                cnv.drawCentredString(320,810,"RESIDENCIAL SOL DE VERÃO & MORADAS PÉ NA AREIA")
                cnv.setFontSize(18)

                cnv.setFillColor("green")
                cnv.drawCentredString(320,780,"PROGRAMAÇÃO DE CHECKOUTS")
                cnv.setFillColor('red')
                cnv.setFont(padr_bold,14)

                cnv.setFillColor("red")
                cnv.setFont(padr_bold,10)
                cnv.drawCentredString(320,750,rel)
                cnv.setFillColor('black')
                cnv.setFont(bold4,10)
                cnv.drawCentredString(320,720,f"Relatório Gerado em {hoje}  ===> Pagina {pagina}")
                cnv.setFont(padr_bold,14)
            if o.data_saida == d:
                if cab:
                    cnv.setFontSize(11)
                    cnv.setFillColor("green")
                    cnv.drawString(10,linha-12, f"Acomodação")
                    cnv.drawString(180,linha-12, f"Cliente:")
                    cnv.drawRightString(550,linha-12, f"limite de horário para saída")
                    linha -= 12
                    cnv.setFillColor("black")
                cab=False
                cnv.setFontSize(10)
                cnv.drawString(10,linha-12, f"{o.acomodacao}")
                cnv.setFontSize(8)
                cnv.drawString(180,linha-12, f"{o.cliente}")
                cnv.drawRightString(550,linha-12, f"{o.checkout}")
                linha -= 12
        cab=True
        linha -= 12
        cnv.line(10, linha, 585, linha)
        linha -= 24
    cnv.showPage()
    cnv.save()
    #Fim código

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename=arquivo)