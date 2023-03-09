from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.urls import reverse_lazy, reverse
from core.project.models import Product, SalesName, ProductFamily, ProductPackage, ProductSeries, MainCustomers, FinalCustomers
from enum import Enum
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import F
from django.utils import timezone
from datetime import datetime
from rest_framework import status
from django.db import connection
from .forms import CreateDummyProductForm, CreateDummySalesNameForm, CreateDummyCustomerForm


class CreateProductEntryPoint(LoginRequiredMixin, View):
    template_name = "other/createProductEntryPoint.html"
    #form_class = CreateDummySalesNameForm
    success_url = ""  # reverse_lazy("tbd")

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class CreateDummyCustomer(LoginRequiredMixin, View):
    template_name = "other/createDummyCustomer.html"
    form_class = CreateDummyCustomerForm
    success_url = reverse_lazy("create_project_view")

    def get(self, request, *args, **kwargs):
        context = {"form": self.form_class()}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            # get or create a main customer with the entered value and append _dummy to it
            inputMainCustomer = form.cleaned_data.get("mainCustomer")
            inputFinalCustomer = form.cleaned_data.get("finalCustomer")

            inputMainCustomer = inputMainCustomer + "_dummy"
            inputFinalCustomer = inputFinalCustomer + "_dummy"

            # get or create a final customer with the entered value and append _dummy to it
            mainCustomerObject, created = MainCustomers.objects.get_or_create(
                customerName=inputMainCustomer)
            finalCustomerObject, created = FinalCustomers.objects.get_or_create(
                finalCustomerName=inputFinalCustomer)

            mainCustomerObject.dummy = True
            finalCustomerObject.dummy = True
            mainCustomerObject.valid = True
            finalCustomerObject.valid = True

            # generate the main - end customer relation and save
            mainCustomerObject.finalCustomers.add(finalCustomerObject)
            mainCustomerObject.save()
            finalCustomerObject.save()

            return redirect(self.success_url)

        else:
            string = "Sorry, encountered a miscelaneous error. Please ensure you did not use exotic characters."
            creationInformation = [string]
            context = {"form": self.form_class(
                request.POST),  "createSalesNameSuccess": False, "creationInformation": creationInformation}
            return render(request, self.template_name, context)


class CreateDummySalesName(LoginRequiredMixin, View):
    template_name = "other/createDummySalesName.html"
    form_class = CreateDummySalesNameForm
    success_url = reverse_lazy("create_project_view")

    def get(self, request, *args, **kwargs):
        context = {"form": self.form_class()}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            family = request.POST.get("product_family")
            series = request.POST.get("product_series")
            package = request.POST.get("product_package")
            product = request.POST.get("product")
            newSalesName = request.POST.get("new_sales_name")

            print("got new informationm family", family, "series", series,
                  "package", package, "product", product, "new sales name", newSalesName, "product", product)

            # check if sales name already exists under not a dummy
            salesNameObjects = SalesName.objects.filter(name=newSalesName)

            if salesNameObjects.count() > 0:
                print("sales name already exists for this rfp!")
                string = "Conflict: there is already at least one identical Sales Name in the data base. The relevant Sales Names are: "

                for obj in salesNameObjects:
                    string = string + str(obj) + ", "

                string = string[:-2] + ". The relevant products is: "

                for obj in salesNameObjects:
                    string = string + str(obj.rfp.rfp) + ", "
                string = string[:-2]

                # to do: add links to the product information

                creationInformation = [string]
                context = {"form": self.form_class(
                    request.POST), "createSalesNameSuccess": False, "creationInformation": creationInformation}
                return render(request, self.template_name, context)

            # create the sales name
            newSalesNameObj, created = SalesName.objects.get_or_create(
                name=newSalesName)

            productObj = Product.objects.get(id=product)

            if created == True:
                newSalesNameObj.rfp = productObj
                newSalesNameObj.dummy = True
                newSalesNameObj.save()

                print("created new sales name", newSalesNameObj)
                string = "Created new Sales Name with ID #" + \
                    str(newSalesNameObj.id) + " and product ID #" + \
                    str(newSalesNameObj.rfp.id)
                creationInformation = [string]

                context = {"form": self.form_class(
                    request.POST), "createSalesNameSuccess": True, "creationInformation": creationInformation}
                return render(request, self.template_name, context)
            else:
                print("retrieved existing sales name", newSalesNameObj)
                string = "The entered dummy Sales Name already exists. See Sales Name ID #" + \
                    str(newSalesNameObj.id) + " and product ID #" + \
                    str(newSalesNameObj.rfp.id)
                creationInformation = [string]
                context = {"form": self.form_class(
                    request.POST),  "createSalesNameSuccess": False, "creationInformation": creationInformation}
                return render(request, self.template_name, context)
        else:
            string = "Sorry, encountered a miscelaneous error. Please ensure you did not use exotic characters for the sales or product name."
            creationInformation = [string]
            context = {"form": self.form_class(
                request.POST),  "createSalesNameSuccess": False, "creationInformation": creationInformation}
            return render(request, self.template_name, context)


class CreateDummyProduct(LoginRequiredMixin, View):
    template_name = "other/createDummyProduct.html"
    form_class = CreateDummyProductForm
    success_url = reverse_lazy("create_project_view")

    def get(self, request, *args, **kwargs):
        context = {"form": self.form_class()}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            family = request.POST.get("product_family")
            series = request.POST.get("product_series")
            package = request.POST.get("product_package")
            product = request.POST.get("product")

            hfg = request.POST.get("hfg")
            ppos = request.POST.get("ppos")
            basicType = request.POST.get("basicType")
            newSalesName = request.POST.get("new_sales_name")
            print("got new informationm family", family, "series", series,
                  "package", package, "product", product, "new sales name", newSalesName)

            # check if product already exists
            productObjects = Product.objects.filter(rfp=product)

            if productObjects.count() > 0:
                print("product name already exists for this rfp!")
                string = "Conflict: there is already at least one identical RFP in the data base. The relevant IDs are: "

                for obj in productObjects:
                    string.append(obj.id) + ", "

                string = string[:-2] + ". The relevant products are: "

                for obj in productObjects:
                    string.append(obj.rfp) + ", "
                string = string[:-2]

                string = string + ". Please create a dummy sales name instead."
                # to do: add links to the product information

                creationInformation = [string]
                context = {"form": self.form_class(
                    request.POST), "createSalesNameSuccess": False, "creationInformation": creationInformation}
                return render(request, self.template_name, context)

            # check if sales name already exists under not a dummy
            salesNameObjects = SalesName.objects.filter(name=newSalesName)

            if salesNameObjects.count() > 0:
                print("sales name already exists for this rfp!")
                string = "Conflict: there is already at least one identical Sales Name in the data base. The relevant IDs are: "

                for obj in salesNameObjects:
                    string.append(obj.id) + ", "

                string = string[:-2] + ". The relevant products are: "

                for obj in salesNameObjects:
                    string.append(obj.rfp.rfp) + ", "
                string = string[:-2]

                # to do: add links to the product information

                creationInformation = [string]
                context = {"form": self.form_class(
                    request.POST), "createSalesNameSuccess": False, "creationInformation": creationInformation}
                return render(request, self.template_name, context)

            # now proceed with the creation of dummy family + series + package + product combination, similar to product import job
            familyObj = ProductFamily.objects.get(id=family)

            # IDs with 0 are the dummys (the database pks begin at 1)
            seriesObj = None
            packageObj = None

            # series
            # if int(series) == 0:
            seriesObj, created = ProductSeries.objects.get_or_create(
                series="Dummy Series", dummy=True, valid=True, family=familyObj)

            if created == True:
                seriesObj.family = familyObj
                seriesObj.description = "Dummy Series"
                seriesObj.save()
            """
            else:
                print("series input", series)
                seriesObj, created = ProductSeries.objects.get(id=series)
            """
            # package
            # if int(package) == 0:
            packageObj, createdPackage = ProductPackage.objects.get_or_create(
                dummy=True, valid=True, series=seriesObj, package="Dummy Package")

            if createdPackage == True:
                packageObj.series = seriesObj
                packageObj.description = "Dummy Package"
                packageObj.save()

            """
            else:
                packageObj, created = ProductPackage.objects.get(id=package)
            """
            # create the product
            productObj, created = Product.objects.get_or_create(
                rfp=product, package=packageObj)

            if created == True:
                productObj.availablePGS = False
                productObj.hfg = hfg
                productObj.ppos = ppos
                productObj.basicType = basicType
                productObj.valid = True
                productObj.dummy = True
                productObj.familyHelper = familyObj.family_name
                productObj.seriesHelper = seriesObj.series
                productObj.packageHelper = packageObj.package
                productObj.availablePGS = False
                # create the sales name
                newSalesNameObj, created = SalesName.objects.get_or_create(
                    name=newSalesName)

                if created == True:
                    newSalesNameObj.rfp = productObj
                    newSalesNameObj.dummy = True
                    newSalesNameObj.save()
                    print("created new sales name", newSalesNameObj)
                    string = "Created new Sales Name with ID #" + \
                        str(newSalesNameObj.id) + " and product ID #" + \
                        str(newSalesNameObj.rfp.id)
                    creationInformation = [string]

                    context = {"form": self.form_class(
                        request.POST), "createSalesNameSuccess": True, "creationInformation": creationInformation}
                    return render(request, self.template_name, context)
                else:
                    print("retrieved existing sales name", newSalesNameObj)
                    string = "The entered dummy Sales Name already exists. See Sales Name ID #" + \
                        str(newSalesNameObj.id) + " and product ID #" + \
                        str(newSalesNameObj.rfp.id)
                    creationInformation = [string]
                    context = {"form": self.form_class(
                        request.POST),  "createSalesNameSuccess": False, "creationInformation": creationInformation}
                    return render(request, self.template_name, context)
        else:
            string = "Sorry, encountered a miscelaneous error. Please ensure you did not use exotic characters for the sales or product name."
        creationInformation = [string]
        context = {"form": self.form_class(
            request.POST),  "createSalesNameSuccess": False, "creationInformation": creationInformation}
        return render(request, self.template_name, context)
