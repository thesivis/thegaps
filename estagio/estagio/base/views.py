from django.core.serializers import json
from django.conf import settings
from django.http import JsonResponse
from .processa import ListaArquivos,PesquisaArquivos
import os,time
from .form import Pesquisa
from .processa import Download
from django.shortcuts import render
from django.core.paginator import Paginator
from estagio.base.lista_arvore.lista_arvore import lista_arvore
from estagio.base.compacta_pesquisa.compacta_pesquisa import compacta_toda_pesquisa, compacta_pesquisa_selecionada
import json
import hashlib
from random import choice
# from .task import add,report_progress
from estagio.celery import app as meu_celery
from .Email.email import send_email
import requests
import random
from django.core.files.storage import FileSystemStorage
from pymongo import MongoClient
lista_arquivos = ListaArquivos
resutadopesquisaPaginado = []
from .MongoDB.MongoCennect import MongoConnect
from django.utils.translation import ugettext as _
from celery import uuid


from estagio.celery import app

import sys


def home(request):

    data = request.POST
    if(not data):
        data = request.GET

    form = Pesquisa(data)
    try:
        if(not request.session['tipo_requisicao']):
            request.session['tipo_requisicao_'] = 'todos_os_arquivos'
    except:
        request.session['tipo_requisicao'] = 'todos_os_arquivos'

    num = int(data.get('page', 1))

    resultadoPesquisa = []
    #if(request.session['tipo_requisicao'] == 'todos_os_arquivos'):
    # Verifica se é uma paginação ou submição de formulario
    con = MongoConnect()
    banco = con.connect("test_database")
    dados_db = banco.teste
    
    filtro = {}
    percent = {}
    if(data.get('porcentagem_um','') != ""):
        percent['$gte'] = int(data.get('porcentagem_um'))
    
    if(data.get('porcentagem_dois','') != ""):
        percent['$lte'] = int(data.get('porcentagem_dois'))

    if(percent):
        filtro['percent'] = percent

    if(data.get('tipoFalha','') != ""):
        filtro['type'] = data.get('tipoFalha','')

    if(data.get('falha_conjunto','') != ""):
        conjunto = int(data.get('falha_conjunto'))
        if(conjunto>=4):
            filtro['column'] = {'$gte':conjunto}
        else:
            filtro['column'] = conjunto

    consulta = dados_db.find(filtro)
    try:
        P = Paginator(list(consulta),8)
        pagina = P.page(num)
    except:
        pagina = P.page(1)

    inferior = 4
    if(pagina.number <= 5):
        inferior = pagina.number - 1
    
    superior = 5
    if(pagina.number + superior > pagina.paginator.num_pages):
        superior = pagina.paginator.num_pages - pagina.number + 1


    contexto = {
        'form': form,
        'resultadoPesquisa': resultadoPesquisa,
        'quantidade': pagina.paginator.num_pages * 8,
        'paginado': pagina,
        'items' : data.items,
        'limite_paginas': range(pagina.number-inferior,pagina.number+superior)
    }
    return render(request, "home.html", contexto)

def contatos(request):
    return render(request,"contatos.html",{"teste":"teste"})

def pesquisa(dados):
    pesquisa_arquivos = PesquisaArquivos
    meuDir = settings.COMPACTA_URL
    resultadoPesquisa  = pesquisa_arquivos.lista_arquivos(dados)
    return resultadoPesquisa

from django.http import HttpResponse
#lista arquivos em forma de arvores
def lista_em_arvore(request):
    arquivosJson = JsonResponse(lista_arvore(request))
    return arquivosJson

#Faz download de um único  arquivo
def download(request,path):
    downloadModel = Download()
    return downloadModel.getDownload(request,path)

#compacta pesquisa selecionada
def view_compacta_pesquisa_selecionada(request):
    dados = request.GET.getlist('data[]')
    teste = json.dumps(dados)
    chave = str(random.getrandbits(128))
    chaveJ = {'chave': chave}
    res = compacta_pesquisa_selecionada(teste,chaveJ)
    return JsonResponse({'status':'ok','id':'','chave':chave})

#compacta toda pesquisas
def view_compacta_toda_pesquisa(request):
    dados = {}
    print(request.session['form'])
    resultadoPesquisa = pesquisa(request.session['form'])
    dadosRequest = json.dumps(resultadoPesquisa)
    task_id = uuid()
    chave = str(task_id)
    chaveJ = {'chave':chave}
    try:
        con = MongoConnect()
        banco = con.connect("fila_download")
    except:
        pass
        # print('Erro ao conectar')

    dados_db_fila = banco.fila
    value = {
        "_id": str(chave),
        "status": "compactando"
    }

    dados = dados_db_fila.insert_one(value).inserted_id
    
    res = compacta_toda_pesquisa.apply_async((dadosRequest,chaveJ,request.session['form']['email']), task_id = task_id)
    return JsonResponse({'status': 'ok','id':res.id,'chave':chave})

#Baixa os arquivos compactados
import mimetypes
from django.http import StreamingHttpResponse
# from django.core.servers.basehttp import FileWrapper
from wsgiref.util import FileWrapper
def baixar_pesquisa(request):
    dados = request.GET
    os.chdir(settings.COMPACTA_URL)
    nome_arquivo = os.getcwd() + "/" + str(dados['chave'])+".zip"
    filename = os.path.basename(nome_arquivo)
    nome_download = str(dados['chave'])+".zip"
    try:
        chunk_size = 8192
        response = StreamingHttpResponse(FileWrapper(open(nome_arquivo, 'rb'), chunk_size),
                                          content_type=mimetypes.guess_type(nome_arquivo)[0])
        response['Content-Length'] = os.path.getsize(nome_arquivo)
        response['Content-Disposition'] = "attachment; filename=%s" % filename
    except Exception as e:
        print('Erro')
        print(e)
        print(type(e))
        print(dir(e))
        return render(request,"home.html",{})

    return response


def define_sessao(request):
    status = request.GET
    if(status['status'] == 'desativado'):
        request.session['tipo_requisicao'] = 'todos_os_arquivos'
    else:
        request.session['tipo_requisicao'] = 'pesquisa_individual'
    return JsonResponse({'status': 'ok'})


def requisicao_enviada(request):
    dados = {}
    for k in request.GET:
        dados[k]= request.GET[k]

    if(dados['tipoFalha'] != ''):
        if(dados['tipoFalha'] == 'ale'):
            dados['tipoFalha_name'] = _("random")
        else:
            dados['tipoFalha_name'] = _("sequential")

    if(dados['falha_conjunto'] != ''):
        nome = 'NET_GLOBALI_GLOBALR_PARI_PAR;all_line;T_UR;Tsolo_URsolo;net;globali;globalr;pari;parr;tsoil;ppt;t;rh;u;rhsoil'
        colunas = nome.split(';')
        dados['falha_conjunto_name'] = colunas[int(dados['falha_conjunto'])]
    try:
        request.session['email'] = request.GET['email']
        request.session['form'] = dados
    except:
        pass
    return render(request,"requisicao_enviada.html", dados)

#sistema de upload
from .upload.upload import Upload
def upload(request):
    # verifica = VerificaUpload()
    instUpload =  Upload()
    constrole_upload = 0
    if(request.method == 'POST'):
        try:
            request.FILES['myfile']
        except:
            return render(request, "upload.html",{"resposta":"Escolha Um Arquivo"})

    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        rashZip, sucess, uploaded_file_url, idTask = instUpload.upload(myfile)

        if(sucess):
            context = {
                    'uploaded_file_url': uploaded_file_url,
                    'status' : 'OK',
                    'file':myfile,
                    'rashZip': rashZip,
                    'idTask' :idTask,
            }
            return render(request, 'upload.html',context)

    return render(request,"upload.html",{'status':'erro'})

from .upload.upload import Upload
from django.http import HttpResponseRedirect
def DownloadUpload(request,file):
    if(file==""):
        return HttpResponseRedirect("/home/")
    dados = request.GET
    os.chdir("/")
    nome_arquivo = settings.MEDIA_URL + "/arquivos/uploads/"+str(file)+".zip"
    nome_download = str(file)+".zip"
    try:
        response = HttpResponse(open(nome_arquivo, 'rb').read(), content_type='x-zip-compressed')
        response['Content-Disposition'] = "attachment; filename=%s" % nome_download
        os.remove(nome_arquivo)
    except:
        return HttpResponseRedirect("/home/")
    return response


#Gerar exibe grafico gerado pelo R
from .Gerar_grafico.Gerar_grafico import GeraArquivoParaGraficoEmR
def gerarGrafico(request):
    os.chdir("/")
    with open("arquivos/arquivos/uploads/grafico/BoxplotVar/R2/metodo_R2.png", "rb") as plot:
        imagem = plot.read()
    response = HttpResponse(imagem, content_type="image/jpg")
    return response

from rpy2.robjects.packages import importr
from rpy2.robjects.packages import STAP,STF
hydro = importr("hydroGOF")

def exemplo(request):
    os.chdir("/")
    with open(os.getcwd() + "/arquivos/uploads/grafico.R", "r") as r:
        string = r.read()
    # print(string)
    try:
     fun = STAP(string, "grafico")
    except:
        pass
    return HttpResponse("Exemplo")

#Um teste usando o Celery
from .Teste.teste import teste
def exemplo_assinc(request):
    valor = request.GET['valor']
    teste.delay(int(valor))
    return HttpResponse("Pronto")

def get_resultado(request):
    dados = request.GET
    res = app.AsyncResult(dados['id'])
    return JsonResponse({'status':res.status})

#Retorna o status do id na fila
def status_stak_celery(request):
    dados = request.GET
    url = "http://localhost:5555/api/tasks"
    resposta = requests.get(url)
    resultadoJson = json.loads(resposta.content.decode('utf-8'))
    return JsonResponse({'id':dados['id'],'tasks':resultadoJson[dados['id']],'total_tasks':resultadoJson})

#retorna o status completo da fila
def fila_celery(request):
    url = "http://localhost:5555/api/tasks"
    resposta = requests.get(url)
    resultadoJson = json.loads(resposta.content.decode('utf-8'))
    return JsonResponse({'total_tasks':resultadoJson})

# from celery import app
def cancelar_requisicao(request):
    os.chdir(settings.COMPACTA_URL)
    dadosRequest = request.GET
    url = "http://localhost:5555/api/task/revoke/"+str(dadosRequest['id'])+"?terminate=true"
    resposta = requests.post(url)
    con = MongoConnect()
    banco = con.connect("fila_download")
    dados_db_fila = banco.fila
    dado = dados_db_fila.update({'_id': str(dadosRequest['chave'])}, {"status": "cancelado"}, upsert=False)
    try:
        os.remove(dadosRequest['chave']+".zip")
    except:
        pass
        # print("Não é possível remover o arquivo solicitado")
    return JsonResponse({'status':'REVOKED'})

from .sincroniza.sincroniza import Sincroniza
def sincroniza_dados(request):
    print('chegou')
    sinc = Sincroniza()
    sinc.inicia()
    return HttpResponse("Pronto")

def cancela_requisicao_upload(request):
    idTask = request.GET['id']
    url = "http://localhost:5555/api/task/revoke/" + str(idTask) + "?terminate=true"
    resposta = requests.post(url)
    return JsonResponse({"ok":"ok"})

def status_requisicao_upload(request):
    idTask = request.GET['id']
    url = "http://localhost:5555/api/task/result/" + str(idTask)
    resposta = requests.get(url)
    resultadoJson = json.loads(resposta.content.decode('utf-8'))
    return JsonResponse({"status": "ok",'statusTask':resultadoJson})
