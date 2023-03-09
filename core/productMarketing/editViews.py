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
from .models import *
from django_tables2 import SingleTableView

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

### email
from django.core.mail import send_mail

# from core.settings import BASE_DIR, EMAIL_HOST_USER
### email
from django.core import serializers
from django.utils import timezone
from django.template import RequestContext
from django.db import connection
from datetime import date, timedelta
import io
import base64
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
import seaborn as sns
import matplotlib.widgets as mw
from enum import Enum
from .forms import *


def editCase0(request, projectId: int):

    # filter conditions. To Do: try catch conditions to handle misuse of URL in browser...
    mainCustomers = MainCustomers.objects.all()
    finalCustomers = FinalCustomers.objects.all()
    oems = OEM.objects.all()
    project = Project.objects.get(id=projectId)

    print(
        "final customers type",
        type(finalCustomers),
        finalCustomers[0],
        "type2",
        type(finalCustomers[0]),
    )

    ### distinct only supported in PostgreSQL
    productFamiliesArray = []  # ["dummy 12346778"]

    productFamilies = dict()  # ["dummy 12346778"]
    allProducts = Product.objects.all()

    for product in allProducts:
        # print("family description", product.familydescription)
        if product.familyfull not in productFamilies:

            #        if productFamilies.contains(product.familydescription):
            productFamiliesArray.append(product.familyfull)
            productFamilies[product.familyfull] = product.familydescription

    ##Product.objects.all().distinct('familydescription')  # ["asd1", "asd2", "asd3"]#ProductFamily.objects.all()

    print("product families type", type(productFamilies), "content", productFamilies)
    salesNames = SalesName.objects.all()
    enterMainCustomerError = False
    enterFinalCustomerError = False
    salesNameError = False
    appMainError = False
    appDetailError = False

    ##### prefill s
    #   enter project form reminder:      exclude = ('user', 'applicationMain', 'applicationDetail', 'product', 'mainCustomer', 'endCustomer',)
    enterProjectForm = EnterProjectForm(
        initial={
            "applicationLine": project.applicationLine,
            "productMarketer": project.productMarketer,
            "spNumber": project.spNumber,
            "projectName": project.projectName,
            "projectDescription": project.projectName,
            "applicationMain": project.applicationMain,
            "applicationDetail": project.applicationDetail,
            "estimatedSop": project.estimatedSop,
            "status": project.status,
            "region": project.region,
            "secondRegion": project.secondRegion,
            "dcChannel": project.dcChannel,
            "customerMain": project.mainCustomer,
            "endCustomer": project.endCustomer,
            "oem": project.oem,
            "salesName": project.salesName,
            "salesContact": project.salesContact,
            "comment": project.comment,
            "projectName": project.projectName,
            "projectDescription": project.projectDescription,
            "priceValidUntil": project.priceValidUntil,
            "distributor": project.distributor,
            "ems": project.ems,
            "tier1": project.tier1,
            "vpaCustomer": project.vpaCustomer,
        }
    )

    salesName = project.salesName
    mainCustomer = project.mainCustomer
    selectedMainCustomer = mainCustomer
    finalCustomer = project.endCustomer
    appMainObj = project.applicationMain
    appDetailObj = project.applicationDetail
    selectedFinalCustomer = finalCustomer
    applicationLine = project.applicationLine
    oem = project.oem
    notification = ""
    selectedSalesName = project.salesName
    productSeries = project.salesName.rfp.series

    applicationMainForm = ApplicationMainForm(
        initial={
            "applicationMain": appMainObj,
            "applicationDetail": appDetailObj,
        }
    )

    distiTierOneEMSList = mainCustomers

    emss = distiTierOneEMSList
    distributors = distiTierOneEMSList
    tierOnes = distiTierOneEMSList

    selectedOem = project.oem
    selectedDistributor = project.distributor
    selectedEms = project.ems
    selectedTierOne = project.tier1
    vpaCustomer = bool(project.vpaCustomer)

    print("vpa customer", type(vpaCustomer), "value", vpaCustomer)
    return render(
        request,
        "productMarketing/projectEdit/projectEdit.html",
        {
            "projectId": projectId,
            "enterProjectForm": enterProjectForm,
            "notification": notification,
            "mainCustomers": mainCustomers,
            "finalCustomers": finalCustomers,
            "oems": oems,
            "applicationMainForm": applicationMainForm,
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
            "step": 0,
            "emss": emss,
            "tierOnes": tierOnes,
            "distributors": distributors,
            "selectedOem": selectedOem,
            "selectedDistributor": selectedDistributor,
            "selectedEms": selectedEms,
            "selectedTierOne": selectedTierOne,
            "vpaCustomer": vpaCustomer,
            "selectedSalesName": selectedSalesName,
        },
    )

    """
    else:

        ### for initial dropdown file in, will be replaced dynamically by htmx
        #productSeries = ProductSeries.objects.all()
        return render(request, "productMarketing/projectEdit/projectEdit.html", {'enterProjectForm': enterProjectForm, 'mainCustomers': mainCustomers, 'finalCustomers': finalCustomers, 'oems': oems, 'applicationMainForm': ApplicationMainForm(request.POST), 'productFamilies': productFamilies, 'salesNames': salesNames, "salesNameError": salesNameError, "enterMainCustomerError": enterMainCustomerError, "enterFinalCustomerError": enterFinalCustomerError, "appMainError": appMainError, "appDetailError": appDetailError, "step": 0,})
    """


def editCase0post(request, projectId: int):
    enterMainCustomerError = False
    enterFinalCustomerError = False
    salesNameError = False
    appMainError = False
    appDetailError = False
    oemNameError = False

    productSeriesArray = []
    productSeries = dict()
    products = Product.objects.all()
    for product in products:
        if product.series not in productSeriesArray:
            productSeriesArray.append(product.series)
            productSeries[product.series] = product.seriesDescription

    productSeries = sorted(productSeries.items())

    applicationMains = ApplicationMain.objects.all()
    applicationDetails = ApplicationDetail.objects.all()

    mainCustomers = MainCustomers.objects.all()
    finalCustomers = FinalCustomers.objects.all()
    oems = OEM.objects.all()
    project = Project.objects.get(id=projectId)
    valid = project.valid

    print(
        "final customers type",
        type(finalCustomers),
        finalCustomers[0],
        "type2",
        type(finalCustomers[0]),
    )

    ### distinct only supported in PostgreSQL
    productFamiliesArray = []  # ["dummy 12346778"]

    productFamilies = dict()  # ["dummy 12346778"]
    allProducts = Product.objects.all()

    for product in allProducts:
        if product.familyfull not in productFamilies:
            productFamiliesArray.append(product.familyfull)
            productFamilies[product.familyfull] = product.familydescription

    salesNames = SalesName.objects.all()
    selectedSalesName = project.salesName
    projectForm = EnterProjectForm(request.POST)
    # applicationMain = ApplicationMainForm(request.POST)

    salesName = None
    mainCustomer = None
    finalCustomer = None
    appMainObj = None
    appDetailObj = None
    # selectedSalesName = None
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

    ### get sales name
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

    print(
        "enter sales name check",
        salesNameFreeTextInput,
        "type",
        type(salesNameFreeTextInput),
        "int",
        salesNameInt,
        "type",
        type(salesNameInt),
    )

    if not salesNameInt:
        print("not salesnameint")

    # SAA-TC497XE-24HO400CC AA
    ## first check if something was entered
    ## try to get sales name from drop down. if not, try to use the free text input.

    modifySalesName: bool = False

    if (not request.POST.get("salesNameFreeText")) & (not salesNameInt):
        modifySalesName = False
        print("modify sales name is false")
    else:
        print("modify sales name is true")
        modifySalesName = True

    if modifySalesName == True:
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
                print("#### fatal error sales name input 1")

        else:
            try:

                salesName = SalesName.objects.get(salesName=salesNameFreeTextInput)
                print("sales name object from free text", salesName)
                salesNames = [salesName]
                selectedSalesName = salesName

            except:
                salesNameError = True

    # tbd if to use here get or create: infineon must decide what should be possible (eg if to allow to create new customers here or use fixed values)
    ## get -> trae una instancia de la tabla. filter: trae un queryset... que es como un array de instancias de la tabla.
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

    except:
        enterFinalCustomerError = True
        print("no final customer detected")

    print("appMainPk", appMainPk, "appDetailPk", appDetailPk)

    try:
        appMainObj = ApplicationMain.objects.get(pk=appMainPk)
    except:
        appMainError = True

    ## oem is optional
    if not selectedOemInput:
        # is false is correct here, OEM could be empty
        oemNameError = False
        print("if not selected oem")
    else:
        try:
            oemObj = OEM.objects.get(oemName=selectedOemInput)
        except:
            oemNameError = True

    try:
        appDetailObj = ApplicationDetail.objects.get(pk=appDetailPk)
        print("appDetailObj", appDetailObj)
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
        print("existing salesname", project.salesName, "new one", salesName)
        print(
            "duplicate check",
            (project.salesName != salesName),
            (project.mainCustomer != mainCustomer),
            (project.endCustomer != finalCustomer),
        )
        #### check if sales name, main customer, end customer changed. if yes, check if there is already a proejct existing with the target combination of data.
        if (
            ((project.salesName != salesName) & (modifySalesName == True))
            | (project.mainCustomer != mainCustomer)
            | (project.endCustomer != finalCustomer)
        ):
            if (
                Project.objects.filter(
                    salesName=salesName,
                    valid=valid,
                    mainCustomer=mainCustomer,
                    endCustomer=finalCustomer,
                ).count()
                > 0
            ):
                existingProjectPk = 0

                existingProject = Project.objects.filter(
                    salesName=salesName,
                    valid=valid,
                    mainCustomer=mainCustomer,
                    endCustomer=finalCustomer,
                ).first()

                print("project already exists")
                notification = (
                    "Project already exists, see project #"
                    + str(existingProject.pk)
                    + ". Please check the entered data or consider modifying / deleting an existing project first."
                )
                status = 0
                return render(
                    request,
                    "productMarketing/projectEdit/projectEdit.html",
                    {
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
                        "step": 0,
                    },
                )

        project_form_result = projectForm.save(commit=False)
        # print(project_form_result)
        project.user = request.user
        # profile = Profile.objects.get(user = request.user)
        # print("getting practice!")
        # practice = Practice.objects.get(profile = profile)
        # product = project_form_result.product
        applicationLine = project_form_result.applicationLine
        oem = project_form_result.oem
        valid = True
        ### the business line is derived from practice field
        # businessLine = practice
        # project.practice = practice

        ##### plausibility checks
        ### combination of main and final customer exists in cube db
        ### SOP in future

        ### same bl, application line, valid, same rfp already exist!
        print("resulting salesname", salesName, "selected salesname", selectedSalesName)
        ### only if the sales name was modyfied
        if modifySalesName == True:
            project.salesName = salesName
        project.mainCustomer = mainCustomer
        project.endCustomer = finalCustomer
        print("time now", datetime.datetime.now())
        project.modifiedDate = datetime.datetime.now()

        project.applicationMain = appMainObj
        project.applicationDetail = appDetailObj
        print("selected tier one", selectedTierOne, "oem error", oemNameError)

        if not selectedOemInput:
            print("skipping oem")
        else:
            if oemNameError == False:
                project.oem = oemObj

        project.distributor = selectedDistributor
        project.tier1 = selectedTierOne
        project.ems = selectedEms
        project.vpaCustomer = vpaCustomer

        applicationMainForm = ApplicationMainForm(
            initial={
                "applicationMain": appMainObj,
                "applicationDetail": appDetailObj,
            }
        )
        print("final apps 2", appMainObj, appDetailObj)

        project.save()
        print("project", project)
        projectId = project.id
        notification = "Project data stored."
        print(notification)
        status = 1

        # url = '/productMarketing/boupEntry1/' + str(projectId) #+ '/' + str(status)
        # return HttpResponseRedirect(url)
        return render(
            request,
            "productMarketing/projectEdit/projectEdit.html",
            {
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
                "step": 0,
                "applicationMainForm": applicationMainForm,
            },
        )

    else:
        print("resulting salesname", salesName, "selected salesname", selectedSalesName)
        print("final apps 1", appMainObj, appDetailObj)
        applicationMainForm = ApplicationMainForm(
            initial={
                "applicationMain": appMainObj,
                "applicationDetail": appDetailObj,
            }
        )

        print(
            "error on form processing", "vpa customer", vpaCustomer, type(vpaCustomer)
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
        # productSeries = ProductSeries.objects.all()

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
            "productMarketing/projectEdit/projectEdit.html",
            {
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
                "step": 0,
                "applicationMainForm": applicationMainForm,
            },
        )
