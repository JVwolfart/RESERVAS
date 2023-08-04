from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cliente, Empreendimento, DadosCliente, Acomodacao, Periodo, Horario, Orcamento, ObsOrcamento, Observacao, Contrato, TipoObservacao, Lancamentos
from django.db.models import Q
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from utils.pdfs import gera_pdf_checkout, gera_pdf_checkin, gera_pdf_reservas, gera_relatorio_financeiro, gera_pdf_contrato, gera_pdf_orcamento





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
    if orc.status == "digitação concluída":
        orc.status = "orçamento gerado"
        orc.save()
    return gera_pdf_orcamento(orc, obs_orc)

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
    return gera_pdf_contrato(orc, obs_contrato)

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
    saldos = saldos[10*(int(page)-1):]
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
    saldos = saldos[10*(int(page)-1):]
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
    saldos = saldos[10*(int(page)-1):]
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
    saldos = saldos[10*(int(page)-1):]
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
    saldos = saldos[10*(int(page)-1):]
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
    return gera_relatorio_financeiro(orcamento, pag, extras)

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

        quant_dias = abs((data_inicial - data_final).days)
        ndatas = []    
        for i in range(0,quant_dias+1):
            dia = data_inicial + timedelta(days=i)
            dia = dia.strftime("%Y-%m-%d")
            dia = datetime.strptime(dia,"%Y-%m-%d")
            #print(dia.date())
            ndatas.append(dia.date())
        if len(orcamentos) == 0:
            messages.add_message(request, messages.INFO, "Não existe checkout previsto para este intervalo de datas até o momento")
            return render(request, "lista_checkout.html")
        else:
            return render(request, "lista_checkout.html", {"orcamentos": orcamentos, "datas": datas, "ndatas": ndatas})
        
@login_required(login_url="login")
def pdf_checkout(request):
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
    return gera_pdf_checkout(data_inicial, data_final, orcamentos)
    

@login_required(login_url="login")
def lista_checkin(request):
    data_inicial = request.POST.get("data_inicial")
    data_final = request.POST.get("data_final")
    if not data_inicial or not data_final:
        messages.add_message(request, messages.INFO, "Informe uma data inicial e uma data final")
        return render(request, "lista_checkin.html")
    data_inicial = datetime.strptime(data_inicial, "%Y-%m-%d")
    data_final = datetime.strptime(data_final, "%Y-%m-%d")
    if data_final < data_inicial:
        messages.add_message(request, messages.ERROR, "Data final não pode ser menor que a data inicial")
        return render(request, "lista_checkin.html")
    else:
        orcamentos = Orcamento.objects.all().filter(
            data_entrada__range=(data_inicial, data_final)
        ).filter(
            confirmado=True
        ).exclude(
            eliminado=True
        ).order_by("data_entrada")
        datas = []
        for o in orcamentos:
            if o.data_entrada not in datas:
                datas.append(o.data_entrada)
        quant_dias = abs((data_inicial - data_final).days)
        ndatas = []    
        for i in range(0,quant_dias+1):
            dia = data_inicial + timedelta(days=i)
            dia = dia.strftime("%Y-%m-%d")
            dia = datetime.strptime(dia,"%Y-%m-%d")
            ndatas.append(dia.date())
        if len(orcamentos) == 0:
            messages.add_message(request, messages.INFO, "Não existe checkin previsto para este intervalo de datas até o momento")
            return render(request, "lista_checkin.html")
        else:
            return render(request, "lista_checkin.html", {"orcamentos": orcamentos, "datas": datas, "ndatas": ndatas})
        

@login_required(login_url="login")
def pdf_checkin(request):
    data_inicial = request.GET.get("data_inicial")
    data_final = request.GET.get("data_final")
    data_inicial = datetime.strptime(data_inicial, "%Y-%m-%d")
    data_final = datetime.strptime(data_final, "%Y-%m-%d")
    orcamentos = Orcamento.objects.all().filter(
            data_entrada__range=(data_inicial, data_final)
    ).filter(
        confirmado=True
    ).exclude(
        eliminado=True
    ).order_by("data_entrada")
    return gera_pdf_checkin(data_inicial, data_final, orcamentos)

@login_required(login_url="login")
def lista_reservas(request):
    data_inicial = request.POST.get("data_inicial")
    data_final = request.POST.get("data_final")
    if not data_inicial or not data_final:
        messages.add_message(request, messages.INFO, "Informe uma data inicial e uma data final")
        return render(request, "lista_checkin_checkout.html")
    data_inicial = datetime.strptime(data_inicial, "%Y-%m-%d")
    data_final = datetime.strptime(data_final, "%Y-%m-%d")
    if data_final < data_inicial:
        messages.add_message(request, messages.ERROR, "Data final não pode ser menor que a data inicial")
        return render(request, "lista_checkin_checkout.html")
    orcamentos_entrada = Orcamento.objects.all().filter(
            data_entrada__range=(data_inicial, data_final)
    ).filter(
        confirmado=True
    ).exclude(
        eliminado=True
    ).order_by("data_entrada")

    orcamentos_saida = Orcamento.objects.all().filter(
            data_saida__range=(data_inicial, data_final)
    ).filter(
        confirmado=True
    ).exclude(
        eliminado=True
    ).order_by("data_saida")
    quant_dias = abs((data_inicial - data_final).days)
    ndatas = []    
    for i in range(0,quant_dias+1):
        dia = data_inicial + timedelta(days=i)
        dia = dia.strftime("%Y-%m-%d")
        dia = datetime.strptime(dia,"%Y-%m-%d")
        ndatas.append(dia.date())
    datas_entrada = []
    datas_saida = []
    datas = []
    for o in orcamentos_entrada:
        if o.data_entrada not in datas:
            datas.append(o.data_entrada)
        if o.data_entrada not in datas_entrada:
            datas_entrada.append(o.data_entrada)
    for o in orcamentos_saida:
        if o.data_saida not in datas:
            datas.append(o.data_saida)
        if o.data_saida not in datas_saida:
            datas_saida.append(o.data_saida)
    datas = sorted(datas)
    return render(request, "lista_checkin_checkout.html", {"ndatas":ndatas, "datas": datas, "orcamentos_entrada": orcamentos_entrada, "orcamentos_saida": orcamentos_saida, "datas_entrada": datas_entrada, "datas_saida": datas_saida})

@login_required(login_url="login")
def pdf_reservas(request):
    data_inicial = request.GET.get("data_inicial")
    data_final = request.GET.get("data_final")
    if not data_inicial or not data_final:
        messages.add_message(request, messages.INFO, "Informe uma data inicial e uma data final")
        return render(request, "lista_checkin_checkout.html")
    data_inicial = datetime.strptime(data_inicial, "%Y-%m-%d")
    data_final = datetime.strptime(data_final, "%Y-%m-%d")
    if data_final < data_inicial:
        messages.add_message(request, messages.ERROR, "Data final não pode ser menor que a data inicial")
        return render(request, "lista_checkin_checkout.html")
    orcamentos_entrada = Orcamento.objects.all().filter(
            data_entrada__range=(data_inicial, data_final)
    ).filter(
        confirmado=True
    ).exclude(
        eliminado=True
    ).order_by("data_entrada")
    orcamentos_saida = Orcamento.objects.all().filter(
            data_saida__range=(data_inicial, data_final)
    ).filter(
        confirmado=True
    ).exclude(
        eliminado=True
    ).order_by("data_saida")
    return gera_pdf_reservas(data_inicial, data_final, orcamentos_entrada, orcamentos_saida)