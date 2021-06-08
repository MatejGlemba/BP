# Create your views here.
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import User, PscObvodu, VekovaSkupina, Konspekt, TypOperacie, Analyza1Model, Analyza2Model, Analyza3Model, Katalog
from django.contrib import messages
from django.urls import reverse
from django.contrib.sessions.models import Session 
import csv, io, os, base64, random
from django.core.paginator import Paginator
import datetime as dt
import xml.etree.ElementTree as ET
from psycopg2 import sql
from pymarc import MARCReader, parse_xml_to_array, Record
import xmltodict, numpy as np, pandas as pd, matplotlib.pyplot as plt
import matplotlib.pylab as plb
import matplotlib
import time
from matplotlib.dates import date2num
from pylab import rcParams
from scipy import stats
from django.db import connection
from django.db.models import Q, Count
from operator import or_
from dateutil.rrule import rrule, MONTHLY, YEARLY, WEEKLY, DAILY
from django.http.response import JsonResponse
from django.core.exceptions import ObjectDoesNotExist


user = {}
importData = None
vystupyData = None
vystupyData2 = None
graphs = None
xmlCat = None
csvFile = None
logy = []
analyzaId = None

def getLogs(request):
    if logy:
        return JsonResponse({'log' : logy.pop()})
    else:
        return JsonResponse({})

def log(message):
    now = dt.datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
    return logy.append(now + " : " + message) 

def index(request):
    if request.method == 'POST' and not user and request.POST["login"] == "admin":
        user["login"] = request.POST['login']
        context = {
            'login' : user["login"]
        }
        
        #Clear models
        PscObvodu.objects.all().delete()
        Konspekt.objects.all().delete()
        TypOperacie.objects.all().delete()
        VekovaSkupina.objects.all().delete()
        Analyza1Model.objects.all().delete()
        Analyza2Model.objects.all().delete()
        Analyza3Model.objects.all().delete()
        #Katalog.objects.all().delete()

        kat = None
        try:
            kat = Katalog.objects.count() > 0
        except ObjectDoesNotExist: 
            kat = None

        if kat:
            context = {
                'login' : user["login"],
                'katalog': True
            }
        else:
            context = {
                'login' : user["login"],
                'katalog': False
            }
        log("Používateľ bol úspešne prihlásený")
        return render(request, 'main.html', context=context)
    elif user:
        context = {
            'login' : user["login"]
        }
        return render(request, 'main.html', context=context)
    elif not user:
        return render(request, 'index.html')

def login(request):
    return render(request, 'login.html')

def logout(request):
    if user:
        user.clear()
        log("User Logged out Successfully")
        return redirect('/')
    else:
        return render(request, 'index.html')

def analyza(request):
    global importData
    global analyzaId
    global xmlCat
    if user:
        if request.method == 'POST' and 'analyza1' in dict(request.POST.items()):
            analyzaId = 1
            inicializaciaCiselnikov()
            log("Číselníky boli načítané")
            if 'fileXML' in dict(request.FILES.items()):
                fileXML = request.FILES['fileXML']
                if fileXML.name.endswith('.xml'):
                    if Katalog.objects.exists() and Katalog.objects.count() > 0:
                        print("som tu")
                    else:
                        xmlSubor(fileXML, request)   
                else:
                    messages.error(request, 'THIS IS NOT A XML FILE')
            fileCSV = request.FILES['fileCSV']
            if fileCSV.name.endswith('.csv'):
                try:
                    get = Analyza1Model.objects.count() > 0
                    Analyza1Model.objects.all().delete()
                except ObjectDoesNotExist: 
                    get = None     
                csvSubor(fileCSV, 1, request)
            else:
                messages.error(request, 'THIS IS NOT A CSV FILE')
            time.sleep(4)
            importData = Analyza1Model.objects.all()
            paginator = Paginator(importData, 5)
            page = request.GET.get('page', 1)
            data = paginator.page(page)
            context = {
                'login' : user["login"],
                'imported' : True,
                'data' : data,
                'analyzaId' : 1,
                'psc' : PscObvodu.objects.all(),
                'vek' : VekovaSkupina.objects.all(),
            }  
            return render(request, 'main.html', context=context)
        elif request.method == 'POST' and 'analyza2' in dict(request.POST.items()):
            analyzaId = 2
            inicializaciaCiselnikov()
            log("Číselníky boli načítané")
            if 'fileXML' in dict(request.FILES.items()):
                fileXML = request.FILES['fileXML']
                if fileXML.name.endswith('.xml'):
                    if Katalog.objects.exists() and Katalog.objects.count() > 0:
                        print("som tu")
                    else:
                        xmlSubor(fileXML, request)
                else:
                    messages.error(request, 'THIS IS NOT A XML FILE')
            fileCSV = request.FILES['fileCSV']
            if fileCSV.name.endswith('.csv'):
                try:
                    get = Analyza2Model.objects.count() > 0
                    Analyza2Model.objects.all().delete()
                except ObjectDoesNotExist: 
                    get = None     
                csvSubor(fileCSV, 2, request)
            else:
                messages.error(request, 'THIS IS NOT A CSV FILE')
            time.sleep(4)
            importData = Analyza2Model.objects.all()
            paginator = Paginator(importData, 5)
            page = request.GET.get('page', 1)
            data = paginator.page(page)
            context = {
                'login' : user["login"],
                'imported' : True,
                'data' : data,
                'analyzaId' : 2,
                'konspekt' : Konspekt.objects.all(),
                'operacia' : TypOperacie.objects.all(),
            }  
            return render(request, 'main.html', context=context)
        elif request.method == 'POST' and 'analyza3' in dict(request.POST.items()):
            analyzaId = 3
            inicializaciaCiselnikov()
            log("Číselníky boli načítané")
            if 'fileXML' in dict(request.FILES.items()):
                fileXML = request.FILES['fileXML']
                if fileXML.name.endswith('.xml'):
                    if Katalog.objects.exists() and Katalog.objects.count() > 0:
                        print("som tu")
                    else:
                        print("nahraj XML")
                        xmlSubor(fileXML, request)
                else:
                    messages.error(request, 'THIS IS NOT A XML FILE')
            fileCSV = request.FILES['fileCSV']
            if fileCSV.name.endswith('.csv'):
                try:
                    get = Analyza3Model.objects.count() > 0
                    Analyza3Model.objects.all().delete()
                except ObjectDoesNotExist: 
                    get = None     
                csvSubor(fileCSV, 3, request)
            else:
                messages.error(request, 'THIS IS NOT A CSV FILE')
            time.sleep(4)
            importData = Analyza3Model.objects.all()
            paginator = Paginator(importData, 5)
            page = request.GET.get('page', 1)
            data = paginator.page(page)
            context = {
                'login' : user["login"],
                'imported' : True,
                'data' : data,
                'analyzaId' : 3,
                'konspekt' : Konspekt.objects.all(),
                'vek' : VekovaSkupina.objects.all(),
            }  
            return render(request, 'main.html', context=context)
        else:
            paginator = Paginator(importData, 5)
            page = request.GET.get('page', 1)
            data = paginator.page(page)
            context = {
                'login' : user["login"],
                'imported' : True,
                'analyzaId' : analyzaId,
                'data' : data,
                'psc' : PscObvodu.objects.all(),
                'vek' : VekovaSkupina.objects.all(),
                'konspekt' : Konspekt.objects.all(),
                'operacia' : TypOperacie.objects.all(),
            }
            return render(request, 'main.html', context=context)   

def analyzaVystup(request, id):
    global vystupyData
    global vystupyData2
    global graphs
    
    if user:
        if id == 1: 
            if request.method == 'POST':
                vstupy = spracujVstupy(request, id)
                log("Vstupy do analýzy boli spracované")
                vystupy = spracovanieDat(vstupy, id)
                vystupyData = vystupy['output'] 
                log("Dáta na základe vstupov boli agregované")
                graphs = analyzaDat(vystupy, id)
                log("Výstupné sústavy z analýzy boli vytvorené")
            paginator = Paginator(vystupyData, 5)
            page = request.GET.get('page', 1)
            data = paginator.page(page)
            context = {
                'login' : user["login"],
                'imported': True,
                'data' : data,
                'analyzaId' : id,
                'graphs' : graphs,
                'psc' : PscObvodu.objects.all(),
                'vek' : VekovaSkupina.objects.all(),
            }   
            return render(request, 'main.html', context=context)
        elif id == 2:
            if request.method == 'POST':
                vstupy = spracujVstupy(request, id)
                log("Vstupy do analýzy boli spracované")
                vystupy = spracovanieDat(vstupy, id)
                vystupyData = vystupy['output'] 
                log("Dáta na základe vstupov boli agregované")
                graphs = analyzaDat(vystupy, id)
                log("Výstupné sústavy z analýzy boli vytvorené")
            paginator = Paginator(vystupyData, 5)
            page = request.GET.get('page', 1)
            data = paginator.page(page)
            context = {
                'login' : user["login"],
                'imported': True,
                'data' : data,
                'analyzaId' : id,
                'graphs' : graphs,
                'konspekt' : Konspekt.objects.all(),
                'vek' : VekovaSkupina.objects.all(),
            }   
            return render(request, 'main.html', context=context)
        elif id == 3:
            if request.method == 'POST':
                vstupy = spracujVstupy(request, id)
                log("Vstupy do analýzy boli spracované")
                vystupy = spracovanieDat(vstupy, id)
                vystupyData = vystupy['output'] 
                vystupyData2 = vystupy['output2']
                log("Dáta na základe vstupov boli agregované")
                graphs = analyzaDat(vystupy, id)
                log("Výstupné sústavy z analýzy boli vytvorené")
            paginator = Paginator(vystupyData, 5)
            page = request.GET.get('page', 1)
            data = paginator.page(page)
            context = {
                'login' : user["login"],
                'imported': True,
                'data' : data,
                'dataAnalyza3' : vystupyData2,
                'analyzaId' : id,
                'graphs' : graphs,
                'konspekt' : Konspekt.objects.all(),
                'vek' : VekovaSkupina.objects.all(),
            }   
            return render(request, 'main.html', context=context)
        else:
            return render(request, 'main.html', context=context)

def inicializaciaCiselnikov():
    ## Ciselnik Psc
    with open('bpapp/tables/psc.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            _, created = PscObvodu.objects.get_or_create(
                psc=row[0],
                obvod=row[1],
                )
    ## Ciselnik Operacie
    with open('bpapp/tables/operacie.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            _, created = TypOperacie.objects.get_or_create(
                id=row[0],
                nazov=row[1],
                )
    
    ## Ciselnik Konspekt
    with open('bpapp/tables/konspekt.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            _, created = Konspekt.objects.get_or_create(
                id=row[0],
                nazov=row[1],
                )
    
    ## Ciselnik Vekova skupina
    v = VekovaSkupina()
    setattr(v, 'id', 0)
    setattr(v, 'skupina', "0-20")
    v.save()
    v = VekovaSkupina()
    setattr(v, 'id', 1)
    setattr(v, 'skupina', "21-30")
    v.save()
    v = VekovaSkupina()
    setattr(v, 'id', 2)
    setattr(v, 'skupina', "31-40")
    v.save()
    v = VekovaSkupina()
    setattr(v, 'id', 3)
    setattr(v, 'skupina', "41-50")
    v.save()
    v = VekovaSkupina()
    setattr(v, 'id', 4)
    setattr(v, 'skupina', "51-60")
    v.save()
    v = VekovaSkupina()
    setattr(v, 'id', 5)
    setattr(v, 'skupina', "61-70")
    v.save()
    v = VekovaSkupina()
    setattr(v, 'id', 6)
    setattr(v, 'skupina', "71-100")
    v.save()

def xmlSubor(file, request):
    global xmlCat
    log("Načítava sa XML súbor")
    records = parse_xml_to_array(file)
    #xmlCat = records
    for record in records:
        obj = Katalog()
        for recordField in record.get_fields('001'):
            if recordField.is_control_field():
                setattr(obj, "katalogId", recordField.value())
       
        konspektField = record.get_fields('072')
        if not konspektField:
            konspektField = record.get_fields('C72')
            if not konspektField:
                setattr(obj, "konspekt", None)
            else:
                subfield = konspektField[0].get_subfields('9')
                try:
                    if subfield[0] and subfield[0].isdigit():
                        setattr(obj, "konspekt", subfield[0])
                except:
                    setattr(obj, "konspekt", None)
        else:   
            subfield = konspektField[0].get_subfields('9')
            try:
                if subfield[0] and subfield[0].isdigit():
                    setattr(obj, "konspekt", subfield[0])
            except:
                setattr(obj, "konspekt", None)

        ## autor
        autorField = record.get_fields('100')
        if not autorField:
            setattr(obj, "autor", None)
        else:
            setattr(obj, "autor", autorField[0].get_subfields('a')[0])
        
        ## vydavatelstvo
        vydavField = record.publisher()
        if not vydavField:
            setattr(obj, "vydavatelstvo", None)
        else:
            setattr(obj, "vydavatelstvo", vydavField)
        obj.save()
    log("XML súbor je načítaný")

def csvSubor(file, id, request):
    log("Načítava sa CSV súbor")
    data = file.read().decode('UTF-8')
    io_string = io.StringIO(data)
    next(io_string) 
    rows = {}
    failCounter = 0
    rowCounter = 0
    maxRowCounter = 0
    for row in csv.reader(io_string, delimiter=',', quotechar="|"):
        if len(row) <= 26:
            if id == 1:
                rows[rowCounter] = validujDataAnal1(row, request)
                if not rows[rowCounter]:
                    failCounter += 1
                    continue
            elif id == 2:
                rows[rowCounter] = validujDataAnal2(row, request)
                if not rows[rowCounter]:
                    failCounter += 1
                    continue
            elif id == 3:
                rows[rowCounter] = validujDataAnal3(row, request)
                if not rows[rowCounter]:
                    failCounter += 1
                    continue
            rowCounter += 1
    log("Dáta z CSV súboru boli úspešne validované")
    log("Počet chybných záznamov:" + str(failCounter))
    vlozDoDB(rows, id)

def validujDataAnal1(row, request):
    rowDict = {}

    ## tcraete
    columnCounter = 1 
    tcreate = row[columnCounter]
    if len(tcreate) == 18 and tcreate[15] == '.' and tcreate[1:9].isdigit():
        tcreate = tcreate[1:5] + '-' + tcreate[5:7] + '-' + tcreate[7:9]
        rowDict.update({'casVytvoreniaTransakcie': tcreate})
    else:
        rowDict = None

    if not rowDict:
        return rowDict
    
    columnCounter += 10
    if obsahujeCislo(row[columnCounter]) and obsahujeCislo(row[columnCounter + 1]) and len(row[columnCounter+1]) == 3: ## "285 Kč" 
        columnCounter += 1
    columnCounter += 4

    ## pohlavie
    anonym = row[columnCounter]
    columnCounter += 1
    if len(anonym) == 3 and anonym[1].isdigit() and int(anonym[1]) in [0, 1]:
        anonym = int(anonym[1])
        pohlavie = row[columnCounter]
        if anonym == 0:
            if pohlavie.isalpha() and len(pohlavie) > 2 and len(pohlavie) < 7 and pohlavie in ["zena", "muz"]:
                rowDict.update({'pohlavie': pohlavie})
            else:
                rowDict.update({'pohlavie': ''})
        elif anonym == 1:
            rowDict.update({'pohlavie': ''})
    else:
        rowDict.update({'pohlavie': ''})

    ## userHash
    columnCounter += 1
    userHash = row[columnCounter]
    if userHash:
        rowDict.update({'pouzivatelId': userHash})
    else:
       rowDict = None

    if not rowDict:
        return rowDict

    ## psc
    columnCounter += 2
    pscOld = row[columnCounter]
    if len(pscOld) == 8 and pscOld[4] == " ":
        psc = pscOld[1:7]
        psc = psc.replace(' ', '')
        obv = None
        if psc.isdigit():
            try:
                obv = PscObvodu.objects.get(psc=psc)
            except:
                obv = PscObvodu.objects.get(psc=99999)
            rowDict.update({'psc_id': obv})
        else:
            rowDict.update({'psc_id': PscObvodu.objects.get(psc=99999)})
    else:
        rowDict.update({'psc_id': PscObvodu.objects.get(psc=99999)})
    
    ## vek
    columnCounter += 1
    if anonym == 0: 
        vek = row[columnCounter].replace('"', '')
        if vek.isdigit() and int(vek) >= 0:   
            rowDict.update({'vek': int(vek)})
        else:
            rowDict.update({'vek': 0})
    elif anonym == 1:
        rowDict.update({'vek': 0})
    
    return rowDict

def validujDataAnal2(row, request):
    rowDict = {}
    columnCounter = 0
    
    ## transaction Id
    transactionId = row[columnCounter]
    rowDict.update({'transakciaId' : transactionId})

    ## tcraete
    columnCounter += 1 
    tcreate = row[columnCounter]
    if len(tcreate) == 18 and tcreate[15] == '.' and tcreate[1:9].isdigit():
        tcreate = tcreate[1:5] + '-' + tcreate[5:7] + '-' + tcreate[7:9]
        rowDict.update({'casVytvoreniaTransakcie': tcreate})
    else:
        rowDict = None
    
    if not rowDict:
        return rowDict

    columnCounter += 2
    ## typ Operacie
    typOp = row[columnCounter]
    if len(typOp) <= 2:
        try:
            obj = TypOperacie.objects.get(id=typOp)
            rowDict.update({'typOperacie_id': obj})
        except ObjectDoesNotExist:
            rowDict = None

    if not rowDict:
        return rowDict    

    columnCounter += 5
    ## konspekt, autor, vydavatelstvo
    if obsahujeCislo(row[columnCounter]):
        konspektId = row[columnCounter].split("*")[1]
        try:
            record = Katalog.objects.get(katalogId=konspektId)
            if record.konspekt and record.autor and record.vydavatelstvo:
                try:
                    kon = Konspekt.objects.get(id=record.konspekt)
                    rowDict.update({'konspekt_id': kon})      
                    rowDict.update({'autor': record.autor})
                    rowDict.update({'vydavatelstvo': record.vydavatelstvo})
                except Konspekt.DoesNotExist:
                    rowDict = None
            else:
                rowDict = None
        except Katalog.DoesNotExist:
            rowDict = None
    else:
        rowDict = None

    if not rowDict:
        return rowDict

    columnCounter += 3
    if obsahujeCislo(row[columnCounter]) and obsahujeCislo(row[columnCounter + 1]) and len(row[columnCounter+1]) == 3: ## "285 Kč" 
        columnCounter += 1
    
    columnCounter += 10
    ## dlzka Vypozicky
    dlzkaVyp = row[columnCounter]
    if dlzkaVyp.isdigit():
        rowDict.update({'dlzkaVypozicky': int(dlzkaVyp)})
    else:
        rowDict = None
    
    if not rowDict:
        return rowDict
   
    return rowDict

def validujDataAnal3(row, request):
    global xmlCat
    rowDict = {}
    columnCounter = 0
    
    ## transaction Id
    transactionId = row[columnCounter]
    rowDict.update({'transakciaId' : transactionId})
    
    ## tcraete
    columnCounter += 1 
    tcreate = row[columnCounter]
    if len(tcreate) == 18 and tcreate[15] == '.' and tcreate[1:9].isdigit():
        tcreate = tcreate[1:5] + '-' + tcreate[5:7] + '-' + tcreate[7:9]
        rowDict.update({'casVytvoreniaTransakcie': tcreate})
    else:
        rowDict = None
    
    if not rowDict:
        return rowDict

    columnCounter += 7
    ## konspekt Id - cbvk_us_cat*m0173078
    if obsahujeCislo(row[columnCounter]):
        konspektId = row[columnCounter].split("*")[1]
        try:
            record = Katalog.objects.get(katalogId=konspektId)
            if record.konspekt:
                try:
                    kon = Konspekt.objects.get(id=record.konspekt)
                    rowDict.update({'konspekt_id': kon})
                except Konspekt.DoesNotExist:
                    rowDict = None     
            else:
                rowDict = None
        except Katalog.DoesNotExist:
            rowDict = None
    else:
        rowDict = None

    if not rowDict:
        return rowDict

    columnCounter += 3
    if obsahujeCislo(row[columnCounter]) and obsahujeCislo(row[columnCounter + 1]) and len(row[columnCounter+1]) == 3: ## "285 Kč" 
        columnCounter += 1
    columnCounter += 4

    anonym = row[columnCounter]
    if len(anonym) == 3 and anonym[1].isdigit() and int(anonym[1]) in [0, 1]:
        anonym = int(anonym[1])

    columnCounter += 5
    ## vekovaSkupina Id 
    vekovaSkupinaId = row[columnCounter]
    if anonym == 0: 
        vek = row[columnCounter].replace('"', '')
        if vek.isdigit() and int(vek) >= 0:
            vek = int(vek)
            if vek <= 20:
                v = VekovaSkupina.objects.get(id=0) 
                rowDict.update({'vekovaSkupina_id': v})
            elif vek <= 30:
                v = VekovaSkupina.objects.get(id=1) 
                rowDict.update({'vekovaSkupina_id': v})
            elif vek <= 40:
                v = VekovaSkupina.objects.get(id=2)
                rowDict.update({'vekovaSkupina_id': v}) 
            elif vek <= 50:
                v = VekovaSkupina.objects.get(id=3)
                rowDict.update({'vekovaSkupina_id': v})
            elif vek <= 60:
                v = VekovaSkupina.objects.get(id=4) 
                rowDict.update({'vekovaSkupina_id': v})
            elif vek <= 70:
                v = VekovaSkupina.objects.get(id=5) 
                rowDict.update({'vekovaSkupina_id': v})
            elif vek <= 100:
                v = VekovaSkupina.objects.get(id=6)
                rowDict.update({'vekovaSkupina_id': v})
            else:
                v = VekovaSkupina.objects.get(id=0)
                rowDict.update({'vekovaSkupina_id': v})
        else:
            v = VekovaSkupina.objects.get(id=0)
            rowDict.update({'vekovaSkupina_id': v})
    elif anonym == 1:
        v = VekovaSkupina.objects.get(id=0)
        rowDict.update({'vekovaSkupina_id': v})
    else:
        v = VekovaSkupina.objects.get(id=0)
        rowDict.update({'vekovaSkupina_id': v})
    #---------------------------------------------
    return rowDict

def obsahujeCislo(inputString):
    return any(char.isdigit() for char in inputString)

def vlozDoDB(rows, id):
    if id == 1: ## Store model for analyza1
        for key, value in rows.items():
            obj = Analyza1Model()
            for k, v in value.items():
                setattr(obj, k, v)
            obj.save()
        doplnVekAPohlavie()
    elif id == 2: ## Store model for analyza2
        for key, value in rows.items():
            obj = Analyza2Model()
            for k, v in value.items():
                setattr(obj, k, v)
            obj.save()
    elif id == 3: ## Store model for analyza3
        for key, value in rows.items():
            obj = Analyza3Model()
            for k, v in value.items():
                setattr(obj, k, v)
            try:
                obj.save()
            except:
                print(key, value)
    log("Dáta boli úspešne uložené v databáze")

def doplnVekAPohlavie():
    ## Put vek
    log("Pridáva sa vek na voľné miesta podľa užívateľov")
    allTransactions = Analyza1Model.objects.all().values('pouzivatelId').distinct('pouzivatelId')
    for transaction in allTransactions:
        objects = Analyza1Model.objects.filter(pouzivatelId=transaction['pouzivatelId'], vek=0)
        vek = random.randint(15,80)
        for obj in objects:
            setattr(obj, 'vek', vek)
            obj.save()   

    ## Put pohlavie
    log("Pridáva sa pohlavie na voľné miesta podľa užívateľov")
    for transaction in allTransactions:
        objects = Analyza1Model.objects.filter(pouzivatelId=transaction['pouzivatelId'], pohlavie='')
        r = random.randint(0,1)
        for obj in objects:
            if r == 0:
                setattr(obj, 'pohlavie', "zena")
            else:
                setattr(obj, 'pohlavie', "muz")
            obj.save()  

def spracujVstupy(request, id):
    vstupy = {}
    postItems = dict(request.POST.items())
    
    if id == 1:
        ## Pohlavie
        pohlavie = {}
        if 'pohlavieM' in postItems:
            pohlavie.update({'pohlavie': 'muz'})
        if 'pohlavieZ' in postItems:
            pohlavie.update({'pohlavie': 'zena'})
        if pohlavie:
            vstupy.update({'pohlavie' : pohlavie})
        
        ## Vekova Skupina
        vekSkupina = {}
        if 'age-all' in postItems:
            vekSkupina.update({'all': True})
        else:
            for obj in VekovaSkupina.objects.all():
                vekId = 'vek_' + str(obj.id)
                if vekId in postItems:
                    vekSkupina.update({vekId: obj.id})
        if vekSkupina:
            vstupy.update({'vekovaSkupina' : vekSkupina})
        
        ## PSC
        psc = {}
        if 'psc-all' in postItems:
            psc.update({'all': True})
        else:
            for obj in PscObvodu.objects.all():
                pscId = 'psc_' + str(obj.psc)
                if pscId in postItems:
                    psc.update({pscId: obj.psc})
        if psc:
            vstupy.update({'pscObvodu' : psc})

        ## Cas
        cas = {}
        if 'od' in postItems and not postItems['od'] == '':
            cas.update({'od': postItems['od']})
        if 'do' in postItems and not postItems['do'] == '':
            cas.update({'do': postItems['do']})
        if cas:
            vstupy.update({'cas': cas})

        ## Interval
        interval = {}
        if 'intervalRok' in postItems:
            vstupy.update({'interval': YEARLY})
        elif 'intervalMesiac' in postItems:
            vstupy.update({'interval': MONTHLY})
        elif 'intervalTyzden' in postItems:
            vstupy.update({'interval': WEEKLY})
        elif 'intervalDen' in postItems:
            vstupy.update({'interval': DAILY})
    elif id == 2:
        ## Typ Operacie
        typOperacie = {}
        if 'operacia-all' in postItems:
            typOperacie.update({'all': True})
        else:
            for obj in TypOperacie.objects.all():
                operId = 'operacia_' + str(obj.id)
                if operId in postItems:
                    typOperacie.update({operId: obj.id})
        if typOperacie:
            vstupy.update({'typOperacie' : typOperacie})
    
        ## Konspekt
        konspekt = {}
        if 'konspekt-all' in postItems:
            konspekt.update({'all': True})
        else:
            for obj in Konspekt.objects.all():
                konspektId = 'konspekt_' + str(obj.id)
                if konspektId in postItems:
                    konspekt.update({konspektId: obj.id}) 
        if konspekt:
            vstupy.update({'konspekt': konspekt})

        ## Cas
        cas = {}
        if 'od' in postItems and not postItems['od'] == '':
            cas.update({'od': postItems['od']})
        if 'do' in postItems and not postItems['do'] == '':
            cas.update({'do': postItems['do']})
        if cas:
            vstupy.update({'cas': cas})

        ## Interval
        interval = {}
        if 'intervalRok' in postItems:
            vstupy.update({'interval': YEARLY})
        elif 'intervalMesiac' in postItems:
            vstupy.update({'interval': MONTHLY})
        elif 'intervalTyzden' in postItems:
            vstupy.update({'interval': WEEKLY})
        elif 'intervalDen' in postItems:
            vstupy.update({'interval': DAILY})
    elif id == 3:
        ## Vekova Skupina
        vekSkupina = {}
        if 'age-all' in postItems:
            vekSkupina.update({'all': True})
        else:
            for obj in VekovaSkupina.objects.all():
                vekId = 'vek_' + str(obj.id)
                if vekId in postItems:
                    vekSkupina.update({vekId: obj.id})
        if vekSkupina:
            vstupy.update({'vekovaSkupina' : vekSkupina})
        
        ## Konspekt
        konspekt = {}
        if 'konspekt-all' in postItems:
            konspekt.update({'all': True})
        else:
            for obj in Konspekt.objects.all():
                konspektId = 'konspekt_' + str(obj.id)
                if konspektId in postItems:
                    konspekt.update({konspektId: obj.id}) 
        if konspekt:
            vstupy.update({'konspekt': konspekt})

        ## Cas
        cas = {}
        if 'od' in postItems and not postItems['od'] == '':
            cas.update({'od': postItems['od']})
        if 'do' in postItems and not postItems['do'] == '':
            cas.update({'do': postItems['do']})
        if cas:
            vstupy.update({'cas': cas})

        ## Interval
        interval = {}
        if 'intervalRok' in postItems:
            vstupy.update({'interval': YEARLY})
        elif 'intervalMesiac' in postItems:
            vstupy.update({'interval': MONTHLY})
        elif 'intervalTyzden' in postItems:
            vstupy.update({'interval': WEEKLY})
        elif 'intervalDen' in postItems:
            vstupy.update({'interval': DAILY})
  
    return vstupy

def spracovanieDat(vstupy, id):
    vystupy = {}

    if id == 1:
        ## casovy interval
        interval = None
        if 'interval' in vstupy:
            interval = vstupy['interval']
        else:
            interval = DAILY

        ## min and max time 
        maxDate = Analyza1Model.objects.all().values('casVytvoreniaTransakcie').order_by('-casVytvoreniaTransakcie')[0]
        minDate = Analyza1Model.objects.all().values('casVytvoreniaTransakcie').order_by('casVytvoreniaTransakcie')[0]  
        dates = [dt.date() for dt in rrule(interval, dtstart=minDate['casVytvoreniaTransakcie'], until=maxDate['casVytvoreniaTransakcie'])]

        ## Histogramy
        histogramy = {}
        ## hist pohlavie
        histPohlavieQ = Analyza1Model.objects.all().values('pohlavie').annotate(dcount=Count('pouzivatelId', distinct = True)).order_by()
        histPohlavie = {}
        for h in histPohlavieQ:
            histPohlavie.update({h['pohlavie'] : h['dcount']})
        histogramy['histPohlavie'] = histPohlavie

        ## hist vekova skupina
        histVek = {}
        for vek in VekovaSkupina.objects.all():
            sk = vek.skupina.split('-')
            vekovaSkupinaGroup = Analyza1Model.objects.all().filter(Q(vek__gte=sk[0],vek__lte=sk[1])).distinct('pouzivatelId')
            histVek.update({vek.skupina:len(vekovaSkupinaGroup)})
        histogramy['histVek']=histVek

        ## hist psc 
        histPscQ = Analyza1Model.objects.values('psc_id').annotate(dcount=Count('pouzivatelId', distinct = True)).order_by()
        histPsc = {}
        for h in histPscQ:
            obv = PscObvodu.objects.get(psc=h['psc_id'])
            histPsc.update({obv.obvod : h['dcount']})
        histogramy['histPsc'] = histPsc

        ## hist cas
        histCas = {}
        #print('DATES',dates)
        counter = 0
        if len(dates) % 2 == 0:
            for date in range(int(len(dates)/2)):
                casGroup = Analyza1Model.objects.all().filter(casVytvoreniaTransakcie__range=[dates[counter], dates[counter+1]])
                histCas.update({dates[counter]:len(casGroup)})
                counter += 2
        else:
            for date in range(int(len(dates)/2)):
                casGroup = Analyza1Model.objects.all().filter(casVytvoreniaTransakcie__range=[dates[counter], dates[counter+1]])
                histCas.update({dates[counter]:len(casGroup)})
                counter += 2
            casGroup = Analyza1Model.objects.all().filter(casVytvoreniaTransakcie__gte=dates[len(dates)-1])
            histCas.update({dates[len(dates)-1]:len(casGroup)})
        histogramy['histCas']=histCas


        ## Grafy
        grafy = {}
                
        ## aggregate query filter
        query = Q()
        queryPsc = Q()
        if 'pscObvodu' in vstupy and 'all' not in vstupy['pscObvodu']:
            for k, v in dict(vstupy['pscObvodu']).items():
                sk = PscObvodu.objects.get(psc=v) 
                queryPsc = queryPsc | Q(psc_id=sk.psc)
        query = query & queryPsc
        queryVekSk = Q()  
        if 'vekovaSkupina' in vstupy and 'all' not in vstupy['vekovaSkupina']:
            for k, v in dict(vstupy['vekovaSkupina']).items():
                sk = VekovaSkupina.objects.get(id=v)
                sk = sk.skupina.split('-')
                queryVekSk = queryVekSk | Q(vek__gte=sk[0],vek__lte=sk[1])
        query = query & queryVekSk
        if 'pohlavie' in vstupy and len(vstupy['pohlavie']) == 1 and 'all' not in vstupy['pohlavie']:
            query = query & Q(pohlavie=vstupy['pohlavie']['pohlavie'])
            
        dateIntervals = None
        if 'cas' in vstupy:
            if len(vstupy['cas']) == 1:
                if 'od' in vstupy['cas']:
                    ## od - do current datetime
                    od = dt.datetime.strptime(vstupy['cas']['od'], '%Y-%m-%d')
                    dateIntervals = [dt.date() for dt in rrule(interval, dtstart=od, until=maxDate['casVytvoreniaTransakcie'])]
                else:
                    ## datetime < do
                    do = dt.datetime.strptime(vstupy['cas']['do'], '%Y-%m-%d')
                    dateIntervals = [dt.date() for dt in rrule(interval, dtstart=minDate['casVytvoreniaTransakcie'], until=do)]      
            else:
                ## od - do
                od = dt.datetime.strptime(vstupy['cas']['od'], '%Y-%m-%d')
                do = dt.datetime.strptime(vstupy['cas']['do'], '%Y-%m-%d')
                dateIntervals = [dt.date() for dt in rrule(interval, dtstart=od, until=do)]      
        else:
            ## od min - do max
            dateIntervals = [dt.date() for dt in rrule(interval, dtstart=minDate['casVytvoreniaTransakcie'], until=maxDate['casVytvoreniaTransakcie'])]      

        # print('QUERY',query)
        graf = {}
        queryTime = Q()
        counter = 0
        if len(dateIntervals) % 2 == 0:
            for dateInterval in range(int(len(dateIntervals)/2)):
                queryTime = Q(casVytvoreniaTransakcie__range=[dateIntervals[counter], dateIntervals[counter+1]])
                # GET 
                group = Analyza1Model.objects.all().filter(query).filter(queryTime)#.distinct('pouzivatelId')
                graf.update({dateIntervals[counter]:len(group)})
                counter += 2
        else:
            for dateInterval in range(int(len(dateIntervals)/2)):
                queryTime = Q(casVytvoreniaTransakcie__range=[dateIntervals[counter], dateIntervals[counter+1]])
                # GET 
                group = Analyza1Model.objects.all().filter(query).filter(queryTime)#.distinct('pouzivatelId')
                graf.update({dateIntervals[counter]:len(group)})
                counter += 2
            queryTime = Q(casVytvoreniaTransakcie__gte=dateIntervals[len(dateIntervals)-1])
            group = Analyza1Model.objects.all().filter(query).filter(queryTime)#.distinct('pouzivatelId')
            graf.update({dateIntervals[len(dateIntervals)-1]:len(group)})
        
        ## Tabulka output
        group = Analyza1Model.objects.all().filter(query).distinct('pouzivatelId')
        vystupy.update({'output': group})        


        grafy['graf']=graf
        #print('VSTUPY:--',vstupy)
        #print('HISTOGRAMY:--',histogramy)
        #print('GRAFY:--',grafy)
        
        
        vystupy.update({'histogramy':histogramy})
        vystupy.update({'grafy':grafy})
    elif id == 2:
        ## casovy interval
        interval = None
        if 'interval' in vstupy:
            interval = vstupy['interval']
        else:
            interval = DAILY

        ## min and max time 
        maxDate = Analyza2Model.objects.all().values('casVytvoreniaTransakcie').order_by('-casVytvoreniaTransakcie')[0]
        minDate = Analyza2Model.objects.all().values('casVytvoreniaTransakcie').order_by('casVytvoreniaTransakcie')[0]  
        dates = [dt.date() for dt in rrule(interval, dtstart=minDate['casVytvoreniaTransakcie'], until=maxDate['casVytvoreniaTransakcie'])]

        ## Histogramy
        histogramy = {}
        ## hist konspekt
        histKonspekt = {}
        #histKonspektQ = Analyza2Model.objects.all().values('konspekt_id').annotate(dcount=Count('transakciaId', distinct = True)).order_by()
        cursor = connection.cursor()
        cursor.execute('select bpapp_konspekt.nazov, count("bpapp_analyza2model"."transakciaId") as c from bpapp_analyza2model inner join bpapp_konspekt on (bpapp_analyza2model.konspekt_id_id = "bpapp_konspekt"."id") group by bpapp_konspekt.nazov')
        result = cursor.fetchall()
        
        for r,v in result:
            histKonspekt.update({r : v})
        histogramy['histKonspekt'] = histKonspekt
    

        ## hist typ Operacie
        histTypOpQ = Analyza2Model.objects.all().values('typOperacie_id').annotate(dcount=Count('transakciaId', distinct = True)).order_by()
        histTypOp = {}
        for h in histTypOpQ:
            histTypOp.update({h['typOperacie_id'] : h['dcount']})
        histogramy['histTypOp'] = histTypOp

        ## hist cas
        histCas = {}
        counter = 0
        if len(dates) % 2 == 0:
            for date in range(int(len(dates)/2)):
                casGroup = Analyza2Model.objects.all().filter(casVytvoreniaTransakcie__range=[dates[counter], dates[counter+1]])
                histCas.update({dates[counter]:len(casGroup)})
                counter += 2
        else:
            for date in range(int(len(dates)/2)):
                casGroup = Analyza2Model.objects.all().filter(casVytvoreniaTransakcie__range=[dates[counter], dates[counter+1]])
                histCas.update({dates[counter]:len(casGroup)})
                counter += 2
            casGroup = Analyza2Model.objects.all().filter(casVytvoreniaTransakcie__gte=dates[len(dates)-1])
            histCas.update({dates[len(dates)-1]:len(casGroup)})
        histogramy['histCas']=histCas


        ## Grafy
        grafy = {}
                
        ## aggregate query filter
        query = Q()
        queryKonspekt = Q()
        if 'konspekt' in vstupy and 'all' not in vstupy['konspekt']:
            for k, v in dict(vstupy['konspekt']).items():
                sk = Konspekt.objects.get(id=v) 
                queryKonspekt = queryKonspekt | Q(konspekt_id=sk.id)
        query = query & queryKonspekt
        queryTypOp = Q()  
        if 'typOperacie' in vstupy and 'all' not in vstupy['typOperacie']:
            for k, v in dict(vstupy['typOperacie']).items():
                sk = TypOperacie.objects.get(id=v)
                queryTypOp = queryTypOp | Q(typOperacie_id=sk.id)
        query = query & queryTypOp

        dateIntervals = None
        if 'cas' in vstupy:
            if len(vstupy['cas']) == 1:
                if 'od' in vstupy['cas']:
                    ## od - do current datetime
                    od = dt.datetime.strptime(vstupy['cas']['od'], '%Y-%m-%d')
                    dateIntervals = [dt.date() for dt in rrule(interval, dtstart=od, until=maxDate['casVytvoreniaTransakcie'])]
                else:
                    ## datetime < do
                    do = dt.datetime.strptime(vstupy['cas']['do'], '%Y-%m-%d')
                    dateIntervals = [dt.date() for dt in rrule(interval, dtstart=minDate['casVytvoreniaTransakcie'], until=do)]      
            else:
                ## od - do
                od = dt.datetime.strptime(vstupy['cas']['od'], '%Y-%m-%d')
                do = dt.datetime.strptime(vstupy['cas']['do'], '%Y-%m-%d')
                dateIntervals = [dt.date() for dt in rrule(interval, dtstart=od, until=do)]      
        else:
            ## od min - do max
            dateIntervals = [dt.date() for dt in rrule(interval, dtstart=minDate['casVytvoreniaTransakcie'], until=maxDate['casVytvoreniaTransakcie'])]      

        # print('QUERY',query)
        graf = {}
        queryTime = Q()
        counter = 0
        if len(dateIntervals) % 2 == 0:
            for dateInterval in range(int(len(dateIntervals)/2)):
                queryTime = Q(casVytvoreniaTransakcie__range=[dateIntervals[counter], dateIntervals[counter+1]])
                # GET 
                group = Analyza2Model.objects.all().filter(query).filter(queryTime)#.distinct('pouzivatelId')
                graf.update({dateIntervals[counter]:len(group)})
                counter += 2
        else:
            for dateInterval in range(int(len(dateIntervals)/2)):
                queryTime = Q(casVytvoreniaTransakcie__range=[dateIntervals[counter], dateIntervals[counter+1]])
                # GET 
                group = Analyza2Model.objects.all().filter(query).filter(queryTime)#.distinct('pouzivatelId')
                graf.update({dateIntervals[counter]:len(group)})
                counter += 2
            queryTime = Q(casVytvoreniaTransakcie__gte=dateIntervals[len(dateIntervals)-1])
            group = Analyza2Model.objects.all().filter(query).filter(queryTime)#.distinct('pouzivatelId')
            graf.update({dateIntervals[len(dateIntervals)-1]:len(group)})
        
        ## Tabulka output
        group = Analyza2Model.objects.all().filter(query).distinct('transakciaId')
        grafy['graf']=graf

        vystupy.update({'output': group})
        vystupy.update({'histogramy':histogramy})
        vystupy.update({'grafy':grafy})
    elif id == 3:
        ## casovy interval
        interval = None
        if 'interval' in vstupy:
            interval = vstupy['interval']
        else:
            interval = DAILY

        ## min and max time 
        maxDate = Analyza3Model.objects.all().values('casVytvoreniaTransakcie').order_by('-casVytvoreniaTransakcie')[0]
        minDate = Analyza3Model.objects.all().values('casVytvoreniaTransakcie').order_by('casVytvoreniaTransakcie')[0]  
        dates = [dt.date() for dt in rrule(interval, dtstart=minDate['casVytvoreniaTransakcie'], until=maxDate['casVytvoreniaTransakcie'])]

        ## Histogramy
        histogramy = {}
        
        ## hist vekova skupina
        histVek = {}
        for vek in VekovaSkupina.objects.all():
            vekovaSkupinaGroup = Analyza3Model.objects.all().filter(vekovaSkupina_id=vek.id).distinct('transakciaId')
            histVek.update({vek.skupina:len(vekovaSkupinaGroup)})
        histogramy['histVek']=histVek

        ## hist konspekt
        histKonspekt = {}
        #histKonspektQ = Analyza2Model.objects.all().values('konspekt_id').annotate(dcount=Count('transakciaId', distinct = True)).order_by()
        cursor = connection.cursor()
        cursor.execute('select bpapp_konspekt.nazov, count("bpapp_analyza3model"."transakciaId") as c from bpapp_analyza3model inner join bpapp_konspekt on (bpapp_analyza3model.konspekt_id_id = "bpapp_konspekt"."id") group by bpapp_konspekt.nazov')
        result = cursor.fetchall()
        
        for r,v in result:
            histKonspekt.update({r : v})
        histogramy['histKonspekt'] = histKonspekt
        
        
        ## Grafy        
        # query do tabulky a na grafy
        conditionQuery = 'where '
        skupinaCounter = 0
        konspektCounter = 0
        query = Q()
        queryVekSk = Q()  
        if 'vekovaSkupina' in vstupy and 'all' not in vstupy['vekovaSkupina']:
            conditionQuery += '('
            for k, v in dict(vstupy['vekovaSkupina']).items():
                sk = VekovaSkupina.objects.get(id=v)
                queryVekSk = queryVekSk | Q(vekovaSkupina_id=sk.id)
                if skupinaCounter == 0:
                    conditionQuery += '"bpapp_vekovaskupina".id = ' + str(sk.id)
                else:
                    conditionQuery += ' or "bpapp_vekovaskupina".id = ' + str(sk.id)
                skupinaCounter += 1
            conditionQuery += ')'
        query = query & queryVekSk

        queryKonspekt = Q()
        if 'konspekt' in vstupy and 'all' not in vstupy['konspekt']:
            if skupinaCounter > 0:
                conditionQuery += ' and ('
            else:
                conditionQuery += '('
            for k, v in dict(vstupy['konspekt']).items():
                sk = Konspekt.objects.get(id=v) 
                queryKonspekt = queryKonspekt | Q(konspekt_id=sk.id)
                if konspektCounter == 0:
                    conditionQuery += 'bpapp_konspekt.nazov = ' + '\'' + sk.nazov + '\''
                else:
                    conditionQuery += ' or bpapp_konspekt.nazov = ' + '\'' + sk.nazov + '\''
                konspektCounter += 1
            conditionQuery += ')'
        query = query & queryKonspekt

        # casove intervaly
        dateIntervals = None
        if 'cas' in vstupy:
            if len(vstupy['cas']) == 1:
                if 'od' in vstupy['cas']:
                    ## od - do current datetime
                    od = dt.datetime.strptime(vstupy['cas']['od'], '%Y-%m-%d')
                    dateIntervals = [dt.date() for dt in rrule(interval, dtstart=od, until=maxDate['casVytvoreniaTransakcie'])]
                else:
                    ## datetime < do
                    do = dt.datetime.strptime(vstupy['cas']['do'], '%Y-%m-%d')
                    dateIntervals = [dt.date() for dt in rrule(interval, dtstart=minDate['casVytvoreniaTransakcie'], until=do)]      
            else:
                ## od - do
                od = dt.datetime.strptime(vstupy['cas']['od'], '%Y-%m-%d')
                do = dt.datetime.strptime(vstupy['cas']['do'], '%Y-%m-%d')
                dateIntervals = [dt.date() for dt in rrule(interval, dtstart=od, until=do)]      
        else:
            ## od min - do max
            dateIntervals = [dt.date() for dt in rrule(interval, dtstart=minDate['casVytvoreniaTransakcie'], until=maxDate['casVytvoreniaTransakcie'])]      

        graf = {}
        counter = 0
        dateQuery = ''
        if skupinaCounter > 0 or konspektCounter > 0:
            conditionQuery += ' and ('
        else:
            conditionQuery += '('
        for dateInterval in range(int(len(dateIntervals))):
            dateQuery = ''
            if counter >= int(len(dateIntervals)) - 1:
                dateQuery = conditionQuery + '"bpapp_analyza3model"."casVytvoreniaTransakcie" = \''+ dateIntervals[counter].strftime("%Y-%m-%d") + '\')'
                stringQueryFirstPart = 'select "bpapp_vekovaskupina".skupina, bpapp_konspekt.nazov, "bpapp_analyza3model"."casVytvoreniaTransakcie", count("bpapp_analyza3model"."transakciaId") as pocet from bpapp_analyza3model inner join bpapp_konspekt on (bpapp_analyza3model.konspekt_id_id = "bpapp_konspekt"."id") inner join bpapp_vekovaskupina on ("bpapp_analyza3model"."vekovaSkupina_id_id" = "bpapp_vekovaskupina"."id") ' 
                stringQuerySecondPart = ' group by "bpapp_vekovaskupina".skupina, bpapp_konspekt.nazov, "bpapp_analyza3model"."casVytvoreniaTransakcie" order by "bpapp_vekovaskupina".skupina, pocet DESC'
                qry_str = stringQueryFirstPart + dateQuery + stringQuerySecondPart
                cursor = connection.cursor()
                cursor.execute(qry_str)
                result = cursor.fetchall()
                graf.update({counter:result})
                #print('COUNTER', counter, 'query', qry_str)
            else:    
                dateQuery = conditionQuery + '"bpapp_analyza3model"."casVytvoreniaTransakcie" >= \''+ dateIntervals[counter].strftime("%Y-%m-%d") + '\' and "bpapp_analyza3model"."casVytvoreniaTransakcie" < \''+ dateIntervals[counter+1].strftime("%Y-%m-%d") + '\')'
                stringQueryFirstPart = 'select "bpapp_vekovaskupina".skupina, bpapp_konspekt.nazov, "bpapp_analyza3model"."casVytvoreniaTransakcie", count("bpapp_analyza3model"."transakciaId") as pocet from bpapp_analyza3model inner join bpapp_konspekt on (bpapp_analyza3model.konspekt_id_id = "bpapp_konspekt"."id") inner join bpapp_vekovaskupina on ("bpapp_analyza3model"."vekovaSkupina_id_id" = "bpapp_vekovaskupina"."id") ' 
                stringQuerySecondPart = ' group by "bpapp_vekovaskupina".skupina, bpapp_konspekt.nazov, "bpapp_analyza3model"."casVytvoreniaTransakcie" order by "bpapp_vekovaskupina".skupina, pocet DESC'
                qry_str = stringQueryFirstPart + dateQuery + stringQuerySecondPart
                cursor = connection.cursor()
                cursor.execute(qry_str)
                result = cursor.fetchall()
                graf.update({counter:result})
                #print('COUNTER', counter, 'query', qry_str)
            counter += 1

        # GET
        grafy = {}
        for key,values in graf.items():
            histPomocnySkupina = {}
            for vek in VekovaSkupina.objects.all():
                histPomocny = {}
                maxCount = 0
                dalsiaSk = False
                for s,k,c,p in values:
                    if vek.skupina == s:
                        maxCount += 1              
                        histPomocny.update({maxCount : k})
                    if maxCount == 3:
                        dalsiaSk = True
                        break
                if dalsiaSk == True or maxCount > 0:
                    if len(histPomocny) < 3:
                        for i in range(maxCount + 1, 4):
                            histPomocny.update({i + 1: '-'})
                    histPomocnySkupina.update({vek.skupina:histPomocny})
                    continue
            grafy.update({c.strftime("%Y-%m-%d"):histPomocnySkupina})
        #print('GRAFY', grafy) 
        ## Tabulka output
        tabulkaOutput = Analyza3Model.objects.all().filter(query).distinct('transakciaId')
                
        vystupy.update({'output': tabulkaOutput})
        vystupy.update({'output2' : grafy})
        vystupy.update({'histogramy':histogramy})
        #vystupy.update({'grafy':grafy})

    return vystupy

def analyzaDat(vystupy, id):
    urlFront = '/static/graphs/'
    path = 'bpapp/static/graphs/'
    graphsDict = {}

    if id == 1:
        ## Hlavne Grafy
        for k,graf in vystupy['grafy'].items():
            ## - vstupne polia pre hlavne grafy
            y = list(graf.values())
            x = []
            for key in list(graf.keys()):
                x.append(key.strftime("%m/%d/%Y"))
            x = matplotlib.dates.datestr2num(x)
            
            ## -------------Main Hist----------------
            plt.bar(graf.keys(), graf.values(), color='g')
            plt.suptitle('Histogram', fontsize=20)
            plt.xlabel('Dátum', fontsize=18)
            plt.ylabel('Počet transakcií', fontsize=16)
            plt.gcf().autofmt_xdate()
            nazov = path + 'mainHist.png'
            plt.savefig(nazov)
            url = urlFront + 'mainHist.png'
            pair = {}
            pair.update({'url': url })
            pair.update({'popis': "Histogram počtu transakcií všetkých užívateľov podľa vstupných parametrov [pohlavie, obvod, veková skupina] vzhľadom na čas ich vytvorenia, ktorý je rozdelený do rozsahu podľa vstupného parametra (defaulnte je to od najstaršej transakcie po najnovšiu) v intervaloch podľa vstupného parametra (defaultne to je Denne)."})
            graphsDict.update({'pairMainHist': pair })
            plt.close()
            
            ## ---------------Main Polynomial--------
            lenX = len(x)
            model = np.poly1d(np.polyfit(x, y, 3))
            line = np.linspace(x[0], x[lenX-1], 10)
            fig, ax = plt.subplots() 
            plt.scatter(x, y)
            plt.plot(line, model(line))
            l = matplotlib.dates.AutoDateLocator()
            f = matplotlib.dates.AutoDateFormatter(l)
            ax.xaxis.set_major_locator(l)
            ax.xaxis.set_major_formatter(f)
            plt.suptitle('Polynomialna regresia', fontsize=20)
            plt.xlabel('Dátum', fontsize=18)
            plt.ylabel('Počet transakcií', fontsize=16)
            plt.gcf().autofmt_xdate()
            nazov = path + 'polyMain.png'
            plt.savefig(nazov)
            url = urlFront + 'polyMain.png'
            pair = {}
            pair.update({'url': url })
            pair.update({'popis': "Graf polynomialnej funkcie, ktorá zodpovedá vstupným parametrom. Ak neboli zadané žiadne, je aplikovaná na všetky dáta. Polynomiálna regresia je vhodnejšia na presnejšiu aproximáciu vstupných nezávislých dát (os x), čím sa snaží čo najlepšie predikovať závislé dáta. Ak sú ale veľké výkyvy hodnôt, môže byť nepresná. V tomto grafe je polynomialna funkcia 3 stupňa." })
            graphsDict.update({'pairPolyMain': pair })
            plt.close()

            ## ---------------Main Linear-------------
            slope, intercept, r, p, std_err = stats.linregress(x, y)
            def func(x):
                return slope * x + intercept
            model = list(map(func, x))
            fig, ax = plt.subplots()
            ax.scatter(x, y)
            ax.plot(x, model)
            l = matplotlib.dates.AutoDateLocator()
            f = matplotlib.dates.AutoDateFormatter(l)
            ax.xaxis.set_major_locator(l)
            ax.xaxis.set_major_formatter(f)
            plt.suptitle('Lineárna regresia', fontsize=20)
            plt.xlabel('Dátum', fontsize=18)
            plt.ylabel('Počet transakcií', fontsize=16)
            plt.gcf().autofmt_xdate()
            nazov = path + 'linMain.png'
            plt.savefig(nazov)
            url = urlFront + 'linMain.png'
            pair = {}
            pair.update({'url': url })
            pair.update({'popis': "Graf lineárnej regresie. Lineárna regresia je základným typom analýzy na princípe \"Supervised learning\". Na rozdieľ od polynomiálnej funkcie, lineárna popisuje lineárny vzťah medzi závislou a nezávislou hodnotou."})
            graphsDict.update({'pairLinMain': pair })
            plt.close()
            
        # POMOCNE HISTOGRAMY
        inc = 1
        for k,v in vystupy['histogramy'].items():
            plt.bar(v.keys(), v.values(), color='g')
            nazov = path + 'histPart' + str(inc) + '.png'
            plt.suptitle('Histogram', fontsize=20)
            plt.ylabel('Počet transakcií', fontsize=16)
            plt.gcf().autofmt_xdate()
            plt.savefig(nazov)
            url = urlFront + 'histPart' + str(inc) + '.png'
            pair = {}
            pair.update({'url' : url })
            if k == 'histVek':
                pair.update({'popis': "Histogram všetkých transakcií používateľov podľa vekových skupín."})
                plt.xlabel('Veková skupina', fontsize=18)
            elif k == 'histCas':
                pair.update({'popis': "Histogram všetkých vykonaných transakcií podľa ich dátumu vytvorenia rozdelené do intervalou podľa vstupu alebo defaultne denne."})
                plt.xlabel('Dátum', fontsize=18)
            elif k == 'histPsc':
                pair.update({'popis': "Histogram všetkých transakcií používateľov podľa ich bydliska."})
                plt.xlabel('Obvod', fontsize=18)
            elif k == 'histPohlavie':
                pair.update({'popis': "Histogram všetkých transakcií používateľov podľa ich pohlavia."})
                plt.xlabel('Pohlavie', fontsize=18)
            graphsDict.update({'pair' + 'histPart' + str(inc): pair})
            plt.close()
            inc += 1
    
    elif id == 2:
        ## Hlavne Grafy
        for k,graf in vystupy['grafy'].items():
            ## - vstupne polia pre hlavne grafy
            y = list(graf.values())
            x = []
            for key in list(graf.keys()):
                x.append(key.strftime("%m/%d/%Y"))
            x = matplotlib.dates.datestr2num(x)
            
            ## -------------Main Hist----------------
            plt.bar(graf.keys(), graf.values(), color='g')
            plt.suptitle('Histogram', fontsize=20)
            plt.xlabel('Dátum', fontsize=18)
            plt.ylabel('Počet transakcií', fontsize=16)
            plt.gcf().autofmt_xdate()
            nazov = path + 'mainHist.png'
            plt.savefig(nazov)
            url = urlFront + 'mainHist.png'
            pair = {}
            pair.update({'url': url })
            pair.update({'popis': "Histogram počtu transakcií podľa vstupných parametrov [Konspekt, Typ Operácie] vzhľadom na čas ich vytvorenia, ktorý je rozdelený do rozsahu podľa vstupného parametra (defaulnte je to od najstaršej transakcie po najnovšiu) v intervaloch podľa vstupného parametra (defaultne to je Denne)."})
            graphsDict.update({'pairMainHist': pair })
            plt.close()
            
            ## ---------------Main Polynomial--------
            lenX = len(x)
            model = np.poly1d(np.polyfit(x, y, 3))
            line = np.linspace(x[0], x[lenX-1], 10)
            fig, ax = plt.subplots() 
            plt.scatter(x, y)
            plt.plot(line, model(line))
            l = matplotlib.dates.AutoDateLocator()
            f = matplotlib.dates.AutoDateFormatter(l)
            ax.xaxis.set_major_locator(l)
            ax.xaxis.set_major_formatter(f)
            plt.suptitle('Polynomialna regresia', fontsize=20)
            plt.xlabel('Dátum', fontsize=18)
            plt.ylabel('Počet transakcií', fontsize=16)
            plt.gcf().autofmt_xdate()
            nazov = path + 'polyMain.png'
            plt.savefig(nazov)
            url = urlFront + 'polyMain.png'
            pair = {}
            pair.update({'url': url })
            pair.update({'popis': "Graf polynomialnej funkcie, ktorá zodpovedá vstupným parametrom. Ak neboli zadané žiadne, je aplikovaná na všetky dáta. Polynomiálna regresia je vhodnejšia na presnejšiu aproximáciu vstupných nezávislých dát (os x), čím sa snaží čo najlepšie predikovať závislé dáta. Ak sú ale veľké výkyvy hodnôt, môže byť nepresná. V tomto grafe je polynomialna funkcia 3 stupňa." })
            graphsDict.update({'pairPolyMain': pair })
            plt.close()

            ## ---------------Main Linear-------------
            slope, intercept, r, p, std_err = stats.linregress(x, y)
            def func(x):
                return slope * x + intercept
            model = list(map(func, x))
            fig, ax = plt.subplots()
            ax.scatter(x, y)
            ax.plot(x, model)
            l = matplotlib.dates.AutoDateLocator()
            f = matplotlib.dates.AutoDateFormatter(l)
            ax.xaxis.set_major_locator(l)
            ax.xaxis.set_major_formatter(f)
            plt.suptitle('Lineárna regresia', fontsize=20)
            plt.xlabel('Dátum', fontsize=18)
            plt.ylabel('Počet transakcií', fontsize=16)
            plt.gcf().autofmt_xdate()
            nazov = path + 'linMain.png'
            plt.savefig(nazov)
            url = urlFront + 'linMain.png'
            pair = {}
            pair.update({'url': url })
            pair.update({'popis': "Graf lineárnej regresie. Lineárna regresia je základným typom analýzy na princípe \"Supervised learning\". Na rozdieľ od polynomiálnej funkcie, lineárna popisuje lineárny vzťah medzi závislou a nezávislou hodnotou."})
            graphsDict.update({'pairLinMain': pair })
            plt.close()
        
        # POMOCNE HISTOGRAMY
        inc = 1
        for k,v in vystupy['histogramy'].items():
            plt.bar(v.keys(), v.values(), color='g')
            nazov = path + 'histPart' + str(inc) + '.png'
            plt.suptitle('Histogram', fontsize=20)
            plt.ylabel('Počet transakcií', fontsize=16)
            plt.gcf().autofmt_xdate()
            plt.savefig(nazov)
            url = urlFront + 'histPart' + str(inc) + '.png'
            pair = {}
            pair.update({'url' : url })
            if k == 'histTypOp':
                pair.update({'popis': "Histogram všetkých transakcií podľa typu operácie."})
                plt.xlabel('Typ Operácie', fontsize=18)
            elif k == 'histCas':
                pair.update({'popis': "Histogram všetkých vykonaných transakcií podľa ich dátumu vytvorenia rozdelené do intervalou podľa vstupu alebo defaultne denne."})
                plt.xlabel('Dátum', fontsize=18)
                plt.subplots_adjust(left=0.155, bottom=0.32, right=0.983)
            elif k == 'histKonspekt':
                pair.update({'popis': "Histogram všetkých transakcií podľa skupiny Konspektu"})
                plt.xlabel('Konspekt', fontsize=18)
            graphsDict.update({'pair' + 'histPart' + str(inc): pair})
            plt.close()
            inc += 1

    elif id == 3:
        # POMOCNE HISTOGRAMY
        inc = 1
        for k,v in vystupy['histogramy'].items():
            plt.bar(v.keys(), v.values(), color='g')
            nazov = path + 'histPart' + str(inc) + '.png'
            plt.suptitle('Histogram', fontsize=20)
            plt.ylabel('Počet transakcií', fontsize=16)
            plt.gcf().autofmt_xdate()
            plt.savefig(nazov)
            url = urlFront + 'histPart' + str(inc) + '.png'
            pair = {}
            pair.update({'url' : url })
            if k == 'histVek':
                pair.update({'popis': "Histogram všetkých transakcií používateľov podľa vekových skupín."})
                plt.xlabel('Veková skupina', fontsize=18)
            elif k == 'histKonspekt':
                pair.update({'popis': "Histogram všetkých transakcií používateľov podľa skupiny Konspektu."})
                plt.xlabel('Konspekt', fontsize=18)
                plt.subplots_adjust(left=0.155, bottom=0.32, right=0.983)
            graphsDict.update({'pair' + 'histPart' + str(inc): pair})
            plt.close()
            inc += 1 
    
    return graphsDict
