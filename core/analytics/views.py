from .models import *
from django.http import JsonResponse
from datetime import date, timedelta
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404, redirect
#from .serializers import *
from django.contrib.auth.decorators import login_required
import pandas as pd
import csv
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from core.project.models import *
from operator import and_, or_
from django.db.models import Q
from functools import reduce
from django.core import serializers
#from .serializers import ProductSerializer


@login_required(login_url="/login/")
def businessInsights(request):
    data = ""

    return render(request, "analytics/businessInsights.html", {'data': data, 'step': 0, })


@login_required(login_url="/login/")
def productMasterData(request):
    print("######### running product master data")

    product_list = Product.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(product_list, 10)

    try:
        product_list = paginator.page(page)
    except PageNotAnInteger:
        product_list = paginator.page(1)
    except EmptyPage:
        product_list = paginator.page(paginator.num_pages)

    # return render(request, 'analytics/businessInsights.html', {'product_list': product_list, 'step': 1, })
    return render(request, 'analytics/productMasterData.html', {'step': 1, })


@login_required(login_url="/login/")
def vrfc(request):
    print("######### running vrfc dump")

    data = ""
    return render(request, "analytics/businessInsights.html", {'data': data, 'step': 2})


@login_required(login_url="/login/")
def dragon(request):
    print("######### running dragon")

    data = ""
    return render(request, "analytics/businessInsights.html", {'data': data, 'step': 3})


@login_required(login_url="/login/")
def pmdFullList(request):

    print("$$$$$$$$$$$$$ request page length", request.GET.get(
        'length'), "draw nr", request.GET.get('draw'), "start value", request.GET.get('start'))
    pageLength = request.GET.get(
        'length')

    page = int(int(request.GET.get('start')) / int(pageLength)) + 1
    print("§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§ requested page", page)

    # start and length are key to determine the
    print("$$$$$$$$$$$$$ request ", request.GET)
    """
        this is the output structure, it reflects 1 to 1 the order in the front end. 
          { "data": "id"},
          { "data": "hfg"},
          { "data": "ppos"},
          { "data": "rfp"},
          { "data": "package"},
          { "data": "basicType"},
          { "data": "availablePGS"},
    """
    # this variable is the column that is currently being ordered by. counting starts at 0.
    orderColumn = int(request.GET.get('order[0][column]'))
    # sort direction
    order = request.GET.get('order[0][dir]')

    print("$$$$$$$$$$$ requested orderColumn, order", orderColumn, order)

    """
    This block is used to filter dynamically. The user enters a search criteria and the backend filters 
    by that search criteria and returns paginated results.
    """

    print("######### running pmdFullList ")
    search_values = []
    fields = ['hfg', 'ppos', 'rfp',
              'basicType', 'availablePGS']

    package_search_value = request.GET.get(
        'columns['+str(4)+'][search][value]')

    for i in [1, 2, 3, 5, 6]:
        value = request.GET.get('columns['+str(i)+'][search][value]')
        search_values.append(value)

    print("##### ---> search values", search_values, len(search_values))
    # if no search values, return all products
    allRelevantProducts = []
    listEmpty = True

    """
    search by package is implemented differently, since it's not part of the main table of this view. 
    """
    for element in search_values:
        if element:
            listEmpty = False

    if package_search_value:
        listEmpty = False

    """
    now for full free text search
    """

    freeTextSearchString = request.GET.get(
        'search[value]')

    if freeTextSearchString:
        print("$$$$$$$$$$$$$$$ freeTextSearchString entered", freeTextSearchString)
        listEmpty = False
        package_search_value = freeTextSearchString
        search_values.clear()
        for i in [1, 2, 3, 5, 6]:
            search_values.append(freeTextSearchString)

    recordCount = 0
    shownRecords = page * pageLength

    print("package search value", package_search_value)
    """
    first, we return all the values if the user has not searched for a particular value.
    """
    if listEmpty == True:
        allRelevantProducts = Product.objects.all()
        recordCount = allRelevantProducts.count()
        """
        # now apply order, if required
        if orderColumn == 0:
            allRelevantProducts.order_by('id')
        elif orderColumn == 1:
            allRelevantProducts.order_by('hfg')
        elif orderColumn == 2:
            allRelevantProducts.order_by('ppos')
        elif orderColumn == 3:
            allRelevantProducts.order_by('rfp')
        elif orderColumn == 4:
            allRelevantProducts.order_by('package')
        elif orderColumn == 5:
            allRelevantProducts.order_by('basicType')
        elif orderColumn == 6:
            allRelevantProducts.order_by('availablePGS')

        paginator = Paginator(allRelevantProducts,
                              request.GET.get('length', 50))

        try:
            allRelevantProducts = paginator.page(page)
        except PageNotAnInteger:
            allRelevantProducts = paginator.page(1)
        except EmptyPage:
            allRelevantProducts = paginator.page(paginator.num_pages)
        """
        allRelevantProductsList = list(allRelevantProducts)

        """
        else we will filter by the requested items.
        If no package is part of the search, the first query is exceuted.
        If a package was searched for, the second query will be executed.
        
        """
    elif freeTextSearchString:
        complex_query = (reduce(or_, (Q(**{fields[i]+'__icontains': value}) for i, value in enumerate(
            search_values)))) | Q(package__package__icontains=package_search_value)

        allRelevantProducts = Product.objects.filter(complex_query)
        recordCount = allRelevantProducts.count()
        print("§§§§§§§§ freeTextSearchString resulting count",
              recordCount, "search values", search_values, "package_search_value", package_search_value)

    else:
        if not package_search_value:
            allRelevantProducts = Product.objects.filter(reduce(and_, (Q(**{fields[i]+'__icontains': value}) for i, value in enumerate(
                search_values))))  # .values('pk', 'hfg', 'ppos', 'rfp', 'basicType', 'availablePGS')
            recordCount = allRelevantProducts.count()

        else:
            # chain the package fk and the other parameters

            complex_query = (reduce(and_, (Q(**{fields[i]+'__icontains': value}) for i, value in enumerate(
                search_values)))) & Q(package__package__icontains=package_search_value)

            allRelevantProducts = Product.objects.filter(complex_query)
            recordCount = allRelevantProducts.count()

    """
    Now order by using the parsed values.
    In other tables, just replace the field name while keeping the order as shown in the front end. 
    """

    column = ""

    if orderColumn == 0:
        column = 'id'
    elif orderColumn == 1:
        column = 'hfg'
    elif orderColumn == 2:
        column = 'ppos'
    elif orderColumn == 3:
        column = 'rfp'
    elif orderColumn == 4:
        column = 'package'
    elif orderColumn == 5:
        column = 'basicType'
    elif orderColumn == 6:
        column = 'availablePGS'

    # apply order direction
    if order == "desc":
        column = "-" + column

    allRelevantProducts = allRelevantProducts.order_by(column)

    """
    Now, sorting can be applied on allRelevantProducts array of objects, based on the user request.
    """

    paginator = Paginator(allRelevantProducts,
                          request.GET.get('length', 50))

    try:
        allRelevantProducts = paginator.page(page)
    except PageNotAnInteger:
        allRelevantProducts = paginator.page(1)
    except EmptyPage:
        allRelevantProducts = paginator.page(paginator.num_pages)

    #print("allRelevantProducts", allRelevantProducts)
    allRelevantProductsList = list(allRelevantProducts)
    #print("allRelevantProductsList", allRelevantProductsList)

    # to do: how to serialize this properly and fast?
    outputArray = []
    for product in allRelevantProductsList:
        prodDict = dict()
        prodDict['id'] = product.pk
        prodDict['hfg'] = product.hfg
        prodDict['ppos'] = product.ppos
        prodDict['rfp'] = product.rfp
        prodDict['package'] = product.package.__str__()
        prodDict['basicType'] = product.basicType
        prodDict['availablePGS'] = product.availablePGS
        outputArray.append(prodDict)

    outputDict = dict()
    outputDict['dataForTable'] = outputArray
    outputDict['iTotalRecords'] = recordCount
    outputDict['iTotalDisplayRecords'] = recordCount

    # print("######### outputDict ", outputDict)
    return JsonResponse(outputDict, safe=False)


@login_required(login_url="/login/")
def pmdFullListSalesNames(request):
    outputDict = dict()
    outputDict['dataForTable'] = []

    print("######### outputDict ", outputDict)
    return JsonResponse(outputDict, safe=False)
