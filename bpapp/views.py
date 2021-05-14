# Create your views here.
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import User, Katalog, Pohlavie, PscObvodu, VekovaSkupina, Konspekt, TypOperacie, Analyza1Model, Analyza2Model, Analyza3Model
from django.contrib import messages
from django.urls import reverse
from django.contrib.sessions.models import Session 
import csv, io, os, base64, random
from django.core.paginator import Paginator
from datetime import datetime
import xml.etree.ElementTree as ET
from pymarc import MARCReader, parse_xml_to_array, Record
import xmltodict, numpy, pandas as pd, matplotlib.pyplot as plt
from scipy import stats


user = {}
id2Flag = None
importData = None
xmlCat = None

def index(request):
    if request.method == 'POST' and not user and request.POST["login"] == "admin":
        user["login"] = request.POST['login']
        context = {
            'login' : user["login"]
        }
        #Transakcia.objects.all().delete()
        Katalog.objects.all().delete()
        PscObvodu.objects.all().delete()
        Konspekt.objects.all().delete()
        TypOperacie.objects.all().delete()
        VekovaSkupina.objects.all().delete()
        Analyza1Model.objects.all().delete()
        Analyza2Model.objects.all().delete()
        Analyza3Model.objects.all().delete()

        messages.success(request, "User Logged in Successfully")
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
        return redirect('/')
    else:
        return render(request, 'index.html')

def analyza(request, id):
    if user:
        if id == 1:
            inicializaciaCiselnikov()
            context = {
                'login' : user["login"],
                'analyzaId' : id,
                'psc' : PscObvodu.objects.all(),
                'vek' : VekovaSkupina.objects.all(),
            }
            return render(request, 'analyza1.html', context=context)
        elif id == 2:
            inicializaciaCiselnikov()
            context = {
                'login' : user["login"],
                'analyzaId' : id,
                'konspekt' : Konspekt.objects.all(),
                'operacia' : TypOperacie.objects.all(),
            }
            return render(request, 'analyza2.html', context=context)
        elif id == 3:
            inicializaciaCiselnikov()
            context = {
                'login' : user["login"],
                'analyzaId' : id,
                'konspekt' : Konspekt.objects.all(),
                'vek' : VekovaSkupina.objects.all(),
            }
            return render(request, 'analyza3.html', context=context)
        else:
            context = {
                'login' : user["login"],
                'analyzaId' : id,
            }
            return render(request, 'main.html', context=context)   

def analyzaVystup(request, id, id2):
    global id2Flag
    global importData
    if user:
        if id == 1: 
            if id2 == 'import' and request.method == 'POST':
                id2Flag = id2
                fileCSV = request.FILES['fileCSV']
                fileXML = request.FILES['fileXML']
                if fileCSV.name.endswith('.csv') and fileXML.name.endswith('.xml'):
                    xmlFile(fileXML, id, request)
                    csvFile(fileCSV, id, request)
                else:
                    messages.error(request, 'THIS IS NOT A CSV or XML FILE')
                importData = Analyza1Model.objects.all()
                paginator = Paginator(importData, 5)
                page = request.GET.get('page', 1)
                data = paginator.page(page)
                context = {
                    'login' : user["login"],
                    'typ' : id2,
                    'flag' : id2Flag,
                    'data' : data,
                }  
            elif id2 == 'uprava' and request.method == 'POST':
                context = {
                    'login' : user["login"],
                    'typ' : id2,
                    'flag' : id2Flag,
                    'data' : importData,
                }  
            elif id2 == 'analyza' and request.method == 'POST':
                id2Flag = id2
            else:
                id2Flag = id2
            # Paginator musi byt aj tu
            context = {
                'login' : user["login"],
                'typ' : id2,
                'flag' : id2Flag,
                'data' : importData,
                'psc' : PscObvodu.objects.all()
                #'graph' : graphic
            }  
            return render(request, 'analyza1.html', context=context)
        elif id == 2 and request.method == 'POST':
            return render(request, 'analyza2.html', context=context)
        elif id == 3 and request.method == 'POST':
            return render(request, 'analyza3.html', context=context)
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
    
    ## Ciselnik Pohlavie
    p = Pohlavie()
    setattr(p, 'id', 0)
    setattr(p, 'pohlavie', "Muž")
    p.save()
    p = Pohlavie()
    setattr(p, 'id', 1)
    setattr(p, 'pohlavie', "Žena")
    p.save()

    ## Ciselnik Pohlavie
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
    setattr(v, 'skupina', "71+")
    v.save()

def hasDigitAndDot(inputString):
    return any(char.isdigit() for char in inputString) and "." not in inputString

def putIntoDB(rows, id):
    for key, value in rows.items():
        if id == 1:
            obj = Analyza1Model()
        elif id == 2:
            obj = Analyza2Model()
        elif id == 3:
            obj = Analyza3Model()
        for key, value in value.items():
            #print(key, value)
            setattr(obj, key, value)
        obj.save()

def displayMarcXml(file):
    records = parse_xml_to_array(file)
    for record in records:
        print(record.leader)
        for field in record.get_fields():
            if field.is_control_field():
                print("controlField", field.tag, field.data)
            else:
                print("datafield", field.tag, field.indicators)
                print("subfields:")
                for k,v in dict(field.subfields_as_dict()).items():
                    print(k, v)
        print("--------------------------------")

def validation(row, id, request):
    if id == 1:
        if row['vek'] <= 0 and not any(char.isdigit() for char in row['vek']):
            row['vek'] = random.randint(15, 80)
        if row['tcreate']: 
            row['tcreate'] = row['tccreate'][0:8]
        if not row['pohlavi']:
            r = random.randint(0,1)
            if r == 0:
                row['pohlavi'] = 'zena'
            else:
                row['pohlavi'] = 'muz'
        #if not row['psc'] or pscNotInAvailablePsc(row['psc']):
            #row['psc'] = get random psc from psc table
    return row

def pscNotInAvailablePsc(psc):
    # check if psc in psc table
    return

def data_processing():
    return

def xmlFile(file, id, request):
    records = parse_xml_to_array(file)
    xmlCat = records
    #for record in records:
    #    obj = Katalog()
    #    setattr(obj, 'record', record.as_json())
    #    obj.save()
    #xml = xmltodict.parse(file)
    #for k,v in xml.items():
        #print(k, v)

def csvFile(file, id, request):
    data = file.read().decode('UTF-8')
    io_string = io.StringIO(data)
    next(io_string) 
    rows = {}
    rowCounter = 0
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        if len(column) <= 26:
            if id == 1:
                rows[rowCounter] = inicializeAnalyze1Tab(column, request)
            elif id == 2:
                rows[rowCounter] = inicializeAnalyze2Tab(column)
            elif id == 3:
                rows[rowCounter] = inicializeAnalyze3Tab(column)
            rowCounter += 1
        else:
            messages.error(request, 'File has more than 26 columns !')
    putIntoDB(rows, id)

def defaultInicialization(column):
    row = {}
    #print(len(column))
    columnCounter = 0
    row.update({'ArlID': column[columnCounter]})
    columnCounter += 1
    createTime = datetime.strptime(column[columnCounter], '"%Y%m%d%H%M%S.%f"')
    row.update({'tcreate': createTime})
    columnCounter += 1
    row.update({'idRow': column[columnCounter]})
    columnCounter += 1
    row.update({'op': column[columnCounter]})
    columnCounter += 1
    row.update({'tag': column[columnCounter]})
    columnCounter += 1
    row.update({'DatOP': column[columnCounter]})
    columnCounter += 1
    row.update({'Pobocka': column[columnCounter]})
    columnCounter += 1
    row.update({'holding': column[columnCounter]})
    columnCounter += 1
    row.update({'catId': column[columnCounter]})
    columnCounter += 1
    row.update({'Tcat_020a': column[columnCounter]})
    columnCounter += 1
    row.update({'Tcat_020q': column[columnCounter]})
    columnCounter += 1
    if hasCommaOrDot(column[columnCounter]):
        Tcat_020c = column[columnCounter]
        columnCounter += 1
        Tcat_020c = Tcat_020c + "," + column[columnCounter]
        row.update({'Tcat_020c': Tcat_020c})
    else:
        row.update({'Tcat_020c': column[columnCounter]})
    columnCounter += 1
    row.update({'Tcat_T015a': column[columnCounter]})
    columnCounter += 1
    row.update({'Tcat_T035a': column[columnCounter]})
    columnCounter += 1
    row.update({'Tcat_T080a': column[columnCounter]})
    columnCounter += 1
    row.update({'isanonym': column[columnCounter]})
    columnCounter += 1
    row.update({'pohlavi': column[columnCounter]})
    columnCounter += 1
    row.update({'userHash': column[columnCounter]})
    columnCounter += 1
    row.update({'userTyp': column[columnCounter]})
    columnCounter += 1
    row.update({'psc': column[columnCounter]})
    columnCounter += 1
    row.update({'vek': column[columnCounter]})
    columnCounter += 1
    row.update({'casVypujceni': column[columnCounter]})
    columnCounter += 1
    row.update({'DelkaTransakce': column[columnCounter]})
    columnCounter += 1
    row.update({'pocetProlongaci': column[columnCounter]})
    columnCounter += 1
    row.update({'pocetUpominek': column[columnCounter]})
    return row

def inicializeAnalyze1Tab(column, request):
    row = {}
    columnCounter = 0
    columnCounter += 1
    row.update({'tcreate': column[columnCounter]})
    columnCounter += 10
    if hasDigitAndDot(column[columnCounter]):
        columnCounter += 1
    columnCounter += 4
    anonym = column[columnCounter]
    if anonym == 0:
        columnCounter += 1
        row.update({'pohlavi': column[columnCounter]})
    elif anonym == 1:
        columnCounter += 1
        row.update({'pohlavi': ""}) ## bez pohlavia
    columnCounter += 1
    row.update({'userHash': column[columnCounter]})
    columnCounter += 2
    if anonym == 0:
        row.update({'psc': column[columnCounter]})
        columnCounter += 1
        row.update({'vek': column[columnCounter]})
    elif anonym == 1:
        row.update({'psc': ""})
        columnCounter += 1
        row.update({'vek': ""})
    return validation(row, 1, request)

def inicializeAnalyze2Tab(column):
    return 

def inicializeAnalyze3Tab(column):
    return

def analysis():
    #products = pd.read_csv(file)
    #print(products['vek'])
    #X = df[['vek', 'casVypujceni']]
    #y = df['ArlID']
    #mymodel = numpy.poly1d(numpy.polyfit(products['vek'], products['casVypujceni'], 3))
    #products.plot(kind = 'scatter', x = 'vek', y = 'casVypujceni')
    #myline = numpy.linspace(0, 100, 4000)
    #plt.scatter(products['vek'], products['casVypujceni'])
    #plt.plot(myline, mymodel(myline))
    #plt.hist2d(products['vek'], products['casVypujceni'])
    #slope, intercept, r, p, std_err = stats.linregress(x, y)

    #x = [1,2,3,5,6,7,8,9,10,12,13,14,15,16,18,19,21,22]
    #y = [100,90,80,60,60,55,60,65,70,70,75,76,78,79,90,99,99,100]
    #mymodel = numpy.poly1d(numpy.polyfit(x, y, 10))
    #myline = numpy.linspace(1, 22, 100)
    #plt.scatter(x, y)
    #plt.plot(myline, mymodel(myline))

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')

    #plt.show()