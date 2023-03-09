from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.safestring import mark_safe
from django.urls import reverse
from enum import Enum
from typing import Any, Iterable, MutableSequence, TypeVar
import datetime
from core.project.models import Product, ProductFamily, ProductPackage, ProductSeries
#from project.models import MainCustomers, FinalCustomers
from django.db.models import F


class CreateDummyCustomerForm(forms.Form):

    mainCustomer = forms.CharField(
        widget=forms.TextInput, required=True, label='Main Customer Name (Bill To)')
    finalCustomer = forms.CharField(
        widget=forms.TextInput, required=True, label='End Customer Name (Ship To)')

    class Meta:
        fields = ('customerName', 'finalCustomers')


"""
to select a product family, series, package
"""


class CreateDummySalesNameForm(forms.Form):

    seriesSelect = ProductSeries.objects.values('series').distinct().order_by(
        "series")
    seriesArray = []
    i = 1
    seriesArray.append((0, "None / Dummy"))

    for c in seriesSelect:
        # print(c)
        seriesArray.append((i, c["series"]))
        i = i + 1

    #########
    packageSelect = ProductPackage.objects.values('package').distinct().order_by(
        "package")
    packageArray = []
    o = 1
    packageArray.append((0, "None / Dummy"))

    for n in packageSelect:
        packageArray.append((o, n["package"]))
        o = o + 1

    product_family = forms.CharField(widget=forms.Select(
        choices=[(c.id, c.family_name) for c in ProductFamily.objects.all().order_by(
            "family_name")]), required=True)

    product_series = forms.CharField(widget=forms.Select(
        choices=seriesArray), required=True)

    product_package = forms.CharField(widget=forms.Select(
        choices=packageArray), required=True)

    product = forms.CharField(widget=forms.Select(
        choices=[(c.id, c.rfp) for c in Product.objects.all().order_by(
            "rfp")]), required=True)

    hfg = forms.CharField(widget=forms.Select(), required=False)
    ppos = forms.CharField(widget=forms.Select(), required=False)
    basicType = forms.CharField(widget=forms.Select(), required=False)

    new_sales_name = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super(CreateDummySalesNameForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

    class Meta:

        labels = {
            'hfg': 'HFG',
            'ppos': 'PPOS',
            'estimatedSop': 'Start of Production',
            'basicType': 'Basic Type',
        }


# to do: inheritance from createDummySalesNameForm
class CreateDummyProductForm(forms.Form):

    seriesSelect = ProductSeries.objects.values('series').distinct().order_by(
        "series")
    seriesArray = []
    i = 1
    seriesArray.append((0, "None / Dummy"))

    # comment FF 2/1/23: removed selection in order to keep all dummy products with dummy identifiers consistently
    """
    for c in seriesSelect:
        # print(c)
        seriesArray.append((i, c["series"]))
        i = i + 1
    """

    #########
    packageSelect = ProductPackage.objects.values('package').distinct().order_by(
        "package")
    packageArray = []
    o = 1
    packageArray.append((0, "None / Dummy"))

    # comment FF 2/1/23: removed selection in order to keep all dummy products with dummy identifiers consistently
    """
    for n in packageSelect:
        packageArray.append((o, n["package"]))
        o = o + 1
    """

    """
    distinctFamilies = Product.objects.annotate(text=F("familyHelper")).values('familyHelper').distinct().order_by(
        "familyHelper")

    familyList = []
    i = 0
    for family in distinctFamilies:
        tuple = (i, family)
        i = i+1
        familyList.append(tuple)

    print("distinct families", distinctFamilies)
    product_family = forms.CharField(widget=forms.Select(
        choices=familyList), required=True)
    """

    product_family = forms.CharField(widget=forms.Select(
        choices=[(c.id, c.family_name) for c in ProductFamily.objects.all().order_by(
            "family_name")]), required=True)
    print("form prod family", ProductFamily.objects.all().order_by(
        "family_name"))
    product_series = forms.CharField(widget=forms.Select(
        choices=seriesArray), required=False)

    product_package = forms.CharField(widget=forms.Select(
        choices=packageArray), required=False)

    product = forms.CharField(required=True)

    hfg = forms.CharField(widget=forms.Select(), required=True, label="HFG")
    ppos = forms.CharField(widget=forms.Select(), required=True, label="PPOS")
    basicType = forms.CharField(
        widget=forms.Select(), required=True, label="Basic Type")

    new_sales_name = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super(CreateDummyProductForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
