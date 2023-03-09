# Francisco Falise, copyright 01/10/2022


from ftplib import parse257
from pickle import TRUE
from sqlite3 import register_converter
from django.db.models import query
from django.forms.fields import EmailField
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django import template
from .forms import *
from .models import *

# from  import SingleTableView

# from .tables import TherapyTable, CommunicationTable
from django.contrib import messages

# from .filters import *
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
import json
import datetime
from django.forms import modelformset_factory

# from .test import *

from django.forms.models import model_to_dict

# from bootstrap_datepicker_plus.widgets import DatePickerInput, TimePickerInput, DateTimePickerInput, MonthPickerInput, YearPickerInput
from django.forms import formset_factory

# email
from django.core.mail import send_mail

# from settings import BASE_DIR, EMAIL_HOST_USER
# email
from django.core import serializers
from django.utils import timezone
from django.template import RequestContext
from django.db import connection
from datetime import date, timedelta
from .interpolator import *

# import matplotlib as plt
# import matplotlib.pyplot as plt
import io
import base64
from .importJobs.salesNames import *
from .importJobs.vhkl import *
from .importJobs.Dragon import *
from .importJobs.generalDb import *
from .queryJobs.boupDataOverview import *
from .queryJobs.warnings import *
from .queryJobs.SQL_query import *
from .editViews import *

####
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response

import time
from .excelFormInputValidator import checkExcelFormInput, TypeOfParameter

# from .diagnosis import decode, decodePrivateInsurers
# from .scan import *
# from .ocr import ocrscan
# from .suitability import physioSuitability
from productMarketingDwh.models import *
from enum import Enum
from .importJobs.vrfcImport import *
from .importJobs.productImport import *
from .BoUpExport import protectCellsInExcel


class operatingSystem(Enum):
    macOs = 1
    windows = 2
    linux = 3


# just for testing , can be deleted


@login_required(login_url="/login/")
def boupExportFile(request):
    protectCellsInExcel(None)
    message = "test123"
    return JsonResponse(message, safe=False)


# template for sending mails, if required.


@login_required(login_url="/login/")
def testmail(request):
    subject = "TrainingData"

    # obj = ExcerciseSet.objects.get(pk=2)
    message = serializers.serialize(
        "json",
        [
            obj,
        ],
    )
    print("message", message)
    # message = 'Hope you are enjoying your Django Tutorials'
    recepient = "fran.falise@gmail.com"
    print("email host", EMAIL_HOST_USER)
    send_mail(subject, message, EMAIL_HOST_USER, [recepient], fail_silently=False)
    return JsonResponse(message, safe=False)


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def rawSqlPerformer(sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)
        row = dictfetchall(cursor)
    return row


def testRawQuery():
    # sql = "SELECT DISTINCT salesName, mainCustomer, endCustomer FROM productMarketingDwh_boup LEFT OUTER JOIN project_salesname ON (productMarketingDwh_boup.salesname = project_salesname.name)"
    # this is the nomenclautre
    # sql = 'SELECT DISTINCT "reviewDate", "mainCustomer", "endCustomer"  FROM public."productMarketingDwh_boup"'
    # distinctBoUpMcEcRfpCombinations = rawSqlPerformer(sql)

    sql = 'SELECT COUNT (*) FROM public."project_product"'
    distinctBoUpMcEcRfpCombinations = rawSqlPerformer(sql)

    print("################ distinctBoUpMcEcRfpCombinations")
    print(distinctBoUpMcEcRfpCombinations)


# for manual import job testing


@login_required(login_url="/login/")
def fullImports(request):
    # testRawQuery()

    runConfigImport(request)
    # print("all main customers", MainCustomers.objects.all())
    # print("all final customers", FinalCustomers.objects.all())

    # for customer in FinalCustomers.objects.all():
    #    print("final customer", customer, "fk", customer.mainCust)

    """

    print("all projects", Project.objects.all())
    allproj = Project.objects.all()
    print("objects", allproj)
    """
    #
    # objects = Project.objects.all()
    # print("objects -->", objects)
    # print("!!!! running full imports")
    # adolfRun()
    # importVrfcOohCsv()
    return HttpResponse(status=200)


# for manual testing with postman
class salesNamesImportJob(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication]

    def get_object(self, request):
        try:
            print("putoelquelee1")

            return JsonResponse("getobject", safe=False)
        except:
            print("putoelquelee2")
            raise Http404

    def get(self, request, format=None):
        # return JsonResponse('get', safe=False)
        data = "asd"
        # return Response(data, status=status.HTTP_200_OK)
        return JsonResponse(
            " wurde addiert oder geaendert", safe=False, status=status.HTTP_201_CREATED
        )

    def post(self, request, format=None):
        print("post!")
        runSalesNameImport()

        return JsonResponse(
            "ran import job!", safe=False, status=status.HTTP_201_CREATED
        )


class vhklImportJob(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication]

    def get_object(self, request):
        try:
            print("putoelquelee1")

            return JsonResponse("getobject", safe=False)
        except:
            print("putoelquelee2")
            raise Http404

    def get(self, request, format=None):
        # return JsonResponse('get', safe=False)
        data = "asd"
        print("get!")
        runvhklImport(request)
        # return Response(data, status=status.HTTP_200_OK)
        return JsonResponse(
            " wurde addiert oder geaendert", safe=False, status=status.HTTP_201_CREATED
        )

    def post(self, request, format=None):
        print("post!")
        runvhklImport(request)

        return JsonResponse(
            "ran import job for vhkl!", safe=False, status=status.HTTP_201_CREATED
        )


class DragonImportJob(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication]

    def get_object(self, request):
        try:
            print("putoelquelee1")

            return JsonResponse("getobject", safe=False)
        except:
            print("putoelquelee2")
            raise Http404

    def get(self, request, format=None):
        # return JsonResponse('get', safe=False)
        data = "asd"
        # return Response(data, status=status.HTTP_200_OK)
        return JsonResponse(
            " wurde addiert oder geaendert", safe=False, status=status.HTTP_201_CREATED
        )

    def post(self, request, format=None):
        print("post!")
        runDragonImport()

        return JsonResponse(
            "ran import job for Dragon!", safe=False, status=status.HTTP_201_CREATED
        )


"""
URL: 
http://localhost:8000/ifx/productMarketing/boupEntry

This is handling the project creation step. 

"""
# main screen for entering new projects via forms.


@login_required(login_url="/login/")
def boupEntry(request):
    # adolfRun()
    # importVrfcOohCsv()

    # runConfigImport()
    print("boup entry first")
    # filter conditions. To Do: try catch conditions to handle misuse of URL in browser...
    enterProjectForm = EnterProjectForm()
    # applicationMainForm = ApplicationMainForm()
    mainCustomers = MainCustomers.objects.all()
    finalCustomers = FinalCustomers.objects.all()
    # distiTierOneEMSList = DistiTierOneEMS.objects.all()
    oems = OEM.objects.all()
    applicationMains = ApplicationMain.objects.all()
    applicationDetails = ApplicationDetail.objects.all()

    # print("final customers type", type(finalCustomers), finalCustomers[0], "type2", type(finalCustomers[0]))

    # distinct only supported in PostgreSQL
    productFamiliesArray = []  # ["dummy 12346778"]

    productFamilies = dict()  # ["dummy 12346778"]
    allProducts = Product.objects.all()

    for product in allProducts:
        # print("family description", product.familydescription)
        if product.familyfull not in productFamilies:

            #        if productFamilies.contains(product.familydescription):
            productFamiliesArray.append(product.familyfull)
            productFamilies[product.familyfull] = product.familydescription

    # Product.objects.all().distinct('familydescription')  # ["asd1", "asd2", "asd3"]#ProductFamily.objects.all()

    print("product families type", type(productFamilies), "content", productFamilies)
    salesNames = SalesName.objects.all()
    enterMainCustomerError = False
    enterFinalCustomerError = False
    salesNameError = False
    appMainError = False
    appDetailError = False
    oemNameError = False

    if request.method == "POST":
        projectForm = EnterProjectForm(request.POST)
        # applicationMain = ApplicationMainForm(request.POST)

        salesName = None
        mainCustomer = None
        finalCustomer = None
        appMainObj = None
        appDetailObj = None
        selectedSalesName = None
        selectedFinalCustomer = None
        selectedMainCustomer = None
        selectedTierOne = None
        selectedDistributor = None
        selectedEms = None
        vpaCustomer = False
        selectedOem = None

        selectedTierOneInput = request.POST.get("tierOne")
        selectedDistributorInput = request.POST.get("distributor")
        selectedEmsInput = request.POST.get("ems")
        vpaCustomerInput = request.POST.get("vpaCustomer")
        selectedOemInput = request.POST.get("oem")

        if not selectedTierOneInput:
            print("missing selectedTierOneInput", selectedTierOneInput)
        else:
            selectedTierOne = selectedTierOneInput
            print("selected tier one", selectedTierOne)

        if not selectedDistributorInput:
            print("missing selectedDistributorInput", selectedDistributorInput)
        else:
            selectedDistributor = selectedDistributorInput

        if not selectedEmsInput:
            print("missing selectedEmsInput")
        else:
            selectedEms = selectedEmsInput

        if not selectedOemInput:
            print("missing selectedOemInput")
        else:
            print("selected oem", selectedOemInput, type(selectedOemInput))
            selectedOem = selectedOemInput

        if not vpaCustomerInput:
            print("missing vpaCustomerInput")
        else:
            print("--> vpaCustomerInput", vpaCustomerInput)
            vpaCustomer = bool(vpaCustomerInput)

        # get sales name
        salesNameInt = request.POST.get("salesName")
        mainCustomerStr = request.POST.get("mainCustomer")
        finalCustomerStr = request.POST.get("finalCustomer")
        salesNameFreeTextInput = request.POST.get("salesNameFreeText")
        appMainPk = request.POST.get("applicationMain")
        appDetailPk = request.POST.get("applicationDetail")
        print(
            "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%5app main",
            appMainPk,
            "appDetailPk",
            appDetailPk,
        )

        if not mainCustomerStr:
            print("missing mainCustomerStr")
            enterMainCustomerError = True
        else:
            print("--> mainCustomerStr", mainCustomerStr)

        if not enterFinalCustomerError:
            print("missing enterFinalCustomerError")
            enterFinalCustomerError = True
        else:
            print("--> enterFinalCustomerError", enterFinalCustomerError)

        print("%%%%---> entered sales name primary key", salesNameInt)
        print(
            "%%%%---> entered main and final customers str + primary key",
            mainCustomerStr,
            "++",
            mainCustomer,
            "------final",
            finalCustomerStr,
            "++",
            finalCustomer,
        )

        print("enter sales name check", salesNameFreeTextInput)
        if not request.POST.get("salesNameFreeText"):
            print("test print A")  # gets printed when empty (NULL or "")
        else:
            print("test print B")  # gets printed when text
            salesName = SalesName.objects.get(salesName=salesNameFreeTextInput)

        # SAA-TC497XE-24HO400CC AA
        # try to get sales name from drop down. if not, try to use the free text input.
        if salesNameFreeTextInput == "":
            if salesNameInt != None:
                print("free text was empty!", type(salesNameInt))
                try:
                    salesName = SalesName.objects.get(pk=salesNameInt)
                    salesNames = [salesName]
                    selectedSalesName = salesName

                except ValueError:
                    salesNameError = True
            else:
                salesNameError = True
                print("#### fatal error sales name input")

        else:
            try:

                salesName = SalesName.objects.get(salesName=salesNameFreeTextInput)
                print("sales name object from free text", salesName)
                salesNames = [salesName]
                selectedSalesName = salesName

            except:
                salesNameError = True

        # tbd if to use here get or create: infineon must decide what should be possible (eg if to allow to create new customers here or use fixed values)
        # get -> trae una instancia de la tabla. filter: trae un queryset... que es como un array de instancias de la tabla.
        try:
            print("--->looking for main customer with name", mainCustomerStr)
            # mainCustomer = MainCustomers.objects.get(customerName = mainCustomerStr.strip())
            mainCustomer = MainCustomers.objects.filter(
                customerName=mainCustomerStr.strip()
            ).first()

            # mainCustomers = []
            # mainCustomers = [mainCustomer]
            print("---> got main customer obj", mainCustomer)
            selectedMainCustomer = mainCustomer  # .first()

        except:
            enterMainCustomerError = True
            print("no main customer detected")

        try:
            print("--->looking for finalCustomer with name", finalCustomerStr)

            finalCustomer = FinalCustomers.objects.filter(
                finalCustomerName=finalCustomerStr.strip()
            ).first()
            # finalCustomers = []
            # finalCustomers = [finalCustomer]
            selectedFinalCustomer = finalCustomer  # .first()
            print("final customer", finalCustomer, "pk", finalCustomer.pk)
            enterFinalCustomerError = False

        except:
            enterFinalCustomerError = True
            print("no final customer detected")

        print("appMainPk", appMainPk, "appDetailPk", appDetailPk)

        try:
            appMainObj = ApplicationMain.objects.get(appMainDescription=appMainPk)
        except:
            appMainError = True

        ## oem is optional
        print("selected oem input", selectedOemInput)
        if not selectedOemInput:
            oemNameError = False
        else:
            try:
                oemObj = OEM.objects.get(oemName=selectedOemInput)
            except:
                oemNameError = True

        try:
            appDetaiObj = ApplicationDetail.objects.get(pk=appDetailPk)
            print("appDetaiObj", appDetaiObj)
        except:
            print("app detail erre steeing true")
            appDetailError = True

        print("app detail errors", appMainError, appDetailError)
        print("form errors", projectForm.errors)
        # print("form errors", applicationMain.errors)

        print(
            salesNameError,
            enterFinalCustomerError,
            enterFinalCustomerError,
            appMainError,
            appDetailError,
            oemNameError,
        )

        if (
            projectForm.is_valid()
            & (salesNameError == False)
            & (enterMainCustomerError == False)
            & (enterFinalCustomerError == False)
            & (appMainError == False)
            & (appDetailError == False)
            & (oemNameError == False)
        ):

            project_form_result = projectForm.save(commit=False)
            valid = True

            # print(project_form_result)

            # applicationLine = project_form_result.applicationLine
            oem = project_form_result.oem
            # plausibility checks
            # combination of main and final customer exists in cube db
            ### SOP in future

            # same bl, application line, valid, same rfp already exist!
            print(
                "resulting salesname",
                salesName,
                "selected salesname",
                selectedSalesName,
            )
            # similar project existing
            if (
                Project.objects.filter(
                    salesName=salesName,
                    mainCustomer=mainCustomer,
                    endCustomer=finalCustomer,
                    valid=valid,
                    draft=False,
                ).count()
                > 0
            ):
                print("project already exists")
                notification = "Project already exists. Please check the entered data."
                status = 0
                return render(
                    request,
                    "productMarketing/entryBase.html",
                    {
                        "segment": "boupEntry",
                        "step": 0,
                        "enterProjectForm": EnterProjectForm(request.POST),
                        "salesNameError": salesNameError,
                        "enterMainCustomerError": enterMainCustomerError,
                        "enterFinalCustomerError": enterFinalCustomerError,
                        "notification": notification,
                        "mainCustomers": mainCustomers,
                        "finalCustomers": finalCustomers,
                        "oems": oems,
                        "productFamilies": productFamilies,
                        "productSeries": productSeries,
                        "salesNames": salesNames,
                        "selectedSalesName": selectedSalesName,
                        "selectedFinalCustomer": selectedFinalCustomer,
                        "selectedMainCustomer": selectedMainCustomer,
                        "selectedOem": selectedOem,
                        "selectedDistributor": selectedDistributor,
                        "selectedEms": selectedEms,
                        "selectedTierOne": selectedTierOne,
                        "vpaCustomer": vpaCustomer,
                    },
                )

            else:
                project_form_result.salesName = salesName
                project_form_result.mainCustomer = mainCustomer
                project_form_result.endCustomer = finalCustomer

                project_form_result.applicationMain = appMainObj
                project_form_result.applicationDetail = appDetaiObj
                print("selected tier one", selectedTierOne)

                try:
                    project_form_result.oem = oemObj
                except:
                    print("did not set oem")
                try:
                    project_form_result.distributor = selectedDistributor
                except:
                    print("did not set disti")
                try:
                    project_form_result.tier1 = selectedTierOne
                except:
                    print("did not set tier1")

                try:
                    project_form_result.ems = selectedEms
                except:
                    print("did not set ems")

                try:
                    project_form_result.vpaCustomer = vpaCustomer
                except:
                    print("did not set vpa customer")

                print("saving form!", project_form_result)
                project_form_result.user = request.user
                project_form_result.save()
                print("project", project_form_result)
                projectId = project_form_result.id
                notification = "Project data stored."
                print(notification)
                status = 1

                url = "/ifx/productMarketing/boupEntry1/" + str(
                    projectId
                )  # + '/' + str(status)
                return HttpResponseRedirect(url)

        else:
            print(
                "resulting salesname",
                salesName,
                "selected salesname",
                selectedSalesName,
            )

            print(
                "error on form processing",
                "vpa customer",
                vpaCustomer,
                type(vpaCustomer),
            )
            print(
                "selectedFinalCustomer",
                selectedFinalCustomer,
                "selectedMainCustomer",
                selectedMainCustomer,
                "selected tier one",
                selectedTierOne,
                "selected ems",
                selectedEms,
                "selected distri",
                selectedDistributor,
            )
            notification = "Error while loading the data"
            productSeriesArray = []
            productSeries = dict()
            products = Product.objects.all()
            for product in products:
                if product.series not in productSeriesArray:
                    productSeriesArray.append(product.series)
                    productSeries[product.series] = product.seriesDescription

            productSeries = sorted(productSeries.items())
            return render(
                request,
                "productMarketing/entryBase.html",
                {
                    "segment": "boupEntry",
                    "step": 0,
                    "enterProjectForm": EnterProjectForm(request.POST),
                    "notification": notification,
                    "mainCustomers": mainCustomers,
                    "finalCustomers": finalCustomers,
                    "oems": oems,
                    "productFamilies": productFamilies,
                    "productSeries": productSeries,
                    "salesNames": salesNames,
                    "mainCustomers": mainCustomers,
                    "finalCustomers": finalCustomers,
                    "salesNameError": salesNameError,
                    "enterMainCustomerError": enterMainCustomerError,
                    "enterFinalCustomerError": enterFinalCustomerError,
                    "appMainError": appMainError,
                    "appDetailError": appDetailError,
                    "selectedSalesName": selectedSalesName,
                    "selectedFinalCustomer": selectedFinalCustomer,
                    "selectedMainCustomer": selectedMainCustomer,
                    "applicationMains": applicationMains,
                    "applicationDetails": applicationDetails,
                    "selectedOem": selectedOem,
                    "selectedDistributor": selectedDistributor,
                    "selectedEms": selectedEms,
                    "selectedTierOne": selectedTierOne,
                    "vpaCustomer": vpaCustomer,
                    "selectedSalesName": selectedSalesName,
                    "oemNameError": oemNameError,
                },
            )

    else:
        print("applicationMains", applicationMains)
        distiTierOneEMSList = mainCustomers
        emss = distiTierOneEMSList
        distributors = distiTierOneEMSList
        tierOnes = distiTierOneEMSList
        # for initial dropdown file in, will be replaced dynamically by htmx
        # productSeries = ProductSeries.objects.all()
        print("appdetailerror", appDetailError)
        return render(
            request,
            "productMarketing/entryBase.html",
            {
                "step": 0,
                "enterProjectForm": enterProjectForm,
                "mainCustomers": mainCustomers,
                "finalCustomers": finalCustomers,
                "oems": oems,
                "applicationMainForm": ApplicationMainForm(request.POST),
                "productFamilies": productFamilies,
                "salesNames": salesNames,
                "salesNameError": salesNameError,
                "enterMainCustomerError": enterMainCustomerError,
                "enterFinalCustomerError": enterFinalCustomerError,
                "appMainError": appMainError,
                "appDetailError": appDetailError,
                "emss": emss,
                "tierOnes": tierOnes,
                "distributors": distributors,
                "applicationMains": applicationMains,
                "applicationDetails": applicationDetails,
                "segment": "boupEntry",
            },
        )


# required for dynamic selection of excercises supported by java script
"""
@login_required(login_url="/login/")
def dropdownApplicationDetail(request):
    data = json.loads(request.body)
    print(data)
    # get variables
    applicationMain = data['applicationMain']

    print("data json", data)
    user = request.user
    print("request.user", request.user, "application Main", applicationMain)

    # get application details
    applicationDetails = ApplicationDetail.objects.get(applicationMain=applicationMain)
    print("applicationDetails", applicationDetails)
   
    return JsonResponse('app detail', safe=False)
"""


def dropdownApplicationDetail(request):
    applicationMain = request.GET.get("applicationMain")
    print("application main input", applicationMain, "type", type(applicationMain))

    applicationMainPk = ApplicationMain.objects.get(appMainDescription=applicationMain)

    applicationDetailsQuery = ApplicationDetail.objects.filter(
        appMain=applicationMainPk
    )
    print("app detail get!!!")
    # form = ApplicationMainForm(request.GET)

    applicationDetailsArray = []
    applicationDetailsDictionary = dict()

    if applicationDetailsQuery.count() > 0:
        for appDetail in applicationDetailsQuery:
            applicationDetailsArray.append(appDetail.appDetailDescription)
    print(
        "got application main",
        applicationMain,
        "resulting query",
        applicationDetailsQuery,
        "resulting array",
        applicationDetailsArray,
    )

    return render(
        request,
        "productMarketing/enterProjectForm/appDetail.html",
        {
            "applicationDetailsArray": applicationDetailsQuery,
        },
    )


def dropdownProductSeries(request):
    print("request get", request.GET)
    family = request.GET.get("family")
    print("selected prod family", family, "desc")

    try:

        # get from product tables all products where product.familyfull is the selected family

        relevantProducts = Product.objects.filter(familyfull=family)
        print("---> relevant products", relevantProducts)

        # since no select distinct statement avaialbale in sqllite, I have to iterate here. The goal is to get the distinct value of seriesDescription based on the selcted family.

        productSeriesArray = []
        productSeries = dict()
        for product in relevantProducts:
            if product.series not in productSeriesArray:
                productSeriesArray.append(product.series)
                productSeries[product.series] = product.seriesDescription

        productSeries = sorted(productSeries.items())

        print("resulting product series", productSeries)
        salesNames = []

        return render(
            request,
            "productMarketing/enterProjectForm/seriesSelect.html",
            {
                "productSeries": productSeries,
                "salesNames": salesNames,
                "family": family,
                "showSeriesSelect": True,
            },
        )

        """
        family = request.GET.get('family')
        print("selected prod family", family, "desc", family.productFamilyDescription)
        
        productSeries = ProductSeries.objects.filter(productFamily = family)
        rfpA = Product.objects.filter(productfamily = family)
        ### this will filter sales names based on the list of rfp's. __in acts as an iterator...
        salesNames = SalesName.objects.filter(rfp__in=rfpA)
        print("-----> rfpA", rfpA, "resulting sales names", salesNames)

        """
    except:
        productSeriesArray = []
        productSeries = dict()
        for product in relevantProducts:
            if product.series not in productSeriesArray:
                productSeriesArray.append(product.series)
                productSeries[product.series] = product.seriesDescription

        productSeries = sorted(productSeries.items())
        salesNames = SalesName.objects.all()
        return render(
            request,
            "productMarketing/enterProjectForm/seriesSelect.html",
            {
                "productSeries": productSeries,
                "salesNames": salesNames,
            },
        )


def dropdownPackage(request, family):
    print("######### dropdownPackage")
    series = request.GET.get("series")
    print("family", family, "series", series)

    relevantProducts = Product.objects.filter(familyfull=family, series=series)
    print("---> relevant products", relevantProducts)

    # since no select distinct statement avaialbale in sqllite, I have to iterate here. The goal is to get the distinct value of packageDescription based on the selcted family AND series.

    packagesArray = []
    packages = dict()
    for product in relevantProducts:
        if product.package not in packagesArray:
            packagesArray.append(product.package)
            print("data --&&", product.package, product.packageDescription)
            print("type", type(packages))
            packages[str(product.package)] = product.packageDescription
            print("#####")

    packages = sorted(packages.items())
    print("packages", packages)

    # get the packages that match this series
    return render(
        request,
        "productMarketing/enterProjectForm/packageSelect.html",
        {
            "packages": packages,
            "family": family,
            "series": series,
        },
    )


def dropdownProductSalesName(request, family, series):
    print("####### dropdownProductSalesName")
    print("family", family)
    # try:
    package = request.GET.get("package")
    print("prod series", series)
    print("package", package)

    rfpA = Product.objects.filter(series=series, familyfull=family, package=package)

    print("input product series", series, "rfp result:", rfpA)
    # print("sales name result", SalesName.objects.filter(rfp = rfpA))
    # and with in sales name

    salesnamesArray = []
    salesNames = dict()

    for product in rfpA:
        salesnameObjects = SalesName.objects.filter(rfp=product)  # .order_by('-id')
        print("evaluating salesname", salesnameObjects)

        # since no select distinct statement avaialbale in sqllite, I have to iterate here.
        # The goal is to get the distinct value of salesname based on the selected family AND series AND package.
        # be aware that product is a foreign key of sales name (one product can have multiple sales names: it's like one car is sold in China with name A and the very same car is sold
        # in USA with name B)

        if salesnameObjects.count() > 0:
            for salesname in salesnameObjects:

                if salesname not in salesnamesArray:
                    salesnamesArray.append(salesname)
                    # salesnames[str(product.package)] = product.packageDescription
                    print("#####")
        else:
            print("sales names are empty!!")
            # TO DO: what to do here??

        # salesNames = SalesName.objects.filter(rfp=rfpA)
        return render(
            request,
            "productMarketing/enterProjectForm/salesName.html",
            {
                "salesNames": salesnamesArray,
            },
        )
    """
    except:
        print("error on sales name select")
        productSeries = ProductSeries.objects.all()
        salesNames = SalesName.objects.all()
        return render(request, "productMarketing/enterProjectForm/salesName.html", {'salesNames': salesNames,})
    """


"""
Step 2: volume (quantities) entry
http://localhost:8000/ifx/productMarketing/boupEntry1/3
"""

# volume entry (manual, yearly)


def volumeEntry(request, projectId):
    print("########### volume entry screen")
    project = Project.objects.get(id=projectId)
    user = request.user
    volumeForm = EnterVolumeFormStandalone()
    volumeAutomaticForm = EnterVolumeAutomaticForm(project=projectId)
    startOfProduction = project.estimatedSop
    # the project id is passed in the request

    if request.method == "POST":
        print("req post", request.POST)

        volumeForm = EnterVolumeFormStandalone(request.POST)
        volumeAutomaticForm = EnterVolumeAutomaticForm(request.POST, project=projectId)
        print("volumeFormInput", volumeForm)
        os = operatingSystem.macOs
        manualEntryInput = request.POST.get("manualEntry")

        # watchout depending on how this crap is entered, the values come as none, bool or string! wtf

        manualEntry = False
        if manualEntryInput != None:
            manualEntry = eval(manualEntryInput)

        print("manual entry?", manualEntry, type(manualEntry))
        excelData = request.POST.get("excelData")
        print("excelData?", excelData)
        excelDataCustomer = request.POST.get("excelDataCustomer")
        # to do: error if decimal volumes...

        # check if excel copy & paste has data, then check if conflicting inputs (excel has data, manual entry is true, etc)
        if excelData:
            excelData = excelData.strip()

            years, outputData, errorMutableSequence = checkExcelFormInput(
                excelData=excelData,
                dataType=TypeOfParameter.volumes,
                sop=project.estimatedSop,
            )
            if len(errorMutableSequence) == 0:
                volumes = outputData
                print(len(years))
                volumesPost = []
                for i in range(0, (len(years)), 1):
                    object, created = ProjectVolumePrices.objects.get_or_create(
                        project=project, calenderYear=int(years[i])
                    )
                    object.quantity = int(volumes[i])
                    object.save()
                    volumesPost.append(int(volumes[i]))
                    print(created, "---> volume object,", object)

                # entries for table projectVolumeMonth with poisson distribution

                year = 0
                monthVolume = linSmoother(years[0], years[-1], volumes)
                print("months:", len(monthVolume), "years", years, "last", years[-1])
                for i in range(0, (len(years)) * 12, 1):

                    if i != 0 and i % 12 == 0:
                        # print(int(years[year]), "----", int(volumes[i]))
                        year = year + 1
                    month = (i % 12) + 1  # +1 so we dont have the 0th month
                    volumeObjectM, created = ProjectVolumeMonth.objects.get_or_create(
                        project=project, calenderYear=int(years[year]), month=month
                    )
                    volumeObjectM.quantity = monthVolume[i]
                    volumeObjectM.save()
                    # volumesPost.append(f(int(years[0])+0.5+(i/12)))
                    print(i)
                    print(created, "---> volume month object,", volumeObjectM)

                # prepare the volume confirmation form
                firstYear = years[0]
                lastYear = years[len(years) - 1]
                deltaYears = int(firstYear) - 2020
                print("pre volumes array", volumesPost)
                print("last year", lastYear)
                if deltaYears > 0:
                    for i in range(0, deltaYears, 1):
                        volumesPost.insert(0, 0)

                deltaYearsEnd = 2045 - int(lastYear)
                print("deltaYearsEnd", deltaYearsEnd, deltaYearsEnd > 0)

                if deltaYearsEnd > 0:
                    for i in range(0, deltaYearsEnd, 1):
                        volumesPost.append(0)
                        print("##")

                yearsInForm = [
                    2020,
                    2021,
                    2022,
                    2023,
                    2024,
                    2025,
                    2026,
                    2027,
                    2028,
                    2029,
                    2030,
                    2031,
                    2032,
                    2034,
                    2035,
                    2036,
                    2037,
                    2038,
                    2039,
                    2040,
                    2041,
                    2042,
                    2043,
                    2044,
                    2045,
                ]

                print("resulting volumes array", volumesPost)

                p20 = volumesPost[0]
                p21 = volumesPost[1]
                p22 = volumesPost[2]
                p23 = volumesPost[3]
                p24 = volumesPost[4]
                p25 = volumesPost[5]
                p26 = volumesPost[6]
                p27 = volumesPost[7]
                p28 = volumesPost[8]
                p29 = volumesPost[9]
                p30 = volumesPost[10]
                p31 = volumesPost[11]
                p32 = volumesPost[12]
                p33 = volumesPost[13]
                p34 = volumesPost[14]
                p35 = volumesPost[15]
                p36 = volumesPost[16]
                p37 = volumesPost[17]
                p38 = volumesPost[18]
                p39 = volumesPost[19]
                p40 = volumesPost[20]

                volumeForm2 = EnterVolumeFormStandalone(
                    initial={
                        "v20": p20,
                        "v21": p21,
                        "v22": p22,
                        "v23": p23,
                        "v24": p24,
                        "v25": p25,
                        "v26": p26,
                        "v27": p27,
                        "v28": p28,
                        "v29": p29,
                        "v30": p30,
                        "v31": p31,
                        "v32": p32,
                        "v33": p33,
                        "v34": p34,
                        "v35": p35,
                        "v36": p36,
                        "v37": p37,
                        "v38": p38,
                        "v39": p39,
                        "v40": p40,
                    }
                )
                return render(
                    request,
                    "productMarketing/entryBase.html",
                    {
                        "step": 1,
                        "volumeForm": volumeForm2,
                        "volumeAutomaticForm": volumeAutomaticForm,
                        "startOfProduction": startOfProduction,
                        "projectId": projectId,
                        "volumeConfirmation": True,
                    },
                )

        # check if excel copy & paste has data, then check if conflicting inputs (excel has data, manual entry is true, etc)
        if excelDataCustomer:
            excelDataCustomer = excelDataCustomer.strip()

            years, outputData, errorMutableSequence = checkExcelFormInput(
                excelData=excelData,
                dataType=TypeOfParameter.volumes,
                sop=project.estimatedSop,
            )
            if len(errorMutableSequence) == 0:
                volumes = outputData

                volumesPost = []
                print("len volumes, len years", len(volumes), len(years))
                for i in range(0, (len(years)), 1):
                    print(int(years[i]), "----", int(volumes[i]))

                    object, created = ProjectVolumePrices.objects.get_or_create(
                        project=project, calenderYear=int(years[i])
                    )
                    object.quantity = int(volumes[i])
                    object.save()
                    """
                    volumeCustomerObject, created = ProjectVolumeCustomerEstimation.objects.get_or_create(project = project, calenderYear = int(years[i]))
                    volumeCustomerObject.quantity = int(volumes[i])
                    volumeCustomerObject.save()
                    volumesPost.append(int(volumes[i]))
                    """
                    print(created, "---> volume Customer object,", object)

                # prepare the volume confirmation form
                firstYear = years[0]
                lastYear = years[len(years) - 1]
                deltaYears = int(firstYear) - 2020
                print("pre volumes array", volumesPost)
                print("last year", lastYear)
                if deltaYears > 0:
                    for i in range(0, deltaYears, 1):
                        volumesPost.insert(0, 0)

                deltaYearsEnd = 2045 - int(lastYear)
                print("deltaYearsEnd", deltaYearsEnd, deltaYearsEnd > 0)

                if deltaYearsEnd > 0:
                    for i in range(0, deltaYearsEnd, 1):
                        volumesPost.append(0)
                        print("##")

                yearsInForm = [
                    2020,
                    2021,
                    2022,
                    2023,
                    2024,
                    2025,
                    2026,
                    2027,
                    2028,
                    2029,
                    2030,
                    2031,
                    2032,
                    2034,
                    2035,
                    2036,
                    2037,
                    2038,
                    2039,
                    2040,
                    2041,
                    2042,
                    2043,
                    2044,
                    2045,
                ]

                print("resulting volumes array", volumesPost)

                p20 = volumesPost[0]
                p21 = volumesPost[1]
                p22 = volumesPost[2]
                p23 = volumesPost[3]
                p24 = volumesPost[4]
                p25 = volumesPost[5]
                p26 = volumesPost[6]
                p27 = volumesPost[7]
                p28 = volumesPost[8]
                p29 = volumesPost[9]
                p30 = volumesPost[10]
                p31 = volumesPost[11]
                p32 = volumesPost[12]
                p33 = volumesPost[13]
                p34 = volumesPost[14]
                p35 = volumesPost[15]
                p36 = volumesPost[16]
                p37 = volumesPost[17]
                p38 = volumesPost[18]
                p39 = volumesPost[19]
                p40 = volumesPost[20]

                volumeForm2 = EnterVolumeFormStandalone(
                    initial={
                        "v20": p20,
                        "v21": p21,
                        "v22": p22,
                        "v23": p23,
                        "v24": p24,
                        "v25": p25,
                        "v26": p26,
                        "v27": p27,
                        "v28": p28,
                        "v29": p29,
                        "v30": p30,
                        "v31": p31,
                        "v32": p32,
                        "v33": p33,
                        "v34": p34,
                        "v35": p35,
                        "v36": p36,
                        "v37": p37,
                        "v38": p38,
                        "v39": p39,
                        "v40": p40,
                    }
                )
                return render(
                    request,
                    "productMarketing/entryBase.html",
                    {
                        "step": 1,
                        "volumeForm": volumeForm2,
                        "volumeAutomaticForm": volumeAutomaticForm,
                        "startOfProduction": startOfProduction,
                        "projectId": projectId,
                        "volumeConfirmation": True,
                    },
                )

        ###
        if manualEntry == True:
            if volumeForm.is_valid():
                volumeFormResult = volumeForm  # .save(commit=False)
                print("volume form", volumeForm)

                # create entries in volume table
                # comment FF: control removed as to allow to continue with a paused data entry (draft)
                """
                if ProjectVolume.objects.filter(project=project, draft=False).exists():
                    print("volume entry already exists, wtf! you should be modifying the project instead!")
                    notification = "Project already exists! (combination of customer and sales name) Try modifying it! Or contact support - ifxsupport@alfa-ai.com"
                    return render(request, "productMarketing/entryStep1.html", {'volumeForm': volumeForm, "notification": notification,})

                else:
                """
                print("creating volume entries")
                # counter starts in 2020
                year = 2020

                for key, value in volumeFormResult.cleaned_data.items():
                    print("key", key, "value", value)
                    if value != None:

                        object, created = ProjectVolumePrices.objects.get_or_create(
                            project=project, calenderYear=year
                        )
                        object.quantity = value
                        object.user = user
                        object.save()
                        year = year + 1

                        # volumeObject, created = ProjectVolume.objects.get_or_create(project = project, calenderYear = year, quantity = value)
                        # volumeObject.quantity = value
                        # print("volume object", volumeObject, "key", key, "quantity", value)
                        # volumeObject.user = user
                        # year = year + 1
                        # volumeObject.save()
                    else:

                        object, created = ProjectVolumePrices.objects.get_or_create(
                            project=project, calenderYear=year
                        )
                        object.quantity = 0
                        object.user = user
                        object.save()
                        year = year + 1

                        """
                        volumeObject, created = ProjectVolume.objects.get_or_create(project = project, calenderYear = year)
                        print("volume object", volumeObject, "key", key, "quantity", value)
                        volumeObject.quantity = 0
                        volumeObject.user = user
                        year = year + 1     
                        volumeObject.save()
                        """
                print("redirecting...")
                url = "/ifx/productMarketing/boupEntry2/" + str(projectId)
                return HttpResponseRedirect(url)
            else:
                print("volume form errors", volumeForm.errors)

        # interpolation!!
        else:
            print("starting interpolation routine!!!")
            # volumeAutomaticForm.startOfProduction
            sop = request.POST.get("startOfProduction")
            # volumeAutomaticForm.endOfProduction
            eop = request.POST.get("endOfProduction")
            # volumeAutomaticForm.initialVolume
            initialVolume = request.POST.get("initialVolume")
            # volumeAutomaticForm.peakVolume
            peakVolume = request.POST.get("peakVolume")
            # volumeAutomaticForm.peakYear
            peakYear = request.POST.get("peakYear")
            # volumeAutomaticForm.distributionType
            distributionType = request.POST.get("distributionType")
            totalVolume = request.POST.get("totalVolume")
            print(
                "sop, eop, initialVolume, peakVolume, peakYear, distributionType, totalVolume--------->",
                sop,
                eop,
                initialVolume,
                peakVolume,
                peakYear,
                distributionType,
                totalVolume,
            )

            # if fields are empty, or total volume is 0, return on error

            if int(totalVolume) == 0:
                # return on error
                notification = "Please fill out all fields!"
                return render(
                    request,
                    "productMarketing/entryBase.html",
                    {
                        "step": 1,
                        "volumeForm": volumeForm,
                        "volumeAutomaticForm": volumeAutomaticForm,
                        "notification": notification,
                        "startOfProduction": startOfProduction,
                        "projectId": projectId,
                    },
                )

            if sop != None:
                sop = int(sop)
                if int(sop) != startOfProduction:
                    print("sop changed!!")
                    project.estimatedSop = int(sop)
                    project.save()

            if eop != None:
                eop = int(eop)

            if initialVolume != None:
                initialVolume = int(initialVolume)

            if peakVolume != None:
                peakVolume = int(peakVolume)

            if peakYear != None:
                peakYear = int(peakYear)

            if totalVolume != None:
                totalVolume = int(totalVolume)

            print("eop none?", eop == None)

            # plausi checks:
            # sop < eop,
            # sop <= peak year <= eop,
            # peak volume != 0
            # initial volume > 0

            (
                eopSmallerEopError,
                sopLargerPeakError,
                peakLargerEopError,
                peakVolError,
                initialVolError,
                totalVolumeError,
            ) = checkConditions(
                sop,
                eop,
                initialVolume,
                peakVolume,
                peakYear,
                distributionType,
                totalVolume,
            )

            if (
                (eopSmallerEopError == False)
                & (sopLargerPeakError == False)
                & (peakLargerEopError == False)
                & (peakVolError == False)
                & (initialVolError == False)
                & (totalVolumeError == False)
            ):

                #########
                print("starting interpolation!!!")
                # for distribution on year level
                monthLevel = True
                yearLevel = True
                if yearLevel == True:
                    interpolationResults = interpolator(
                        sop,
                        eop,
                        initialVolume,
                        peakVolume,
                        peakYear,
                        distributionType,
                        totalVolume,
                    )
                    print("interpolation results!!!", interpolationResults)

                    # the interpolation is an array... it's 0 element is of SoP year

                    ##########
                    # insert into volumes table

                    year = sop

                    for index in range(0, eop - sop, 1):
                        quantity = int(interpolationResults[index])

                        object, created = ProjectVolumePrices.objects.get_or_create(
                            project=project, calenderYear=year
                        )
                        object.quantity = quantity
                        object.user = user
                        object.save()
                        year = year + 1

                        """
                        volumeObject, created = ProjectVolume.objects.get_or_create(project = project, calenderYear = year)
                        print("volume object", volumeObject, "quantity", quantity)
                        volumeObject.user = user
                        year = year + 1
                        volumeObject.quantity = quantity
                        volumeObject.save()
                        """
                if monthLevel == True:

                    interpolationResults = yearToMonthPoissonSmoother(
                        sop, eop, totalVolume, peakYear
                    )
                    print("interpolation results!!!", interpolationResults)

                    # the interpolation is an array of arrays... it's 0 element is of SoP year, its 0 0 element is first month of SoP

                    ##########
                    # insert into volumes month table
                    year = sop
                    month = 1
                    for index in range(0, (eop - sop) * 12, 1):
                        if month == 13:
                            month = 1
                            year = year + 1

                        quantity = int(interpolationResults[index])

                        (
                            volumeObject,
                            created,
                        ) = ProjectVolumeMonth.objects.get_or_create(
                            project=project, calenderYear=year, month=month
                        )
                        print(
                            "volume object",
                            volumeObject,
                            "created",
                            created,
                            "quantity",
                            quantity,
                        )

                        volumeObject.user = user
                        volumeObject.quantity = quantity
                        volumeObject.month = month
                        volumeObject.save()
                        month = month + 1

                # show volume confirmation screen!

                print("redirecting...")
                url = "/ifx/productMarketing/boupEntry2/" + str(projectId)
                return HttpResponseRedirect(url)

            """
            calenderYear = models.IntegerField()
            quantity = models.IntegerField()
            source = models.CharField(max_length=30, choices=ALLOWABLE_TYPES_VOLUME_SOURCE, blank=True, null=True) 
            date = models.DateTimeField(default=now, editable=False, blank=True, null=True) 
            user = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True) 
            """

            notification = "Please fill out all fields!"
            return render(
                request,
                "productMarketing/entryBase.html",
                {
                    "step": 1,
                    "volumeForm": volumeForm,
                    "volumeAutomaticForm": volumeAutomaticForm,
                    "notification": notification,
                    "startOfProduction": startOfProduction,
                    "projectId": projectId,
                },
            )
    else:
        print("volumeAutomaticForm", volumeAutomaticForm)
        return render(
            request,
            "productMarketing/entryBase.html",
            {
                "step": 1,
                "volumeForm": volumeForm,
                "volumeAutomaticForm": volumeAutomaticForm,
                "startOfProduction": startOfProduction,
                "projectId": projectId,
                "volumeConfirmation": False,
            },
        )


###


def distributionConfigurator(request, projectId):
    print("rquest", request)
    try:
        distributionType = request.GET.get("distributionType")
        print("-----> distributionType", distributionType, "post", request)

        if distributionType == "poisson":
            volumeAutomaticForm = EnterVolumeAutomaticForm(project=projectId)
            return render(
                request,
                "productMarketing/enterVolumeForm/distributionConfiguratorPoisson.html",
                {
                    "volumeAutomaticForm": volumeAutomaticForm,
                },
            )

    except:
        productSeries = ProductSeries.objects.all()
        salesNames = SalesName.objects.all()
        return render(
            request,
            "productMarketing/enterProjectForm/seriesSelect.html",
            {
                "productSeries": productSeries,
                "salesNames": salesNames,
            },
        )


"""
Step 3a: select price source.
For now, it will be only "Excel copy & paste"
http://localhost:8000/ifx/productMarketing/boupEntry2/3
"""

# select pricing source


def priceSelection(request, projectId):
    print("########### price source selection screen")

    project = Project.objects.get(id=projectId)
    sourceSelectionForm = SelectPriceSourceForm()

    if request.method == "POST":
        sourceSelectionForm = SelectPriceSourceForm(request.POST)
        print("volumeFormInput", sourceSelectionForm)

        for key, value in sourceSelectionForm.cleaned_data.items():
            print("--->key", key, "value", value)

            if value == "excel":

                url = "/ifx/productMarketing/boupEntry2a/" + str(projectId)
                return HttpResponseRedirect(url)

            if value == "manual":
                url = "/ifx/productMarketing/boupEntry3/" + str(projectId) + "/0"
                return HttpResponseRedirect(url)

            # vpa db is source
            elif value == "pricesDB":
                url = "/ifx/productMarketing/boupEntry3/" + str(projectId) + "/1"
                return HttpResponseRedirect(url)
            # vpa db is source
            else:
                url = "/ifx/productMarketing/boupEntry3/" + str(projectId) + "/2"
                return HttpResponseRedirect(url)

    return render(
        request,
        "productMarketing/entryBase.html",
        {
            "step": 2,
            "sourceSelectionForm": sourceSelectionForm,
        },
    )


"""
Step 3b: enter price
For now, it will be only "Excel copy & paste"
http://localhost:8000/ifx/productMarketing/boupEntry2a/3
"""
# select pricing source


def priceEnterExcel(request, projectId):
    print("########### price data enter from excel")

    project = Project.objects.get(id=projectId)
    sourceSelectionForm = SelectPriceSourceForm()
    user = request.user

    os = operatingSystem.macOs

    if request.method == "POST":
        currencyInput = request.POST.get("currency")
        excelData = request.POST.get("excelData")
        sourceSelectionForm2 = SelectPriceSourceForm(request.POST)
        priceValidUntil = request.POST.get("priceValidUntil")
        familyPrices = request.POST.get("familyPrices")
        priceComments = request.POST.get("priceComments")

        if excelData:
            excelData = excelData.strip()
            years, outputData, errorMutableSequence = checkExcelFormInput(
                excelData=excelData,
                dataType=TypeOfParameter.prices,
                sop=project.estimatedSop,
            )

            if len(errorMutableSequence) == 0:

                prices = outputData
                print("project", project)
                print("years", years)
                print("prices", prices)
                for i in range(0, (len(years)), 1):

                    object, created = ProjectVolumePrices.objects.get_or_create(
                        project=project, calenderYear=int(years[i])
                    )
                    object.price = float(prices[i])
                    object.currency = currencyInput

                    object.priceValidUntil = priceValidUntil
                    object.priceSourceComment = priceComments
                    project.familyPriceApplicable = familyPrices
                    object.user = user
                    object.save()
                    project.save()
                    # year = year + 1

                    """
                    priceObject, created = ProjectPrices.objects.get_or_create(project = project, calenderYear = int(years[i]), valid = True)
                    ## if object already exist, modify
                    priceObject.currency = currencyInput
                    priceObject.user = user
                    priceObject.price = float(prices[i])

                    priceObject.save()
                    print(created, "price object", priceObject)
                    """
                url = "/ifx/productMarketing/boupEntry3/" + str(projectId) + "/0"
                return HttpResponseRedirect(url)
            else:
                return render(
                    request,
                    "productMarketing/entryBase.html",
                    {
                        "step": 2,
                        "sourceSelectionForm": sourceSelectionForm2,
                        "excel": True,
                        "notification": "Error on processing or price data missing.",
                    },
                )

        else:
            return render(
                request,
                "productMarketing/entryBase.html",
                {
                    "step": 2,
                    "sourceSelectionForm": sourceSelectionForm2,
                    "excel": True,
                    "notification": "Error on processing or price data missing.",
                },
            )

    return render(
        request,
        "productMarketing/entryBase.html",
        {"step": 2, "sourceSelectionForm": sourceSelectionForm, "excel": True},
    )


##     path('productMarketing/boupEntry3/<int:projectId>/<int:mode>', views.priceConfirmation, name='priceConfirmation'),
# review pricing, evtl. edit prices
def priceConfirmation(request, projectId, mode):
    project = Project.objects.get(id=projectId)
    priceConfirmationForm = PriceConfirmationForm()
    user = request.user
    print("%%%%%%%%%%%%% price confirmaiton screen")
    if request.method == "POST":
        priceConfirmationFormResult = PriceConfirmationForm(request.POST)
        # priceConfirmationFormResult.currency
        currency = request.POST.get("currency")
        print("selected currecny", currency)

        # To Do: check that for every year for which a volume was entered, a price exist. And viceversa too.

        ###
        if False:  # ProjectPrices.objects.filter(project=project).exists():
            print("prices for project already exist")
            notification = "Prices for this project already exist. Please try modifying the project data."
            status = 0
            return render(
                request,
                "productMarketing/entryStep3.html",
                {
                    "priceConfirmationForm": priceConfirmationFormResult,
                    "notification": notification,
                    "status": status,
                },
            )

        else:
            if priceConfirmationFormResult.is_valid():
                print("##### price confirmation")
                # counter starts in 2020
                year = 2020
                currency = "EUR"
                for key, value in priceConfirmationFormResult.cleaned_data.items():
                    if key == "currency":
                        currency = value

                for key, value in priceConfirmationFormResult.cleaned_data.items():
                    print("key", key, "value", value)
                    if key != "currency":
                        if value != None:

                            object, created = ProjectVolumePrices.objects.get_or_create(
                                project=project, calenderYear=year
                            )
                            object.price = value
                            object.currency = currency
                            object.user = user
                            object.save()
                            year = year + 1

                        else:
                            # priceObject, created = ProjectPrices.objects.get_or_create(project = project, calenderYear = year, price = 0.0, valid = True, user = user, currency = currency)

                            object, created = ProjectVolumePrices.objects.get_or_create(
                                project=project, calenderYear=year
                            )
                            object.price = 0.0
                            object.currency = currency
                            object.user = user
                            object.save()
                            year = year + 1

                # check if price for each volume
                prodYears = checkVolumeEntry(projectId)
                sop = prodYears[0]
                eop = prodYears[-1]
                prices = []
                for key, value in priceConfirmationFormResult.cleaned_data.items():
                    print("key right now", key)
                    for i in prodYears:
                        if key == "v" + str(i)[2:]:
                            prices.append(value)
                print("check which prices are avaiable", prices)
                if checkConditionsAtPrice(sop, eop, prices) == True:
                    notification = (
                        "Error on price processing, pricemissing for years from "
                        + str(sop)
                        + " up to including "
                        + str(eop)
                    )

                    # error dictionary as return after each step (function in new script PlausibilityCheck): for each req one TRUE/FALSE for each project id

                    status = 0
                    return render(
                        request,
                        "productMarketing/entryBase.html",
                        {
                            "step": 3,
                            "priceConfirmationForm": priceConfirmationFormResult,
                            "notification": notification,
                        },
                    )

                # redirect
                url = "/ifx/productMarketing/boupEntry4/" + str(projectId)
                return HttpResponseRedirect(url)
            else:
                notification = "Error on price processing, please check all values."
                status = 0
                return render(
                    request,
                    "productMarketing/entryBase.html",
                    {
                        "step": 3,
                        "priceConfirmationForm": priceConfirmationFormResult,
                        "notification": notification,
                    },
                )

    else:
        prices = []
        years = [
            2020,
            2021,
            2022,
            2023,
            2024,
            2025,
            2026,
            2027,
            2028,
            2029,
            2030,
            2031,
            2032,
            2034,
            2035,
            2036,
            2037,
            2038,
            2039,
            2040,
            2041,
            2042,
            2043,
            2044,
            2045,
        ]
        print("fetching prices!!")
        currency = "EUR"
        pricesExisted = False
        for year in years:
            try:
                object = ProjectVolumePrices.objects.get(
                    project=project, calenderYear=int(year)
                )
                prices.append(object.price)
                currency = object.currency
                pricesExisted = True

                """
                priceObject = ProjectPrices.objects.get(project = project, calenderYear = int(year), valid = True)
                prices.append(priceObject.price)
                currency = priceObject.currency
                pricesExisted = True
                """
            except:
                prices.append(0.0)
        print("resulting prices array", prices)

        p20 = prices[0]
        p21 = prices[1]
        p22 = prices[2]
        p23 = prices[3]
        p24 = prices[4]
        p25 = prices[5]
        p26 = prices[6]
        p27 = prices[7]
        p28 = prices[8]
        p29 = prices[9]
        p30 = prices[10]
        p31 = prices[11]
        p32 = prices[12]
        p33 = prices[13]
        p34 = prices[14]
        p35 = prices[15]
        p36 = prices[16]
        p37 = prices[17]
        p38 = prices[18]
        p39 = prices[19]
        p40 = prices[20]

        priceConfirmationForm2 = PriceConfirmationForm(
            initial={
                "currency": currency,
                "v20": p20,
                "v21": p21,
                "v22": p22,
                "v23": p23,
                "v24": p24,
                "v25": p25,
                "v26": p26,
                "v27": p27,
                "v28": p28,
                "v29": p29,
                "v30": p30,
                "v31": p31,
                "v32": p32,
                "v33": p33,
                "v34": p34,
                "v35": p35,
                "v36": p36,
                "v37": p37,
                "v38": p38,
                "v39": p39,
                "v40": p40,
            }
        )

        # manual entry
        if mode == 0:
            # check if price for each year exists
            prodYears = checkVolumeEntry(projectId)
            sop = prodYears[0]
            eop = prodYears[-1]
            print(prodYears)
            check = checkConditionsAtPrice(sop, eop, prices)
            print(check)
            return render(
                request,
                "productMarketing/entryBase.html",
                {
                    "step": 3,
                    "priceConfirmationForm": priceConfirmationForm2,
                    "pricesExisted": pricesExisted,
                    "check": check,
                    "sop": sop,
                    "eop": eop,
                },
            )

        # take data from prices db if possible, else fallback
        elif mode == 1:

            # load prices from DB or mock data, parse into form, and show

            return render(
                request,
                "productMarketing/entryBase.html",
                {
                    "step": 3,
                    "priceConfirmationForm": priceConfirmationForm2,
                    "pricesExisted": pricesExisted,
                },
            )

        # take data from vpa db if possible, else fallback
        else:
            # load prices from DB or mock data, parse into form, and show

            return render(
                request,
                "productMarketing/entryBase.html",
                {
                    "step": 3,
                    "priceConfirmationForm": priceConfirmationForm2,
                    "pricesExisted": pricesExisted,
                },
            )

    return render(
        request,
        "productMarketing/entryStep3.html",
        {
            "priceConfirmationForm": priceConfirmationForm,
        },
    )


# overview, submit and evaluate (eg. for family price conflict)

"""
http://localhost:8000/ifx/productMarketing/boupEntry4/3

Project overview with graphics. Right now using seaborn, should switch to Chart.JS
"""


def boupEntryOverview(request, projectId):

    # fetch vorherstellungskosten
    # to do on imports: check consistency of currencies; gaps of years
    user = request.user

    years = [
        2020,
        2021,
        2022,
        2023,
        2024,
        2025,
        2026,
        2027,
        2028,
        2029,
        2030,
        2031,
        2032,
        2034,
        2035,
        2036,
        2037,
        2038,
        2039,
        2040,
        2041,
        2042,
        2043,
        2044,
        2045,
    ]
    months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    all_months = []
    missing_months = []
    vhk = []
    volumes = []
    volumesMonth = []
    prices = []
    pricesExisted = False
    currencyPrices = ""
    currencyVhk = ""
    region = ["EU"]

    project = Project.objects.get(id=projectId)

    for year in years:
        try:
            object = ProjectVolumePrices.objects.get(
                project=project, calenderYear=int(year)
            )
            # priceObject = ProjectPrices.objects.get(project = project, calenderYear = int(year), valid = True)

            # to do: what if quantity or price are empty or 0?
            prices.append(float(object.price))
            currencyPrices = object.currency
            volumes.append(object.quantity)

        except:
            prices.append(0)
            volumes.append(0)

    i = 0
    for year in years:
        for month in months:
            try:
                volumeMonthObject = ProjectVolumeMonth.objects.get(
                    project=project, calenderYear=year, month=month
                )
                volumesMonth.append(volumeMonthObject.quantity)
                all_months.append(i + 1)
                i = i + 1
            except:
                missing_months.append(i + 1)

    try:
        costObject = VhkCy.objects.get(RFP=project.salesName.rfp.pk, valid=True)
        for year in years:
            # costObject = VhkCy.objects.get(RFP = project.salesName.rfp.pk, calendarYear = year)
            varName = "cy" + str(year)
            costValue = getattr(costObject, varName)
            vhk.append(float(costValue))
            currencyVhk = costObject.currency.currency
    except:
        for year in years:
            vhk.append(0)
        # to avoid error
        currencyVhk = "EUR"

    for year in years:
        try:
            region.append(project.region)
        except:
            region.append("Not avaiable")
    ##### revenue and gm

    revenue = []
    grossMargin = []
    grossMarginPct = []

    # FY calculations through month aggregation
    revenue_month = []
    grossMargin_month = []
    grossMarginPct_month = []

    fxErrorPrices = False

    print("projectId", projectId)
    print("prices", prices)
    print("vhk", vhk)
    print("volumes", volumes)
    print("volumes for month", volumesMonth)
    print("currencies", currencyPrices, currencyVhk)

    # check if price currency matches cost currency, else batch transform
    if currencyPrices != "EUR":
        print("currencies do not match! converting to EUR")
        # get current rate
        fx = 1.0
        #currencyObj = Currencies.objects.get(currency=currencyPrices)

        try:
            """
            fxObject = ExchangeRates.objects.get(currency=currencyObj.pk, valid=True)
            fx = fxObject.rate
            """
            from currencies.models import Currency
            fxObject = Currency.objects.get(code=currencyPrices, is_active=True)
            fx = float(fxObject.factor)
        except:
            print("failed currency exchange!! aborting!!")
            fxErrorPrices = True

        print("lenghts", len(prices), len(years))
        for index in range((len(years) - 1)):
            prices[index] = prices[index] * float(fx)

    if currencyVhk != "EUR":
        print("currencies vhk do not match! converting to EUR")
        # get current rate
        fx = 1.0
        #currencyObj = Currencies.objects.get(currency=currencyVhk)
        #print("currobj", currencyObj.currency)

        try:
            """
            fxObject = ExchangeRates.objects.get(currency=currencyObj.pk, valid=True)
            fx = fxObject.rate
            """
            from currencies.models import Currency
            fxObject = Currency.objects.get(code=currencyPrices, is_active=True)
            fx = float(fxObject.factor)
        except:
            print("failed currency exchange!! aborting!!")
            fxErrorPrices = True

        for index in range((len(years) - 1)):
            vhk[index] = vhk[index] * float(fx)

    # will be first in EUR
    print("------------> final results without considering family prices")

    if fxErrorPrices == False:
        for index in range(len(years)):
            revenueValue = prices[index] * volumes[index]
            grossMarginValue = revenueValue - (vhk[index] * volumes[index])
            revenue.append(revenueValue)
            grossMargin.append(grossMarginValue)
            grossMarginPctValue = 0
            try:
                grossMarginPctValue = grossMarginValue * 100 / revenueValue
                grossMarginPct.append(grossMarginPctValue)
            except:
                grossMarginPct.append(0)
            print(
                "%%%%%%%%%%% final result, year",
                years[index],
                "volume",
                volumes[index],
                "price",
                prices[index],
                "currency: EUR",
                "revenue",
                revenueValue,
                "gross margin",
                grossMarginValue,
                "cost",
                vhk[index],
                "margin pctg",
                grossMarginPctValue,
            )

        # for monthly calculation aggregated into FY
        for index in range(len(years)):
            for month in months:
                try:
                    month_value = volumesMonth[(index * 12) + month - 1]
                except:
                    # since only values until 2024 and not up to 2045(because entry is for 2020 to 2024)
                    month_value = 0
                revenueMonthValue = prices[index] * month_value
                grossMarginMonthValue = revenueMonthValue - (vhk[index] * month_value)
                revenue_month.append(revenueMonthValue)
                grossMargin_month.append(grossMarginMonthValue)
                grossMarginMonthPctValue = 0

                try:
                    grossMarginMonthPctValue = (
                        grossMarginMonthValue * 100 / revenueMonthValue
                    )
                    grossMarginPct_month.append(grossMarginMonthPctValue)
                except:
                    grossMarginPct_month.append(0)
                    print(
                        "%%%%%%%%%%% final result, year",
                        years[index],
                        "month",
                        month,
                        "volume",
                        month_value,
                        "price",
                        prices[index],
                        "currency: EUR",
                        "revenue",
                        revenueMonthValue,
                        "gross margin",
                        grossMarginMonthValue,
                        "cost",
                        vhk[index],
                        "margin pctg",
                        grossMarginMonthPctValue,
                    )

    # calculation to agg. into FY
    revenue_FY = []
    grossProfit_FY = []
    grossProfitPct_FY = []
    volumes_FY = []

    for idx in range(len(years)):
        if idx == 0:
            revenue_FY.append(sum(revenue_month[:9]))
            grossProfit_FY.append(sum(grossMargin_month[:9]))
            grossProfitPct_FY.append(sum(grossMarginPct_month[:9]))
            volumes_FY.append(sum(volumesMonth[:9]))
        elif idx == len(years) - 1:
            revenue_FY.append(sum(revenue_month[-3:]))
            grossProfit_FY.append(sum(grossMargin_month[-3:]))
            grossProfitPct_FY.append(sum(grossMarginPct_month[-3:]))
            volumes_FY.append(sum(volumesMonth[-3:]))
        else:
            current_start = 8 + 12 * (idx - 1)
            current_end = 8 + 12 * idx
            revenue_FY.append(sum(revenue_month[current_start : current_end + 1]))
            grossProfit_FY.append(
                sum(grossMargin_month[current_start : current_end + 1])
            )
            grossProfitPct_FY.append(
                sum(grossMarginPct_month[current_start : current_end + 1])
            )
            volumes_FY.append(sum(volumesMonth[current_start : current_end + 1]))

    print("lens", len(years), len(grossMargin), len(revenue))
    print("%%%%%&&&&& gross margins", grossMargin)
    print("%%%%%&&&&& revenue", revenue)
    print("%%%%%&&&&& cumulative gross margin", sum(grossMargin))
    print("%%%%%&&&&& cumulative revenue", sum(grossMargin))

    # create entry in BoUp TABLE
    start_time = time.time()
    if not project.oem:
        oem = ""
    else:
        oem = project.oem  # oem = project.oem.oemName

    statusProbability = float(project.status.status)

    print("oem", oem)
    """
    BoUpObject, created = BoUp.objects.get_or_create(
                                ID_APP = project,
                                applicationLine = project.applicationLine,
                                productMarketer = project.productMarketer,
                                hfg = project.salesName.rfp.hfg,
                                ppos = project.salesName.rfp.ppos,
                                spNumber = project.spNumber,
                                applicationMain = project.applicationMain,  
                                applicationDetail = project.applicationDetail,                                     
                                rfp = project.salesName.rfp,
                                salesName = project.salesName,
                                #priceSource, #defaulted 
                                familyPriceApplicable = project.familyPriceApplicable,
                                familyPriceDetails = project.familyPriceDetails,
                                priceType = project.priceType,
                                #currency, #defaulted 
                                #fxRate, #defaulted
                                comment = project.comment, 
                                region = project.region,
                                projectName = project.projectName,
                                mainCustomer = project.mainCustomer,#mainCustomer = project.mainCustomer.customerName,
                                endCustomer = project.endCustomer,#endCustomer = project.endCustomer.finalCustomerName,
                                distributor = project.distributor,
                                tier1 = project.tier1,
                                oem = oem,
                                ems = project.ems,
                                vpaCustomer = project.vpaCustomer,
                                #dragonId, #defaulted 			 
                                salesContact = project.salesContact,
                                probability = statusProbability,
                                #statusProbability, #defaulted 	
                                sop = project.estimatedSop,
                                availablePGS = project.salesName.rfp.availablePGS,
                                modifiedBy = project.user,#modifiedBy = project.user.username,
                                modifiedDate = project.modifiedDate,
                                creationDate = project.creationDate,
                                #timeBottomUp, #defaulted 			
                                #basicType, #defaulted			
                                package = project.salesName.rfp.package,
                                series = project.salesName.rfp.series,
                                #gen, #defaulted 				
                                #seriesLong, #defaulted 		 
                                #genDetail,	#defaulted 
                                            )
    """
    print("related object", project.projectvolumeprices)
    BoUpObject, created = BoUp.objects.get_or_create(
        ID_APP=project,
        # applicationLine = project.applicationLine,
        productMarketer=project.productMarketer,
        hfg=project.salesName.rfp.hfg,
        ppos=project.salesName.rfp.ppos,
        spNumber=project.spNumber,
        applicationMain=project.applicationMain,
        applicationDetail=project.applicationDetail,
        rfp=project.salesName.rfp,
        salesName=project.salesName,
        familyPriceApplicable=project.familyPriceApplicable,
        familyPriceDetails=project.familyPriceDetails,
        priceType=project.priceType,
        comment=project.comment,
        region=project.region,
        projectName=project.projectName,
        # mainCustomer = project.mainCustomer.customerName,
        mainCustomer=project.mainCustomer,
        # endCustomer = project.endCustomer.finalCustomerName,
        endCustomer=project.endCustomer,
        distributor=project.distributor,
        tier1=project.tier1,
        ems=project.ems,
        vpaCustomer=project.vpaCustomer,
        salesContact=project.salesContact,
        probability=statusProbability,
        sop=project.estimatedSop,
        availablePGS=project.salesName.rfp.availablePGS,
        modifiedBy=user,  # project.user,#modifiedBy = project.user.username,
        modifiedDate=project.modifiedDate,
        creationDate=project.creationDate,
        package=project.salesName.rfp.package,
        series=project.salesName.rfp.seriesHelper,
    )
    """
    bis oem

    """
    try:
        BoUpObject.oem = oem
    except:
        print("could not set oem!", oem)

    BoUpObject.gmLifeTime = sum(grossMargin)
    BoUpObject.revEurLifeTime = sum(revenue)
    BoUpObject.volLifeTime = sum(volumes)
    BoUpObject.volWeightedLifeTime = sum(volumes) * statusProbability

    BoUpObject.vol2020 = volumes[0]
    BoUpObject.vol2021 = volumes[1]
    BoUpObject.vol2022 = volumes[2]
    BoUpObject.vol2023 = volumes[3]
    BoUpObject.vol2024 = volumes[4]
    BoUpObject.vol2025 = volumes[5]
    BoUpObject.vol2026 = volumes[6]
    BoUpObject.vol2027 = volumes[7]
    BoUpObject.vol2028 = volumes[8]
    BoUpObject.vol2029 = volumes[9]
    BoUpObject.vol2030 = volumes[10]
    BoUpObject.vol2031 = volumes[11]
    BoUpObject.vol2032 = volumes[12]
    BoUpObject.vol2033 = volumes[13]
    BoUpObject.vol2034 = volumes[14]
    BoUpObject.vol2035 = volumes[15]
    BoUpObject.vol2036 = volumes[16]
    BoUpObject.vol2037 = volumes[17]
    BoUpObject.vol2038 = volumes[18]
    BoUpObject.vol2039 = volumes[19]
    BoUpObject.vol2040 = volumes[20]
    BoUpObject.vol2041 = volumes[21]
    BoUpObject.vol2042 = volumes[22]
    BoUpObject.vol2043 = volumes[23]
    BoUpObject.vol2044 = 0.0

    # original code linked all volCustomer to first entry in volumes
    BoUpObject.volCustomer2020 = volumes[0]
    BoUpObject.volCustomer2021 = volumes[0]
    BoUpObject.volCustomer2022 = volumes[0]
    BoUpObject.volCustomer2023 = volumes[0]
    BoUpObject.volCustomer2024 = volumes[0]
    BoUpObject.volCustomer2025 = volumes[0]
    BoUpObject.volCustomer2026 = volumes[0]
    BoUpObject.volCustomer2027 = volumes[0]
    BoUpObject.volCustomer2028 = volumes[0]
    BoUpObject.volCustomer2029 = volumes[0]
    BoUpObject.volCustomer2030 = volumes[0]
    BoUpObject.volCustomer2031 = volumes[0]
    BoUpObject.volCustomer2032 = volumes[0]
    BoUpObject.volCustomer2033 = volumes[0]
    BoUpObject.volCustomer2034 = volumes[0]
    BoUpObject.volCustomer2035 = volumes[0]
    BoUpObject.volCustomer2036 = volumes[0]
    BoUpObject.volCustomer2037 = volumes[0]
    BoUpObject.volCustomer2038 = volumes[0]
    BoUpObject.volCustomer2039 = volumes[0]
    BoUpObject.volCustomer2040 = volumes[0]
    BoUpObject.volCustomer2041 = volumes[0]
    BoUpObject.volCustomer2042 = volumes[0]
    BoUpObject.volCustomer2043 = volumes[0]
    BoUpObject.volCustomer2044 = volumes[0]

    BoUpObject.price2020 = prices[0]
    BoUpObject.price2021 = prices[1]
    BoUpObject.price2022 = prices[2]
    BoUpObject.price2023 = prices[3]
    BoUpObject.price2024 = prices[4]
    BoUpObject.price2025 = prices[5]
    BoUpObject.price2026 = prices[6]
    BoUpObject.price2027 = prices[7]
    BoUpObject.price2028 = prices[8]
    BoUpObject.price2029 = prices[9]
    BoUpObject.price2030 = prices[10]
    BoUpObject.price2031 = prices[11]
    BoUpObject.price2032 = prices[12]
    BoUpObject.price2033 = prices[13]
    BoUpObject.price2034 = prices[14]
    BoUpObject.price2035 = prices[15]
    BoUpObject.price2036 = prices[16]
    BoUpObject.price2037 = prices[17]
    BoUpObject.price2038 = prices[18]
    BoUpObject.price2039 = prices[19]
    BoUpObject.price2040 = prices[20]
    BoUpObject.price2041 = prices[21]
    BoUpObject.price2042 = prices[22]
    BoUpObject.price2043 = prices[23]
    BoUpObject.price2044 = 0.0

    BoUpObject.vhk2020 = vhk[0]
    BoUpObject.vhk2021 = vhk[1]
    BoUpObject.vhk2022 = vhk[2]
    BoUpObject.vhk2023 = vhk[3]
    BoUpObject.vhk2024 = vhk[4]
    BoUpObject.vhk2025 = vhk[5]
    BoUpObject.vhk2026 = vhk[6]
    BoUpObject.vhk2027 = vhk[7]
    BoUpObject.vhk2028 = vhk[8]
    BoUpObject.vhk2029 = vhk[9]
    BoUpObject.vhk2030 = vhk[10]
    BoUpObject.vhk2031 = vhk[11]
    BoUpObject.vhk2032 = vhk[12]
    BoUpObject.vhk2033 = vhk[13]
    BoUpObject.vhk2034 = vhk[14]
    BoUpObject.vhk2035 = vhk[15]
    BoUpObject.vhk2036 = vhk[16]
    BoUpObject.vhk2037 = vhk[17]
    BoUpObject.vhk2038 = vhk[18]
    BoUpObject.vhk2039 = vhk[19]
    BoUpObject.vhk2040 = vhk[20]
    BoUpObject.vhk2041 = vhk[21]
    BoUpObject.vhk2042 = vhk[22]
    BoUpObject.vhk2043 = vhk[23]
    BoUpObject.vhk2044 = 0.0

    BoUpObject.gm2020 = grossMargin[0]
    BoUpObject.gm2021 = grossMargin[1]
    BoUpObject.gm2022 = grossMargin[2]
    BoUpObject.gm2023 = grossMargin[3]
    BoUpObject.gm2024 = grossMargin[4]
    BoUpObject.gm2025 = grossMargin[5]
    BoUpObject.gm2026 = grossMargin[6]
    BoUpObject.gm2027 = grossMargin[7]
    BoUpObject.gm2028 = grossMargin[8]
    BoUpObject.gm2029 = grossMargin[9]
    BoUpObject.gm2030 = grossMargin[10]
    BoUpObject.gm2031 = grossMargin[11]
    BoUpObject.gm2032 = grossMargin[12]
    BoUpObject.gm2033 = grossMargin[13]
    BoUpObject.gm2034 = grossMargin[14]
    BoUpObject.gm2035 = grossMargin[15]
    BoUpObject.gm2036 = grossMargin[16]
    BoUpObject.gm2037 = grossMargin[17]
    BoUpObject.gm2038 = grossMargin[18]
    BoUpObject.gm2039 = grossMargin[19]
    BoUpObject.gm2040 = grossMargin[20]
    BoUpObject.gm2041 = grossMargin[21]
    BoUpObject.gm2042 = grossMargin[22]
    BoUpObject.gm2043 = grossMargin[23]
    BoUpObject.gm2044 = 0.0

    BoUpObject.wVol2020 = float(volumes[0]) * statusProbability
    BoUpObject.wVol2021 = float(volumes[1]) * statusProbability
    BoUpObject.wVol2022 = float(volumes[2]) * statusProbability
    BoUpObject.wVol2023 = float(volumes[3]) * statusProbability
    BoUpObject.wVol2024 = float(volumes[4]) * statusProbability
    BoUpObject.wVol2025 = float(volumes[5]) * statusProbability
    BoUpObject.wVol2026 = float(volumes[6]) * statusProbability
    BoUpObject.wVol2027 = float(volumes[7]) * statusProbability
    BoUpObject.wVol2028 = float(volumes[8]) * statusProbability
    BoUpObject.wVol2029 = float(volumes[9]) * statusProbability
    BoUpObject.wVol2030 = float(volumes[10]) * statusProbability
    BoUpObject.wVol2031 = float(volumes[11]) * statusProbability
    BoUpObject.wVol2032 = float(volumes[12]) * statusProbability
    BoUpObject.wVol2033 = float(volumes[13]) * statusProbability
    BoUpObject.wVol2034 = float(volumes[14]) * statusProbability
    BoUpObject.wVol2035 = float(volumes[15]) * statusProbability
    BoUpObject.wVol2036 = float(volumes[16]) * statusProbability
    BoUpObject.wVol2037 = float(volumes[17]) * statusProbability
    BoUpObject.wVol2038 = float(volumes[18]) * statusProbability
    BoUpObject.wVol2039 = float(volumes[19]) * statusProbability
    BoUpObject.wVol2040 = float(volumes[20]) * statusProbability
    BoUpObject.wVol2041 = float(volumes[21]) * statusProbability
    BoUpObject.wVol2042 = float(volumes[22]) * statusProbability
    BoUpObject.wVol2043 = float(volumes[23]) * statusProbability
    BoUpObject.wVol2044 = 0.0

    BoUpObject.wRev2020 = revenue[0] * statusProbability
    BoUpObject.wRev2021 = revenue[1] * statusProbability
    BoUpObject.wRev2022 = revenue[2] * statusProbability
    BoUpObject.wRev2023 = revenue[3] * statusProbability
    BoUpObject.wRev2024 = revenue[4] * statusProbability
    BoUpObject.wRev2025 = revenue[5] * statusProbability
    BoUpObject.wRev2026 = revenue[6] * statusProbability
    BoUpObject.wRev2027 = revenue[7] * statusProbability
    BoUpObject.wRev2028 = revenue[8] * statusProbability
    BoUpObject.wRev2029 = revenue[9] * statusProbability
    BoUpObject.wRev2030 = revenue[10] * statusProbability
    BoUpObject.wRev2031 = revenue[11] * statusProbability
    BoUpObject.wRev2032 = revenue[12] * statusProbability
    BoUpObject.wRev2033 = revenue[13] * statusProbability
    BoUpObject.wRev2034 = revenue[14] * statusProbability
    BoUpObject.wRev2035 = revenue[15] * statusProbability
    BoUpObject.wRev2036 = revenue[16] * statusProbability
    BoUpObject.wRev2037 = revenue[17] * statusProbability
    BoUpObject.wRev2038 = revenue[18] * statusProbability
    BoUpObject.wRev2039 = revenue[19] * statusProbability
    BoUpObject.wRev2040 = revenue[20] * statusProbability
    BoUpObject.wRev2041 = revenue[21] * statusProbability
    BoUpObject.wRev2042 = revenue[22] * statusProbability
    BoUpObject.wRev2043 = revenue[23] * statusProbability
    BoUpObject.wRev2044 = 0.0

    BoUpObject.fy_vol2020 = volumes_FY[0]
    BoUpObject.fy_vol2021 = volumes_FY[1]
    BoUpObject.fy_vol2022 = volumes_FY[2]
    BoUpObject.fy_vol2023 = volumes_FY[3]
    BoUpObject.fy_vol2024 = volumes_FY[4]
    BoUpObject.fy_vol2025 = volumes_FY[5]
    BoUpObject.fy_vol2026 = volumes_FY[6]
    BoUpObject.fy_vol2027 = volumes_FY[7]
    BoUpObject.fy_vol2028 = volumes_FY[8]
    BoUpObject.fy_vol2029 = volumes_FY[9]
    BoUpObject.fy_vol2030 = volumes_FY[10]
    BoUpObject.fy_vol2031 = volumes_FY[11]
    BoUpObject.fy_vol2032 = volumes_FY[12]
    BoUpObject.fy_vol2033 = volumes_FY[13]
    BoUpObject.fy_vol2034 = volumes_FY[14]
    BoUpObject.fy_vol2035 = volumes_FY[15]
    BoUpObject.fy_vol2036 = volumes_FY[16]
    BoUpObject.fy_vol2037 = volumes_FY[17]
    BoUpObject.fy_vol2038 = volumes_FY[18]
    BoUpObject.fy_vol2039 = volumes_FY[19]
    BoUpObject.fy_vol2040 = volumes_FY[20]
    BoUpObject.fy_vol2041 = volumes_FY[21]
    BoUpObject.fy_vol2042 = volumes_FY[22]
    BoUpObject.fy_vol2043 = volumes_FY[23]
    BoUpObject.fy_vol2044 = 0.0

    BoUpObject.fy_gm2020 = grossProfit_FY[0]
    BoUpObject.fy_gm2021 = grossProfit_FY[1]
    BoUpObject.fy_gm2022 = grossProfit_FY[2]
    BoUpObject.fy_gm2023 = grossProfit_FY[3]
    BoUpObject.fy_gm2024 = grossProfit_FY[4]
    BoUpObject.fy_gm2025 = grossProfit_FY[5]
    BoUpObject.fy_gm2026 = grossProfit_FY[6]
    BoUpObject.fy_gm2027 = grossProfit_FY[7]
    BoUpObject.fy_gm2028 = grossProfit_FY[8]
    BoUpObject.fy_gm2029 = grossProfit_FY[9]
    BoUpObject.fy_gm2030 = grossProfit_FY[10]
    BoUpObject.fy_gm2031 = grossProfit_FY[11]
    BoUpObject.fy_gm2032 = grossProfit_FY[12]
    BoUpObject.fy_gm2033 = grossProfit_FY[13]
    BoUpObject.fy_gm2034 = grossProfit_FY[14]
    BoUpObject.fy_gm2035 = grossProfit_FY[15]
    BoUpObject.fy_gm2036 = grossProfit_FY[16]
    BoUpObject.fy_gm2037 = grossProfit_FY[17]
    BoUpObject.fy_gm2038 = grossProfit_FY[18]
    BoUpObject.fy_gm2039 = grossProfit_FY[19]
    BoUpObject.fy_gm2040 = grossProfit_FY[20]
    BoUpObject.fy_gm2041 = grossProfit_FY[21]
    BoUpObject.fy_gm2042 = grossProfit_FY[22]
    BoUpObject.fy_gm2043 = grossProfit_FY[23]
    BoUpObject.fy_gm2044 = 0.0

    BoUpObject.fy_wVol2020 = float(volumes_FY[0]) * statusProbability
    BoUpObject.fy_wVol2021 = float(volumes_FY[1]) * statusProbability
    BoUpObject.fy_wVol2022 = float(volumes_FY[2]) * statusProbability
    BoUpObject.fy_wVol2023 = float(volumes_FY[3]) * statusProbability
    BoUpObject.fy_wVol2024 = float(volumes_FY[4]) * statusProbability
    BoUpObject.fy_wVol2025 = float(volumes_FY[5]) * statusProbability
    BoUpObject.fy_wVol2026 = float(volumes_FY[6]) * statusProbability
    BoUpObject.fy_wVol2027 = float(volumes_FY[7]) * statusProbability
    BoUpObject.fy_wVol2028 = float(volumes_FY[8]) * statusProbability
    BoUpObject.fy_wVol2029 = float(volumes_FY[9]) * statusProbability
    BoUpObject.fy_wVol2030 = float(volumes_FY[10]) * statusProbability
    BoUpObject.fy_wVol2031 = float(volumes_FY[11]) * statusProbability
    BoUpObject.fy_wVol2032 = float(volumes_FY[12]) * statusProbability
    BoUpObject.fy_wVol2033 = float(volumes_FY[13]) * statusProbability
    BoUpObject.fy_wVol2034 = float(volumes_FY[14]) * statusProbability
    BoUpObject.fy_wVol2035 = float(volumes_FY[15]) * statusProbability
    BoUpObject.fy_wVol2036 = float(volumes_FY[16]) * statusProbability
    BoUpObject.fy_wVol2037 = float(volumes_FY[17]) * statusProbability
    BoUpObject.fy_wVol2038 = float(volumes_FY[18]) * statusProbability
    BoUpObject.fy_wVol2039 = float(volumes_FY[19]) * statusProbability
    BoUpObject.fy_wVol2040 = float(volumes_FY[20]) * statusProbability
    BoUpObject.fy_wVol2041 = float(volumes_FY[21]) * statusProbability
    BoUpObject.fy_wVol2042 = float(volumes_FY[22]) * statusProbability
    BoUpObject.fy_wVol2043 = float(volumes_FY[23]) * statusProbability
    BoUpObject.fy_wVol2044 = 0.0

    BoUpObject.fy_wRev2020 = revenue_FY[0] * statusProbability
    BoUpObject.fy_wRev2021 = revenue_FY[1] * statusProbability
    BoUpObject.fy_wRev2022 = revenue_FY[2] * statusProbability
    BoUpObject.fy_wRev2023 = revenue_FY[3] * statusProbability
    BoUpObject.fy_wRev2024 = revenue_FY[4] * statusProbability
    BoUpObject.fy_wRev2025 = revenue_FY[5] * statusProbability
    BoUpObject.fy_wRev2026 = revenue_FY[6] * statusProbability
    BoUpObject.fy_wRev2027 = revenue_FY[7] * statusProbability
    BoUpObject.fy_wRev2028 = revenue_FY[8] * statusProbability
    BoUpObject.fy_wRev2029 = revenue_FY[9] * statusProbability
    BoUpObject.fy_wRev2030 = revenue_FY[10] * statusProbability
    BoUpObject.fy_wRev2031 = revenue_FY[11] * statusProbability
    BoUpObject.fy_wRev2032 = revenue_FY[12] * statusProbability
    BoUpObject.fy_wRev2033 = revenue_FY[13] * statusProbability
    BoUpObject.fy_wRev2034 = revenue_FY[14] * statusProbability
    BoUpObject.fy_wRev2035 = revenue_FY[15] * statusProbability
    BoUpObject.fy_wRev2036 = revenue_FY[16] * statusProbability
    BoUpObject.fy_wRev2037 = revenue_FY[17] * statusProbability
    BoUpObject.fy_wRev2038 = revenue_FY[18] * statusProbability
    BoUpObject.fy_wRev2039 = revenue_FY[19] * statusProbability
    BoUpObject.fy_wRev2040 = revenue_FY[20] * statusProbability
    BoUpObject.fy_wRev2041 = revenue_FY[21] * statusProbability
    BoUpObject.fy_wRev2042 = revenue_FY[22] * statusProbability
    BoUpObject.fy_wRev2043 = revenue_FY[23] * statusProbability
    BoUpObject.fy_wRev2044 = 0.0

    BoUpObject.save()
    print(
        created, "BoUp object", BoUpObject, "time of creation", time.time() - start_time
    )

    # get data from boup

    total_df = restructure_single(BoUpObject.id)

    id_list = total_df["id"].tolist()
    Reviewed_list = total_df["Reviewed"].tolist()
    reviewDate_list = total_df["reviewDate"].tolist()
    ID_APP_id_list = total_df["ID_APP_id"].tolist()
    applicationLine_list = total_df["applicationLine"].tolist()
    productMarketer_id_list = total_df["productMarketer_id"].tolist()
    hfg_list = total_df["hfg"].tolist()
    ppos_list = total_df["ppos"].tolist()
    spNumber_list = total_df["spNumber"].tolist()
    applicationMain_id_list = total_df["applicationMain_id"].tolist()
    applicationDetail_id_list = total_df["applicationDetail_id"].tolist()
    rfp_id_list = total_df["rfp_id"].tolist()
    salesName_id_list = total_df["salesName_id"].tolist()
    priceSource_list = total_df["priceSource"].tolist()
    familyPriceApplicable_list = total_df["familyPriceApplicable"].tolist()
    familyPriceDetails_list = total_df["familyPriceDetails"].tolist()
    priceType_list = total_df["priceType"].tolist()
    currency_list = total_df["currency"].tolist()
    fxRate_list = total_df["fxRate"].tolist()
    comment_list = total_df["comment"].tolist()
    region_list = total_df["region"].tolist()
    projectName_list = total_df["projectName"].tolist()
    mainCustomer_id_list = total_df["mainCustomer_id"].tolist()
    endCustomer_id_list = total_df["endCustomer_id"].tolist()
    distributor_list = total_df["distributor"].tolist()
    tier1_list = total_df["tier1"].tolist()
    oem_id_list = total_df["oem_id"].tolist()
    ems_list = total_df["ems"].tolist()
    vpaCustomer_list = total_df["vpaCustomer"].tolist()
    dragonId_list = total_df["dragonId"].tolist()
    salesContact_list = total_df["salesContact"].tolist()
    probability_list = total_df["probability"].tolist()
    statusProbability_list = total_df["statusProbability"].tolist()
    sop_list = total_df["sop"].tolist()
    availablePGS_list = total_df["availablePGS"].tolist()
    modifiedBy_id_list = total_df["modifiedBy_id"].tolist()
    modifiedDate_list = total_df["modifiedDate"].tolist()
    creationDate_list = total_df["creationDate"].tolist()
    timeBottomUp_list = total_df["timeBottomUp"].tolist()
    basicType_list = total_df["basicType"].tolist()
    package_list = total_df["package"].tolist()
    series_list = total_df["series"].tolist()
    gen_list = total_df["gen"].tolist()
    seriesLong_list = total_df["seriesLong"].tolist()
    genDetail_list = total_df["genDetail"].tolist()
    gmLifeTime_list = total_df["gmLifeTime"].tolist()
    revEurLifeTime_list = total_df["revEurLifeTime"].tolist()
    volLifeTime_list = total_df["volLifeTime"].tolist()
    volWeightedLifeTime_list = total_df["volWeightedLifeTime"].tolist()
    year_list = total_df["year"].tolist()
    vol_list = total_df["vol"].tolist()
    volCustomer_list = total_df["volCustomer"].tolist()
    price_list = total_df["price"].tolist()
    vhk_list = total_df["vhk"].tolist()
    gm_list = total_df["gm"].tolist()
    wVol_list = total_df["wVol"].tolist()
    wRev_list = total_df["wRev"].tolist()
    fy_vol_list = total_df["fy_vol"].tolist()
    fy_gm_list = total_df["fy_gm"].tolist()
    fy_wVol_list = total_df["fy_wVol"].tolist()
    fy_wRev_list = total_df["fy_wRev"].tolist()

    df_list = []
    df_list.append(id_list)  # 0
    df_list.append(Reviewed_list)  # 1
    df_list.append(reviewDate_list)  # 2
    df_list.append(ID_APP_id_list)  # 3
    df_list.append(applicationLine_list)  # 4
    df_list.append(productMarketer_id_list)  # 5
    df_list.append(hfg_list)  # 6
    df_list.append(ppos_list)  # 7
    df_list.append(spNumber_list)  # 8
    df_list.append(applicationMain_id_list)  # 9
    df_list.append(applicationDetail_id_list)  # 10
    df_list.append(rfp_id_list)  # 11
    df_list.append(salesName_id_list)  # 12
    df_list.append(priceSource_list)  # 13
    df_list.append(familyPriceApplicable_list)  # 14
    df_list.append(familyPriceDetails_list)  # 15
    df_list.append(priceType_list)  # 16
    df_list.append(currency_list)  # 17
    df_list.append(fxRate_list)  # 18
    df_list.append(comment_list)  # 19
    df_list.append(region_list)  # 20
    df_list.append(projectName_list)  # 21
    df_list.append(mainCustomer_id_list)  # 22
    df_list.append(endCustomer_id_list)  # 23
    df_list.append(distributor_list)  # 24
    df_list.append(tier1_list)  # 25
    df_list.append(oem_id_list)  # 26
    df_list.append(ems_list)  # 27
    df_list.append(vpaCustomer_list)  # 28
    df_list.append(dragonId_list)  # 29
    df_list.append(salesContact_list)  # 30
    df_list.append(probability_list)  # 31
    df_list.append(statusProbability_list)  # 32
    df_list.append(sop_list)  # 33
    df_list.append(availablePGS_list)  # 34
    df_list.append(modifiedBy_id_list)  # 35
    df_list.append(modifiedDate_list)  # 36
    df_list.append(creationDate_list)  # 37
    df_list.append(timeBottomUp_list)  # 38
    df_list.append(basicType_list)  # 39
    df_list.append(package_list)  # 40
    df_list.append(series_list)  # 41
    df_list.append(gen_list)  # 42
    df_list.append(seriesLong_list)  # 43
    df_list.append(genDetail_list)  # 44
    df_list.append(gmLifeTime_list)  # 45
    df_list.append(revEurLifeTime_list)  # 46
    df_list.append(volLifeTime_list)  # 47
    df_list.append(volWeightedLifeTime_list)  # 48
    df_list.append(year_list)  # 49
    df_list.append(vol_list)  # 50
    df_list.append(volCustomer_list)  # 51
    df_list.append(price_list)  # 52
    df_list.append(vhk_list)  # 53
    df_list.append(gm_list)  # 54
    df_list.append(wVol_list)  # 55
    df_list.append(wRev_list)  # 56
    df_list.append(fy_vol_list)  # 57
    df_list.append(fy_gm_list)  # 58
    df_list.append(fy_wVol_list)  # 59
    df_list.append(fy_wRev_list)  # 60

    # this here is to get the whole BoUp table set and create graphics based on the SQL query
    """
    dfAllBoUp = pd.DataFrame(list(BoUp.objects.all().values()))
    dfQuery = restructure_whole(dfAllBoUp)
    
    print("quick testing 1")
    print(BoUpCy(dfAllBoUp))
    print("second one")
    print(BoUpFy(dfAllBoUp))
    
    print("quick testing 2")
    print(checkBoUpEntryGapsPrice(dfQuery))
    print("second one")
    print(checkBoUpEntryGapsVol(dfQuery))
    """

    """
    #sqlRes = sql_group_series_endcustomer(dfQuery, 2020, 2030) #logic to determine what should be the first year and what should be the last year
    sqlRes = sql_group_family_gen_series_endcustomer_year(dfQuery)

    #redesign sqlresult to use it in chart.js
    sqlRes_list = []
    for col in sqlRes[0].columns:
        sqlRes_list.append(sqlRes[0][col].tolist() )
    print(projectId)
    print("here is the error dic table", errorDicTableLvl(projectId))
    print("here is the error dic project", errorDicProjectLvl(projectId))
   
    print("sql res")
    print(sqlRes) 
    """
    # plots
    plt.switch_backend("agg")

    # xy graph with matplotlib
    # plt.figure()
    # plt.scatter(years, revenue, label = "Revenue")
    # plt.scatter(years, grossMargin, label = "Gross Margin")
    # plt.plot(years, revenue)
    # plt.plot(years, grossMargin)

    # plt.title('Revenue and Gross Margin ')
    # plt.xlabel("Year")
    # plt.ylabel("EUR")
    # plt.legend()

    # xy graph with seaborn
    sns.set_style("darkgrid")

    print("checking out", total_df["price"])
    rev_margin = sns.lineplot(
        total_df["year"],
        total_df["price"] * total_df["vol"],
        label="Revenue",
        marker="o",
    )
    sns.lineplot(total_df["year"], total_df["gm"], label="Cost Margin", marker="o")
    rev_margin.set(title="Revenue and Cost Margin", xlabel="Year", ylabel="EUR")

    revenueMarginPlot = io.BytesIO()
    plt.savefig(revenueMarginPlot, format="jpg")
    revenueMarginPlot.seek(0)
    revenueMarginPlotBase64 = base64.b64encode(revenueMarginPlot.read())
    plt.clf()

    encodedrevenueMarginPlotBase64 = str(revenueMarginPlotBase64)
    encodedrevenueMarginPlotBase64 = encodedrevenueMarginPlotBase64[2:]
    encodedrevenueMarginPlotBase64 = encodedrevenueMarginPlotBase64[:-1]

    print("first done")
    rev_margin_FY = sns.lineplot(
        total_df["year"], revenue_FY, label="Revenue", marker="o"
    )
    sns.lineplot(total_df["year"], total_df["fy_gm"], label="Cost Margin", marker="o")
    rev_margin_FY.set(title="Revenue and Cost Margin FY", xlabel="Year", ylabel="EUR")

    revenueMarginPlot_FY = io.BytesIO()
    plt.savefig(revenueMarginPlot_FY, format="jpg")
    revenueMarginPlot_FY.seek(0)
    revenueMarginPlotBase64_FY = base64.b64encode(revenueMarginPlot_FY.read())
    plt.clf()

    encodedrevenueMarginPlotBase64_FY = str(revenueMarginPlotBase64_FY)
    encodedrevenueMarginPlotBase64_FY = encodedrevenueMarginPlotBase64_FY[2:]
    encodedrevenueMarginPlotBase64_FY = encodedrevenueMarginPlotBase64_FY[:-1]

    print("second done")
    monthPlot = sns.lineplot(all_months, volumesMonth, label="Volume", marker="o")
    monthPlot.set(title="Volume by month", xlabel="Month", ylabel="EUR")

    monthVolumePlot = io.BytesIO()
    plt.savefig(monthVolumePlot, format="jpg")
    monthVolumePlot.seek(0)
    monthVolumePlotBase64 = base64.b64encode(monthVolumePlot.read())
    plt.clf()

    monthVolumePlotBase64 = str(monthVolumePlotBase64)
    monthVolumePlotBase64 = monthVolumePlotBase64[2:]
    monthVolumePlotBase64 = monthVolumePlotBase64[:-1]
    print("third done")

    fig, ax = plt.subplots()
    ax2 = ax.twinx()
    volPrice = sns.lineplot(x=total_df["year"], y=total_df["vol"], ax=ax, marker="o")
    sns.lineplot(
        total_df["year"], total_df["price"], ax=ax2, color="orange", marker="o"
    )
    ax.legend(handles=[a.lines[0] for a in [ax, ax2]], labels=["Prices", "Volumes"])
    ax.set_ylabel("Pieces")
    ax2.set_ylabel("EUR")
    volPrice.set(title="Volume and Price")

    volumePricePlot = io.BytesIO()
    plt.savefig(volumePricePlot, format="jpg")
    volumePricePlot.seek(0)
    volumePricePlotBase64 = base64.b64encode(volumePricePlot.read())
    plt.clf()

    encodedvolumePricePlotBase64 = str(volumePricePlotBase64)
    encodedvolumePricePlotBase64 = encodedvolumePricePlotBase64[2:]
    encodedvolumePricePlotBase64 = encodedvolumePricePlotBase64[:-1]
    print("forth done")
    """
    fig= plt.figure()
    ax = fig.add_subplot()
    a = 1
    a_slider_ax  = fig.add_axes([0.6, 0.75, 0.25, 0.03])
    a_slider = mw.Slider(a_slider_ax, 'Price Multiplikator', 0, 5, valinit = a)

    def sliders_on_change(val):

        p.set_ydata([x*a_slider.val for x in prices])

        fig.canvas.draw_idle()

    a_slider.on_changed(sliders_on_change)
    p,=ax.plot(years, prices, 'r-')
    

    SliderPlot = io.BytesIO()
    plt.savefig(SliderPlot, format='jpg')
    SliderPlot.seek(0)
    SliderPlotBase64 = base64.b64encode(SliderPlot.read())
    plt.clf()


    encodedSliderPlotBase64 = str(SliderPlotBase64)
    encodedSliderPlotBase64 = encodedSliderPlotBase64[2:]
    encodedSliderPlotBase64 = encodedSliderPlotBase64[:-1]
    """

    df = pd.DataFrame(
        {
            "YEAR": total_df["year"],
            "region": ["EU" for x in total_df["year"]],
            "grossMargin": [float(x) for x in total_df["gm"]],
        }
    )
    df.set_index("YEAR", inplace=True)

    # group data by product and display sales as line chart
    df.groupby("region")["grossMargin"].plot(legend=True)

    regionPlot = io.BytesIO()
    plt.savefig(regionPlot, format="jpg")
    regionPlot.seek(0)
    regionPlotBase64 = base64.b64encode(regionPlot.read())
    plt.clf()

    encodedregionPlotBase64 = str(regionPlotBase64)
    encodedregionPlotBase64 = encodedregionPlotBase64[2:]
    encodedregionPlotBase64 = encodedregionPlotBase64[:-1]

    print("fifth done")

    plt.close()

    """
        Conflict checks:
    •	Display what you have created
    o	Graph of volume
    o	Expected revenue
    o	Price curve over time
    o	Expected gross margin
    •	For the next project: if we do price db we can show you here how it deviates from other customers
    •	For this project ass added value: put here oem and tier 1 information. Existing volume at this t1…. How much of your project represents for this tier 1 … are you creating a lot of business? Or evtl to be combined with pricing db
    •	Show if family prices apply

    ## check if matches protifability vorgaben, warnings or blocks
    ## automail to PM lead upon completion
    
    Evtl: competing order from tier1 or OEM… based on the data for this OEM you are competing at OEM level with this order and compare here the prices….

    """

    # save draft & continue later

    # save project

    project = Project.objects.get(id=projectId)
    reportForm = ReportForm()

    return render(
        request,
        "productMarketing/entryBase.html",
        {
            "step": 4,
            "overviewForm": reportForm,
            "revenueMarginPlotBase64": encodedrevenueMarginPlotBase64,
            "volumePricePlotBase64": encodedvolumePricePlotBase64,
            "RegionPlotBase64": encodedregionPlotBase64,
            "MonthVolumeBase64": monthVolumePlotBase64,
            "FYrevenueBase64": encodedrevenueMarginPlotBase64_FY,
            "projectId": projectId,
            "year_gm": df_list,
        },
    )


# for editing
def projectEdit(request, case, projectId):
    # case 0: key facts, 1: volume entry, 2: price entry, 3: review

    enterProjectForm = EnterProjectForm()
    applicationMainForm = ApplicationMainForm()

    print("########### project edit screen, project pk", projectId)

    if request.method == "POST":
        print("post")

    if case == 0:

        # testView =
        # print("returning testview", testView)

        if request.method == "POST":
            return editCase0post(request, projectId)

        return editCase0(request, projectId)

    else:

        years = [
            2099,
            2021,
            2022,
            2023,
            2024,
            2025,
            2026,
            2027,
            2028,
            2029,
            2030,
            2031,
            2032,
            2034,
            2035,
            2036,
            2037,
            2038,
            2039,
            2040,
            2041,
            2042,
            2043,
            2044,
            2045,
        ]
        volumes = []
        customerVolumes = []
        prices = []
        project = Project.objects.get(id=projectId)

        for year in years:

            try:
                object = ProjectVolumePrices.objects.get(
                    project=project, calenderYear=year
                )
                volumes.append(object.quantity)
                customerVolumes.append(object.quantityCustomerEstimation)
            except:
                volumes.append(0)
                customerVolumes.append(0)

        print("volumes", volumes)
        return render(
            request,
            "productMarketing/projectEdit/projectEdit.html",
            {
                "projectId": projectId,
                "enterProjectForm": enterProjectForm,
                "applicationMainForm": applicationMainForm,
                "step": case,
                "volumes": volumes,
                "years": years,
                "customerVolumes": customerVolumes,
            },
        )


# project management
def projectManagement(request, case):
    # case 0: key facts, 1: volume entry, 2: price entry, 3: review

    if case == 0:

        return render(
            request,
            "productMarketing/projectManagement/projectManagement.html",
            {
                "segment": "projectManagement",
                "step": case,
            },
        )

    else:

        return render(
            request,
            "productMarketing/projectManagement/projectManagement.html",
            {
                "segment": "projectManagement",
                "step": case,
            },
        )
