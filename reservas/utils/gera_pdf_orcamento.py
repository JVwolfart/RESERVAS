from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
#from reportlab.lib      import colors
from reportlab.platypus import Paragraph
from pathlib import Path
from datetime import datetime
#import os

caminho = Path(__file__).parent

print(caminho)

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

def gera_pdf_orcamento(orc, obs_orc):
    ### variáveis do projeto
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
    condiçao_pag =obs_orc.condicoes_pagamento.title()
    #obs importantes
    obs_importante = obs_orc.obs.title()

    #informações adicionias
    info = obs_orc.informacoes_adicionais.title()
    #descrição da acomodação
    desc_acomod=orc.acomodacao.descricao.title()

    ##### inicio do projeto ########

    #transforma mm em pontos
    def mm2p(mm):
        return mm/0.352777
    ## gera nome do arquivo personalizado para cada cliente
    cliente = hospede.replace("(","-").replace(")","-").replace("/","-")
    arquivo = f"orcamentos/orcamento-{n_orçamento}-{acomodação} {cliente}.pdf"
    #url_pdf = os.path.join(caminho, arquivo)
    cnv =  canvas.Canvas(f"media/{arquivo}", pagesize=A4)

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


    #cnv.rect(mm2p(2),mm2p(linha-45),mm2p(205),mm2p(41))
    cnv.showPage()
    cnv.save()
    try:
        return arquivo
    except:
        return "Erro ao gerar PDF"
