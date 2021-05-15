# Create your views here.
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import User, Katalog, PscObvodu, VekovaSkupina, Konspekt, TypOperacie, Analyza1Model, Analyza2Model, Analyza3Model
from django.contrib import messages
from django.urls import reverse
from django.contrib.sessions.models import Session 
import csv, io, os, base64, random
from django.core.paginator import Paginator
import datetime as dt
import xml.etree.ElementTree as ET
from pymarc import MARCReader, parse_xml_to_array, Record
import xmltodict, numpy as np, pandas as pd, matplotlib.pyplot as plt
import matplotlib.pylab as plb
import matplotlib.dates as mdates
from matplotlib.dates import date2num
from pylab import rcParams
from scipy import stats
from django.db.models import Q, Count
from operator import or_
from functools import reduce
from dateutil.rrule import rrule, MONTHLY, YEARLY, WEEKLY, DAILY


user = {}
importData = None
vystupyData = None
xmlCat = None
csvFile = None

def index(request):
    if request.method == 'POST' and not user and request.POST["login"] == "admin":
        user["login"] = request.POST['login']
        context = {
            'login' : user["login"]
        }
        #Clear models
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
    global importData
    global vystupyData
    if user:
        if id == 1: 
            if id2 == 'import' and request.method == 'POST':
                fileCSV = request.FILES['fileCSV']
                #fileXML = request.FILES['fileXML']
                if fileCSV.name.endswith('.csv'):# and fileXML.name.endswith('.xml'):
                   # xmlFile(fileXML, id, request)
                    csvFile(fileCSV, id, request)
                else:
                    messages.error(request, 'THIS IS NOT A CSV or XML FILE')
                importData = Analyza1Model.objects.all()
            elif id2 == 'uprava' and request.method == 'POST':
                vstupy = spracujVstupy(request, id)
                vystupyData = data_processing(vstupy, id)
                analysis(vystupyData)
            elif id2 == 'analyza':
                analysis(vystupyData)
            paginator = Paginator(importData, 5)
            page = request.GET.get('page', 1)
            data = paginator.page(page)
            context = {
                'login' : user["login"],
                'typ' : id2,
                'analyzaId' : id,
                'data' : data,
                'psc' : PscObvodu.objects.all(),
                'vek' : VekovaSkupina.objects.all(),
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

def inicializeAnalyze1Tab(column, request):
    row = {}
    ## tcraete
    columnCounter = 1
    tcreate = column[columnCounter]
    if len(tcreate) == 18 and tcreate[15] == '.' and tcreate[1:9].isdigit():
        tcreate = tcreate[1:5] + '-' + tcreate[5:7] + '-' + tcreate[7:9]
        row.update({'casVytvoreniaTransakcie': tcreate})
    else:
        messages.error(request, 'Wrong form of tcreate field')
    
    columnCounter += 10
    if hasDigitAndDot(column[columnCounter]): ## check for price, sometimes it has comma inside instead of dot
        columnCounter += 1
    columnCounter += 4

    ## pohlavie
    anonym = column[columnCounter]
    columnCounter += 1
    if len(anonym) == 3 and anonym[1].isdigit() and int(anonym[1]) in (0, 1):
        anonym = int(anonym[1])
        pohlavie = column[columnCounter]
        if anonym == 0:
            if pohlavie.isalpha() and len(pohlavie) > 2 and len(pohlavie) < 7 and pohlavie in ["zena", "muz"]:
                row.update({'pohlavie': pohlavie})
            else:
                r = random.randint(0,1)
                if r == 0:
                    pohlavie = "zena"
                else:
                    pohlavie = "muz"
                row.update({'pohlavie': pohlavie})
        elif anonym == 1:
            r = random.randint(0,1)
            if r == 0:
                pohlavie = "zena"
            else:
                pohlavie = "muz"
            row.update({'pohlavie': pohlavie})
    else:
        r = random.randint(0,1)
        if r == 0:
            pohlavie = "zena"
        else:
            pohlavie = "muz"
        row.update({'pohlavie': pohlavie})
        #messages.error(request, 'Wrong form of pohlavie field')

    ## userHash
    columnCounter += 1
    userHash = column[columnCounter]
    if userHash:
        row.update({'pouzivatelId': userHash})
    else:
        messages.error(request, 'Missing UserHash field')

    ## psc
    columnCounter += 2
    pscOld = column[columnCounter]
    if len(pscOld) == 8 and pscOld[4] == " ":
        psc = pscOld[1:7]
        psc = psc.replace(' ', '')
        obv = None
        if psc.isdigit():
            try:
                obv = PscObvodu.objects.get(psc=psc)
            except:
                obv = PscObvodu.objects.get(psc=99999)
                #messages.error(request, 'Wrong form of psc field [Not digit]')
            row.update({'psc_id': obv})
        else:
            #messages.error(request, 'Wrong form of psc field [Not digit]')
            row.update({'psc_id': PscObvodu.objects.get(psc=99999)})
    else:
        #messages.error(request, 'Wrong form of psc field')
        row.update({'psc_id': PscObvodu.objects.get(psc=99999)})
    
    ## vek
    columnCounter += 1
    if anonym == 0: 
        vek = column[columnCounter].replace('"', '')
        if vek.isdigit() and int(vek) > 5:   
            row.update({'vek': int(vek)})
        else:
            row.update({'vek': random.randint(15, 80)})
            #messages.error(request, 'Wrong form of vek field')
    elif anonym == 1:
        row.update({'vek': random.randint(15, 80)})
    
    return row

def inicializeAnalyze2Tab(column):
    return 

def inicializeAnalyze3Tab(column):
    return

def hasDigitAndDot(inputString):
    return any(char.isdigit() for char in inputString) and "." not in inputString

def putIntoDB(rows, id):
    for key, value in rows.items():
        if id == 1: ## Store model for analyza1
            obj = Analyza1Model()
            for key, value in value.items():
                setattr(obj, key, value)
            obj.save()
        elif id == 2: ## Store model for analyza1
            obj = Analyza2Model()
        elif id == 3: ## Store model for analyza1
            obj = Analyza3Model()
        
def spracujVstupy(request, id):
    vstupy = {}
    postItems = dict(request.POST.items())
   
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
    
    return vstupy

def data_processing(vstupy, id):
    vystupy = {}

    ## casovy interval
    interval = None
    if 'interval' in vstupy:
        interval = vstupy['interval']
    else:
        interval = DAILY

    print('Interval',interval)

    ## min and max time 
    maxDate = Analyza1Model.objects.all().values('casVytvoreniaTransakcie').order_by('-casVytvoreniaTransakcie')[0]
    minDate = Analyza1Model.objects.all().values('casVytvoreniaTransakcie').order_by('casVytvoreniaTransakcie')[0]  
    dates = [dt.date() for dt in rrule(interval, dtstart=minDate['casVytvoreniaTransakcie'], until=maxDate['casVytvoreniaTransakcie'])]

    ## Histogramy
    histogramy = {}

    ## hist pohlavie
    histPohlavieQ = Analyza1Model.objects.values('pohlavie').annotate(dcount=Count('*')).order_by()
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
    histPscQ = Analyza1Model.objects.values('psc_id').annotate(dcount=Count('*')).order_by()
    histPsc = {}
    for h in histPscQ:
        obv = PscObvodu.objects.get(psc=h['psc_id'])
        histPsc.update({obv.obvod : h['dcount']})
    histogramy['histPsc'] = histPsc

    ## hist cas
    histCas = {}
    for date in range(len(dates)):
        if date + 1 >= len(dates):
            casGroup = Analyza1Model.objects.all().filter(casVytvoreniaTransakcie__gte=dates[date])
        else:
            casGroup = Analyza1Model.objects.all().filter(casVytvoreniaTransakcie__range=[dates[date], dates[date+1]])
        histCas.update({dates[date]:len(casGroup)})
    histogramy['histCas']=histCas


    ## Grafy
    grafy = {}
            
    ## aggregate query filter
    query = Q()
    if 'pscObvodu' in vstupy and 'all' not in vstupy['vekovaSkupina']:
        for k, v in dict(vstupy['pscObvodu']).items():
            sk = PscObvodu.objects.get(psc=v) 
            query = query | Q(psc_id=sk.psc)     
    if 'vekovaSkupina' in vstupy and 'all' not in vstupy['vekovaSkupina']:
        for k, v in dict(vstupy['vekovaSkupina']).items():
            sk = VekovaSkupina.objects.get(id=v)
            sk = sk.skupina.split('-')
            query = query | Q(vek__gte=sk[0],vek__lte=sk[1])
    if 'pohlavie' in vstupy and len(vstupy['pohlavie']) == 1 and 'all' not in vstupy['pohlavie']:
        query = query | Q(pohlavie=vstupy['pohlavie']['pohlavie'])
        

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
    for dateInterval in range(len(dateIntervals)):
        if dateInterval + 1 >= len(dateIntervals):
            query = query | Q(casVytvoreniaTransakcie__gte=dateIntervals[dateInterval])
        else:
            query = query | Q(casVytvoreniaTransakcie__range=[dateIntervals[dateInterval], dateIntervals[dateInterval+1]])
        # GET 
        group = Analyza1Model.objects.all().filter(query).distinct('pouzivatelId')
        graf.update({dateIntervals[dateInterval]:len(group)})
    
    grafy['graf']=graf
    
    ## All together
    vystupy.update({'histogramy':histogramy})
    vystupy.update({'grafy':grafy})
    return vystupy

def to_integer(dt_time):
    return dt_time.year + dt_time.month + dt_time.day

def analysis(vystupy):
    #print(vystupy)

    # Polynomial regression
    for k,graf in vystupy['grafy'].items():
        z = list(graf.keys())
        y = list(graf.values())
        x = []
        for a in z:
            x.append(to_integer(a))

        mymodel = np.poly1d(np.polyfit(y, x, 3))
        myline = np.linspace(1, 22, 100)
        plt.scatter(y, x)
        plt.plot(myline, mymodel(myline))
        plt.show()
        
        
        plt.scatter(x, y)
        plt.show()
        
        slope, intercept, r, p, std_err = stats.linregress(x, y)
        def myfunc(x):
            return slope * x + intercept
        mymodel = list(map(myfunc, x))
        plt.scatter(x, y)
        plt.plot(y, mymodel)
        plt.show()

        DF = pd.DataFrame({
            'day':     x,
            'balance': y
        })
        rcParams['figure.figsize'] = 20, 10
        fig, ax = plt.subplots()
        DF['day'] = DF['day'].apply(date2num)      #-->Update

        ax.bar(DF['day'], DF['balance'], color='lightblue')
        plt.xlabel('day', fontsize=20)
        myFmt = mdates.DateFormatter('%Y-%m')
        ax.xaxis.set_major_formatter(myFmt)
        plt.show()

    
    # make up some dat
    #z = []
    #for c in cas:
    #    z.append(dt.datetime.strptime(c, '%Y-%m-%d'))
    #x = [dt.datetime.now() + dt.timedelta(hours=i) for i in range(12)]
    #y = [i+random.gauss(0,1) for i,_ in enumerate(cas)]

    #print(z)
    # plot
    #plt.plot(cas,y)
    # beautify the x-labels
    #plt.gcf().autofmt_xdate()
    #plt.show()

    print(vystupy['histogramy'])
    for k,v in vystupy['histogramy'].items():
        plt.bar(v.keys(), v.values(), color='g')
        plt.show()

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

    #buffer = io.BytesIO()
    #plt.savefig(buffer, format='png')
    #buffer.seek(0)
    #image_png = buffer.getvalue()
    #buffer.close()

    #graphic = base64.b64encode(image_png)
    #graphic = graphic.decode('utf-8')

    #plt.show()

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

def defaultInicialization(column):
    row = {}
    #print(len(column))
    columnCounter = 0
    row.update({'ArlID': column[columnCounter]})
    columnCounter += 1
    createTime = dt.strptime(column[columnCounter], '"%Y%m%d%H%M%S.%f"')
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
    if hasDigitAndDot(column[columnCounter]):
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