from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
#from reportlab.lib      import colors
from reportlab.platypus import Paragraph
from pathlib import Path
from datetime import datetime, timedelta
import io
from django.http import FileResponse
#import os



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

def mm2p(mm):
    return mm/0.352777

def gera_pdf_checkout(data_inicial, data_final, orcamentos):
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
    buffer = io.BytesIO()
    arquivo = f"Programação de limpezas do dia {data_inicial.date()} até o dia {data_final.date()}.pdf"
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
    for d in ndatas:
        if d in datas:
            cnv.setFontSize(15)
            cnv.setFillColor("red")
            cnv.drawString(10,linha,f"Saídas programadas para a data de: {datetime.strftime(d, '%d/%m/%Y')} {semana[d.weekday()]}")
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
        else:
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
                    cnv.setFontSize(13)

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
            cnv.setFontSize(15)
            cnv.setFillColor("red")
            cnv.drawCentredString(300, linha, f"### Sem saídas programadas para o dia {datetime.strftime(d, '%d/%m/%Y')} {semana[d.weekday()]} ###")
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

def gera_pdf_checkin(data_inicial, data_final, orcamentos):
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
        #print(dia.date())
        ndatas.append(dia.date())
    buffer = io.BytesIO()
    arquivo = f"Programação de Revisão de limpezas do dia {data_inicial.date()} até o dia {data_final.date()}.pdf"
    rel = f"Programação de Revisão de limpezas do dia {datetime.strftime(data_inicial, '%d/%m/%Y')} até o dia {datetime.strftime(data_final, '%d/%m/%Y')}."
    cnv =  canvas.Canvas(buffer, pagesize=A4)
    hoje = datetime.now()
    hoje = datetime.strftime(hoje,'%d/%m/%Y %H:%M:%S')
    
    cnv.setTitle(f"Programação de Revisão de limpezas do dia {datetime.strftime(data_inicial, '%d/%m/%Y')} até o dia {datetime.strftime(data_final, '%d/%m/%Y')}")

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
    cnv.drawCentredString(320,780,"PROGRAMAÇÃO DE CHECKINS")
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
    for d in ndatas:
        if d in datas:
            cnv.setFontSize(15)
            cnv.setFillColor("red")
            cnv.drawString(10,linha,f"Entradas programadas para a data de: {datetime.strftime(d, '%d/%m/%Y')} {semana[d.weekday()]}")
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
                    cnv.drawCentredString(320,780,"PROGRAMAÇÃO DE CHECKINS")
                    cnv.setFillColor('red')
                    cnv.setFont(padr_bold,14)

                    cnv.setFillColor("red")
                    cnv.setFont(padr_bold,10)
                    cnv.drawCentredString(320,750,rel)
                    cnv.setFillColor('black')
                    cnv.setFont(bold4,10)
                    cnv.drawCentredString(320,720,f"Relatório Gerado em {hoje}  ===> Pagina {pagina}")
                    cnv.setFont(padr_bold,14)
                if o.data_entrada == d:
                    if cab:
                        cnv.setFontSize(11)
                        cnv.setFillColor("green")
                        cnv.drawString(10,linha-12, f"Acomodação")
                        cnv.drawString(180,linha-12, f"Cliente:")
                        cnv.drawRightString(550,linha-12, f"limite de horário para entrada")
                        linha -= 12
                        cnv.setFillColor("black")
                    cab=False
                    cnv.setFontSize(10)
                    cnv.drawString(10,linha-12, f"{o.acomodacao}")
                    cnv.setFontSize(8)
                    cnv.drawString(180,linha-12, f"{o.cliente}")
                    cnv.drawRightString(550,linha-12, f"{o.checkin}")
                    linha -= 12
            cab=True
            linha -= 12
            cnv.line(10, linha, 585, linha)
            linha -= 24
        else:
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
                    cnv.setFontSize(13)

                    cnv.setFillColor("green")
                    cnv.drawCentredString(320,780,"PROGRAMAÇÃO DE CHECKINS")
                    cnv.setFillColor('red')
                    cnv.setFont(padr_bold,14)

                    cnv.setFillColor("red")
                    cnv.setFont(padr_bold,10)
                    cnv.drawCentredString(320,750,rel)
                    cnv.setFillColor('black')
                    cnv.setFont(bold4,10)
                    cnv.drawCentredString(320,720,f"Relatório Gerado em {hoje}  ===> Pagina {pagina}")
                    cnv.setFont(padr_bold,14)
            cnv.setFontSize(15)
            cnv.setFillColor("red")
            cnv.drawCentredString(300, linha, f"### Sem entradas programadas para o dia {datetime.strftime(d, '%d/%m/%Y')} {semana[d.weekday()]} ###")
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

def gera_pdf_reservas(data_inicial, data_final, orcamentos_entrada, orcamentos_saida):
    quant_dias = abs((data_inicial - data_final).days)
    ndatas = []    
    for i in range(0,quant_dias+1):
        dia = data_inicial + timedelta(days=i)
        dia = dia.strftime("%Y-%m-%d")
        dia = datetime.strptime(dia,"%Y-%m-%d")
        #print(dia.date())
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
    buffer = io.BytesIO()
    arquivo = f"Relatório das reservas por dia do dia {data_inicial.date()} até o dia {data_final.date()}.pdf"
    rel = f"Relatório das reservas por dia do dia {datetime.strftime(data_inicial, '%d/%m/%Y')} até o dia {datetime.strftime(data_final, '%d/%m/%Y')}."
    cnv =  canvas.Canvas(buffer, pagesize=A4)
    hoje = datetime.now()
    hoje = datetime.strftime(hoje,'%d/%m/%Y %H:%M:%S')
    
    cnv.setTitle(f"Relatório das reservas por dia do dia {datetime.strftime(data_inicial, '%d/%m/%Y')} até o dia {datetime.strftime(data_final, '%d/%m/%Y')}")

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
    cnv.setFontSize(13)

    cnv.setFillColor("green")
    cnv.drawCentredString(320,780,"RELATÓRIO DAS RESERVAS POR DIA (ENTRADAS/SAÍDAS)")
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
    for d in ndatas:
        cnv.setFontSize(15)
        cnv.setFillColor("black")
        cnv.drawString(10,linha,f"Dia {datetime.strftime(d, '%d/%m/%Y')} {semana[d.weekday()]}")
        linha -= 12
        if d in datas_entrada:
            cnv.setFontSize(10)
            cnv.setFillColor("red")
            cnv.drawString(10,linha,f"Entradas programadas para a data de: {datetime.strftime(d, '%d/%m/%Y')} {semana[d.weekday()]}")
            cnv.setFillColor("black")
            cab=True
            for o in orcamentos_entrada:
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
                    cnv.setFontSize(13)

                    cnv.setFillColor("green")
                    cnv.drawCentredString(320,780,"RELATÓRIO DAS RESERVAS POR DIA (ENTRADAS/SAÍDAS)")
                    cnv.setFillColor('red')
                    cnv.setFont(padr_bold,14)

                    cnv.setFillColor("red")
                    cnv.setFont(padr_bold,10)
                    cnv.drawCentredString(320,750,rel)
                    cnv.setFillColor('black')
                    cnv.setFont(bold4,10)
                    cnv.drawCentredString(320,720,f"Relatório Gerado em {hoje}  ===> Pagina {pagina}")
                    cnv.setFont(padr_bold,14)
                if o.data_entrada == d:
                    if cab:
                        cnv.setFontSize(11)
                        cnv.setFillColor("green")
                        cnv.drawString(10,linha-12, f"Acomodação")
                        cnv.drawString(180,linha-12, f"Cliente:")
                        cnv.drawRightString(550,linha-12, f"limite de horário para entrada")
                        linha -= 12
                        cnv.setFillColor("black")
                    cab=False
                    cnv.setFontSize(10)
                    cnv.drawString(10,linha-12, f"{o.acomodacao}")
                    cnv.setFontSize(8)
                    cnv.drawString(180,linha-12, f"{o.cliente}")
                    cnv.drawRightString(550,linha-12, f"{o.checkin}")
                    linha -= 12
            cab=True
            #linha -= 12
            #cnv.line(10, linha, 585, linha)
            linha -= 24
        else:
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
                    cnv.setFontSize(13)

                    cnv.setFillColor("green")
                    cnv.drawCentredString(320,780,"RELATÓRIO DAS RESERVAS POR DIA (ENTRADAS/SAÍDAS)")
                    cnv.setFillColor('red')
                    cnv.setFont(padr_bold,14)

                    cnv.setFillColor("red")
                    cnv.setFont(padr_bold,10)
                    cnv.drawCentredString(320,750,rel)
                    cnv.setFillColor('black')
                    cnv.setFont(bold4,10)
                    cnv.drawCentredString(320,720,f"Relatório Gerado em {hoje}  ===> Pagina {pagina}")
                    cnv.setFont(padr_bold,14)
            linha -= 12
            cnv.setFontSize(15)
            cnv.setFillColor("red")
            cnv.drawCentredString(300, linha, "### Sem entradas programadas para esse dia ###")
            linha -= 24
        
        if d in datas_saida:
            cnv.setFontSize(10)
            cnv.setFillColor("red")
            cnv.drawString(10,linha,f"Saídas programadas para a data de: {datetime.strftime(d, '%d/%m/%Y')} {semana[d.weekday()]}")
            cnv.setFillColor("black")
            cab=True
            for o in orcamentos_saida:
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
                    cnv.setFontSize(13)

                    cnv.setFillColor("green")
                    cnv.drawCentredString(320,780,"RELATÓRIO DAS RESERVAS POR DIA (ENTRADAS/SAÍDAS)")
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
        else:
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
                    cnv.setFontSize(13)

                    cnv.setFillColor("green")
                    cnv.drawCentredString(320,780,"RELATÓRIO DAS RESERVAS POR DIA (ENTRADAS/SAÍDAS)")
                    cnv.setFillColor('red')
                    cnv.setFont(padr_bold,14)

                    cnv.setFillColor("red")
                    cnv.setFont(padr_bold,10)
                    cnv.drawCentredString(320,750,rel)
                    cnv.setFillColor('black')
                    cnv.setFont(bold4,10)
                    cnv.drawCentredString(320,720,f"Relatório Gerado em {hoje}  ===> Pagina {pagina}")
                    cnv.setFont(padr_bold,14)
            cnv.setFontSize(15)
            cnv.setFillColor("red")
            cnv.drawCentredString(300, linha, "### Sem saídas programadas para esse dia ###")
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

def gera_relatorio_financeiro(orcamento, pag, extras):
    tot_pag = 0
    tot_extra = 0
    saldo = 0
    for p in pag:
        tot_pag += p.valor

    for e in extras: 
        tot_extra += e.valor
    saldo = orcamento.total_valor_reserva + tot_extra - tot_pag
    buffer = io.BytesIO()
    valor_diarias = (orcamento.n_dias-orcamento.dias_pacote)*orcamento.valor_diaria
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

    linha_extras = linha_f_pagto - 6
    cnv.setFont(padr_bold,size_calculo-3)
    cnv.setFillColor("blue")
    cnv.drawString(mm2p(3),mm2p(linha_extras),"Data Lançamento")
    cnv.drawString(mm2p(33),mm2p(linha_extras),"Valor")
    cnv.drawString(mm2p(53),mm2p(linha_extras),"Descrição")

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


    linha_pos = linha_pag-4
    cnv.setFont(padr,size_calculo-5)
    cnv.setFillColor("black")
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
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename=arquivo)

def gera_pdf_contrato(orc, obs_contrato):
    buffer = io.BytesIO()
    if orc.modificado:
        modificado = "***Modificado"
        motivo = f"Motivo: {orc.obs_modificacao}"
    else:
        modificado = ""
        motivo = ""
    
    data_contrato = f"{datetime.strftime(obs_contrato.data_contrato, '%d/%m/%Y')}"
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

def gera_pdf_orcamento(orc, obs_orc):
    buffer = io.BytesIO()

    if orc.modificado:
        modificado = "***Modificado"
        motivo = f"Motivo: {orc.obs_modificacao}"
    else:
        modificado = ""
        motivo = ""
    data_orçamento = f"{datetime.strftime(orc.data_orcamento, '%d/%m/%Y')}"
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