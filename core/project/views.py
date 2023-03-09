from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, ListView, DetailView
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from .models import Project, ProjectError
from .forms import (
    ProjectCreateForm,
    VolumeForm,
    VolumeMonthForm,
    PricingForm,
    VolumeAutomaticForm,
    ReportForm,
)
from productMarketingDwh.models import *
from productMarketing.interpolator import *
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import F
from .models import (
    Project,
    Product,
    SalesName,
    ProductPackage,
    ProductSeries,
    ProductFamily,
    PriceStatus,
)
from django.utils import timezone
from datetime import datetime
from rest_framework import status
from django.db import connection

from django.core.exceptions import ValidationError
from .helperFunctions import getProjectOverview, HighLevelProjectProblems
from productMarketing.BoUpExport import *

import time
from productMarketing.queryJobs.SQL_query import *

from django_filters.views import FilterView
from ajax_datatable.views import AjaxDatatableView
from .filters import ProjectFilter, ProjectErrorFilter
import numpy as np
from .bottomUpPersistor import bottomUpPersistor
from django.http import HttpResponseRedirect
from django.contrib import messages
from currencies.utils import (
    calculate,
    convert,
    get_active_currencies_qs,
    get_currency_code,
)
from django.db.models import Max


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def rawSqlPerformer(sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)
        row = dictfetchall(cursor)
    return row


def BulkProcessing(request):
    from .bulkProcessing import entryPointValidator

    entryPointValidator("PSE1", None, 0)


def EditProjectKeyFacts(request, projectId):
    success_url = reverse_lazy("create_project_view")
    request.session["project_id"] = projectId
    request.session["editMode"] = True
    request.session["keyFactsEdit"] = True

    return redirect(success_url)


def CreateProjectEntryPoint(request):
    success_url = reverse_lazy("create_project_view")
    request.session["project_id"] = 0
    request.session["editMode"] = False
    request.session["keyFactsEdit"] = False

    return redirect(success_url)


class CreateProjectView(LoginRequiredMixin, View):
    template_name = "project/project_create_view/step1.html"
    form_class = ProjectCreateForm
    success_url = reverse_lazy("create_volume_view")
    editMode = False

    def get(self, request, *args, **kwargs):

        context = {}
        if request.session["keyFactsEdit"]:
            """
            print(
                "editing!",
                request.session["project_id"],
                request.session["keyFactsEdit"],
            )
            """

            projectId = request.session["project_id"]
            project = Project.objects.get(id=projectId)

            # check if editing
            if (project.is_viewing == True) & (project.is_viewing_user != request.user):
                self.success_url = reverse_lazy(
                    "project_deepdive",
                    kwargs={"projectId": request.session["project_id"]},
                )
                messages.error(
                    request, "The project is locked for editing by another user."
                )

                return redirect(self.success_url)

            context = {
                "form": self.form_class(instance=project, editMode=True),
                "editMode": True,
                "project": project,
                "projectId": projectId,
            }
            request.session["keyFactsEdit"] = False
            # print("output session project id", request.session["project_id"])

            return render(request, self.template_name, context)

        else:
            # print("no editing!")
            context = {"form": self.form_class(), "editMode": False}

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        print("%%% POST")
        form = self.form_class(request.POST, request=request)
        # if submitted form is valid
        series = form["product_series"]
        projectId = None
        editMode = False
        projectObj = None

        if request.session["editMode"]:
            # print("input session project id", request.session["project_id"])
            self.success_url = reverse_lazy(
                "project_deepdive", kwargs={"projectId": request.session["project_id"]}
            )
            projectId = request.session["project_id"]
            editMode = True
            projectObj = Project.objects.get(id=request.session["project_id"])
            form = self.form_class(
                request.POST, request=request, instance=projectObj)

        # print("series", request.POST.get("product_series"))
        # print("post, salesname", request.POST.get("sales_name"))
        salesNameInput = request.POST.get("sales_name")
        salesNameObj = None

        # if it's an int, then it was selected without filtering by series, package, etc...
        try:
            salesNameInt = int(salesNameInput)
            salesNameObj = SalesName.objects.get(id=salesNameInt)

        except:
            salesNameObj = SalesName.objects.get(name=salesNameInput)

        # remember old state
        _mutable = request.POST._mutable
        # set to mutable
        request.POST._mutable = True
        request.POST["sales_name"] = salesNameObj.pk
        # print("salesnameobj", salesNameObj, "pk", salesNameObj.pk)
        # print("salesname output request", request.POST["sales_name"])

        # set mutable flag back
        request.POST._mutable = _mutable

        """
        Problem encountered during testing. modifying an element of the unique constraint key (End Customer, Main Customer, App Main, App Detail, Sales Name, Dummy, Draft, Product Marketer)
        will lead to Django creating a new project ID, keeping the old one and the new one losing all information about prices, volumes, etc...
        So here we will discern between edit mode and create mode. 
        """
        if (form.is_valid()) & (editMode == True):
            # retrieve the current project object

            oldAppMain = projectObj.applicationMain
            oldAppDetail = projectObj.applicationDetail
            oldSalesName = projectObj.sales_name
            oldMainCustomer = projectObj.mainCustomer
            oldEndCustomer = projectObj.finalCustomer
            oldDummy = projectObj.dummy
            oldDraft = projectObj.draft
            oldProductMarketer = projectObj.productMarketer
            newAppMain = form.cleaned_data.get("applicationMain")
            newAppDetail = form.cleaned_data.get("applicationDetail")
            newSalesName = form.cleaned_data.get("sales_name")
            newMainCustomer = form.cleaned_data.get("mainCustomer")
            newEndCustomer = form.cleaned_data.get("finalCustomer")
            newDummy = form.cleaned_data.get("dummy")
            # newDraft = form.cleaned_data.get("draft") # draft is not available in form!
            newProductMarketer = form.cleaned_data.get("productMarketer")
            """
            print("old vs new", oldAppMain, newAppMain, oldAppDetail, newAppDetail, "sn",
                  oldSalesName, newSalesName, "dummy", oldDummy, newDummy, type(oldDummy), type(newDummy), "draft", oldDraft, "mc/ec", oldMainCustomer, newMainCustomer,  oldEndCustomer, newEndCustomer)
            print((oldAppMain != newAppMain), (oldAppDetail != newAppDetail), (oldSalesName != newSalesName), (oldMainCustomer !=
                  newMainCustomer), (oldEndCustomer != newEndCustomer), (oldDummy != newDummy), (oldProductMarketer != newProductMarketer))
            """
            # check if these values have changed
            if (
                (oldAppMain != newAppMain)
                | (oldAppDetail != newAppDetail)
                | (oldSalesName != newSalesName)
                | (oldMainCustomer != newMainCustomer)
                | (oldEndCustomer != newEndCustomer)
                | (oldDummy != newDummy)
                | (oldProductMarketer != newProductMarketer)
            ):
                # print("change in unique constraint values!")
                # check for unique constraint violation

                randomNumber = random.randrange(0, 99999)
                syntheticProjectNameInput = (
                    str(newDummy)
                    + "-"
                    + str(project.applicationLine).replace(" ", "_")
                    + "-"
                    + str(project.productMarketer).replace(" ", "_")
                    + "-"
                    + str(newAppMain).replace(" ", "_")
                    + "-"
                    + str(project.applicationDetail).replace(" ", "_")
                    + "-"
                    + str(project.mainCustomer).replace(" ", "_")
                    + "-"
                    + str(project.finalCustomer).replace(" ", "_")
                    + "-"
                    + str(newSalesName).replace(" ", "_")
                    + "_"
                    + str(project.estimatedSop).replace("", "noSop")
                    + "_"
                    + str(project.region).replace(" ", "_")
                    + "_"
                    + str(randomNumber)
                )
                syntheticProjectName = hashlib.sha256(
                    syntheticProjectNameInput.encode("utf-8")
                ).hexdigest()

                currentProjects = Project.objects.filter(
                    applicationMain=newAppMain,
                    applicationDetail=newAppDetail,
                    sales_name=newSalesName,
                    mainCustomer=newMainCustomer,
                    finalCustomer=newEndCustomer,
                    dummy=newDummy,
                    draft=oldDraft,
                    productMarketer=newProductMarketer,
                )

                if currentProjects.count() > 0:
                    self.success_url = reverse_lazy(
                        "project_deepdive",
                        kwargs={"projectId": request.session["project_id"]},
                    )

                    conflictingProjectsString = ""

                    for otherProject in currentProjects:
                        conflictingProjectsString = conflictingProjectsString + str(
                            otherProject.id
                        )

                    errorString = (
                        "The modification you are willing to do conflicts with an existing project and would lead to a deletion. Conflicting project: "
                        + conflictingProjectsString
                    )
                    messages.error(request, errorString)
                    return redirect(self.success_url)
                else:
                    # print("modifying key facts for project object", projectObj.id)
                    # so if there is no conflicting project modifiy the key attributes of the existing project. and then continue as usual with modifications of the remaining stuff.
                    projectObj.applicationMain = newAppMain
                    projectObj.applicationDetail = newAppDetail
                    projectObj.mainCustomer = newMainCustomer
                    projectObj.finalCustomer = newEndCustomer
                    projectObj.sales_name = newSalesName
                    projectObj.dummy = newDummy
                    projectObj.draft = oldDraft
                    projectObj.productMarketer = newProductMarketer

                    ####
                    projectObj.user = request.user
                    projectObj.estimatedSop = form.cleaned_data.get(
                        "estimatedSop")
                    projectObj.status = form.cleaned_data.get("status")
                    projectObj.region = form.cleaned_data.get("region")
                    projectObj.dcChannel = form.cleaned_data.get("dcChannel")
                    projectObj.valid = form.cleaned_data.get("valid")
                    projectObj.comment = form.cleaned_data.get("comment")
                    projectObj.projectName = form.cleaned_data.get(
                        "projectName")
                    # print("input proj desc", form.cleaned_data.get("projectDescription"), "input dc chl", form.cleaned_data.get("dcChannel"))
                    # projectObj.projectDescription = form.cleaned_data.get("projectDescription")
                    projectObj.distributor = form.cleaned_data.get(
                        "distributor")
                    projectObj.ems = form.cleaned_data.get("ems")
                    projectObj.oem = form.cleaned_data.get("oem")
                    projectObj.vpaCustomer = form.cleaned_data.get(
                        "vpaCustomer")
                    projectObj.salesContact = form.cleaned_data.get(
                        "salesContact")
                    projectObj.modreason = "keyFacts"

                    projectObj.save()
                    # print("output id of unique key mod", projectObj.id)
                    self.success_url = reverse_lazy(
                        "project_deepdive",
                        kwargs={"projectId": request.session["project_id"]},
                    )
                    messages.success(
                        request, "Project key facts were modified successfully."
                    )

                    # if not a draft (already in BoUp table), update BoUp table
                    if project.draft == False:
                        self.success_url = reverse_lazy(
                            "boupEntryOverview", kwargs={"projectId": projectId}
                        )
                    return redirect(self.success_url)
            else:
                form.clean()
                project = form.save()
                project.user = request.user
                project.modreason = "keyFacts"

                print(
                    "#####%%%%%%%%%% trying to modify project",
                    project.applicationMain,
                    project.applicationDetail,
                    "me / ec",
                    project.mainCustomer,
                    project.finalCustomer,
                    "draft",
                    project.draft,
                    project.sales_name,
                    "dummy",
                    project.dummy,
                    "user",
                    project.user,
                )

                project.save()
                # print("################ project form is valid. assigned ID", project.id)
                # stored project id in session to get in future
                request.session["project_id"] = project.id

                if request.session["editMode"]:
                    self.success_url = reverse_lazy(
                        "project_deepdive",
                        kwargs={"projectId": request.session["project_id"]},
                    )

                    # if not a draft (already in BoUp table), update BoUp table
                    if project.draft == False:
                        self.success_url = reverse_lazy(
                            "boupEntryOverview", kwargs={"projectId": projectId}
                        )

                messages.success(
                    request, "Project key facts were modified successfully."
                )
                return redirect(self.success_url)
        elif form.is_valid():

            # project saved in db
            # try:
            project = form.save()
            project.user = request.user
            project.modreason = "keyFacts"

            print(
                "#####%%%%%%%%%% trying to create project",
                project.applicationMain,
                project.applicationDetail,
                "me / ec",
                project.mainCustomer,
                project.finalCustomer,
                "draft",
                project.draft,
                project.sales_name,
                "dummy",
                project.dummy,
                "user",
                project.user,
            )

            project.save()
            # print("################ project form is valid. assigned ID", project.id)
            # stored project id in session to get in future
            request.session["project_id"] = project.id

            if request.session["editMode"]:
                self.success_url = reverse_lazy(
                    "project_deepdive",
                    kwargs={"projectId": request.session["project_id"]},
                )

            if "save_n_continue" in request.POST:
                self.success_url = reverse_lazy("project_management_all_view")
            return redirect(self.success_url)
            """
            except:

            """
        else:
            for error in form.errors:
                print("### error:", error)

            # print("form is not valid", form.errors)
        context = {
            "form": self.form_class(request.POST, request=request),
            "editMode": False,
            "projectId": 0,
        }

        if request.session["editMode"]:
            print(
                "trying to set session id",
                request.session,
                request.session["editMode"],
                "project id",
                projectId,
            )
            context = {
                "form": self.form_class(request.POST, request=request),
                "editMode": True,
                "projectId": projectId,
            }

        return render(request, self.template_name, context)


def EditProjectDraftEntry(request, projectId):
    # print("########### selecting volume entry")
    redirect_url = reverse_lazy("edit_project_draft_view")
    request.session["project_id"] = projectId
    return redirect(redirect_url)


class EditProjectDraftView(LoginRequiredMixin, View):
    template_name = "project/project_create_view/step1.html"
    form_class = ProjectCreateForm
    success_url = reverse_lazy("create_volume_view")

    def get(self, request, *args, **kwargs):
        print("edit view, kwargs", kwargs)
        # = projectId  # 11kwargs["projectId"]
        projectId = request.session["project_id"]
        project = Project.objects.get(id=projectId)
        # print("### editing project ->", project, "projectId", project.id)
        context = {
            "form": self.form_class(instance=project, editMode=True),
            "editMode": True,
            "projectId": projectId,
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        projectId = request.session["project_id"]
        project = Project.objects.get(id=projectId)
        form = self.form_class(
            request.POST, request=request, editMode=True, instance=project
        )
        series = form["product_series"]
        salesNameInput = request.POST.get("sales_name")
        salesNameObj = None

        try:
            salesNameInt = int(salesNameInput)
            salesNameObj = SalesName.objects.get(id=salesNameInt)

        except:
            salesNameObj = SalesName.objects.get(name=salesNameInput)

        _mutable = request.POST._mutable
        request.POST._mutable = True
        request.POST["sales_name"] = salesNameObj.pk
        request.POST._mutable = _mutable

        if form.is_valid():
            # project saved in db
            project = form.save()
            project.user = request.user
            project.modreason = "keyFacts"
            project.save()
            print(
                "################ project form is valid. assigned ID",
                project.id,
                "app main",
                project.applicationMain,
            )
            # stored project id in session to get in future
            request.session["project_id"] = project.id
            return redirect(self.success_url)
        else:
            for error in form.errors:
                print("### error:", error)
            # print("form is not valid")

        context = {
            "form": self.form_class(request.POST, request=request),
            "editMode": False,
        }

        if request.session["editMode"]:
            context = {
                "form": self.form_class(request.POST, request=request),
                "editMode": True,
                "projectId": projectId,
            }

        return render(request, self.template_name, context)


def SelectVolumeEntryType(request):
    print("########### selecting volume entry")

    if request.session["editMode"]:
        # print("request session on edit", request.session["project_id"])
        project = Project.objects.get(id=request.session["project_id"])

        if (project.is_viewing == True) & (project.is_viewing_user != request.user):

            success_url = reverse_lazy(
                "project_deepdive",
                kwargs={"projectId": request.session["project_id"]},
            )
            messages.error(
                request, "The project is locked for editing by another user."
            )

            return redirect(success_url)

        return render(
            request,
            "project/project_create_view/step2a.html",
            {
                "segment": "boupOverviewSlim",
                "editMode": True,
                "projectId": request.session["project_id"],
            },
        )

    else:
        return render(
            request,
            "project/project_create_view/step2a.html",
            {
                "segment": "boupOverviewSlim",
                "editMode": False,
                "projectId": request.session["project_id"],
                # "projectId": 0
            },
        )


def VolumeTypeSelectMonthYear(request):

    if request.session["editMode"]:
        return render(
            request,
            "project/project_create_view/step2a_month_or_year.html",
            {
                "segment": "boupOverviewSlim",
                "editMode": True,
                "projectId": request.session["project_id"],
            },
        )
    else:

        return render(
            request,
            "project/project_create_view/step2a_month_or_year.html",
            {
                "segment": "boupOverviewSlim",
                "editMode": False,
                "projectId": request.session["project_id"],
                #  "projectId": 0
            },
        )


class CreateVolumeExcelView(LoginRequiredMixin, View):
    template_name = "project/project_create_view/step2b_excel.html"
    form_class = VolumeForm
    success_url = reverse_lazy("create_volume_customer_excel_view")

    """
    def get_context_data(self,*args, **kwargs):
        project_id = self.request.session.get("project_id", None)
        print("&&& called get_context_Data")
        context = super().get_context_data(*args,**kwargs)
        project = Project.objects.get(id=project_id)
        estimatedSop = project.estimatedSop

        yearsGraphs = [
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
                        2033,
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
                        2046,
                        2047,
                        2048,
                        2049,
                        2050,
                    ]
        orders = [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ]
        plannedQuantities = [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ]

        #prepare graphs to display planned quantities and order items 
        
        allPlanedItemsObj = ProjectVolumePrices.objects.select_related()
        rfp = project.sales_name.rfp
        mainCustomer = project.mainCustomer
        endCustomer = project.finalCustomer

        allPlanedItemsObj = allPlanedItemsObj.filter(
            project__sales_name__rfp=rfp,
            valid=True,
            quantity__gt=0,
            project__mainCustomer=mainCustomer,
            project__finalCustomer=endCustomer,
        )

        for obj in allPlanedItemsObj:
            probability = 1.0

            try:
                probability = obj.project.status.status / 100
            except:
                pass

            year = int(obj.calenderYear)
            relevantIndex = yearsGraphs.index(year)
            currentQuantity = plannedQuantities[relevantIndex]
            newQuantity = currentQuantity + (obj.quantity * probability)
            plannedQuantities[relevantIndex] = newQuantity

        allOrders = VrfcOrdersOnHand.objects.filter(
            rfp=rfp, mainCustomerVrfc=mainCustomer, endCustomerVrfc=endCustomer
        )

        for obj in allOrders:
            year = int(obj.year)
            print("year", year, type(year))
            print("yearsGraphs", yearsGraphs)
            relevantIndex = yearsGraphs.index(year)
            currentQuantity = orders[relevantIndex]
            newQuantity = currentQuantity + obj.quantity
            orders[relevantIndex] = newQuantity

        initial_dict = {"startOfProductionYear": estimatedSop}
        context = {
            "form": self.form_class(initial=initial_dict),
            #"months": months,
            #"volumes": volumes,
            #"years": years,
            #"dataCondition": dataCondition,
            "editMode": False,
            "project": project,
            "yearsGraphs": yearsGraphs,
            "orders": orders,
            "plannedQuantities": plannedQuantities,
        }

        if self.request.session["editMode"]:

            if (project.is_viewing == True) & (
                project.is_viewing_user != self.request.user
            ):
                print(
                    "%%%%%%%%%%%%%%%%%% project is locked for editing",
                    project.is_viewing,
                )

                self.success_url = reverse_lazy(
                    "project_deepdive",
                    kwargs={"projectId": self.request.session["project_id"]},
                )
                messages.error(
                    self.request, "The project is locked for editing by another user."
                )

                #return redirect(self.success_url)

            context = {
                "form": self.form_class(initial=initial_dict),
                #"months": months,
                #"volumes": volumes,
                #"years": years,
                #"dataCondition": dataCondition,
                "editMode": True,
                "projectId": self.request.session["project_id"],
                "project": project,
                "yearsGraphs": yearsGraphs,
                "orders": orders,
                "plannedQuantities": plannedQuantities,
            }

        return context
    """

    def get(self, request, *args, **kwargs):
        # getting project instance that was created in first step
        project_id = request.session.get("project_id", None)
        if project_id:
            project = Project.objects.get(id=project_id)
            # getting estimated SOP from created project
            # feeding that sop to startOfProduction field
            initial_dict = {"startOfProduction": project.estimatedSop, "request": request}

            # check if volumes are already existing for this project. if yes, prefill the jexcel with it.
            volumes = []
            years = []
            dataCondition = 0

            """
            prepare graphs to display planned quantities and order items 
            """
            yearsGraphs = [
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
                2033,
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
                2046,
                2047,
                2048,
                2049,
                2050,
            ]
            orders = [
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
            ]
            plannedQuantities = [
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
            ]

            allPlanedItemsObj = ProjectVolumePrices.objects.select_related()
            rfp = project.sales_name.rfp
            mainCustomer = project.mainCustomer
            endCustomer = project.finalCustomer

            allPlanedItemsObj = allPlanedItemsObj.filter(
                project__sales_name__rfp=rfp,
                valid=True,
                quantity__gt=0,
                project__mainCustomer=mainCustomer,
                project__finalCustomer=endCustomer,
            )

            for obj in allPlanedItemsObj:
                probability = 1.0

                try:
                    probability = obj.project.status.status / 100
                except:
                    pass

                year = int(obj.calenderYear)
                relevantIndex = yearsGraphs.index(year)
                currentQuantity = plannedQuantities[relevantIndex]
                newQuantity = currentQuantity + (obj.quantity * probability)
                plannedQuantities[relevantIndex] = newQuantity

            allOrders = VrfcOrdersOnHand.objects.filter(
                rfp=rfp, mainCustomerVrfc=mainCustomer, endCustomerVrfc=endCustomer
            )

            for obj in allOrders:
                year = int(obj.year)
                relevantIndex = yearsGraphs.index(year)
                currentQuantity = orders[relevantIndex]
                newQuantity = currentQuantity + obj.quantity
                orders[relevantIndex] = newQuantity

            try:
                objects = ProjectVolumePrices.objects.filter(
                    project=project, valid=True, quantity__gt=0
                ).order_by("calenderYear")

                if objects.count() > 0:
                    dataCondition = 1
                    for object in objects:
                        volumes.append(object.quantity)
                        years.append(object.calenderYear)
            except:
                pass

            # to avoid problem with empty volumes

            if len(years) == 0:
                dataCondition = 0

            context = {
                "form": self.form_class(initial=initial_dict),
                "dataCondition": dataCondition,
                "volumes": volumes,
                "years": years,
                "editMode": False,
                "project": project,
                "orders": orders,
                "plannedQuantities": plannedQuantities,
                "yearsGraphs": yearsGraphs,
            }

            if request.session["editMode"]:
                # check if editing
                if (project.is_viewing == True) & (
                    project.is_viewing_user != request.user
                ):
                    self.success_url = reverse_lazy(
                        "project_deepdive",
                        kwargs={"projectId": request.session["project_id"]},
                    )
                    messages.error(
                        request, "The project is locked for editing by another user."
                    )

                    return redirect(self.success_url)

                context = {
                    "form": self.form_class(initial=initial_dict),
                    "dataCondition": dataCondition,
                    "volumes": volumes,
                    "years": years,
                    "editMode": True,
                    "projectId": request.session["project_id"],
                    "project": project,
                    "orders": orders,
                    "plannedQuantities": plannedQuantities,
                    "yearsGraphs": yearsGraphs,
                }

            return render(request, self.template_name, context)
        else:
            return redirect(reverse("create_project_view"))

    def post(self, request, *args, **kwargs):
        project_id = request.session.get("project_id", None)
        project = Project.objects.get(id=project_id)
        estimatedSop = project.estimatedSop
        initial_dict = {"startOfProduction": estimatedSop, "request": request}

        form = self.form_class(request.POST, initial=initial_dict)

        if form.is_valid():
            # process the data submitted in the form...
            # following data will be extracted after running clean method defined under VolumeForm in forms.py file
            # field_value = form.cleaned_data.get("field_name")
            project = Project.objects.get(id=project_id)
            volumes = form.cleaned_data.get("volume") #form.volume
            years = form.cleaned_data.get("years") # form.years  # 
            volumesPost = []
            print("((( form is valid a)))")

            """
            new Feb 2023: clean years and volumes previous to linSmoother... so if user entered 
            [2020, 2021, 2022, 2023, 2024] and [100, 200, 0, 0, 0] to avoid misinterpolation -> [2020, 2021], [100, 200]
            [2020, 2021, 2022, 2023, 2024] and [0, 200, 100, 0, 0] ->  [2021, 2022] [200, 100]
            """

            from .helperFunctions import cleanYearsVolumes
            years, volumes = cleanYearsVolumes(years, volumes)
            
            # first disable all the existing volume entries for this project.
            currentVolumes = ProjectVolumePrices.objects.filter(
                project=project)
            currentMonthVolumes = ProjectVolumeMonth.objects.filter(
                project=project)
            currentVolumes.update(quantity=0)
            currentMonthVolumes.update(quantity=0)

            runDate = datetime.datetime.now(tz=timezone.utc)

            # my custom code (Saadat)
            # this will generate dictionary with year as key and volume as value of user entered values
            # e.g {2020: 1020, 2021: 1203}
            years_with_volume = dict(zip(years, volumes))
            # getting already existing project and calendaryear
            existing_values_list = list(
                ProjectVolumePrices.objects.values_list(
                    "project__id", "calenderYear"
                ).order_by("id")
            )
            existing_qs = list(
                ProjectVolumePrices.objects.all().order_by("id"))
            existing_dict = dict(zip(existing_values_list, existing_qs))
            # existing_dict {(3, 2025): <ProjectVolumePrices: ID: 21 - QTY: 0 - YR: 2025> ... left side: year and project ID; full object

            # makeing list of user entered years to compare with above list. for each user entered year, the project ID is added.
            entered_values = [(project.id, year) for year in years]
            # entered_values [(3, 2025), (3, 2026), (3, 2027), (3, 2028), (3, 2029)]

            print("%%% entered values volumes", entered_values)

            # this list will store queryset that already exist
            # and we can bulk_update on this queryset
            duplicate = []

            # this list store the values that doesnt exist already
            # so we can run bulk_create with these
            newYears = []
            # seperating new and old queryset
            # this will check if entered_values entry (e.g. (3, 2025)) is in the key of existing_dict. if it is, it will be appended to dict.
            for value in entered_values:
                if value in existing_dict:
                    existing_dict_value = existing_dict.get(value)
                    duplicate.append(existing_dict_value)
                else:
                    # appending year because we already have value of year.
                    newYears.append(value[1])

            # assigning new values to existing queryset. years with volume is the user input.
            for obj in duplicate:
                currentQuantity = obj.quantity
                obj.quantity = years_with_volume.get(obj.calenderYear)
                obj.valid = True
                obj.user = request.user

            # bulk update values that we added new values above
            ProjectVolumePrices.objects.bulk_update(
                duplicate, ["quantity", "valid", "user"]
            )

            # creating new instances
            instance_objs = [
                ProjectVolumePrices(
                    project=project,
                    calenderYear=year,
                    quantity=years_with_volume.get(year),
                    valid=True,
                    user=request.user,
                )
                for year in newYears
            ]

            # queryset of newly created volumes
            newly_created_volumes = ProjectVolumePrices.objects.bulk_create(
                instance_objs
            )

            # my custom code ends here... (Saadat)

            # rewrite of log objects

            for obj in newly_created_volumes:
                (logobject, logcreated,) = ProjectVolumePricesLog.objects.get_or_create(
                    project=project,
                    calenderYear=obj.calenderYear,
                    runTimestamp=runDate,
                )

                logobject.quantity = obj.quantity
                logobject.user = request.user
                logobject.modreason = "volumesCreation"
                logobject.save()

            for obj in duplicate:
                (logobject, logcreated,) = ProjectVolumePricesLog.objects.get_or_create(
                    project=project,
                    calenderYear=obj.calenderYear,
                    runTimestamp=runDate,
                )
                logobject.quantity = obj.quantity
                logobject.user = request.user
                logobject.modreason = "volumesModification"
                logobject.save()

            """
            for i in range(0, (len(years)), 1):

                obj, created = ProjectVolumePrices.objects.get_or_create(
                    project=project, calenderYear=int(years[i])
                )

                currentQuantity = obj.quantity
                obj.quantity = int(volumes[i])
                obj.valid = True
                obj.user = request.user
                obj.save()

                runDate = datetime.datetime.now(tz=timezone.utc)
                # create log entry only on creation or modification
                if created == True:
                    (
                        logobject,
                        logcreated,
                    ) = ProjectVolumePricesLog.objects.get_or_create(
                        project=project,
                        calenderYear=int(years[i]),
                        runTimestamp=runDate,
                    )
                    logobject.quantity = obj.quantity
                    logobject.quantity = obj.quantity
                    logobject.quantity = obj.quantity
                    logobject.user = request.user
                    logobject.modreason = "volumesCreation"
                    logobject.save()
                elif currentQuantity != int(volumes[i]):
                    (
                        logobject,
                        logcreated,
                    ) = ProjectVolumePricesLog.objects.get_or_create(
                        project=project,
                        calenderYear=int(years[i]),
                        runTimestamp=runDate,
                    )
                    logobject.quantity = obj.quantity
                    logobject.user = request.user
                    logobject.modreason = "volumesModification"
                    logobject.save()
                else:
                    pass

                print(created, "---> volume object,", obj)
            """

            """
            The next block of code will create the monthly volume entries.
            This one is the largest "killer" of database calls.
            The iteration is based on user entered years. For each year, 12 months are created.
            The linSmoother function generates the monthly volume based on the yearly volume (linear interpolation).
            The ProjectVolumeMonth objects are created with a) projectId, calenderYear, month.
            Then, the monthVolume is assigned.
            """

            year = 0

            monthVolume = linSmoother(years[0], years[-1], volumes)

            print("months:", len(monthVolume),
                  "years", years, "last", years[-1])
            print("%%% month volume output", monthVolume)

            """
            For Saadat: please insert here your code for bulk creation of volumes at monthly level.

            """
            months = [month for month in range(1, 13)]

            # my custom code (Saadat)
            # this will generate dictionary with year as key and {month : volume} as value of user entered values
            # e.g {2020: {1:1302, 2:1304, 3:1430, ..., 12:1620}, 2021: {1:1203, ..., 12:1104}}
            years_with_months_volume = {}
            for count, year in enumerate(years):
                years_with_months_volume[year] = {
                    month: volume
                    for month, volume in zip(
                        months,
                        monthVolume[count * 12: (count + 1) * 12],
                    )
                }

            # getting already existing project, calendaryear and month
            # e.g (1, 2020, 1)
            existing_values_list = list(
                ProjectVolumeMonth.objects.values_list(
                    "project__id", "calenderYear", "month"
                ).order_by("id")
            )
            existing_qs = list(ProjectVolumeMonth.objects.all().order_by("id"))
            # merging vlaues_list and queryset in dict form
            # e.g {(1, 2020, 1): <QuerysetObject xxxxx >}
            existing_dict = dict(zip(existing_values_list, existing_qs))
            # makeing list of user entered years to compare with above list. for each user entered year, the project ID is added.

            entered_values_month = []

            for year in years_with_months_volume:
                for month in months:
                    entered_values_month.append((project.id, year, month))

            # this list will store queryset that already exist
            # and we can bulk_update on this queryset
            duplicate = []

            # this list store the values that doesnt exist already
            # so we can run bulk_create with these
            new = []

            # seperating new and old queryset

            for value in entered_values_month:
                # (3, 2028, 12)
                if value in list(existing_dict.keys()):
                    existing_dict_value = existing_dict.get(value)
                    duplicate.append(existing_dict_value)
                else:
                    # value contains combination of project id, year and month
                    # that aren't available in database
                    new.append(value)

            # assigning new values to existing queryset
            for obj in duplicate:
                currentQuantity = obj.quantity
                months_with_quantity = years_with_months_volume.get(
                    obj.calenderYear
                )  # {1:1200, 2:1243, 3:2343}
                quantity = months_with_quantity.get(obj.month)
                obj.quantity = quantity
                obj.valid = True
                obj.user = request.user

            # bulk update values that we added new values above
            ProjectVolumeMonth.objects.bulk_update(
                duplicate, ["quantity", "valid", "user"]
            )

            # creating new instances
            # (projectID, year, month)
            instance_objs = [
                ProjectVolumeMonth(
                    project=project,
                    calenderYear=obj[1],
                    quantity=years_with_months_volume.get(year).get(obj[2]),
                    valid=True,
                    user=request.user,
                )
                for obj in new
            ]
            # queryset of newly created volumes
            newly_created_volumes = ProjectVolumeMonth.objects.bulk_create(
                instance_objs
            )

            """

            old code of Francisco starts here:
            """
            # for i in range(0, (len(years)) * 12, 1):

            #     if i != 0 and i % 12 == 0:
            #         # print(int(years[year]), "----", int(volumes[i]))
            #         year = year + 1
            #     month = (i % 12) + 1  # +1 so we dont have the 0th month
            #     volumeObjectM, created = ProjectVolumeMonth.objects.get_or_create(
            #         project=project, calenderYear=int(years[year]), month=month
            #     )

            #     currentVolumeM = volumeObjectM.quantity
            #     volumeObjectM.quantity = monthVolume[i]
            #     volumeObjectM.valid = True
            #     volumeObjectM.user = request.user

            #     if created == False:
            #         obj.modifiedDate = datetime.datetime.now(tz=timezone.utc)

            #     volumeObjectM.save()
            #     # volumesPost.append(f(int(years[0])+0.5+(i/12)))
            #     print(i)
            #     print(created, "---> volume month object,", volumeObjectM)

            #     # runDate = datetime.now(tz=timezone.utc)
            #     # create log entry
            #     if created == True:
            #         logobject, logcreated = ProjectVolumeMonthLog.objects.get_or_create(
            #             project=project,
            #             calenderYear=int(years[year]),
            #             runTimestamp=runDate,
            #             month=month,
            #         )
            #         logobject.quantity = obj.quantity
            #         logobject.user = request.user
            #         logobject.modreason = "volumesCreation"
            #         logobject.save()
            #     elif currentVolumeM != monthVolume[i]:
            #         logobject, logcreated = ProjectVolumeMonthLog.objects.get_or_create(
            #             project=project,
            #             calenderYear=int(years[year]),
            #             runTimestamp=runDate,
            #             month=month,
            #         )
            #         logobject.quantity = obj.quantity
            #         logobject.user = request.user
            #         logobject.modreason = "volumesModification"
            #         logobject.save()
            #     else:
            #         pass

            # project.modreason = "volumes"
            # project.save()

            print("redirecting on success")

            if request.session["editMode"]:
                self.success_url = reverse_lazy(
                    "project_deepdive",
                    kwargs={"projectId": request.session["project_id"]},
                )

                # if not a draft (already in BoUp table), update BoUp table
                if project.draft == False:
                    self.success_url = reverse_lazy(
                        "boupEntryOverview",
                        kwargs={"projectId": request.session["project_id"]},
                    )

            return redirect(self.success_url)

        else:
            print("&&& form is not valid B")
            excelData = request.POST.get("excelData")
            years = []
            volumes = []
            dataCondition = 0

            try:
                yearsA, volumesA = excelData.split("\n")
                years = yearsA.strip().split(",")
                volumes = volumesA.strip().split(",")
                volumes = [float(x) for x in volumes]
                years = [float(x) for x in years]
                dataCondition = 1
            except:
                print("failed completely to recover entered data... sorry")

            if dataCondition == 1:
                if len(years) == 0:
                    dataCondition = 0
            formNew = self.form_class(request.POST, initial=initial_dict)

            """
            prepare graphs to display planned quantities and order items 
            """
            yearsGraphs = [
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
                2033,
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
                2046,
                2047,
                2048,
                2049,
                2050,
            ]
            orders = [
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
            ]
            plannedQuantities = [
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
            ]

            allPlanedItemsObj = ProjectVolumePrices.objects.select_related()
            rfp = project.sales_name.rfp
            mainCustomer = project.mainCustomer
            endCustomer = project.finalCustomer

            allPlanedItemsObj = allPlanedItemsObj.filter(
                project__sales_name__rfp=rfp,
                valid=True,
                quantity__gt=0,
                project__mainCustomer=mainCustomer,
                project__finalCustomer=endCustomer,
            )

            for obj in allPlanedItemsObj:
                probability = 1.0

                try:
                    probability = obj.project.status.status / 100
                except:
                    pass

                year = int(obj.calenderYear)
                relevantIndex = yearsGraphs.index(year)
                currentQuantity = plannedQuantities[relevantIndex]
                newQuantity = currentQuantity + (obj.quantity * probability)
                plannedQuantities[relevantIndex] = newQuantity

            allOrders = VrfcOrdersOnHand.objects.filter(
                rfp=rfp, mainCustomerVrfc=mainCustomer, endCustomerVrfc=endCustomer
            )

            for obj in allOrders:
                year = int(obj.year)
                relevantIndex = yearsGraphs.index(year)
                currentQuantity = orders[relevantIndex]
                newQuantity = currentQuantity + obj.quantity
                orders[relevantIndex] = newQuantity
                
            context = {
                "form": formNew,
                "dataCondition": dataCondition,
                "volumes": volumes,
                "years": years,
                "editMode": False,
                "yearsGraph": yearsGraphs,
                "orders": orders,
                "plannedQuantities": plannedQuantities,
            }

            if request.session["editMode"]:
                context = {
                    "form": formNew,
                    "dataCondition": dataCondition,
                    "volumes": volumes,
                    "years": years,
                    "editMode": True,
                    "projectId": request.session["project_id"],
                    "projectId": 0,
                    "yearsGraph": yearsGraphs,
                    "orders": orders,
                    "plannedQuantities": plannedQuantities,
                }
            print("//// returnign on error", context)

            # context = {"form": form}
            return render(request, self.template_name, context)


class CreateCustomerVolumeExcelView(LoginRequiredMixin, View):
    print("$$$$$ running customer volumes")
    template_name = "project/project_create_view/step2d_customer.html"
    form_class = VolumeForm
    success_url = reverse_lazy("create_pricing_view")

    def get(self, request, *args, **kwargs):

        # getting project instance that was created in first step
        project_id = request.session.get("project_id", None)
        if project_id:
            project = Project.objects.get(id=project_id)
            # getting estimated SOP from created project
            estimatedSop = project.estimatedSop
            # feeding that sop to startOfProduction field
            initial_dict = {"startOfProduction": estimatedSop}

            # check if volumes are already existing for this project. if yes, prefill the jexcel with it.
            volumes = []
            years = []
            dataCondition = 0

            try:
                objects = ProjectVolumePrices.objects.filter(
                    project=project, valid=True
                ).order_by("calenderYear")

                noneType = type(None)

                if objects.count() > 0:
                    dataCondition = 1
                    for object in objects:
                        print("monthly volume read",
                              object.quantityCustomerEstimation)
                        if type(object.quantityCustomerEstimation) != noneType:
                            volumes.append(object.quantityCustomerEstimation)
                            years.append(object.calenderYear)
                        else:
                            years.append(object.calenderYear)

            except:
                print("could not fetch volume data!!!!")
                pass

            context = {
                "form": self.form_class(initial=initial_dict),
                "dataCondition": dataCondition,
                "volumes": volumes,
                "years": years,
                "editMode": False,
                "project": project,
            }

            if request.session["editMode"]:
                if (project.is_viewing == True) & (
                    project.is_viewing_user != request.user
                ):
                    print(
                        "%%%%%%%%%%%%%%%%%% project is locked for editing",
                        project.is_viewing,
                    )

                    self.success_url = reverse_lazy(
                        "project_deepdive",
                        kwargs={"projectId": request.session["project_id"]},
                    )
                    messages.error(
                        request, "The project is locked for editing by another user."
                    )

                    return redirect(self.success_url)

                context = {
                    "form": self.form_class(initial=initial_dict),
                    "dataCondition": dataCondition,
                    "volumes": volumes,
                    "years": years,
                    "editMode": True,
                    "projectId": request.session["project_id"],
                    "project": project,
                }

            print(
                "rendering view with sop",
                estimatedSop,
                "volumes",
                volumes,
                "years",
                years,
                "data condition",
                dataCondition,
            )
            return render(request, self.template_name, context)
        else:
            return redirect(reverse("create_project_view"))

    def post(self, request, *args, **kwargs):
        project_id = request.session.get("project_id", None)
        project = Project.objects.get(id=project_id)
        estimatedSop = project.estimatedSop
        initial_dict = {"startOfProduction": estimatedSop}

        form = self.form_class(request.POST, initial=initial_dict)
        if form.is_valid():
            project = Project.objects.get(id=project_id)
            volumes = form.volume  # form.cleaned_data.get("volume")
            years = form.years  # form.cleaned_data.get("years")
            volumesPost = []

            runDate = datetime.now(tz=timezone.utc)

            # reset the customer values
            currentVolumes = ProjectVolumePrices.objects.filter(
                project=project)
            currentVolumes.update(quantityCustomerEstimation=0)

            # now redo the entries
            for i in range(0, (len(years)), 1):
                object, created = ProjectVolumePrices.objects.get_or_create(
                    project=project, calenderYear=int(years[i])
                )

                # for the sake of consistency, check if this was set to invalid.??
                object.quantityCustomerEstimation = int(volumes[i])
                object.valid = True
                object.user = request.user

                if created == False:
                    object.modifiedDate = datetime.now(tz=timezone.utc)

                object.save()
                volumesPost.append(int(volumes[i]))
                print(created, "---> volume object,", object)

                # runDate = datetime.now(tz=timezone.utc)
                # create log entry
                logobject, logcreated = ProjectVolumePricesLog.objects.get_or_create(
                    project=project, calenderYear=int(years[i]), runTimestamp=runDate
                )
                logobject.quantityCustomerEstimation = object.quantity
                logobject.user = request.user
                logobject.modreason = "customerVolumes"
                logobject.save()

            if request.session["editMode"]:
                self.success_url = reverse_lazy(
                    "project_deepdive",
                    kwargs={"projectId": request.session["project_id"]},
                )
            if "save_n_continue" in request.POST:
                self.success_url = reverse_lazy("project_management_all_view")
            return redirect(self.success_url)

        else:

            excelData = request.POST.get("excelData")
            years = []
            volumes = []
            dataCondition = 1
            print("excelData", excelData)

            try:
                yearsA, volumesA = excelData.split("\n")
                print("excelData", excelData)
                years = yearsA.strip().split(",")
                volumes = volumesA.strip().split(",")
                volumes = [float(x) for x in volumes]
                years = [float(x) for x in years]
                print("years", years, "volumes", volumes)
                dataCondition = 1
            except:
                print("failed completely to recover entered data... sorry")

            if dataCondition == 1:
                if len(years) == 0:
                    dataCondition = 0
            print("lean yeears", len(years),
                  "resulting data condition", dataCondition)

            context = {
                "form": self.form_class(request.POST, initial=initial_dict),
                "dataCondition": dataCondition,
                "volumes": volumes,
                "years": years,
                "editMode": False,
                "project": project,
            }

            if request.session["editMode"]:
                context = {
                    "form": self.form_class(request.POST, initial=initial_dict),
                    "dataCondition": dataCondition,
                    "volumes": volumes,
                    "years": years,
                    "editMode": True,
                    "projectId": request.session["project_id"],
                    "project": project,
                }

            for error in form.errors:
                print("---------> form error", error)

            # context = {"form": form}
            return render(request, self.template_name, context)


class CreateVolumeExcelMonthView(LoginRequiredMixin, View):
    print("$$$$$ running CreateVolumeExcelMonthView")
    template_name = "project/project_create_view/step2c_excelMonth.html"
    form_class = VolumeMonthForm
    success_url = reverse_lazy("create_volume_customer_excel_view")


    # get does not change wrt to CreateVolumeExcelView
    def get(self, request, *args, **kwargs):
        project_id = request.session.get("project_id", None)
        if project_id:
            project = Project.objects.get(id=project_id)
            estimatedSop = project.estimatedSop
            ################################
            # check if volumes are already existing for this project. if yes, prefill the jexcel with it.
            volumes = []
            years = []
            months = []
            dataCondition = 0

            # try:
            objects = ProjectVolumeMonth.objects.filter(
                project=project, quantity__gt=0
            ).order_by("calenderYear", "month")

            noneType = type(None)
            dataCondition = 1

            yearsGraphs = [
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
                2033,
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
                2046,
                2047,
                2048,
                2049,
                2050,
            ]
            orders = [
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
            ]
            plannedQuantities = [
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
            ]

            """
            prepare graphs to display planned quantities and order items 
            """

            allPlanedItemsObj = ProjectVolumePrices.objects.select_related()
            rfp = project.sales_name.rfp
            mainCustomer = project.mainCustomer
            endCustomer = project.finalCustomer

            allPlanedItemsObj = allPlanedItemsObj.filter(
                project__sales_name__rfp=rfp,
                valid=True,
                quantity__gt=0,
                project__mainCustomer=mainCustomer,
                project__finalCustomer=endCustomer,
            )

            for obj in allPlanedItemsObj:
                probability = 1.0

                try:
                    probability = obj.project.status.status / 100
                except:
                    pass

                year = int(obj.calenderYear)
                relevantIndex = yearsGraphs.index(year)
                currentQuantity = plannedQuantities[relevantIndex]
                newQuantity = currentQuantity + (obj.quantity * probability)
                plannedQuantities[relevantIndex] = newQuantity

            allOrders = VrfcOrdersOnHand.objects.filter(
                rfp=rfp, mainCustomerVrfc=mainCustomer, endCustomerVrfc=endCustomer
            )

            for obj in allOrders:
                year = int(obj.year)
                print("year", year, type(year))
                print("yearsGraphs", yearsGraphs)
                relevantIndex = yearsGraphs.index(year)
                currentQuantity = orders[relevantIndex]
                newQuantity = currentQuantity + obj.quantity
                orders[relevantIndex] = newQuantity

            if objects.count() > 0:
                for object in objects:
                    """
                    print(
                        object.calenderYear,
                        object.month,
                        " volume month read",
                        object.quantity,
                    )
                    """
                    if type(object.quantity) != noneType:
                        volumes.append(object.quantity)
                        months.append(object.month)
                        years.append(object.calenderYear)

            """
            except:
                print("could not fetch volume month data for prefill")
                pass
            """
            # to avoid problem with empty volumes. watchout, slightly different implementaiton here than in the regular volume excel view in order to show years as a helper for the user in the front end.

            if len(volumes) == 0:
                dataCondition = 0

            ################################
            initial_dict = {"startOfProductionYear": estimatedSop}
            context = {
                "form": self.form_class(initial=initial_dict),
                "months": months,
                "volumes": volumes,
                "years": years,
                "dataCondition": dataCondition,
                "editMode": False,
                "project": project,
                "yearsGraphs": yearsGraphs,
                "orders": orders,
                "plannedQuantities": plannedQuantities,
            }

            if request.session["editMode"]:

                if (project.is_viewing == True) & (
                    project.is_viewing_user != request.user
                ):
                    print(
                        "%%%%%%%%%%%%%%%%%% project is locked for editing",
                        project.is_viewing,
                    )

                    self.success_url = reverse_lazy(
                        "project_deepdive",
                        kwargs={"projectId": request.session["project_id"]},
                    )
                    messages.error(
                        request, "The project is locked for editing by another user."
                    )

                    return redirect(self.success_url)

                context = {
                    "form": self.form_class(initial=initial_dict),
                    "months": months,
                    "volumes": volumes,
                    "years": years,
                    "dataCondition": dataCondition,
                    "editMode": True,
                    "projectId": request.session["project_id"],
                    "project": project,
                    "yearsGraphs": yearsGraphs,
                    "orders": orders,
                    "plannedQuantities": plannedQuantities,
                }

            print("rendering view with sop", estimatedSop)
            return render(request, self.template_name, context)
        else:
            return redirect(reverse("create_project_view"))

    def post(self, request, *args, **kwargs):
        project_id = request.session.get("project_id", None)
        project = Project.objects.get(id=project_id)
        estimatedSop = project.estimatedSop
        initial_dict = {"startOfProduction": estimatedSop}

        form = self.form_class(request.POST, initial=initial_dict)
        print("initialized form after post with project ID", project_id)

        if form.is_valid():
            print("form is valid!")
            project = Project.objects.get(id=project_id)
            project.user = request.user
            project.save()

            volumes = form.cleaned_data.get("volume")
            years = form.cleaned_data.get("years")
            months = form.cleaned_data.get("months")

            print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            print("will use cleaned values, volumes")
            print(volumes)
            print("&&&&&&&&& years")
            print(years)
            print("%%%%%%%%%%%% months")
            print(months)
            volumesPost = []
            runYears = [
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
                2046,
                2047,
                2048,
                2049,
            ]

            # reset volumes
            currentVolumes = ProjectVolumePrices.objects.filter(
                project=project)
            currentMonthVolumes = ProjectVolumeMonth.objects.filter(
                project=project)
            currentVolumes.update(quantity=0)
            currentMonthVolumes.update(quantity=0)
            runDate = datetime.datetime.now(tz=timezone.utc)

            yearlyVolumes = []
            yearsSingle = []
            yearVolume = 0
            lastYear = 0

            """
            get the respective yearly volumes
            if the year changes, take that into account. user input could start even in december of a given year.
            
            """
            for i in range(0, (len(years)), 1):

                if i == 0:
                    lastYear = years[i]

                if years[i] != lastYear:
                    yearlyVolumes.append(yearVolume)
                    yearsSingle.append(lastYear)
                    yearVolume = volumes[i]
                else:
                    yearVolume = yearVolume + volumes[i]

                lastYear = years[i]

                """
                if this is the last entry, append to array too.
                """
                if (i == (len(years) - 1)) & (years[i] == lastYear):
                    yearlyVolumes.append(yearVolume)
                    yearsSingle.append(lastYear)

            for i in range(0, (len(yearsSingle)), 1):

                """
                if int(years[i]) in runYears:
                    continue
                else:
                    pass
                """

                object, created = ProjectVolumePrices.objects.get_or_create(
                    project=project, calenderYear=int(yearsSingle[i])
                )

                currentQuantity = object.quantity
                yearVolume = yearlyVolumes[i]
                object.valid = True
                object.quantity = int(yearVolume)
                object.save()

                print(
                    created,
                    "---> volume object,",
                    object,
                    "used year",
                    i,
                    years[i],
                    "year volume",
                    yearVolume,
                )
                runYears.append(int(years[i]))

                # create only a log entry on change
                if created == True:
                    (
                        logobject,
                        logcreated,
                    ) = ProjectVolumePricesLog.objects.get_or_create(
                        project=project,
                        calenderYear=int(years[i]),
                        runTimestamp=runDate,
                    )
                    logobject.quantity = object.quantity
                    logobject.user = request.user
                    logobject.modreason = "volumesCreation"
                    logobject.save()
                elif currentQuantity != int(yearVolume):
                    (
                        logobject,
                        logcreated,
                    ) = ProjectVolumePricesLog.objects.get_or_create(
                        project=project,
                        calenderYear=int(years[i]),
                        runTimestamp=runDate,
                    )
                    logobject.quantity = object.quantity
                    logobject.user = request.user
                    logobject.modreason = "volumesModification"
                    logobject.save()
                else:
                    pass

            for i in range(0, len(months), 1):
                volumeObjectM, created = ProjectVolumeMonth.objects.get_or_create(
                    project=project, calenderYear=int(years[i]), month=int(months[i])
                )
                currentQuantityM = volumeObjectM.quantity
                volumeObjectM.quantity = volumes[i]
                volumeObjectM.valid = True
                volumeObjectM.save()
                # volumesPost.append(f(int(years[0])+0.5+(i/12)))
                print(i)
                print(
                    created,
                    "---> volume month object,",
                    volumeObjectM,
                    "year",
                    volumeObjectM.calenderYear,
                    "mth",
                    volumeObjectM.month,
                    "qty",
                    volumeObjectM.quantity,
                )

                # create only a log entry on change
                if created == True:
                    logobject, logcreated = ProjectVolumeMonthLog.objects.get_or_create(
                        project=project,
                        calenderYear=int(years[i]),
                        runTimestamp=runDate,
                        month=int(months[i]),
                    )
                    logobject.quantity = volumes[i]
                    logobject.user = request.user
                    logobject.modreason = "volumesCreation"
                    logobject.save()
                elif currentQuantityM != volumes[i]:
                    logobject, logcreated = ProjectVolumeMonthLog.objects.get_or_create(
                        project=project,
                        calenderYear=int(years[i]),
                        runTimestamp=runDate,
                        month=int(months[i]),
                    )
                    logobject.quantity = volumes[i]
                    logobject.user = request.user
                    logobject.modreason = "volumesModification"
                    logobject.save()
                else:
                    pass

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

            if request.session["editMode"]:
                self.success_url = reverse_lazy(
                    "project_deepdive",
                    kwargs={"projectId": request.session["project_id"]},
                )
                # if not a draft (already in BoUp table), update BoUp table
                if project.draft == False:
                    self.success_url = reverse_lazy(
                        "boupEntryOverview",
                        kwargs={"projectId": request.session["project_id"]},
                    )
            if "save_n_continue" in request.POST:
                self.success_url = reverse_lazy("project_management_all_view")
            return redirect(self.success_url)

        else:
            print("form is not valid", form.errors)

            if project_id:
                project = Project.objects.get(id=project_id)
                estimatedSop = project.estimatedSop

                volumes = []
                years = []
                months = []
                dataCondition = 0

                objects = ProjectVolumeMonth.objects.filter(project=project).order_by(
                    "calenderYear", "month"
                )

                noneType = type(None)
                dataCondition = 1

                if objects.count() > 0:
                    for object in objects:
                        """
                        print(
                            object.calenderYear,
                            object.month,
                            " volume month read",
                            object.quantity,
                        )
                        """
                        if type(object.quantity) != noneType:
                            volumes.append(object.quantity)
                            months.append(object.month)
                            years.append(object.calenderYear)

                if len(volumes) == 0:
                    dataCondition = 0

                """
                prepare graphs to display planned quantities and order items 
                """
                yearsGraphs = [
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
                    2033,
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
                    2046,
                    2047,
                    2048,
                    2049,
                    2050,
                ]
                orders = [
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                ]
                plannedQuantities = [
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                ]

                allPlanedItemsObj = ProjectVolumePrices.objects.select_related()
                rfp = project.sales_name.rfp
                mainCustomer = project.mainCustomer
                endCustomer = project.finalCustomer

                allPlanedItemsObj = allPlanedItemsObj.filter(
                    project__sales_name__rfp=rfp,
                    valid=True,
                    quantity__gt=0,
                    project__mainCustomer=mainCustomer,
                    project__finalCustomer=endCustomer,
                )

                for obj in allPlanedItemsObj:
                    probability = 1.0

                    try:
                        probability = obj.project.status.status / 100
                    except:
                        pass

                    year = int(obj.calenderYear)
                    relevantIndex = yearsGraphs.index(year)
                    currentQuantity = plannedQuantities[relevantIndex]
                    newQuantity = currentQuantity + \
                        (obj.quantity * probability)
                    plannedQuantities[relevantIndex] = newQuantity

                allOrders = VrfcOrdersOnHand.objects.filter(
                    rfp=rfp, mainCustomerVrfc=mainCustomer, endCustomerVrfc=endCustomer
                )

                for obj in allOrders:
                    year = int(obj.year)
                    relevantIndex = yearsGraphs.index(year)
                    currentQuantity = orders[relevantIndex]
                    newQuantity = currentQuantity + obj.quantity
                    orders[relevantIndex] = newQuantity

                ################################
                initial_dict = {"startOfProductionYear": estimatedSop}
                context = {
                    "form": self.form_class(request.POST, initial=initial_dict),
                    "months": months,
                    "volumes": volumes,
                    "years": years,
                    "dataCondition": dataCondition,
                    "editMode": False,
                    "project": project,
                    "yearsGraph": yearsGraphs,
                    "orders": orders,
                    "plannedQuantities": plannedQuantities,
                }

                if request.session["editMode"]:
                    context = {
                        "form": self.form_class(request.POST, initial=initial_dict),
                        "months": months,
                        "volumes": volumes,
                        "years": years,
                        "dataCondition": dataCondition,
                        "editMode": True,
                        "projectId": request.session["project_id"],
                        "project": project,
                        "yearsGraph": yearsGraphs,
                        "orders": orders,
                        "plannedQuantities": plannedQuantities,
                    }

                print("rendering view with sop", estimatedSop)
                return render(request, self.template_name, context)

            """
            context = {"form": form, "editMode": False}

            if request.session["editMode"]:
                context = {
                    "form": form,
                    "editMode": True,
                    "projectId": request.session["project_id"],
                }

            return render(request, self.template_name, context)
            """


"""
class CreateVolumeExcelMonthView(LoginRequiredMixin, View):
    print("$$$$$ running CreateVolumeExcelView")
    template_name = "project/project_create_view/step2c_excelMonth.html"
    form_class = VolumeMonthForm
    success_url = reverse_lazy("create_pricing_view")

    # get does not change wrt to CreateVolumeExcelView
    def get(self, request, *args, **kwargs):
        project_id = request.session.get("project_id", None)
        if project_id:
            project = Project.objects.get(id=project_id)
            estimatedSop = project.estimatedSop
            initial_dict = {"startOfProduction": estimatedSop}
            context = {"form": self.form_class(initial=initial_dict)}
            print("rendering view with sop", estimatedSop)
            return render(request, self.template_name, context)
        else:
            return redirect(reverse("create_project_view"))

    def post(self, request, *args, **kwargs):
        project_id = request.session.get("project_id", None)
        project = Project.objects.get(id=project_id)
        estimatedSop = project.estimatedSop
        initial_dict = {"startOfProduction": estimatedSop}

        form = self.form_class(request.POST, initial=initial_dict)
        print("initialized form after post with project ID", project_id)

        if form.is_valid():
            print("form is valid!")
            project = Project.objects.get(id=project_id)
            project.user = request.user
            project.save()

            volumes = form.cleaned_data.get("volume")
            years = form.cleaned_data.get("years")
            months = form.cleaned_data.get("months")
            print(len(years))
            print("monthly data entry", months)
            # tbd...

        else:
            print("form is not valid", form.errors)
            context = {"form": form}
            return render(request, self.template_name, context)
"""


class CreateVolumeAutomaticView(LoginRequiredMixin, View):
    template_name = "project/project_create_view/step2b_automatic.html"
    form_class = VolumeAutomaticForm
    success_url = reverse_lazy("create_volume_customer_excel_view")

    def get(self, request, *args, **kwargs):
        # getting project instance that was created in first step
        project_id = request.session.get("project_id", None)
        if project_id:
            project = Project.objects.get(id=project_id)
            # getting estimated SOP from created project
            estimatedSop = project.estimatedSop

            currentVolumes = ProjectVolumePrices.objects.filter(
                project=project)
            yearsGraphs = [
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
                2033,
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
                2046,
                2047,
                2048,
                2049,
                2050,
            ]
            orders = [
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
            ]
            plannedQuantities = [
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
            ]

            """
            prepare graphs to display planned quantities and order items 
            """

            allPlanedItemsObj = ProjectVolumePrices.objects.select_related()
            rfp = project.sales_name.rfp
            mainCustomer = project.mainCustomer
            endCustomer = project.finalCustomer

            allPlanedItemsObj = allPlanedItemsObj.filter(
                project__sales_name__rfp=rfp,
                valid=True,
                quantity__gt=0,
                project__mainCustomer=mainCustomer,
                project__finalCustomer=endCustomer,
            )

            for obj in allPlanedItemsObj:
                probability = 1.0

                try:
                    probability = obj.project.status.status / 100
                except:
                    pass

                year = int(obj.calenderYear)
                relevantIndex = yearsGraphs.index(year)
                currentQuantity = plannedQuantities[relevantIndex]
                newQuantity = currentQuantity + (obj.quantity * probability)
                plannedQuantities[relevantIndex] = newQuantity

            allOrders = VrfcOrdersOnHand.objects.filter(
                rfp=rfp, mainCustomerVrfc=mainCustomer, endCustomerVrfc=endCustomer
            )

            for obj in allOrders:
                year = int(obj.year)
                print("getting year", year)
                relevantIndex = yearsGraphs.index(year)
                currentQuantity = orders[relevantIndex]
                newQuantity = currentQuantity + obj.quantity
                orders[relevantIndex] = newQuantity

            functionalWarnings = []

            if currentVolumes.count() > 0:
                redirectUrl = reverse("create_volume_select_view")
                warningString = "We already encountered volume data for this project. If you continue using this form you will overwrite the existing data. In order to review the current data, please follow"
                warningString = (
                    warningString + '<a href="' + redirectUrl + '"> this link.</a>'
                )

                # 'You already created a project draft. Please edit it under <a href="{0}">this link</a>.').format(redirectUrl)
                functionalWarnings.append(warningString)

            # feeding that sop to startOfProduction field
            initial_dict = {"startOfProduction": estimatedSop}
            context = {
                "form": self.form_class(initial=initial_dict),
                "functionalWarnings": functionalWarnings,
                "editMode": False,
                "yearsGraphs": yearsGraphs,
                "orders": orders,
                "plannedQuantities": plannedQuantities,
            }

            if request.session["editMode"]:
                context = {
                    "form": self.form_class(initial=initial_dict),
                    "functionalWarnings": functionalWarnings,
                    "editMode": True,
                    "projectId": request.session["project_id"],
                    "yearsGraphs": yearsGraphs,
                    "orders": orders,
                    "plannedQuantities": plannedQuantities,
                }

                if (project.is_viewing == True) & (
                    project.is_viewing_user != request.user
                ):
                    print(
                        "%%%%%%%%%%%%%%%%%% project is locked for editing",
                        project.is_viewing,
                    )

                    self.success_url = reverse_lazy(
                        "project_deepdive",
                        kwargs={"projectId": request.session["project_id"]},
                    )
                    messages.error(
                        request, "The project is locked for editing by another user."
                    )

                    return redirect(self.success_url)

            return render(request, self.template_name, context)
        else:
            return redirect(reverse("create_project_view"))

    def post(self, request, *args, **kwargs):
        project_id = request.session.get("project_id", None)
        project = Project.objects.get(id=project_id)
        estimatedSop = project.estimatedSop

        # feeding that sop to startOfProduction field
        initial_dict = {"startOfProduction": estimatedSop}
        context = {"form": self.form_class(initial=initial_dict)}
        form = self.form_class(request.POST, initial=initial_dict)

        if form.is_valid():
            project.user = request.user
            project.save()

            # process the data submitted in the form...
            # following data will be extracted after running clean method defined under VolumeForm in forms.py file
            # field_value = form.cleaned_data.get("field_name")
            print("prices form is valid!")
            excelData = form.cleaned_data.get("excelData")

            # here automatic volume distribution
            print("starting interpolation routine!!!")
            excelData = form.cleaned_data.get("excelData")

            sop = int(estimatedSop)
            # request.POST.get("endOfProduction") # volumeAutomaticForm.endOfProduction
            eop = int(form.cleaned_data.get("endOfProduction"))
            # initialVolume = request.POST.get("initialVolume") # volumeAutomaticForm.initialVolume
            # peakVolume = request.POST.get("peakVolume")  #volumeAutomaticForm.peakVolume
            # request.POST.get("peakYear")  #volumeAutomaticForm.peakYear
            peakYear = int(form.cleaned_data.get("peakYear"))
            # distributionType = request.POST.get("distributionType") # volumeAutomaticForm.distributionType
            # request.POST.get("totalVolume")
            totalVolume = int(form.cleaned_data.get("totalVolume"))
            print(
                "sop, eop, initialVolume, peakVolume, peakYear, distributionType, totalVolume--------->",
                sop,
                eop,
                peakYear,
                totalVolume,
            )

            """
            if sop != None:
                sop = int(sop)
                if int(sop) != sop:
                    print("sop changed!!")
                    project.estimatedSop = int(sop)
                    project.save()
            """

            #########
            print("starting interpolation!!!")
            # for distribution on year level
            monthLevel = False
            if monthLevel == False:
                interpolationResults = interpolator(
                    int(sop),
                    int(eop),
                    None,
                    None,
                    int(peakYear),
                    None,
                    int(totalVolume),
                )
                print("interpolation results!!!", interpolationResults)

                """
                Feb 2023: new way of possion interpolation at monthly level
                """
                fullInterpolation = interpolatorMonthly(
                    int(sop), int(eop), int(totalVolume), int(peakYear)
                )

                newVolumes = []

                for index in range(1, len(fullInterpolation), 1):
                    if index % 11 == 0:
                        relevantChunk = fullInterpolation[(index-11):index]
                        print("relevant chunk", relevantChunk)
                        yearlySum = sum(relevantChunk)
                        newVolumes.append(yearlySum)

                print(sum(newVolumes), "%%%% new volumes, yearly", newVolumes)
                print("interpolation results month!!!", interpolationResultsMonth)
                interpolationResults = newVolumes
                interpolationResultsMonth = fullInterpolation

                # the interpolation result is an array... it's 0 element is of SoP year
                """
                commented out in Feb 23
                interpolationResultsMonth = yearToMonthPoissonSmoother(
                    int(sop), int(eop), int(totalVolume), int(peakYear)
                )
                """
             
                # if the interpolation succeeded, first disable all the existing volume entries for this project.
                currentVolumes = ProjectVolumePrices.objects.filter(
                    project=project)
                currentMonthVolumes = ProjectVolumeMonth.objects.filter(
                    project=project)
                currentVolumes.update(quantity=0)
                currentMonthVolumes.update(quantity=0)

                ##########
                # insert into volumes table
                years = []
                year = sop

                runDate = datetime.datetime.now(tz=timezone.utc)
                print(
                    "len interpolationResults",
                    interpolationResults,
                    "len",
                    len(interpolationResults),
                )
                for index in range(0, len(interpolationResults), 1):
                    quantity = int(interpolationResults[index])
                    volumeObject, created = ProjectVolumePrices.objects.get_or_create(
                        project=project, calenderYear=year
                    )
                    print("volume object", volumeObject, "quantity", quantity)
                    volumeObject.user = request.user
                    years.append(year)
                    year = year + 1
                    currentQuantity = volumeObject.quantity
                    volumeObject.quantity = quantity

                    volumeObject.valid = True
                    volumeObject.user = request.user

                    if created == False:
                        volumeObject.modifiedDate = datetime.datetime.now(
                            tz=timezone.utc
                        )
                    volumeObject.save()

                    project.modreason = "customerVolumes"
                    project.save()

                    # runDate = datetime.now(tz=timezone.utc)
                    # create log entry
                    # create only a log entry on change
                    if created == True:
                        (
                            logobject,
                            logcreated,
                        ) = ProjectVolumePricesLog.objects.get_or_create(
                            project=project,
                            calenderYear=int(year),
                            runTimestamp=runDate,
                        )
                        logobject.quantity = volumeObject.quantity
                        logobject.user = request.user
                        logobject.modreason = "volumesCreation"
                        logobject.save()
                    elif currentQuantity != quantity:
                        (
                            logobject,
                            logcreated,
                        ) = ProjectVolumePricesLog.objects.get_or_create(
                            project=project,
                            calenderYear=int(year),
                            runTimestamp=runDate,
                        )
                        logobject.quantity = volumeObject.quantity
                        logobject.user = request.user
                        logobject.modreason = "volumesModification"
                        logobject.save()
                    else:
                        pass

                """
                %%%%%%%%%%%%%%%%%%%%%%%%%%%% frage an patric -> warum ist die logik für year vs. monthly hier getrennt???
                """
                #########

                # the interpolation is an array of arrays... it's 0 element is of SoP year, its 0 0 element is first month of SoP
                ##########
                # insert into volumes month table
                year = sop
                month = 1
                runDate = datetime.datetime.now(tz=timezone.utc)
                for index in range(0, (eop - sop) * 12, 1):
                    if month == 13:
                        month = 1
                        year = year + 1

                    quantity = int(interpolationResultsMonth[index])
                    volumeObject, created = ProjectVolumeMonth.objects.get_or_create(
                        project=project, calenderYear=year, month=month
                    )
                    """
                    print(
                        "volume object",
                        volumeObject,
                        "created",
                        created,
                        "quantity",
                        quantity,
                    )
                    """

                    currentVolume = volumeObject.quantity
                    volumeObject.user = request.user
                    volumeObject.quantity = quantity
                    volumeObject.month = month
                    volumeObject.valid = True

                    if created == False:
                        volumeObject.modifiedDate = datetime.datetime.now(
                            tz=timezone.utc
                        )

                    volumeObject.save()
                    month = month + 1

                    # create only a log entry on change
                    if created == True:
                        (
                            logobject,
                            logcreated,
                        ) = ProjectVolumeMonthLog.objects.get_or_create(
                            project=project,
                            calenderYear=int(year),
                            runTimestamp=runDate,
                            month=int(month),
                        )
                        logobject.quantity = volumeObject.quantity
                        logobject.user = request.user
                        logobject.modreason = "volumesCreation"
                        logobject.save()
                    elif currentQuantity != volumeObject.quantity:
                        (
                            logobject,
                            logcreated,
                        ) = ProjectVolumeMonthLog.objects.get_or_create(
                            project=project,
                            calenderYear=int(year),
                            runTimestamp=runDate,
                            month=int(month),
                        )
                        logobject.quantity = volumeObject.quantity
                        logobject.user = request.user
                        logobject.modreason = "volumesModification"
                        logobject.save()
                    else:
                        pass

                project.modreason = "volumes"
                project.save()

                """
                %%%%%%%%%%%%%%%%%%%%%%%%%%%% frage an patrict -> warum ist die logik hier getrennt???
                """
            else:

                interpolationResults = yearToMonthPoissonSmoother(
                    sop, eop, totalVolume, peakYear
                )
                print("interpolation results!!!", interpolationResults)

                # the interpolation is an array of arrays... it's 0 element is of SoP year, its 0 0 element is first month of SoP
                ##########
                # insert into volumes month table
                year = sop
                month = 1
                runDate = datetime.now(tz=timezone.utc)
                for index in range(0, (eop - sop) * 12, 1):
                    if month == 13:
                        month = 1
                        year = year + 1

                    quantity = int(interpolationResults[index])
                    volumeObject, created = ProjectVolumeMonth.objects.get_or_create(
                        project=project, calenderYear=year, month=month
                    )
                    """
                    print(
                        "volume object",
                        volumeObject,
                        "created",
                        created,
                        "quantity",
                        quantity,
                    )
                    """

                    volumeObject.user = request.user
                    volumeObject.quantity = quantity
                    volumeObject.month = month
                    volumeObject.save()
                    month = month + 1

                    # runDate = datetime.now(tz=timezone.utc)
                    # create log entry
                    logobject, logcreated = ProjectVolumeMonthLog.objects.get_or_create(
                        project=project,
                        calenderYear=year,
                        runTimestamp=runDate,
                        month=month,
                    )
                    logobject.quantity = object.quantity
                    logobject.user = request.user
                    logobject.modreason = "volumes"
                    logobject.save()

                project.modreason = "volumes"
                project.save()

            # show volume confirmation screen!

            print("redirecting...")
            if request.session["editMode"]:
                self.success_url = reverse_lazy(
                    "project_deepdive",
                    kwargs={"projectId": request.session["project_id"]},
                )
                # if not a draft (already in BoUp table), update BoUp table
                if project.draft == False:
                    self.success_url = reverse_lazy(
                        "boupEntryOverview",
                        kwargs={"projectId": request.session["project_id"]},
                    )
            if "save_n_continue" in request.POST:
                self.success_url = reverse_lazy("project_management_all_view")
            return redirect(self.success_url)

        context = {"form": self.form_class(request.POST), "editMode": False}

        """
        prepare graphs to display planned quantities and order items 
        """
        yearsGraphs = [
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
            2033,
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
            2046,
            2047,
            2048,
            2049,
            2050,
        ]
        orders = [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ]
        plannedQuantities = [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ]

        allPlanedItemsObj = ProjectVolumePrices.objects.select_related()
        rfp = project.sales_name.rfp
        mainCustomer = project.mainCustomer
        endCustomer = project.finalCustomer

        allPlanedItemsObj = allPlanedItemsObj.filter(
            project__sales_name__rfp=rfp,
            valid=True,
            quantity__gt=0,
            project__mainCustomer=mainCustomer,
            project__finalCustomer=endCustomer,
        )

        for obj in allPlanedItemsObj:
            probability = 1.0

            try:
                probability = obj.project.status.status / 100
            except:
                pass

            year = int(obj.calenderYear)
            relevantIndex = yearsGraphs.index(year)
            currentQuantity = plannedQuantities[relevantIndex]
            newQuantity = currentQuantity + (obj.quantity * probability)
            plannedQuantities[relevantIndex] = newQuantity

        allOrders = VrfcOrdersOnHand.objects.filter(
            rfp=rfp, mainCustomerVrfc=mainCustomer, endCustomerVrfc=endCustomer
        )

        for obj in allOrders:
            year = int(obj.year)
            relevantIndex = yearsGraphs.index(year)
            currentQuantity = orders[relevantIndex]
            newQuantity = currentQuantity + obj.quantity
            orders[relevantIndex] = newQuantity

        if request.session["editMode"]:
            context = {
                "form": self.form_class(request.POST),
                "editMode": True,
                "projectId": request.session["project_id"],
                "yearsGraph": yearsGraphs,
                "orders": orders,
                "plannedQuantities": plannedQuantities,
            }

        return render(request, self.template_name, context)


"""
class CreateVolumeMonthExcelView(LoginRequiredMixin, View):
    print("$$$$$ running CreateVolumeMonthExcelView")
    template_name = "project/project_create_view/step2c.html"
    form_class = VolumeMonthForm
    success_url = reverse_lazy("create_pricing_view")

    def get(self, request, *args, **kwargs):

        # getting project instance that was created in first step
        project_id = request.session.get("project_id", None)
        if project_id:
            project = Project.objects.get(id=project_id)
            # getting estimated SOP from created project
            estimatedSop = project.estimatedSop
            # feeding that sop to startOfProduction field
            initial_dict = {"startOfProduction": estimatedSop}  # month empty
            context = {"form": self.form_class(initial=initial_dict)}
            print("rendering view with sop", estimatedSop)
            return render(request, self.template_name, context)
        else:
            return redirect(reverse("create_project_view"))

    def post(self, request, *args, **kwargs):
        project_id = request.session.get("project_id", None)
        project = Project.objects.get(id=project_id)
        estimatedSop = project.estimatedSop
        initial_dict = {"startOfProductionYear": estimatedSop}

        form = self.form_class(request.POST, initial=initial_dict)
        print("initialized form after post with project ID", project_id)
        if form.is_valid():
            # process the data submitted in the form...
            # following data will be extracted after running clean method defined under VolumeForm in forms.py file
            # field_value = form.cleaned_data.get("field_name")
            print("form is valid!")
            project = Project.objects.get(id=project_id)
            excelData = form.cleaned_data.get("excelData")
            excelData = excelData.strip()
            project.user = request.user
            project.save()

            years, months, outputData, errorMutableSequence = checkExcelFormMonthInput(
                excelData=excelData, dataType=TypeOfParameter.volumes, sopYear=project.estimatedSop)

            if len(errorMutableSequence) == 0:
                volumes = outputData
                years = list(set(years)).sort()  # to make list unique
                print(len(years))
                volumesPost = []
                year = 0
                for i in range(0, (len(years))*12, 1):

                    if i != 0 and i % 12 == 0:
                        # print(int(years[year]), "----", int(volumes[i]))
                        year = year + 1
                    month = (i % 12)+1  # +1 so we dont have the 0th month
                    volumeObjectM, created = ProjectVolumeMonth.objects.get_or_create(
                        project=project, calenderYear=int(years[year]), month=month)
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

                if (deltaYearsEnd > 0):
                    for i in range(0, deltaYearsEnd, 1):
                        volumesPost.append(0)
                        print("##")

            return redirect(self.success_url)
        else:

            context = {"form": form}
            return render(request, self.template_name, context)
"""


class CreatePricingView(LoginRequiredMixin, View):
    template_name = "project/project_create_view/step3.html"
    form_class = PricingForm
    success_url = reverse_lazy("project_overviewB")

    def get(self, request, *args, **kwargs):
        print("%% getting pricing view")
        project_id = request.session.get("project_id", None)
        project = Project.objects.get(id=project_id)

        """
        currency = forms.ChoiceField(choices=(("USD", "USD"), ("EUR", "EURO")))
        price_commitment_until = forms.IntegerField(min_value=2020, max_value=2050)
        startOfProduction = forms.DecimalField(label="SoP Year", required=False)

        comment = forms.CharField(required=False)



        project.familyPriceApplicable = familyPrices
        project.familyPriceDetails = priceComments
        priceTypeObj = PriceStatus.objects.get(priceType=priceType)
        project.priceType = priceTypeObj
        project.save()
        """

        # check if prices are already existing for this project. if yes, prefill the jexcel with it.
        prices = []
        volumes = []
        years = []
        dataCondition = 0
        priceValidUntil = None
        priceComment = None
        currencyProject = None

        try:
            objects = (
                ProjectVolumePrices.objects.filter(
                    project=project, valid=True, quantity__gt=0
                )
                | (
                    ProjectVolumePrices.objects.filter(
                        project=project, valid=True, price__gt=0
                    )
                )
            ).order_by("calenderYear")

            noneType = type(None)

            if objects.count() > 0:
                dataCondition = 1
                for object in objects:
                    if type(object.price) != noneType:
                        prices.append(float(object.price))
                        volumes.append(float(object.quantity))
                        years.append(object.calenderYear)
                    priceValidUntil = object.priceValidityUntil
                    priceComment = object.priceSourceComment
                    currencyProject = object.currency

        except:
            messages.error(
                request,
                "A misc error happened while preparing data. Please ensure you have created volumes before entering prices.",
            )

        # to avoid problem with empty prices
        if (len(prices) == 0) | (len(years) == 0):
            dataCondition = 0
            messages.error(
                request,
                "A misc error happened while preparing data. Please ensure you have created volumes before entering prices.",
            )

        print("volumes", volumes, "lens", len(prices), len(years))
        # feeding that sop to startOfProduction field
        initial_dict = {
            "startOfProduction": project.estimatedSop,
            "priceType": project.priceType,
            "familyPrices": project.familyPriceApplicable,
            "price_commitment_until": priceValidUntil,
            "comment": priceComment,
        }

        print(
            "lean yeears",
            len(years),
            "years values",
            years,
            "resulting data condition",
            dataCondition,
            "len prices",
            len(prices),
            "prices",
            prices,
        )

        context = {
            "form": self.form_class(initial=initial_dict),
            "prices": prices,
            "years": years,
            "dataCondition": dataCondition,
            "volumes": volumes,
            "editMode": False,
            "projectId": project_id,
        }

        if request.session["editMode"]:

            fxRate = 1.0

            if (project.is_viewing == True) & (project.is_viewing_user != request.user):
                print(
                    "%%%%%%%%%%%%%%%%%% project is locked for editing",
                    project.is_viewing,
                )

                self.success_url = reverse_lazy(
                    "project_deepdive",
                    kwargs={"projectId": request.session["project_id"]},
                )
                messages.error(
                    request, "The project is locked for editing by another user."
                )

                return redirect(self.success_url)

            fxErrorPrices = False
            currencyObj = None

            try:
                """
                currencyObj = Currencies.objects.select_related().get(
                    currency=currencyProject
                )
                fxObject = ExchangeRates.objects.get(
                    currency=currencyObj, valid=True)
                fxRate = fxObject.rate
                """
                from currencies.models import Currency
                fxObject = float(Currency.objects.get(code=currencyProject).factor)
            except:
                fxErrorPrices = True

            if fxErrorPrices == True:
                fxRate = "N/A"
                currencyObj = "N/A"

            context = {
                "form": self.form_class(initial=initial_dict),
                "prices": prices,
                "years": years,
                "dataCondition": dataCondition,
                "volumes": volumes,
                "editMode": True,
                "projectId": request.session["project_id"],
                "fxRate": fxRate,
                "projectId": project_id,
                "contractualCurrency": currencyObj,
            }

        # context = {"form": self.form_class(initial=initial_dict)}
        # context = {"form": self.form_class()}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        project_id = request.session.get("project_id", None)
        project = Project.objects.get(id=project_id)
        initial_dict = {"startOfProduction": project.estimatedSop}
        print("initial dict pricing form", initial_dict)
        form = self.form_class(request.POST, initial=initial_dict)
        print("form initialized", initial_dict)

        if form.is_valid():
            # process the data submitted in the form...
            # following data will be extracted after running clean method defined under VolumeForm in forms.py file
            # field_value = form.cleaned_data.get("field_name")

            # to do: check that for all valid entries of volumes there is also a price entered... otherwise raise exception.

            print("using request user", request.user)
            project.user = request.user

            prices = form.cleaned_data.get("prices")
            years = form.cleaned_data.get("years")
            prices = form.cleaned_data.get("prices")
            currencyInput = form.cleaned_data.get("currency")
            priceValidUntil = form.cleaned_data.get("price_commitment_until")
            priceComments = form.cleaned_data.get("comment")
            familyPrices = form.cleaned_data.get("familyPrices")
            priceType = form.cleaned_data.get("priceType")
            familyPriceComment = form.cleaned_data.get("familyPriceComment")

            """
            if automatic pricing was used, we will have to delete existing prices and overwrite by the selected choice
            """

            useAutomaticPricing = form.cleaned_data.get("useAutomaticPricing")

            runDate = datetime.datetime.now(tz=timezone.utc)

            # reset all prices
            currentPrices = ProjectVolumePrices.objects.filter(project=project)
            currentPrices.update(
                price=0.0,
                priceValidityUntil=0,
                priceSourceComment="",
                currency=currencyInput,
            )

            project.familyPriceApplicable = familyPrices
            project.familyPriceApplicable = familyPrices
            project.familyPriceDetails = familyPriceComment
            project.otherPriceComments = priceComments
            priceTypeObj = PriceStatus.objects.get(priceType=priceType)
            project.priceType = priceTypeObj

            if useAutomaticPricing == True:
                if currentPrices.count() == 0:
                    excelData = request.POST.get("excelData")
                    years = []
                    prices = []
                    dataCondition = 0
                    print("excelData", excelData)
                    print("$$$$$$$$$ reloading pricing form")
                    volumes = []

                    try:
                        yearsA, pricesA = excelData.split("\n")
                        print("excelData", excelData)
                        years = yearsA.strip().split(",")
                        prices = pricesA.strip().split(",")
                        prices = [float(x) for x in prices]
                        years = [float(x) for x in years]
                        print("years", years, "prices", prices)
                        dataCondition = 1
                        noneType = type(None)

                        try:
                            objects = ProjectVolumePrices.objects.filter(
                                project=project
                            ).order_by("calenderYear")
                            if objects.count() > 0:
                                for object in objects:
                                    if type(object.quantity) != noneType:
                                        volumes.append(float(object.quantity))
                        except:
                            pass

                    except:
                        print("failed completely to recover entered data... sorry")
                        try:
                            objects = ProjectVolumePrices.objects.filter(
                                project=project
                            ).order_by("calenderYear")

                            noneType = type(None)
                            if objects.count() > 0:
                                dataCondition = 1
                                for object in objects:
                                    if type(object.price) != noneType:
                                        prices.append(float(object.price))
                                    years.append(object.calenderYear)
                                    if type(object.quantity) != noneType:
                                        volumes.append(float(object.quantity))
                        except:
                            pass
                    if dataCondition == 1:
                        if len(years) == 0:
                            dataCondition = 0
                    print(
                        "lean yeears",
                        len(years),
                        "resulting data condition",
                        dataCondition,
                    )

                    context = {
                        "form": self.form_class(request.POST, initial=initial_dict),
                        "dataCondition": dataCondition,
                        "prices": prices,
                        "years": years,
                        "volumes": volumes,
                        "editMode": False,
                        "projectId": project.id,
                    }

                    if request.session["editMode"]:
                        context = {
                            "form": self.form_class(request.POST, initial=initial_dict),
                            "dataCondition": dataCondition,
                            "prices": prices,
                            "years": years,
                            "volumes": volumes,
                            "editMode": True,
                            "projectId": request.session["project_id"],
                        }

                    messages.error(
                        request,
                        "Failed to compute automatic pricing. Please ensure that you have completed project details such as quantities before continuing.",
                    )

                    # context = {"form": form}
                    return render(request, self.template_name, context)

                declineIncrease = form.cleaned_data.get("declineIncrease")
                initialPrice = form.cleaned_data.get("initialPrice")
                priceChange = float(form.cleaned_data.get("priceChange"))

                # years have to be generated based on existing volume entries
                years = []
                prices = []
                sopYear = project.estimatedSop
                lastYear = currentPrices.aggregate(Max("calenderYear"))
                lastYear = int(lastYear["calenderYear__max"])
                years = [year for year in range(sopYear, (lastYear + 1))]
                print("inital price", initialPrice, type(initialPrice))
                lastPrice = initialPrice
                for year in years:
                    if year == sopYear:
                        prices.append(initialPrice)
                    else:
                        factor = 1.0

                        if declineIncrease == False:
                            factor = 1.0 - priceChange / 100
                        else:
                            factor = 1.0 + priceChange / 100

                        newPrice = float(lastPrice) * factor
                        prices.append(newPrice)
                        print(
                            "updating price",
                            newPrice,
                            "factor",
                            factor,
                            "pricechange",
                            priceChange,
                            "year",
                            year,
                        )
                        lastPrice = newPrice

                for i in range(0, (len(years)), 1):
                    object, created = ProjectVolumePrices.objects.get_or_create(
                        project=project, calenderYear=int(years[i])
                    )

                    currentPrice = float(object.price)
                    object.price = float(prices[i])
                    object.currency = currencyInput
                    object.priceValidityUntil = priceValidUntil
                    object.priceSourceComment = priceComments
                    object.user = request.user
                    object.save()

                    print("---------> prices object updating", object.quantity)

                    # runDate = datetime.now(tz=timezone.utc)
                    # create log entry
                    if created == True:
                        (
                            logobject,
                            logcreated,
                        ) = ProjectVolumePricesLog.objects.get_or_create(
                            project=project,
                            calenderYear=int(years[i]),
                            runTimestamp=runDate,
                        )
                        logobject.price = object.price
                        logobject.currency = object.currency
                        logobject.user = request.user
                        logobject.modreason = "pricesCreation"
                        logobject.save()
                    elif currentPrice != object.price:
                        (
                            logobject,
                            logcreated,
                        ) = ProjectVolumePricesLog.objects.get_or_create(
                            project=project,
                            calenderYear=int(years[i]),
                            runTimestamp=runDate,
                        )
                        logobject.price = object.price
                        logobject.currency = object.currency
                        logobject.user = request.user
                        logobject.modreason = "pricesModification"
                        logobject.save()
                    else:
                        pass

            else:
                print("no auto pricing")

                for i in range(0, (len(years)), 1):
                    object, created = ProjectVolumePrices.objects.get_or_create(
                        project=project, calenderYear=int(years[i])
                    )
                    currentPrice = float(object.price)
                    object.price = float(prices[i])
                    object.currency = currencyInput

                    object.priceValidityUntil = priceValidUntil
                    object.priceSourceComment = priceComments
                    object.user = request.user
                    object.save()

                    print("---------> prices object updating", object.quantity)

                    # runDate = datetime.now(tz=timezone.utc)
                    # create log entry
                    if created == True:
                        (
                            logobject,
                            logcreated,
                        ) = ProjectVolumePricesLog.objects.get_or_create(
                            project=project,
                            calenderYear=int(years[i]),
                            runTimestamp=runDate,
                        )
                        logobject.price = object.price
                        logobject.currency = object.currency
                        logobject.user = request.user
                        logobject.modreason = "pricesCreation"
                        logobject.save()
                    elif currentPrice != object.price:
                        (
                            logobject,
                            logcreated,
                        ) = ProjectVolumePricesLog.objects.get_or_create(
                            project=project,
                            calenderYear=int(years[i]),
                            runTimestamp=runDate,
                        )
                        logobject.price = object.price
                        logobject.currency = object.currency
                        logobject.user = request.user
                        logobject.modreason = "pricesModification"
                        logobject.save()
                    else:
                        pass

                project.contractualCurrency = currencyInput
                project.modreason = "prices"
                project.save()

            context = {}

            if request.session["editMode"]:
                self.success_url = reverse_lazy(
                    "project_deepdive",
                    kwargs={"projectId": request.session["project_id"]},
                )

                # if not a draft (already in BoUp table), update BoUp table
                if project.draft == False:
                    self.success_url = reverse_lazy(
                        "boupEntryOverview",
                        kwargs={"projectId": request.session["project_id"]},
                    )
            if "save_n_continue" in request.POST:
                self.success_url = reverse_lazy("project_management_all_view")
            return redirect(self.success_url)

        else:
            print("form is not valid")
            excelData = request.POST.get("excelData")
            years = []
            prices = []
            dataCondition = 0
            print("excelData", excelData)
            print("$$$$$$$$$ reloading pricing form")
            volumes = []

            try:
                yearsA, pricesA = excelData.split("\n")
                print("excelData", excelData)
                years = yearsA.strip().split(",")
                prices = pricesA.strip().split(",")
                prices = [float(x) for x in prices]
                years = [float(x) for x in years]
                print("years", years, "prices", prices)
                dataCondition = 1
                noneType = type(None)

                try:
                    objects = ProjectVolumePrices.objects.filter(
                        project=project
                    ).order_by("calenderYear")
                    if objects.count() > 0:
                        for object in objects:
                            if type(object.quantity) != noneType:
                                volumes.append(float(object.quantity))
                except:
                    pass

            except:
                print("failed completely to recover entered data... sorry")
                try:
                    objects = ProjectVolumePrices.objects.filter(
                        project=project
                    ).order_by("calenderYear")

                    noneType = type(None)
                    if objects.count() > 0:
                        dataCondition = 1
                        for object in objects:
                            if type(object.price) != noneType:
                                prices.append(float(object.price))
                            years.append(object.calenderYear)
                            if type(object.quantity) != noneType:
                                volumes.append(float(object.quantity))
                except:
                    pass
            if dataCondition == 1:
                if len(years) == 0:
                    dataCondition = 0
            print("lean yeears", len(years),
                  "resulting data condition", dataCondition)

            context = {
                "form": self.form_class(request.POST, initial=initial_dict),
                "dataCondition": dataCondition,
                "prices": prices,
                "years": years,
                "volumes": volumes,
                "editMode": False,
                "projectId": project.id,
            }

            if request.session["editMode"]:
                context = {
                    "form": self.form_class(request.POST, initial=initial_dict),
                    "dataCondition": dataCondition,
                    "prices": prices,
                    "years": years,
                    "volumes": volumes,
                    "editMode": True,
                    "projectId": request.session["project_id"],
                }

            # context = {"form": form}
            return render(request, self.template_name, context)

        print("raised validaiton error?")


"""
used for filtering end customers based on selected main customer
"""


@csrf_exempt
def end_customers_list_json(request):
    if request.method == "POST":
        query = request.POST.get("query")
        # the query is the selected main customer
        mainCustomer = MainCustomers.objects.get(id=query)
        print("main customers query", query, mainCustomer)
        #
        endCustomersList = mainCustomer.finalCustomers.values_list(
            "id", flat=True)
        print("endcustomers list", endCustomersList)
        if endCustomersList.count() > 0:
            asd1 = FinalCustomers.objects.filter(id__in=endCustomersList)
            print("asd 1", asd1)
            endCustomers = (
                FinalCustomers.objects.filter(
                    id__in=endCustomersList, valid=True)
                .annotate(text=F("finalCustomerName"))
                .values("id", "text")
            )
            print("endcustomers list 2", endCustomers)
            return JsonResponse({"data": list(endCustomers)}, safe=True)
        return JsonResponse({}, safe=True)


"""
def series_list_json(request):
    if request.method == "POST":
        query = request.POST.get("query")
        print("series list query", query)
        if query:
            product_series = (
                ProductSeries.objects.filter(family__id=query)
                .annotate(text=F("series"))
                .values("id", "text")
            )
            return JsonResponse({"data": list(product_series)}, safe=True)
        return JsonResponse({}, safe=True)
"""


@csrf_exempt
def series_list_json(request):
    if request.method == "POST":
        query = request.POST.get("query")
        print("series list query", query)
        # get a list of series
        if query:

            product_series = (
                Product.objects.filter(familyHelper=query)
                .distinct()
                .order_by("seriesHelper")
                .annotate(text=F("seriesHelper"))
                .values("familyHelper", "text")
            )

            """
            product_series = (
                ProductSeries.objects.filter(family__id=query)
                .annotate(text=F("series"))
                .values("id", "text")
            )
            """
            return JsonResponse({"data": list(product_series)}, safe=True)
        return JsonResponse({}, safe=True)


"""
@csrf_exempt
def package_list_json(request):
    if request.method == "POST":
        query = request.POST.get("query")
        print("package list query", query)
        if query:
            product_packages = (
                ProductPackage.objects.filter(series__id=query)
                .annotate(text=F("package"))
                .values("id", "text")
            )
            return JsonResponse({"data": list(product_packages)}, safe=True)
        return JsonResponse({}, safe=True)
"""


@csrf_exempt
def package_list_json(request):
    if request.method == "POST":
        print("req post", request.POST)
        family = request.POST.get("family")
        series = request.POST.get("series")
        print("package list query, series", family, series)

        if family:
            product_packages = (
                Product.objects.filter(
                    familyHelper=family, seriesHelper=series)
                .annotate(text=F("packageHelper"))
                .values("packageHelper", "seriesHelper", "familyHelper", "text")
            ).distinct()
            print("returning prod package", product_packages)
            print("list", list(product_packages))
            return JsonResponse({"data": list(product_packages)}, safe=True)
        return JsonResponse({}, safe=True)


@csrf_exempt
def hfg_info_json(request):
    if request.method == "POST":
        query = request.POST.get("query")
        if query:
            print("got query", query)
            salesNamesQuerySet = SalesName.objects.filter(id=query)

            hfg = "n/a"
            ppos = "n/a"
            product = "n/a"

            if salesNamesQuerySet.count() > 0:
                firstSalesName = salesNamesQuerySet.first()
                ppos = firstSalesName.rfp.ppos
                hfg = firstSalesName.rfp.hfg
                product = firstSalesName.rfp.rfp

            return JsonResponse(
                {"hfg": hfg, "ppos": ppos, "product": product}, safe=True
            )
        return JsonResponse({}, safe=True)


@csrf_exempt
def product_list_json(request):
    if request.method == "POST":
        package = request.POST.get("package")
        family = request.POST.get("family")
        series = request.POST.get("series")

        print("executing query", package, family, series)
        if package:
            products = (
                Product.objects.filter(
                    packageHelper=package, familyHelper=family, seriesHelper=series
                )
                .annotate(text=F("rfp"))
                .values("id", "text")
            )
            return JsonResponse({"data": list(products)}, safe=True)
        return JsonResponse({}, safe=True)


@csrf_exempt
def product_json(request):
    if request.method == "POST":
        query = request.POST.get("query")
        if query:
            product_ids = Product.objects.filter(package__package=query).values_list(
                "id", flat=True
            )

            salesNamesQuerySet = SalesName.objects.filter(
                rfp__id__in=product_ids)

            sales_names = salesNamesQuerySet.annotate(text=F("name")).values(
                "id", "text"
            )

            hfg = "n/a"
            ppos = "n/a"
            product = "n/a"

            if salesNamesQuerySet.count() > 0:
                firstSalesName = salesNamesQuerySet.first()
                ppos = firstSalesName.rfp.ppos
                hfg = firstSalesName.rfp.hfg
                product = firstSalesName.rfp.rfp

            return JsonResponse(
                {
                    "data": list(sales_names),
                },
                safe=True,
            )
        return JsonResponse({}, safe=True)


@csrf_exempt
def sales_name_json(request):
    if request.method == "POST":
        query = request.POST.get("query")
        print("executing sales name query based on product", query)
        if query:
            product_ids = Product.objects.filter(
                id=query).values_list("id", flat=True)
            print("resulting products id", product_ids)

            salesNamesQuerySet = SalesName.objects.filter(
                rfp__id__in=product_ids)

            sales_names = salesNamesQuerySet.annotate(text=F("name")).values(
                "id", "text"
            )

            print("resulting sales_names id", sales_names)

            hfg = "n/a"
            ppos = "n/a"
            product = "n/a"
            plHfg = "n/a"

            if salesNamesQuerySet.count() > 0:
                firstSalesName = salesNamesQuerySet.first()
                ppos = firstSalesName.rfp.ppos
                hfg = firstSalesName.rfp.hfg
                plHfg = firstSalesName.rfp.plHfg
                product = firstSalesName.rfp.rfp

            return JsonResponse(
                {
                    "data": list(sales_names),
                    "hfg": hfg,
                    "ppos": ppos,
                    "product": product,
                    "plHfg": plHfg
                },
                safe=True,
            )
        return JsonResponse({}, safe=True)


"""
check if there is already a project planed for the same final customer, sales name, main and detail application, sales name
conflictsSalesName
"""


@csrf_exempt
def checkInputPlausi(
    request, salesName, appMain, appDetail, mainCustomer, finalCustomer
):

    queryset = Project.objects.filter(
        sales_name=salesName,
        applicationMain=appMain,
        applicationDetail=appDetail,
        mainCustomer=mainCustomer,
        finalCustomer=finalCustomer,
        draft=False,
    )

    print(
        "checking conflicts at sales name level",
        salesName,
        appMain,
        appDetail,
        mainCustomer,
        finalCustomer,
    )
    if queryset.count() > 0:
        print("--> queryset checkInputPlausi", queryset)
        idList = [1]
        for object in queryset:
            idList.append(object.id)
        print("returning idlist", idList)
        return JsonResponse(
            {"conflictsSalesName": idList}, safe=True, status=status.HTTP_201_CREATED
        )

    else:
        print("empty queryset checkInputPlausi", salesName)

    return JsonResponse({"conflictsSalesName": []}, safe=True)


"""
check if there is already a project planed for the same final customer, sales name, main and detail application, rfp
conflict rfp warning
"""


@csrf_exempt
def checkInputPlausiRfpLevel(
    request, salesName, appMain, appDetail, mainCustomer, finalCustomer
):

    salesNameObj = SalesName.objects.get(id=salesName)
    rfp = salesNameObj.rfp

    queryset = Project.objects.filter(
        sales_name__rfp=rfp,
        applicationMain=appMain,
        applicationDetail=appDetail,
        mainCustomer=mainCustomer,
        finalCustomer=finalCustomer,
        draft=True,
    )
    print(
        "checking conflicts at rfp level",
        salesName,
        appMain,
        appDetail,
        mainCustomer,
        finalCustomer,
    )

    if queryset.count() > 0:
        print("--> queryset result checkInputPlausiRfpLevel", queryset)
        idList = [1]
        for object in queryset:
            idList.append(object.id)
        print("returning idlist", idList)
        return JsonResponse(
            {"conflictsRfp": idList}, safe=True, status=status.HTTP_201_CREATED
        )

    else:
        print("empty queryset checkInputPlausiRfpLevel", salesNameObj, "rfp", rfp)

    return JsonResponse({"conflictsRfp": []}, safe=True)


# for product configuration


@csrf_exempt
def hfgData(request):
    if request.method == "POST":
        print("hfg json", request.POST)
        query = request.POST.get("query")

        if query:
            print("got query hfg data", query[0])
            familyObj = ProductFamily.objects.get(id=query)
            family = familyObj.family_name
            # based on the product family, get all distinct HFGs, PPOS and Basic Types available.

            # SELECT DISTINCT "hfg", "ppos", "basicType"  FROM public."project_product"
            # sql = "SELECT DISTINCT 'hfg', 'ppos', 'basicType' FROM public.project_product WHERE 'familyHelper' = '" + family + "'"

            """
            --SELECT ppos FROM public.project_product WHERE "familyHelper" = 'AUTOPSOC'; -- funca
            --SELECT ppos FROM public.project_product WHERE 'familyHelper' = 'AUTOPSOC' -- no funca
            --SELECT DISTINCT hfg, ppos, basicType FROM public.project_product WHERE "familyHelper" = 'AUTOPSOC'; -- no funca
            SELECT DISTINCT hfg, ppos, "basicType" FROM public.project_product WHERE "familyHelper" = 'AUTOPSOC'; -- funca
            
            """
            # sql = 'SELECT DISTINCT hfg, ppos, "basicType" FROM public.project_product WHERE "familyHelper" = ' + "'" + family + "'"
            sql = (
                #                'SELECT DISTINCT hfg FROM public.project_product WHERE "familyHelper" = '  # postgresql
                'SELECT DISTINCT hfg FROM project_product WHERE "familyHelper" = '  # sqlite
                + "'"
                + family
                + "'"
            )

            print("raw sql", sql)

            distinctHfgs = rawSqlPerformer(sql)  # array of dictionaries
            print("unique distinctBoUpMcEcRfpCombinations", distinctHfgs)

            hfg = []

            i = 0
            for c in distinctHfgs:
                # print(c)
                hfg.append(c["hfg"])
                i = i + 1

            """
            seriesSelect = ProductSeries.objects.values('series').distinct().order_by(
                "series")

            product_ids = Product.objects.filter(package__package=query).values_list(
                "id", flat=True
            )
            print("product ids, plural", product_ids)
            sales_names = (
                SalesName.objects.filter(rfp__id__in=product_ids)
                .annotate(text=F("name"))
                .values("id", "text")
            )
            """
            print("returning", hfg)

            return JsonResponse({"hfg": hfg}, safe=True)
        return JsonResponse({}, safe=True)


@csrf_exempt
def pposData(request):
    if request.method == "POST":
        query = request.POST.get("query")
        print("ppos json", query)

        if query:
            print("got query of hfg", query)
            sql = (
                # 'SELECT DISTINCT ppos FROM public.project_product WHERE "hfg" = ' # postgresql
                'SELECT DISTINCT ppos FROM project_product WHERE "hfg" = '  # postgresql
                + "'"
                + query
                + "'"
            )
            distinctPpos = rawSqlPerformer(sql)  # array of dictionaries
            ppos = []

            i = 0
            for c in distinctPpos:
                # print(c)
                ppos.append(c["ppos"])
                i = i + 1

            print("returning", ppos)

            return JsonResponse({"ppos": ppos}, safe=True)
        return JsonResponse({}, safe=True)


@csrf_exempt
def basicTypeData(request):
    if request.method == "POST":
        query = request.POST.get("query")
        print("basicType json", query)

        if query:
            print("got query of ppos for basicType", query)
            sql = (
                # 'SELECT DISTINCT "basicType" FROM public.project_product WHERE "ppos" = ' # postgresql
                'SELECT DISTINCT "basicType" FROM project_product WHERE "ppos" = '
                + "'"
                + query
                + "'"
            )
            distinctbasicType = rawSqlPerformer(sql)  # array of dictionaries
            basicType = []
            i = 0
            for c in distinctbasicType:
                # print(c)
                basicType.append(c["basicType"])
                i = i + 1

            return JsonResponse({"basicType": basicType}, safe=True)
        return JsonResponse({}, safe=True)


"""
will create the entries in BoUp table
"""


class ProjectDeepdive(LoginRequiredMixin, View):
    template_name = "project/project_deepdive/overview.html"
    form_class = PricingForm
    success_url = reverse_lazy("create_volume_view")

    finalRevenue = []
    finalVolume = []
    finalPrice = []
    finalGrossMargin = []
    finalGrossMarginPct = []
    final_revenue_month = []
    final_grossMargin_month = []
    final_grossMarginPct_month = []
    finalVhk = []
    final_revenue_FY = []
    final_grossProfit_FY = []
    final_grossProfitPct_FY = []
    final_volumes_FY = []
    vhkCy = []
    finalTotalCost = []
    asp = []
    weightedGrossMargin = []
    weightedGrossMarginPct = []
    weightedRevenue = []
    weightedVolume = []

    def get(self, request, projectId, *args, **kwargs):


        request.session["project_id"] = projectId
        request.session["editMode"] = True
        request.session["keyFactsEdit"] = False

        """
        # clear project id from session

        try:
            del request.session["project_id"]
        except KeyError:
            pass
        """

        project = Project.objects.select_related().get(id=projectId)
        probability = 1

        try:
            probability = float(project.status.status) / 100.0
        except:
            pass

        (
            revenue,
            volumes,
            prices,
            grossMargin,
            grossMarginPct,
            revenue_month,
            grossMargin_month,
            grossMarginPct_month,
            vhk,
            revenue_FY,
            grossProfit_FY,
            grossProfitPct_FY,
            volumes_FY,
            VhkCy,
            totalCost,
            sumRevenue,
            sumGrossMargin,
            sumCost,
            years,
            errors,
            weightedGrossMargin,
            weightedGrossMarginPct,
            weightedRevenue,
            asp,
            weightedVolume,
            sumVolume,
            sumWeightedVolume,
            sumWeightedRevenue,
            averageAsp,
            sumWeightedGrossMargin,
            projectCurrency,
            fxRate,
        ) = getProjectOverview(projectId, request.user, probability, None)

        # now for front end purposes, trim years / prices / revenues / gross maring arrays to the first non zero element

        firstRev = 999
        firstVol = 999
        firstPrice = 999
        try:
            if len(revenue) > 0:
                firstRev = next(x for x, val in enumerate(revenue) if val > 0)
            if len(volumes) > 0:
                firstVol = next(x for x, val in enumerate(volumes) if val > 0)
            if len(prices) > 0:
                firstPrice = next(x for x, val in enumerate(prices) if val > 0)
            minFirst = min(firstRev, firstVol, firstPrice)
            print("!B")
            if (type(minFirst) == type(1)) & (minFirst != 999):
                revenue = revenue[minFirst:]
                volumes = volumes[minFirst:]
                prices = prices[minFirst:]
                grossMargin = grossMargin[minFirst:]
                years = years[minFirst:]
                weightedGrossMargin = weightedGrossMargin[minFirst:]
                weightedGrossMarginPct = weightedGrossMarginPct[minFirst:]
                weightedRevenue = weightedRevenue[minFirst:]
                weightedVolume = weightedVolume[minFirst:]
        except:
            pass

        # transfer
        self.finalRevenue = revenue
        self.finalVolume = volumes
        self.finalPrice = prices
        self.finalGrossMargin = grossMargin
        self.finalGrossMarginPct = grossMarginPct
        self.final_revenue_month = revenue_month
        self.final_grossMargin_month = grossMargin_month
        self.final_grossMarginPct_month = grossMarginPct_month
        self.finalVhk = vhk
        self.final_revenue_FY = revenue_FY
        self.final_grossProfit_FY = grossProfit_FY
        self.final_grossProfitPct_FY = grossProfitPct_FY
        self.final_volumes_FY = volumes_FY
        self.vhkCy = VhkCy
        self.finalTotalCost = totalCost
        self.asp = asp
        self.weightedVolume = weightedVolume

        if HighLevelProjectProblems.vhkError in errors:
            sumCost = "N/A"
            sumGrossMargin = "N/A"
            sumWeightedGrossMargin = "N/A"

        if HighLevelProjectProblems.fxError in errors:
            sumCost = "N/A"
            sumGrossMargin = "N/A"
            sumWeightedGrossMargin = "N/A"
            averageAsp = "N/A"
            sumWeightedRevenue = "N/A"
            sumRevenue = "N/A"

        if HighLevelProjectProblems.pricesAndVolumesMissingCompletely in errors:
            sumCost = "N/A"
            sumGrossMargin = "N/A"
            sumWeightedGrossMargin = "N/A"
            averageAsp = "N/A"
            sumWeightedRevenue = "N/A"
            sumRevenue = "N/A"
            sumVolume = "N/A"
            sumWeightedVolume = "N/A"

        if HighLevelProjectProblems.projectKeyFactsError in errors:
            sumCost = "N/A"
            sumGrossMargin = "N/A"
            sumWeightedGrossMargin = "N/A"
            averageAsp = "N/A"
            sumWeightedRevenue = "N/A"
            sumRevenue = "N/A"
            sumVolume = "N/A"
            sumWeightedVolume = "N/A"

        if HighLevelProjectProblems.pricesAreZero in errors:
            sumGrossMargin = "N/A"
            sumWeightedGrossMargin = "N/A"
            averageAsp = "N/A"
            sumWeightedRevenue = "N/A"
            sumRevenue = "N/A"

        if (HighLevelProjectProblems.volumeIsZero in errors) | (
            HighLevelProjectProblems.otherProjectIntegrityError in errors
        ):
            sumGrossMargin = "N/A"
            sumWeightedGrossMargin = "N/A"
            averageAsp = "N/A"
            sumWeightedRevenue = "N/A"
            sumRevenue = "N/A"
            sumVolume = "N/A"
            sumWeightedVolume = "N/A"

        if type(sumWeightedVolume) != type("thisIsAString"):
            sumWeightedVolume = int(round(sumWeightedVolume))

        if type(sumVolume) != type("thisIsAString"):
            sumVolume = int(round(sumVolume))

        if type(sumWeightedRevenue) != type("thisIsAString"):
            sumWeightedRevenue = int(round(sumWeightedRevenue, 0))

        if type(sumRevenue) != type("thisIsAString"):
            sumRevenue = int(round(sumRevenue, 0))

        if type(averageAsp) != type("thisIsAString"):
            averageAsp = round(averageAsp, 2)

        if type(sumGrossMargin) != type("thisIsAString"):
            sumGrossMargin = int(round(sumGrossMargin, 0))

        if type(sumWeightedGrossMargin) != type("thisIsAString"):
            sumWeightedGrossMargin = int(round(sumWeightedGrossMargin, 0))

        if type(sumCost) != type("thisIsAString"):
            sumCost = round(sumCost, 2)

        context = {
            "step": 0,
            "project": project,
            "revenue": revenue,
            "volumes": volumes,
            "weightedVolume": weightedVolume,
            "prices": prices,
            "grossMargin": grossMargin,
            "years": years,
            "projectLevelErrors": errors,
            "sumRevenue": sumRevenue,
            "sumGrossMargin": sumGrossMargin,
            "sumCost": sumCost,
            "sumVolume": sumVolume,
            "sumWeightedVolume": sumWeightedVolume,
            "sumWeightedRevenue": sumWeightedRevenue,
            "averageAsp": averageAsp,
            "sumWeightedGrossMargin": sumWeightedGrossMargin,
            "projectCurrency": projectCurrency,
            "fxRate": fxRate,
            "weightedGrossMargin": weightedGrossMargin,
            "weightedRevenue": weightedRevenue,
        }

        return render(request, self.template_name, context)


class ProjectDeepdiveHistory(DetailView):
    model = Project
    template_name = "project/project_deepdive/project_history.html"


class ProjectDeepdiveHistoryAjax(AjaxDatatableView):
    model = ProjectVolumePricesLog
    search_values_separator = "+"
    length_menu = [[10, 20, 50, 100], [10, 20, 50, 100]]

    column_defs = [
        {
            "name": "date",
            "title": "Date",
        },
        {
            "name": "user",
            "title": "User",
            "foreign_field": "user__username",
        },
        {
            "name": "modifiedDate",
            "title": "Modified Date",
        },
        {
            "name": "project",
            "title": "Project",
            "foreign_field": "project__projectName",
        },
        {
            "name": "valid",
            "title": "Valid",
            "choices": True,
            "autofilter": True,
        },
        {
            "name": "calenderYear",
            "title": "Calendar Year",
        },
        {
            "name": "quantity",
            "title": "Quantity",
        },
        {
            "name": "quantityCustomerEstimation",
            "title": "QTY EST",
        },
        {
            "name": "volumeComment",
            "title": "Volume Comment",
        },
        {
            "name": "source",
            "title": "Source",
        },
        {
            "name": "priceSource",
            "title": "Price Source",
        },
        {
            "name": "priceComment",
            "title": "Price Comment",
        },
        {
            "name": "currency",
            "title": "Currency",
        },
        {
            "name": "price",
            "title": "Price",
        },
        {
            "name": "priceValidityUntil",
            "title": "Price Validity Until",
        },
        {
            "name": "priceSourceComment",
            "title": "Price Source Comment",
        },
        {
            "name": "runTimestamp",
            "title": "Runtime Stamp",
        },
        {
            "name": "modreason",
            "title": "Mod Reason",
        },
    ]

    def get_initial_queryset(self, request=None):

        # We accept either GET or POST
        if not getattr(request, "REQUEST", None):
            request.REQUEST = request.GET if request.method == "GET" else request.POST

        queryset = self.model.objects.all()

        if "project_id" in request.REQUEST:
            project_id = int(request.REQUEST.get("project_id"))
            queryset = queryset.filter(project__id=project_id)

        return queryset


class ProjectOverview(LoginRequiredMixin, View):
    template_name = "project/project_create_view/step3.html"
    form_class = PricingForm
    success_url = reverse_lazy("create_volume_view")

    finalRevenue = []
    finalVolume = []
    finalPrice = []
    finalGrossMargin = []
    finalGrossMarginPct = []
    final_revenue_month = []
    final_grossMargin_month = []
    final_grossMarginPct_month = []
    finalVhk = []
    final_revenue_FY = []
    final_grossProfit_FY = []
    final_grossProfitPct_FY = []
    final_volumes_FY = []
    vhkCy = []
    finalTotalCost = []
    asp = []
    weightedGrossMargin = []
    weightedGrossMarginPct = []
    weightedRevenue = []
    weightedVolume = []

    def get(self, request, *args, **kwargs):

        projectId = request.session["project_id"]

        """
        # clear project id from session

        try:
            del request.session["project_id"]
        except KeyError:
            pass
        """
        # fetch vorherstellungskosten
        # to do on imports: check consistency of currencies; gaps of years

        project = Project.objects.get(id=projectId)
        try:
            probability = float(project.status.status) / 100.0
        except:
            probability = 0

        (
            revenue,
            volumes,
            prices,
            grossMargin,
            grossMarginPct,
            revenue_month,
            grossMargin_month,
            grossMarginPct_month,
            vhk,
            revenue_FY,
            grossProfit_FY,
            grossProfitPct_FY,
            volumes_FY,
            VhkCy,
            totalCost,
            sumRevenue,
            sumGrossMargin,
            sumCost,
            years,
            errors,
            weightedGrossMargin,
            weightedGrossMarginPct,
            weightedRevenue,
            asp,
            weightedVolume,
            sumVolume,
            sumWeightedVolume,
            sumWeightedRevenue,
            averageAsp,
            sumWeightedGrossMargin,
            projectCurrency,
            fxRate,
        ) = getProjectOverview(projectId, request.user, probability, None)
        # transfer
        self.finalRevenue = revenue
        self.finalVolume = volumes
        self.finalPrice = prices
        self.finalGrossMargin = grossMargin
        self.finalGrossMarginPct = grossMarginPct
        self.final_revenue_month = revenue_month
        self.final_grossMargin_month = grossMargin_month
        self.final_grossMarginPct_month = grossMarginPct_month
        self.finalVhk = vhk
        self.final_revenue_FY = revenue_FY
        self.final_grossProfit_FY = grossProfit_FY
        self.final_grossProfitPct_FY = grossProfitPct_FY
        self.final_volumes_FY = volumes_FY
        self.vhkCy = VhkCy
        self.finalTotalCost = totalCost
        self.asp = asp
        self.weightedVolume = weightedVolume

        # if keyword argument fatal error BoUp remotion / addendum, add here to the project level errors
        try:
            if self.kwargs["fatalErrorDraftInstance"]:
                errors.append(
                    "Fatal error while creating draft instance. Most likely, there is already a draft with the same combinaton of Main and End Customers, Main and Detail Application and Sales Name. You can only have a single draft for this combination of parameters."
                )
        except:
            pass

        context = {
            "step": 4,
            "projectId": projectId,
            "project": project,
            "revenue": revenue,
            "volumes": volumes,
            "prices": prices,
            "grossMargin": grossMargin,
            "years": years,
            "projectLevelErrors": errors,
            "sumRevenue": sumRevenue,
            "sumGrossMargin": sumGrossMargin,
            "sumCost": sumCost,
            "sumVolume": sumVolume,
            "sumWeightedVolume": sumWeightedVolume,
            "sumWeightedRevenue": sumWeightedRevenue,
            "averageAsp": averageAsp,
            "sumWeightedGrossMargin": sumWeightedGrossMargin,
        }

        return render(request, "project/project_create_view/step4.html", context)

    """
    upon post: 
    if the user wishes to, leave it as a draft in ProjectVolumePrices. (user clicks on a button with a link to the project list)
    If not, persist into BoUp definitely. (POST)
    """

    def post(self, request, *args, **kwargs):
        # request.session["project_id"] = 2
        projectId = request.session["project_id"]

        # params dict
        params = {
            "finalRevenue": self.finalRevenue,
            "finalVolume": self.finalVolume,
            "finalPrice": self.finalPrice,
            "finalGrossMargin": self.finalGrossMargin,
            "finalGrossMarginPct": self.finalGrossMarginPct,
            "final_revenue_month": self.final_revenue_month,
            "final_grossMargin_month": self.final_grossMargin_month,
            "final_grossMarginPct_month": self.final_grossMarginPct_month,
            "finalVhk": self.finalVhk,
            "final_revenue_FY": self.final_revenue_FY,
            "final_grossProfit_FY": self.final_grossProfit_FY,
            "final_grossProfitPct_FY": self.final_grossProfitPct_FY,
            "final_volumes_FY": self.final_volumes_FY,
            "vhkCy": self.vhkCy,
            "finalTotalCost": self.finalTotalCost,
            "asp": self.asp,
            "weightedGrossMargin": self.weightedGrossMargin,
            "weightedGrossMarginPct": self.weightedGrossMarginPct,
            "weightedRevenue": self.weightedRevenue,
            "weightedVolume": self.weightedVolume,
        }

        persistor = bottomUpPersistor(params)
        success, outputValues, message, nada = persistor.persist(
            projectId=projectId,
            request=request,
            bulk=False,
            boUpObjectInput=None,
            probability=1.0,
            helperObjects=None,
            vhkUpdate=False,
            runDate=None,
        )

        revenue = outputValues["revenue"]
        grossMargin = outputValues["grossMargin"]
        years = outputValues["years"]
        errors = outputValues["errors"]
        sumRevenue = outputValues["sumRevenue"]
        sumGrossMargin = outputValues["sumGrossMargin"]
        sumCost = outputValues["sumCost"]
        sumVolume = outputValues["sumVolume"]
        sumWeightedVolume = outputValues["sumWeightedVolume"]
        sumWeightedRevenue = outputValues["sumWeightedRevenue"]
        averageAsp = outputValues["averageAsp"]
        sumWeightedGrossMargin = outputValues["sumWeightedGrossMargin"]

        """
        project = Project.objects.get(id=projectId)
        probability = float(project.status.status) / 100.0

        if len(self.finalVolume) == 0:
            (
                revenue,
                volumes,
                prices,
                grossMargin,
                grossMarginPct,
                revenue_month,
                grossMargin_month,
                grossMarginPct_month,
                vhk,
                revenue_FY,
                grossProfit_FY,
                grossProfitPct_FY,
                volumes_FY,
                VhkCy,
                totalCost,
                sumRevenue,
                sumGrossMargin,
                sumCost,
                years,
                errors,
                weightedGrossMargin,
                weightedGrossMarginPct,
                weightedRevenue,
                asp,
                weightedVolume,
                sumVolume,
                sumWeightedVolume,
                sumWeightedRevenue,
                averageAsp,
                sumWeightedGrossMargin,
            ) = getProjectOverview(projectId, request.user, probability)
            # transfer
            self.finalRevenue = revenue
            self.finalVolume = volumes
            self.finalPrice = prices
            self.finalGrossMargin = grossMargin
            self.finalGrossMarginPct = grossMarginPct
            self.final_revenue_month = revenue_month
            self.final_grossMargin_month = grossMargin_month
            self.final_grossMarginPct_month = grossMarginPct_month
            self.finalVhk = vhk
            self.final_revenue_FY = revenue_FY
            self.final_grossProfit_FY = grossProfit_FY
            self.final_grossProfitPct_FY = grossProfitPct_FY
            self.final_volumes_FY = volumes_FY
            self.vhkCy = VhkCy
            self.finalTotalCost = totalCost
            self.weightedGrossMargin = weightedGrossMargin
            self.weightedGrossMarginPct = weightedGrossMarginPct
            self.weightedRevenue = weightedRevenue
            self.asp = asp
            self.weightedVolume = weightedVolume

        project.draft = False
        revenue = self.finalRevenue
        volumes = self.finalVolume
        prices = self.finalPrice
        grossMargin = self.finalGrossMargin
        grossMarginPct = self.finalGrossMarginPct
        revenue_month = self.final_revenue_month
        grossMargin_month = self.final_grossMargin_month
        grossMarginPct_month = self.final_grossMarginPct_month
        vhk = self.finalVhk
        revenue_FY = self.final_revenue_FY
        grossProfit_FY = self.final_grossProfit_FY
        grossProfitPct_FY = self.final_grossProfitPct_FY
        volumes_FY = self.final_volumes_FY
        VhkCy = self.vhkCy

        # create entry in BoUp TABLE
        start_time = time.time()
        if not project.oem:
            oem = ""
        else:
            oem = project.oem  # oem = project.oem.oemName

        statusProbability = float(project.status.status) / 100.0

        print("oem", oem)

        print("related object", project.projectvolumeprices)
        BoUpObject = None
        try:
            # based on unique key
            BoUpObject, created = BoUp.objects.get_or_create(
                applicationMain=project.applicationMain,
                applicationDetail=project.applicationDetail,
                mainCustomer=project.mainCustomer,
                endCustomer=project.finalCustomer,
                salesName=project.sales_name,
                productMarketer=project.productMarketer,
            )
            print("unique key created")

        except:
            print("... going to raise validation error")
            raise ValidationError("Major conflict in creation of bottom up entry.")

        try:
            BoUpObject.ID_APP = project
            BoUpObject.productMarketer = project.productMarketer
            BoUpObject.hfg = project.sales_name.rfp.hfg
            BoUpObject.ppos = project.sales_name.rfp.ppos
            BoUpObject.spNumber = project.spNumber
            BoUpObject.familyPriceApplicable = project.familyPriceApplicable
            BoUpObject.familyPriceDetails = project.familyPriceDetails
            BoUpObject.priceType = project.priceType
            BoUpObject.comment = project.comment
            # change all these to FK?
            BoUpObject.region = project.region.region
            BoUpObject.secondRegion = project.region.region
            BoUpObject.dcChannel = (
                project.dcChannel.dcChannelDescription if project.dcChannel else ""
            )
            BoUpObject.priceType = (
                project.priceType.priceTypeDisplay if project.priceType else ""
            )

            BoUpObject.projectName = project.projectName
            BoUpObject.distributor = project.distributor
            BoUpObject.tier1 = project.tier1
            BoUpObject.ems = project.ems
            BoUpObject.vpaCustomer = project.vpaCustomer
            BoUpObject.salesContact = project.salesContact
            BoUpObject.statusProbability = project.status.statusDisplay
            BoUpObject.probability = statusProbability
            BoUpObject.sop = project.estimatedSop
            BoUpObject.availablePGS = project.sales_name.rfp.availablePGS
            # project.user,#modifiedBy = project.user.username,
            BoUpObject.modifiedBy = request.user
            BoUpObject.modifiedDate = project.modifiedDate
            BoUpObject.creationDate = project.creationDate
            BoUpObject.package = project.sales_name.rfp.package.package
            BoUpObject.series = project.sales_name.rfp.package.series.series
            BoUpObject.rfp = project.sales_name.rfp
            BoUpObject.dummy = project.dummy
            BoUpObject.save()
        except:
            print("... going to raise second validation error")
            raise ValidationError("Detail conflict in creation of bottom up entry.")

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

        BoUpObject.wVol2020 = float(weightedVolume[0])
        BoUpObject.wVol2021 = float(weightedVolume[1])
        BoUpObject.wVol2022 = float(weightedVolume[2])
        BoUpObject.wVol2023 = float(weightedVolume[3])
        BoUpObject.wVol2024 = float(weightedVolume[4])
        BoUpObject.wVol2025 = float(weightedVolume[5])
        BoUpObject.wVol2026 = float(weightedVolume[6])
        BoUpObject.wVol2027 = float(weightedVolume[7])
        BoUpObject.wVol2028 = float(weightedVolume[8])
        BoUpObject.wVol2029 = float(weightedVolume[9])
        BoUpObject.wVol2030 = float(weightedVolume[10])
        BoUpObject.wVol2031 = float(weightedVolume[11])
        BoUpObject.wVol2032 = float(weightedVolume[12])
        BoUpObject.wVol2033 = float(weightedVolume[13])
        BoUpObject.wVol2034 = float(weightedVolume[14])
        BoUpObject.wVol2035 = float(weightedVolume[15])
        BoUpObject.wVol2036 = float(weightedVolume[16])
        BoUpObject.wVol2037 = float(weightedVolume[17])
        BoUpObject.wVol2038 = float(weightedVolume[18])
        BoUpObject.wVol2039 = float(weightedVolume[19])
        BoUpObject.wVol2040 = float(weightedVolume[20])
        BoUpObject.wVol2041 = float(weightedVolume[21])
        BoUpObject.wVol2042 = float(weightedVolume[22])
        BoUpObject.wVol2043 = float(weightedVolume[23])
        BoUpObject.wVol2044 = 0.0

        BoUpObject.wRev2020 = weightedRevenue[0]
        BoUpObject.wRev2021 = weightedRevenue[1]
        BoUpObject.wRev2022 = weightedRevenue[2]
        BoUpObject.wRev2023 = weightedRevenue[3]
        BoUpObject.wRev2024 = weightedRevenue[4]
        BoUpObject.wRev2025 = weightedRevenue[5]
        BoUpObject.wRev2026 = weightedRevenue[6]
        BoUpObject.wRev2027 = weightedRevenue[7]
        BoUpObject.wRev2028 = weightedRevenue[8]
        BoUpObject.wRev2029 = weightedRevenue[9]
        BoUpObject.wRev2030 = weightedRevenue[10]
        BoUpObject.wRev2031 = weightedRevenue[11]
        BoUpObject.wRev2032 = weightedRevenue[12]
        BoUpObject.wRev2033 = weightedRevenue[13]
        BoUpObject.wRev2034 = weightedRevenue[14]
        BoUpObject.wRev2035 = weightedRevenue[15]
        BoUpObject.wRev2036 = weightedRevenue[16]
        BoUpObject.wRev2037 = weightedRevenue[17]
        BoUpObject.wRev2038 = weightedRevenue[18]
        BoUpObject.wRev2039 = weightedRevenue[19]
        BoUpObject.wRev2040 = weightedRevenue[20]
        BoUpObject.wRev2041 = weightedRevenue[21]
        BoUpObject.wRev2042 = weightedRevenue[22]
        BoUpObject.wRev2043 = weightedRevenue[23]
        BoUpObject.wRev2044 = 0.0

        # now ASP and weighted gross margin:   asp = weighted revenue / weighted volume. weighted gross margin = weighted revenue - weighted volume * cost per unit (aka VHK)
        BoUpObject.wGrossMargin2020 = weightedGrossMargin[0]
        BoUpObject.wGrossMargin2021 = weightedGrossMargin[1]
        BoUpObject.wGrossMargin2022 = weightedGrossMargin[2]
        BoUpObject.wGrossMargin2023 = weightedGrossMargin[3]
        BoUpObject.wGrossMargin2024 = weightedGrossMargin[4]
        BoUpObject.wGrossMargin2025 = weightedGrossMargin[5]
        BoUpObject.wGrossMargin2026 = weightedGrossMargin[6]
        BoUpObject.wGrossMargin2027 = weightedGrossMargin[7]
        BoUpObject.wGrossMargin2028 = weightedGrossMargin[8]
        BoUpObject.wGrossMargin2029 = weightedGrossMargin[9]
        BoUpObject.wGrossMargin2030 = weightedGrossMargin[10]
        BoUpObject.wGrossMargin2031 = weightedGrossMargin[11]
        BoUpObject.wGrossMargin2032 = weightedGrossMargin[12]
        BoUpObject.wGrossMargin2033 = weightedGrossMargin[13]
        BoUpObject.wGrossMargin2034 = weightedGrossMargin[14]
        BoUpObject.wGrossMargin2035 = weightedGrossMargin[15]
        BoUpObject.wGrossMargin2036 = weightedGrossMargin[16]
        BoUpObject.wGrossMargin2037 = weightedGrossMargin[17]
        BoUpObject.wGrossMargin2038 = weightedGrossMargin[18]
        BoUpObject.wGrossMargin2039 = weightedGrossMargin[19]
        BoUpObject.wGrossMargin2040 = weightedGrossMargin[20]
        BoUpObject.wGrossMargin2041 = weightedGrossMargin[21]
        BoUpObject.wGrossMargin2042 = weightedGrossMargin[22]
        BoUpObject.wGrossMargin2043 = weightedGrossMargin[23]
        BoUpObject.wGrossMargin2044 = 0.0

        BoUpObject.asp2020 = asp[0]
        BoUpObject.asp2021 = asp[1]
        BoUpObject.asp2022 = asp[2]
        BoUpObject.asp2023 = asp[3]
        BoUpObject.asp2024 = asp[4]
        BoUpObject.asp2025 = asp[5]
        BoUpObject.asp2026 = asp[6]
        BoUpObject.asp2027 = asp[7]
        BoUpObject.asp2028 = asp[8]
        BoUpObject.asp2029 = asp[9]
        BoUpObject.asp2030 = asp[10]
        BoUpObject.asp2031 = asp[11]
        BoUpObject.asp2032 = asp[12]
        BoUpObject.asp2033 = asp[13]
        BoUpObject.asp2034 = asp[14]
        BoUpObject.asp2035 = asp[15]
        BoUpObject.asp2036 = asp[16]
        BoUpObject.asp2037 = asp[17]
        BoUpObject.asp2038 = asp[18]
        BoUpObject.asp2039 = asp[19]
        BoUpObject.asp2040 = asp[20]
        BoUpObject.asp2041 = asp[21]
        BoUpObject.asp2042 = asp[22]
        BoUpObject.asp2043 = asp[23]
        BoUpObject.asp2044 = 0.0

        #########

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
            "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%",
            created,
            "BoUp object",
            BoUpObject,
            "time of creation",
            time.time() - start_time,
        )
        print("boup object ID", BoUpObject.id)

        """

        """

        # get data from boup
        total_df = restructure_single(BoUpObject.id)

        id_list = total_df['id'].tolist()
        Reviewed_list = total_df['Reviewed'].tolist()
        reviewDate_list = total_df['reviewDate'].tolist()
        ID_APP_id_list = total_df['ID_APP_id'].tolist()
        applicationLine_list = total_df['applicationLine'].tolist()
        productMarketer_id_list = total_df['productMarketer_id'].tolist()
        hfg_list = total_df['hfg'].tolist()
        ppos_list = total_df['ppos'].tolist()
        spNumber_list = total_df['spNumber'].tolist()
        applicationMain_id_list = total_df['applicationMain_id'].tolist()
        applicationDetail_id_list = total_df['applicationDetail_id'].tolist()
        rfp_id_list = total_df['rfp_id'].tolist()
        salesName_id_list = total_df['salesName_id'].tolist()
        priceSource_list = total_df['priceSource'].tolist()
        familyPriceApplicable_list = total_df['familyPriceApplicable'].tolist()
        familyPriceDetails_list = total_df['familyPriceDetails'].tolist()
        priceType_list = total_df['priceType'].tolist()
        currency_list = total_df['currency'].tolist()
        fxRate_list = total_df['fxRate'].tolist()
        comment_list = total_df['comment'].tolist()
        region_list = total_df['region'].tolist()
        projectName_list = total_df['projectName'].tolist()
        mainCustomer_id_list = total_df['mainCustomer_id'].tolist()
        endCustomer_id_list = total_df['endCustomer_id'].tolist()
        distributor_list = total_df['distributor_id'].tolist()
        tier1_list = total_df['tier1_id'].tolist()
        oem_id_list = total_df['oem_id'].tolist()
        ems_list = total_df['ems_id'].tolist()
        vpaCustomer_list = total_df['vpaCustomer_id'].tolist()
        dragonId_list = total_df['dragonId'].tolist()
        salesContact_list = total_df['salesContact'].tolist()
        probability_list = total_df['probability'].tolist()
        statusProbability_list = total_df['statusProbability'].tolist()
        sop_list = total_df['sop'].tolist()
        availablePGS_list = total_df['availablePGS'].tolist()
        modifiedBy_id_list = total_df['modifiedBy_id'].tolist()
        modifiedDate_list = total_df['modifiedDate'].tolist()
        creationDate_list = total_df['creationDate'].tolist()
        timeBottomUp_list = total_df['timeBottomUp'].tolist()
        basicType_list = total_df['basicType'].tolist()
        package_list = total_df['package'].tolist()
        series_list = total_df['series'].tolist()
        gen_list = total_df['gen'].tolist()
        seriesLong_list = total_df['seriesLong'].tolist()
        genDetail_list = total_df['genDetail'].tolist()
        gmLifeTime_list = total_df['gmLifeTime'].tolist()
        revEurLifeTime_list = total_df['revEurLifeTime'].tolist()
        volLifeTime_list = total_df['volLifeTime'].tolist()
        volWeightedLifeTime_list = total_df['volWeightedLifeTime'].tolist()
        year_list = total_df['year'].tolist()
        vol_list = total_df['vol'].tolist()
        volCustomer_list = total_df['volCustomer'].tolist()
        price_list = total_df['price'].tolist()
        vhk_list = total_df['vhk'].tolist()
        gm_list = total_df['gm'].tolist()
        wVol_list = total_df['wVol'].tolist()
        wRev_list = total_df['wRev'].tolist()
        m_vol_list = total_df['m_vol'].tolist()
        m_gm_list = total_df['m_gm'].tolist()
        m_wVol_list = total_df['m_wVol'].tolist()
        fy_wRev_list = total_df['fy_wRev'].tolist()

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
        df_list.append(m_vol_list)  # 57
        df_list.append(m_gm_list)  # 58
        df_list.append(m_wVol_list)  # 59
        df_list.append(fy_wRev_list)  # 60

        df_boup = pd.DataFrame(list(BoUp.objects.all().values()))
        protectCellsInExcel(df_boup)
    # this here is to get the whole BoUp table set and create graphics based on the SQL query
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
        # sqlRes = sql_group_series_endcustomer(dfQuery, 2020, 2030) #logic to determine what should be the first year and what should be the last year
        sqlRes = sql_group_family_gen_series_endcustomer_year(dfQuery)

        # redesign sqlresult to use it in chart.js
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
        """
        plt.switch_backend('agg')

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

        print("checking out", total_df['price'])
        rev_margin = sns.lineplot(
            total_df['year'], total_df['price']*total_df['vol'], label="Revenue", marker="o")
        sns.lineplot(total_df['year'], total_df['gm'],
                     label="Gross Margin", marker="o")
        rev_margin.set(title='Revenue and Gross Margin',
                       xlabel='Year', ylabel='EUR')

        revenueMarginPlot = io.BytesIO()
        plt.savefig(revenueMarginPlot, format='jpg')
        revenueMarginPlot.seek(0)
        revenueMarginPlotBase64 = base64.b64encode(revenueMarginPlot.read())
        plt.clf()

        encodedrevenueMarginPlotBase64 = str(revenueMarginPlotBase64)
        encodedrevenueMarginPlotBase64 = encodedrevenueMarginPlotBase64[2:]
        encodedrevenueMarginPlotBase64 = encodedrevenueMarginPlotBase64[:-1]

        print("first done")
        rev_margin_FY = sns.lineplot(
            total_df['year'], revenue_FY, label="Revenue", marker="o")
        sns.lineplot(total_df['year'], total_df['m_gm'],
                     label="Gross Margin", marker="o")
        rev_margin_FY.set(title='Revenue and Gross Margin FY',
                          xlabel='Year', ylabel='EUR')

        revenueMarginPlot_FY = io.BytesIO()
        plt.savefig(revenueMarginPlot_FY, format='jpg')
        revenueMarginPlot_FY.seek(0)
        revenueMarginPlotBase64_FY = base64.b64encode(
            revenueMarginPlot_FY.read())
        plt.clf()

        encodedrevenueMarginPlotBase64_FY = str(revenueMarginPlotBase64_FY)
        encodedrevenueMarginPlotBase64_FY = encodedrevenueMarginPlotBase64_FY[2:]
        encodedrevenueMarginPlotBase64_FY = encodedrevenueMarginPlotBase64_FY[:-1]

        print("second done")
        monthPlot = sns.lineplot(all_months, volumesMonth,
                                 label="Volume", marker="o")
        monthPlot.set(title='Volume by month', xlabel='Month', ylabel='EUR')

        monthVolumePlot = io.BytesIO()
        plt.savefig(monthVolumePlot, format='jpg')
        monthVolumePlot.seek(0)
        monthVolumePlotBase64 = base64.b64encode(monthVolumePlot.read())
        plt.clf()

        monthVolumePlotBase64 = str(monthVolumePlotBase64)
        monthVolumePlotBase64 = monthVolumePlotBase64[2:]
        monthVolumePlotBase64 = monthVolumePlotBase64[:-1]
        print("third done")

        fig, ax = plt.subplots()
        ax2 = ax.twinx()
        volPrice = sns.lineplot(
            x=total_df['year'], y=total_df['vol'], ax=ax,  marker="o")
        sns.lineplot(total_df['year'], total_df['price'],
                     ax=ax2, color="orange", marker="o")
        ax.legend(handles=[a.lines[0]
                           for a in [ax, ax2]], labels=["Volumes", "Prices"])
        ax.set_ylabel('Pieces')
        ax2.set_ylabel('EUR')
        volPrice.set(title='Volume and Price')

        volumePricePlot = io.BytesIO()
        plt.savefig(volumePricePlot, format='jpg')
        volumePricePlot.seek(0)
        volumePricePlotBase64 = base64.b64encode(volumePricePlot.read())
        plt.clf()

        encodedvolumePricePlotBase64 = str(volumePricePlotBase64)
        encodedvolumePricePlotBase64 = encodedvolumePricePlotBase64[2:]
        encodedvolumePricePlotBase64 = encodedvolumePricePlotBase64[:-1]
        print("forth done")
        '''
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
        '''

        df = pd.DataFrame(
            {'YEAR': total_df['year'],
             'region': ["EU" for x in total_df['year']],
             'grossMargin': [float(x) for x in total_df['gm']]
             })
        df.set_index('YEAR', inplace=True)

        # group data by product and display sales as line chart
        df.groupby('region')['grossMargin'].plot(legend=True)

        regionPlot = io.BytesIO()
        plt.savefig(regionPlot, format='jpg')
        regionPlot.seek(0)
        regionPlotBase64 = base64.b64encode(regionPlot.read())
        plt.clf()

        encodedregionPlotBase64 = str(regionPlotBase64)
        encodedregionPlotBase64 = encodedregionPlotBase64[2:]
        encodedregionPlotBase64 = encodedregionPlotBase64[:-1]

        print("fifth done")

        plt.close()
        """

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

        # check if matches protifability vorgaben, warnings or blocks
        # automail to PM lead upon completion
        
        Evtl: competing order from tier1 or OEM… based on the data for this OEM you are competing at OEM level with this order and compare here the prices….

        """

        reportForm = ReportForm()

        if success == True:
            successMessages = [
                "Project was saved successfully and is now active in the Bottom Up!"
            ]
        else:
            successMessages = ["An error ocurred while persisting the data!"]

            raise ValidationError(
                "Major conflict in creation of bottom up entry.")

        return render(
            request,
            "project/project_create_view/step4.html",
            {
                "step": 4,
                "overviewForm": reportForm,
                "projectId": projectId,
                "revenue": revenue,
                "grossMargin": grossMargin,
                "years": years,
                "projectLevelErrors": errors,
                "successMessages": successMessages,
                "sumRevenue": sumRevenue,
                "sumGrossMargin": sumGrossMargin,
                "sumCost": sumCost,
                "sumVolume": sumVolume,
                "sumWeightedVolume": sumWeightedVolume,
                "sumWeightedRevenue": sumWeightedRevenue,
                "averageAsp": averageAsp,
                "sumWeightedGrossMargin": sumWeightedGrossMargin,
            },
        )


class ProjectManagementAll(LoginRequiredMixin, FilterView):
    queryset = Project.objects.select_related(
        "applicationMain",
        "applicationDetail",
        "status",
        "mainCustomer",
        "finalCustomer",
        "sales_name",
        "user",
    )
    template_name = "project/project_management.html"
    paginate_by = 10
    filterset_class = ProjectFilter

    def get_queryset(self):
        queryset = super(ProjectManagementAll, self).get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset


class ProjectManagementInProgress(LoginRequiredMixin, FilterView):
    queryset = Project.objects.select_related(
        "applicationMain",
        "applicationDetail",
        "status",
        "mainCustomer",
        "finalCustomer",
        "sales_name",
        "user",
    )
    template_name = "project/project_management.html"
    paginate_by = 10
    filterset_class = ProjectFilter

    def get_queryset(self):
        queryset = super(ProjectManagementInProgress, self).get_queryset()
        queryset = queryset.filter(user=self.request.user)
        queryset = queryset.filter(Q(status__status__gt=100))
        return queryset


class ProjectManagementDraft(LoginRequiredMixin, FilterView):
    queryset = Project.objects.select_related(
        "applicationMain",
        "applicationDetail",
        "status",
        "mainCustomer",
        "finalCustomer",
        "sales_name",
        "user",
    )
    template_name = "project/project_management.html"
    paginate_by = 10
    filterset_class = ProjectFilter

    def get_queryset(self):
        queryset = super(ProjectManagementDraft, self).get_queryset()
        queryset = queryset.filter(user=self.request.user).filter(draft=True)
        return queryset


class ProjectManagementCompleted(LoginRequiredMixin, FilterView):
    queryset = Project.objects.select_related(
        "applicationMain",
        "applicationDetail",
        "status",
        "mainCustomer",
        "finalCustomer",
        "sales_name",
        "user",
    )
    template_name = "project/project_management.html"
    paginate_by = 10
    filterset_class = ProjectFilter

    def get_queryset(self):

        queryset = super(ProjectManagementCompleted, self).get_queryset()
        queryset = queryset.filter(
            user=self.request.user).filter(status__status=100)
        return queryset


class ProjectManagementCanceled(LoginRequiredMixin, FilterView):
    queryset = Project.objects.select_related(
        "applicationMain",
        "applicationDetail",
        "status",
        "mainCustomer",
        "finalCustomer",
        "sales_name",
        "user",
    )
    template_name = "project/project_management.html"
    paginate_by = 10
    filterset_class = ProjectFilter

    def get_queryset(self):
        queryset = super(ProjectManagementCanceled, self).get_queryset()
        queryset = queryset.filter(
            user=self.request.user).filter(status__status=0)
        return queryset


class ProjectManagementQualityChecks(LoginRequiredMixin, FilterView):
    queryset = ProjectError.objects.select_related("project")
    template_name = "project/project_management_errors_list.html"
    paginate_by = 10
    filterset_class = ProjectErrorFilter

    def get_queryset(self):
        queryset = super(ProjectManagementQualityChecks, self).get_queryset()
        project_ids = queryset.filter(
            project__productMarketer__user=self.request.user
        ).values_list("project", flat=True)
        queryset = Project.objects.filter(id__in=project_ids).select_related(
            "applicationMain",
            "applicationDetail",
            "status",
            "mainCustomer",
            "finalCustomer",
            "sales_name",
            "user",
        )
        return queryset


class ProjectManagementTopTenRevenue(LoginRequiredMixin, FilterView):
    queryset = Project.objects.select_related(
        "applicationMain",
        "applicationDetail",
        "status",
        "mainCustomer",
        "finalCustomer",
        "sales_name",
        "user",
    )
    template_name = "project/project_management.html"
    paginate_by = 10
    filterset_class = ProjectFilter

    def get_queryset(self):
        # we need the ten projects with largest revenue
        boupObjects = BoUp.objects.filter(
            productMarketer__user=self.request.user
        ).order_by("-revEurLifeTime")[:10]
        projectList = boupObjects.values_list("ID_APP", flat=True)
        queryset = super(ProjectManagementTopTenRevenue, self).get_queryset()
        queryset = queryset.filter(user=self.request.user, id__in=projectList)

        return queryset


def saveAndSubmit(request, projectId):
    project = Project.objects.get(id=projectId)
    success_url = reverse_lazy("project_deepdive", kwargs={
                               "projectId": projectId})

    params = {
        "finalRevenue": [],
        "finalVolume": [],
        "finalPrice": 0,
        "finalGrossMargin": 0,
        "finalGrossMarginPct": 0,
        "final_revenue_month": 0,
        "final_grossMargin_month": 0,
        "final_grossMarginPct_month": 0,
        "finalVhk": 0,
        "final_revenue_FY": 0,
        "final_grossProfit_FY": 0,
        "final_grossProfitPct_FY": 0,
        "final_volumes_FY": 0,
        "vhkCy": 0,
        "finalTotalCost": 0,
        "asp": 0,
        "weightedGrossMargin": 0,
        "weightedGrossMarginPct": 0,
        "weightedRevenue": 0,
        "weightedVolume": 0,
    }

    persistor = bottomUpPersistor(params)
    success, outputValues, errorMessage, nada = persistor.persist(
        projectId=projectId,
        request=request,
        bulk=False,
        boUpObjectInput=None,
        probability=1.0,
        helperObjects=None,
        vhkUpdate=False,
        runDate=None,
    )

    if success == True:
        if project.draft == False:
            messages.success(
                request, "Project was updated in the bottom Bottom Up table."
            )
        else:
            messages.success(
                request,
                "Project was submitted to the Bottom Up table and is now active.",
            )

        # if the above worked, remove the draft flag
        project.draft = False
        project.user = request.user
        project.save()
        return redirect(success_url)
    else:
        messages.error(request, errorMessage)

        return redirect(success_url)


def saveAsDraft(request, projectId):

    success_url = reverse_lazy("project_deepdive", kwargs={
                               "projectId": projectId})

    # set project as draft
    try:
        project = Project.objects.get(id=projectId)
        project.user = request.user
        project.draft = True
        project.save()
        boupObject = BoUp.objects.get(ID_APP=projectId)
        boupObject.delete()
        messages.success(
            request,
            "Project was removed from Bottom Up table and is now set as draft.",
        )
        return redirect(success_url)
    except:
        # to do: show project_deep dive with an error
        print("constraint violated!!")
        messages.error(
            request,
            "Unique constraint violated! You already have a draft with the same Main and End Customers, Main and Application Detail and Sales Name. You can only keep one in the system. You must either a) delete the existing draft or b) delete this project and continue working on the existing draft.",
        )
        return redirect(success_url)


def deleteProject(request, projectId):
    success_url = reverse_lazy("project_management_all_view")
    print("deleting project!", projectId)

    try:
        project = Project.objects.get(id=projectId)
        project.delete()
        messages.success(
            request,
            "Project and all related entries (excepting logs) were deleted successfully.",
        )
        return redirect(success_url)
    except:
        messages.error(
            request,
            "An internal server error ocurred while trying to delete the project. Either the database is locked or the project did no longer exist. The operation was reverted.",
        )
        return redirect(success_url)


def reviewProject(request, projectId):
    success_url = reverse_lazy("project_management_all_view")
    print("reviewing project!", projectId)

    try:
        project = Project.objects.get(id=projectId)
        project.project.salesNameDefaulted = False
        project.projectReviewed = True
        project.reviewDate = datetime.now(tz=timezone.utc)
        messages.success(
            request,
            "Project was set as reviewed.",
        )
        return redirect(success_url)
    except:
        messages.error(
            request,
            "An internal server error ocurred while trying to set the project as reviewed. Either the database is locked or the project did no longer exist. The operation was reverted.",
        )
        return redirect(success_url)
