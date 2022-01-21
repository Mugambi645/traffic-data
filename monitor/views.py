from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
import requests
import time
import psutil
import os
from datetime import datetime
from .models import Monitor
from urllib.parse import urlparse
from django.core.paginator import Paginator

#traffic monitor
def monitor(request):
    dataSaved = Monitor.objects.all().order_by('-datetime')
    # Getting loadover15 minutes 
    load1, load5, load15 = psutil.getloadavg()
    cpu_usage = int((load15/os.cpu_count()) * 100)
    ram_usage = int(psutil.virtual_memory()[2])
    p = Paginator(dataSaved, 100)
    #shows number of items in page
    totalSiteVisits = (p.count)
    #find unique page viewers & Duration
    pageNum = request.GET.get('page', 1)
    page1 = p.page(pageNum)
    #unique page viewers
    a = Monitor.objects.order_by().values('ip').distinct()
    pp = Paginator(a, 10)
    #shows number of items in page
    unique = (pp.count)
    #update time
    now = datetime.now()
    data = {
        "now":now,
        "unique":unique,
        "totalSiteVisits":totalSiteVisits,
        "cpu_usage": cpu_usage,
        "ram_usage": ram_usage,
        "dataSaved": page1,
    }
    return render(request, 'monitor.html', data)
#home page
def home(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    response = requests.get('http://api.ipstack.com/'+ip+'?access_key=cb8b193e3fc700dec1000a3309048930') #change from HTTP to HTTPS on the IPSTACK API if you have a premium account
    rawData = response.json()
    print(rawData) # print this out to look at the response
    continent = rawData['continent_name']
    country = rawData['country_name']
    capital = rawData['city']
    city = rawData['location']['capital']
    now = datetime.now()
    datetimenow = now.strftime("%Y-%m-%d %H:%M:%S")
    saveNow = Monitor(
        continent=continent,
        country=country,
        capital=capital,
        city=city,
        datetime=datetimenow,
        ip=ip
    )
    saveNow.save()
    return render(request, 'monitor.html')
