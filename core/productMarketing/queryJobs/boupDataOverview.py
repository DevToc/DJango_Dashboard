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
from ..models import *
from django_tables2 import SingleTableView

# from .tables import TherapyTable, CommunicationTable
from django.contrib import messages

# from .filters import *
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
import json
import datetime
from django.forms import modelformset_factory
from currencies.models import Currency

# from bootstrap_datepicker_plus.widgets import DatePickerInput, TimePickerInput, DateTimePickerInput, MonthPickerInput, YearPickerInput
from django.forms import formset_factory

# email
from django.core.mail import send_mail

# from core.settings import BASE_DIR, EMAIL_HOST_USER
# email
from django.core import serializers
from django.utils import timezone
from django.template import RequestContext
from django.db import connection
from datetime import date, timedelta
import io
import base64

####
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

# from .diagnosis import decode, decodePrivateInsurers
# from .scan import *
# from .ocr import ocrscan
# from .suitability import physioSuitability

from productMarketingDwh.models import *
from enum import Enum

# calculate while opening site


def getBoupTableData(request, allData):

    # tbd - one view for the own department (to reduce query), and then one view for atv mc
    print("aaa")
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
    ]

    # get all projects
    projects = Project.objects.all()
    print("---> projects", type(projects))

    # for each project, get the respective volumes that are active, the respective prices that are active, compute the revenue and gross margins

    # since no distinct
    totalVolumesWeighted = []

    totalVolumes = [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    ]
    totalVolumesWeighted = [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    ]
    totalAsps = [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    ]
    totalMargin = [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    ]
    totalMarginWeighted = [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    ]
    productSeriesArray = [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    ]
    totalRevenues = [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    ]
    totalRevenuesWeighted = [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    ]
    productSeries = dict()
    outputArray = []

    if projects.count() > 0:
        for project in projects:
            # helper arrays
            vhk = []
            volumes = []
            month_volumes = []
            prices = []
            ##### revenue and gm
            revenue = []
            grossProfit = []
            grossProfitPct = []

            # further info
            pricesExisted = False
            currencyPrices = ""
            currencyVhk = ""
            project = Project.objects.get(id=project.pk)
            print("------> analyzing project", project, "id", project.pk)
            print("rfp of project", project.sales_name.rfp)
            statusProbability = 1.0

            try:
                statusProbability = float(project.status.status) / 100.0
            except:
                pass

            for year in years:
                try:
                    priceObject = ProjectVolumePrices.objects.get(
                        project=project, calenderYear=int(year), valid=True
                    )
                    prices.append(float(priceObject.price))
                    currencyPrices = priceObject.currency
                except:
                    prices.append(0)

            for year in years:
                try:
                    volumeObject = ProjectVolumePrices.objects.get(
                        project=project, calenderYear=year
                    )
                    volumes.append(volumeObject.quantity)

                except:
                    volumes.append(0)

            months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
            for year in years:
                for month in months:
                    try:
                        volumeMObject = ProjectVolumeMonth.objects.get(
                            project=project, calenderYear=year, month=month
                        )
                        month_volumes.append(volumeMObject.quantity)

                    except:
                        month_volumes.append(0)

            for year in years:
                try:
                    costObject = VhkCy.objects.get(
                        RFP=project.sales_name.rfp.pk, calendarYear=year, valid=True
                    )
                    vhk.append(float(costObject.cost))
                    currencyVhk = costObject.currency.currency
                except:
                    vhk.append(0)

            # if no currency VHK available, it means that there is not a single currency entry
            if currencyVhk == "":
                print("not a single VHK found! returning on error!")
                # message = "No VHKs availbale for this RFP! Please contact the admin!"
                # return render(request, "productMarketing/entryStep4.html", {'message': message, 'error': True, })

            ##### revenue and gm
            revenue = []
            grossProfit = []
            grossProfitPct = []
            weightedVolume = []

            # FY calculations through month aggregation
            revenue_month = []
            grossProfit_month = []
            grossProfitPct_month = []
            weightedVolume_month = []

            fxErrorPrices = False
            print("projectId", project.pk)
            print("prices", prices)
            print("vhk", vhk)
            print("volumes", volumes)
            print("month volumes", month_volumes)
            print("currencies", currencyPrices, "vhk", currencyVhk)

            # check if price currency matches cost currency, else batch transform
            if currencyPrices != "EUR":
                print("1: currencies do not match! converting to EUR", currencyPrices)
                # get current rate
                fx = 1.0

                try:
                    """
                    currencyObj = Currencies.objects.get(
                        currency=currencyPrices)
                    fxObject = ExchangeRates.objects.get(
                        currency=currencyObj.pk, valid=True
                    )
                    fx = float(fxObject.rate)
                    """
                    fx = float(Currency.objects.get(code=currencyVhk).factor)

                except:
                    print("failed currency exchange!! aborting!!")
                    fxErrorPrices = True

                print("lenghts", len(prices), len(years))
                for index in range((len(years) - 1)):
                    prices[index] = prices[index] * float(fx)

            if currencyVhk != "EUR":
                print("2: currencies vhk do not match! converting to EUR", currencyVhk)
                # get current rate
                fx = 1.0

                try:
                    """
                    currencyObj = Currencies.objects.get(currency=currencyVhk)
                    print("currobj", currencyObj.currency)
                    fxObject = ExchangeRates.objects.get(
                        currency=currencyObj.pk, valid=True
                    )
                    fx = float(fxObject.rate)
                    """
                    fx = float(Currency.objects.get(code=currencyVhk).factor)
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
                    grossProfitValue = revenueValue - \
                        (vhk[index] * volumes[index])
                    revenue.append(revenueValue)
                    grossProfit.append(grossProfitValue)
                    weightedVolume.append(volumes[index] * statusProbability)
                    grossMarginPctValue = 0

                    # for overall figures

                    totalVolumes[index] = totalVolumes[index] + volumes[index]
                    totalVolumesWeighted[index] = (
                        totalVolumesWeighted[index] +
                        volumes[index] * statusProbability
                    )
                    totalRevenues[index] = totalRevenues[index] + revenueValue
                    totalRevenuesWeighted[index] = (
                        totalRevenuesWeighted[index] +
                        revenueValue * statusProbability
                    )
                    totalAsps[index] = totalAsps[index] + prices[index]
                    totalMargin[index] = totalMargin[index] + grossProfitValue
                    totalMarginWeighted[index] = (
                        totalMarginWeighted[index]
                        + grossProfitValue * statusProbability
                    )

                    try:
                        grossMarginPctValue = grossProfitValue * 100 / revenueValue
                        grossProfitPct.append(grossMarginPctValue)
                    except:
                        grossProfitPct.append(0)
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
                        grossProfitValue,
                        "cost",
                        vhk[index],
                        "margin pctg",
                        grossMarginPctValue,
                    )

                # for monthly calculation aggregated into FY
                for index in range(len(years)):
                    for month in months:
                        revenueMonthValue = (
                            prices[index] *
                            month_volumes[(index * 12) + month - 1]
                        )
                        grossProfitMonthValue = revenueMonthValue - (
                            vhk[index] *
                            month_volumes[(index * 12) + month - 1]
                        )
                        revenue_month.append(revenueMonthValue)
                        grossProfit_month.append(grossProfitMonthValue)
                        weightedVolume_month.append(
                            month_volumes[(index * 12) + month -
                                          1] * statusProbability
                        )
                        grossMarginMonthPctValue = 0

                        try:
                            grossMarginMonthPctValue = (
                                grossProfitMonthValue * 100 / revenueMonthValue
                            )
                            grossProfitPct_month.append(
                                grossMarginMonthPctValue)
                        except:
                            grossProfitPct_month.append(0)
                        print(
                            "%%%%%%%%%%% final result, year",
                            years[index],
                            "month",
                            month,
                            "volume",
                            month_volumes[(index * 12) + month - 1],
                            "price",
                            prices[index],
                            "currency: EUR",
                            "revenue",
                            revenueMonthValue,
                            "gross margin",
                            grossProfitMonthValue,
                            "cost",
                            vhk[index],
                            "margin pctg",
                            grossMarginMonthPctValue,
                        )

            print("lens", len(years), len(grossProfit), len(revenue))
            print("%%%%%&&&&& gross margins", grossProfit)
            print("%%%%%&&&&& revenue", revenue)
            cummulativeGrossMargin = sum(grossProfit)
            cummulativeRevenue = sum(revenue)
            cummulativeVolume = sum(volumes)
            cummulativeWeightedVolume = cummulativeVolume * statusProbability
            print("%%%%%&&&&& cumulative gross margin", sum(grossProfit))
            print("%%%%%&&&&& cumulative revenue", sum(revenue))

            # calculation to agg. into FY
            revenue_FY = []
            grossProfit_FY = []
            grossProfitPct_FY = []
            weightedVolume_FY = []
            volumes_FY = []

            for idx in range(len(years)):
                if idx == 0:
                    revenue_FY.append(sum(revenue_month[:9]))
                    grossProfit_FY.append(sum(grossProfit_month[:9]))
                    grossProfitPct_FY.append(sum(grossProfitPct_month[:9]))
                    weightedVolume_FY.append(sum(weightedVolume_month[:9]))
                    volumes_FY.append(sum(month_volumes[:9]))
                elif idx == len(years) - 1:
                    revenue_FY.append(sum(revenue_month[-3:]))
                    grossProfit_FY.append(sum(grossProfit_month[-3:]))
                    grossProfitPct_FY.append(sum(grossProfitPct_month[-3:]))
                    weightedVolume_FY.append(sum(weightedVolume_month[-3:]))
                    volumes_FY.append(sum(month_volumes[-3:]))
                else:
                    current_start = 8 + 12 * (idx - 1)
                    current_end = 8 + 12 * idx
                    revenue_FY.append(
                        sum(revenue_month[current_start: current_end + 1])
                    )
                    grossProfit_FY.append(
                        sum(grossProfit_month[current_start: current_end + 1])
                    )
                    grossProfitPct_FY.append(
                        sum(grossProfitPct_month[current_start: current_end + 1])
                    )
                    weightedVolume_FY.append(
                        sum(weightedVolume_month[current_start: current_end + 1])
                    )
                    volumes_FY.append(
                        sum(month_volumes[current_start: current_end + 1])
                    )

            """
            if product.series not in productSeriesArray:
                productSeriesArray.append(product.series)
                productSeries[product.series] = product.seriesDescription
            """
            if (len(volumes) > 0) & (len(revenue) > 0):
                idApp = project.pk
                applicationLine = project.applicationLine
                productMarketer = project.productMarketer
                hfg = project.sales_name.rfp.hfg
                ppos = project.sales_name.rfp.ppos
                spNumber = project.spNumber
                applicationMain = project.applicationMain
                applicationDetail = project.applicationDetail
                rfp = project.sales_name.rfp
                salesName = project.sales_name
                priceSource = project.priceType.priceType
                familyPriceApplicable = project.familyPriceApplicable
                familyPriceHelper = project.familyPriceDetails

                currency = "EUR"
                fxRate = 1.0
                comments = project.comment
                region = project.region
                projectName = project.projectName
                dragonId = project.salesOpportunity.dragonId
                # statusProbability = 0.9 #project.status
                Probability = project.status.statusDisplay
                sop = project.estimatedSop
                pposAvailablePgs = project.sales_name.rfp.availablePGS
                modifiedBy = project.user.username
                modifiedDate = project.modifiedDate
                creationDate = project.creationDate
                timeBottomUp = "0"
                basicType = project.sales_name.rfp.basicType
                package = project.sales_name.rfp.packageHelper
                series = project.sales_name.rfp.seriesHelper
                gen = project.sales_name.rfp.familyHelper
                seriesLong = project.sales_name.rfp.package.series.description
                genDetail = project.sales_name.rfp.package.series.family.family_name
                gmLifeTime = cummulativeGrossMargin
                revEurLifeTime = cummulativeRevenue
                volLifeTime = cummulativeVolume
                volWeightedLifeTime = cummulativeWeightedVolume

                outputDict = dict()  # ["dummy 12346778"]

                if allData == True:

                    vol2020 = volumes[0]
                    vol2021 = volumes[1]
                    vol2022 = volumes[2]
                    vol2023 = volumes[3]
                    vol2024 = volumes[4]
                    vol2025 = volumes[5]
                    vol2026 = volumes[6]
                    vol2027 = volumes[7]
                    vol2028 = volumes[8]
                    vol2029 = volumes[9]
                    vol2030 = volumes[10]
                    vol2031 = volumes[11]
                    vol2032 = volumes[12]
                    vol2033 = volumes[13]
                    vol2034 = volumes[14]
                    vol2035 = volumes[15]
                    vol2036 = volumes[16]
                    vol2037 = volumes[17]
                    vol2038 = volumes[18]
                    vol2039 = volumes[19]
                    vol2040 = volumes[20]
                    vol2041 = volumes[21]
                    vol2042 = volumes[22]
                    vol2043 = volumes[23]
                    # volumes[24]  ### por que volumes no lelga hasta aca??
                    vol2044 = 0.0

                    # workaround
                    volumesCustomer = volumes
                    volCustomer2020 = volumesCustomer[0]
                    volCustomer2021 = volumesCustomer[0]
                    volCustomer2022 = volumesCustomer[0]
                    volCustomer2023 = volumesCustomer[0]
                    volCustomer2024 = volumesCustomer[0]
                    volCustomer2025 = volumesCustomer[0]
                    volCustomer2026 = volumesCustomer[0]
                    volCustomer2027 = volumesCustomer[0]
                    volCustomer2028 = volumesCustomer[0]
                    volCustomer2029 = volumesCustomer[0]
                    volCustomer2030 = volumesCustomer[0]
                    volCustomer2031 = volumesCustomer[0]
                    volCustomer2032 = volumesCustomer[0]
                    volCustomer2033 = volumesCustomer[0]
                    volCustomer2034 = volumesCustomer[0]
                    volCustomer2035 = volumesCustomer[0]
                    volCustomer2036 = volumesCustomer[0]
                    volCustomer2037 = volumesCustomer[0]
                    volCustomer2038 = volumesCustomer[0]
                    volCustomer2039 = volumesCustomer[0]
                    volCustomer2040 = volumesCustomer[0]
                    volCustomer2041 = volumesCustomer[0]
                    volCustomer2042 = volumesCustomer[0]
                    volCustomer2043 = volumesCustomer[0]
                    volCustomer2044 = volumesCustomer[0]

                    # marketer estimated price
                    price2020 = prices[0]
                    price2021 = prices[1]
                    price2022 = prices[2]
                    price2023 = prices[3]
                    price2024 = prices[4]
                    price2025 = prices[5]
                    price2026 = prices[6]
                    price2027 = prices[7]
                    price2028 = prices[8]
                    price2029 = prices[9]
                    price2030 = prices[10]
                    price2031 = prices[11]
                    price2032 = prices[12]
                    price2033 = prices[13]
                    price2034 = prices[14]
                    price2035 = prices[15]
                    price2036 = prices[16]
                    price2037 = prices[17]
                    price2038 = prices[18]
                    price2039 = prices[19]
                    price2040 = prices[20]
                    price2041 = prices[21]
                    price2042 = prices[22]
                    price2043 = prices[23]
                    # price2044 = prices[24]

                    # vhks
                    vhk2020 = vhk[0]
                    vhk2021 = vhk[1]
                    vhk2022 = vhk[2]
                    vhk2023 = vhk[3]
                    vhk2024 = vhk[4]
                    vhk2025 = vhk[5]
                    vhk2026 = vhk[6]
                    vhk2027 = vhk[7]
                    vhk2028 = vhk[8]
                    vhk2029 = vhk[9]
                    vhk2030 = vhk[10]
                    vhk2031 = vhk[11]
                    vhk2032 = vhk[12]
                    vhk2033 = vhk[13]
                    vhk2034 = vhk[14]
                    vhk2035 = vhk[15]
                    vhk2036 = vhk[16]
                    vhk2037 = vhk[17]
                    vhk2038 = vhk[18]
                    vhk2039 = vhk[19]
                    vhk2040 = vhk[20]
                    vhk2041 = vhk[21]
                    vhk2042 = vhk[22]
                    vhk2043 = vhk[23]
                    vhk2044 = 0.0  # vhk[24]

                    # yearly gross margins

                    gm2020 = grossProfit[0]
                    gm2021 = grossProfit[1]
                    gm2022 = grossProfit[2]
                    gm2023 = grossProfit[3]
                    gm2024 = grossProfit[4]
                    gm2025 = grossProfit[5]
                    gm2026 = grossProfit[6]
                    gm2027 = grossProfit[7]
                    gm2028 = grossProfit[8]
                    gm2029 = grossProfit[9]
                    gm2030 = grossProfit[10]
                    gm2031 = grossProfit[11]
                    gm2032 = grossProfit[12]
                    gm2033 = grossProfit[13]
                    gm2034 = grossProfit[14]
                    gm2035 = grossProfit[15]
                    gm2036 = grossProfit[16]
                    gm2037 = grossProfit[17]
                    gm2038 = grossProfit[18]
                    gm2039 = grossProfit[19]
                    gm2040 = grossProfit[20]
                    gm2041 = grossProfit[21]
                    gm2042 = grossProfit[22]
                    gm2043 = grossProfit[23]
                    gm2044 = 0.0  # grossProfit[24]

                    # weighted volume (volume * probability)
                    print("volumes", volumes)
                    print(
                        "type volumes 0",
                        type(volumes[0]),
                        "type statusProbability",
                        type(statusProbability),
                        "value",
                        statusProbability,
                    )
                    wVol2020 = float(volumes[0]) * statusProbability
                    wVol2021 = float(volumes[1]) * statusProbability
                    wVol2022 = float(volumes[2]) * statusProbability
                    wVol2023 = float(volumes[3]) * statusProbability
                    wVol2024 = float(volumes[4]) * statusProbability
                    wVol2025 = float(volumes[5]) * statusProbability
                    wVol2026 = float(volumes[6]) * statusProbability
                    wVol2027 = float(volumes[7]) * statusProbability
                    wVol2028 = float(volumes[8]) * statusProbability
                    wVol2029 = float(volumes[9]) * statusProbability
                    wVol2030 = float(volumes[10]) * statusProbability
                    wVol2031 = float(volumes[11]) * statusProbability
                    wVol2032 = float(volumes[12]) * statusProbability
                    wVol2033 = float(volumes[13]) * statusProbability
                    wVol2034 = float(volumes[14]) * statusProbability
                    wVol2035 = float(volumes[15]) * statusProbability
                    wVol2036 = float(volumes[16]) * statusProbability
                    wVol2037 = float(volumes[17]) * statusProbability
                    wVol2038 = float(volumes[18]) * statusProbability
                    wVol2039 = float(volumes[19]) * statusProbability
                    wVol2040 = float(volumes[20]) * statusProbability
                    wVol2041 = float(volumes[21]) * statusProbability
                    wVol2042 = float(volumes[22]) * statusProbability
                    wVol2043 = float(volumes[23]) * statusProbability
                    wVol2044 = 0.0  # grossProfit[24]* statusProbability

                    # yearly revenue (weighted)
                    wRev2020 = revenue[0] * statusProbability
                    wRev2021 = revenue[1] * statusProbability
                    wRev2022 = revenue[2] * statusProbability
                    wRev2023 = revenue[3] * statusProbability
                    wRev2024 = revenue[4] * statusProbability
                    wRev2025 = revenue[5] * statusProbability
                    wRev2026 = revenue[6] * statusProbability
                    wRev2027 = revenue[7] * statusProbability
                    wRev2028 = revenue[8] * statusProbability
                    wRev2029 = revenue[9] * statusProbability
                    wRev2030 = revenue[10] * statusProbability
                    wRev2031 = revenue[11] * statusProbability
                    wRev2032 = revenue[12] * statusProbability
                    wRev2033 = revenue[13] * statusProbability
                    wRev2034 = revenue[14] * statusProbability
                    wRev2035 = revenue[15] * statusProbability
                    wRev2036 = revenue[16] * statusProbability
                    wRev2037 = revenue[17] * statusProbability
                    wRev2038 = revenue[18] * statusProbability
                    wRev2039 = revenue[19] * statusProbability
                    wRev2040 = revenue[20] * statusProbability
                    wRev2041 = revenue[21] * statusProbability
                    wRev2042 = revenue[22] * statusProbability
                    wRev2043 = revenue[23] * statusProbability
                    wRev2044 = 0.0  # volumes[24]* statusProbability

                    # monthy stuff
                    fy_vol2020 = volumes_FY[0]
                    fy_vol2021 = volumes_FY[1]
                    fy_vol2022 = volumes_FY[2]
                    fy_vol2023 = volumes_FY[3]
                    fy_vol2024 = volumes_FY[4]
                    fy_vol2025 = volumes_FY[5]
                    fy_vol2026 = volumes_FY[6]
                    fy_vol2027 = volumes_FY[7]
                    fy_vol2028 = volumes_FY[8]
                    fy_vol2029 = volumes_FY[9]
                    fy_vol2030 = volumes_FY[10]
                    fy_vol2031 = volumes_FY[11]
                    fy_vol2032 = volumes_FY[12]
                    fy_vol2033 = volumes_FY[13]
                    fy_vol2034 = volumes_FY[14]
                    fy_vol2035 = volumes_FY[15]
                    fy_vol2036 = volumes_FY[16]
                    fy_vol2037 = volumes_FY[17]
                    fy_vol2038 = volumes_FY[18]
                    fy_vol2039 = volumes_FY[19]
                    fy_vol2040 = volumes_FY[20]
                    fy_vol2041 = volumes_FY[21]
                    fy_vol2042 = volumes_FY[22]
                    fy_vol2043 = volumes_FY[23]
                    fy_vol2044 = 0.0  # volumes_FY[24]

                    fy_gm2020 = grossProfit_FY[0]
                    fy_gm2021 = grossProfit_FY[1]
                    fy_gm2022 = grossProfit_FY[2]
                    fy_gm2023 = grossProfit_FY[3]
                    fy_gm2024 = grossProfit_FY[4]
                    fy_gm2025 = grossProfit_FY[5]
                    fy_gm2026 = grossProfit_FY[6]
                    fy_gm2027 = grossProfit_FY[7]
                    fy_gm2028 = grossProfit_FY[8]
                    fy_gm2029 = grossProfit_FY[9]
                    fy_gm2030 = grossProfit_FY[10]
                    fy_gm2031 = grossProfit_FY[11]
                    fy_gm2032 = grossProfit_FY[12]
                    fy_gm2033 = grossProfit_FY[13]
                    fy_gm2034 = grossProfit_FY[14]
                    fy_gm2035 = grossProfit_FY[15]
                    fy_gm2036 = grossProfit_FY[16]
                    fy_gm2037 = grossProfit_FY[17]
                    fy_gm2038 = grossProfit_FY[18]
                    fy_gm2039 = grossProfit_FY[19]
                    fy_gm2040 = grossProfit_FY[20]
                    fy_gm2041 = grossProfit_FY[21]
                    fy_gm2042 = grossProfit_FY[22]
                    fy_gm2043 = grossProfit_FY[23]
                    fy_gm2044 = 0.0  # grossProfit_FY[24]

                    fy_wVol2020 = float(volumes_FY[0]) * statusProbability
                    fy_wVol2021 = float(volumes_FY[1]) * statusProbability
                    fy_wVol2022 = float(volumes_FY[2]) * statusProbability
                    fy_wVol2023 = float(volumes_FY[3]) * statusProbability
                    fy_wVol2024 = float(volumes_FY[4]) * statusProbability
                    fy_wVol2025 = float(volumes_FY[5]) * statusProbability
                    fy_wVol2026 = float(volumes_FY[6]) * statusProbability
                    fy_wVol2027 = float(volumes_FY[7]) * statusProbability
                    fy_wVol2028 = float(volumes_FY[8]) * statusProbability
                    fy_wVol2029 = float(volumes_FY[9]) * statusProbability
                    fy_wVol2030 = float(volumes_FY[10]) * statusProbability
                    fy_wVol2031 = float(volumes_FY[11]) * statusProbability
                    fy_wVol2032 = float(volumes_FY[12]) * statusProbability
                    fy_wVol2033 = float(volumes_FY[13]) * statusProbability
                    fy_wVol2034 = float(volumes_FY[14]) * statusProbability
                    fy_wVol2035 = float(volumes_FY[15]) * statusProbability
                    fy_wVol2036 = float(volumes_FY[16]) * statusProbability
                    fy_wVol2037 = float(volumes_FY[17]) * statusProbability
                    fy_wVol2038 = float(volumes_FY[18]) * statusProbability
                    fy_wVol2039 = float(volumes_FY[19]) * statusProbability
                    fy_wVol2040 = float(volumes_FY[20]) * statusProbability
                    fy_wVol2041 = float(volumes_FY[21]) * statusProbability
                    fy_wVol2042 = float(volumes_FY[22]) * statusProbability
                    fy_wVol2043 = float(volumes_FY[23]) * statusProbability
                    fy_wVol2044 = 0.0  # grossProfit[24]* statusProbability

                    fy_wRev2020 = revenue_FY[0] * statusProbability
                    fy_wRev2021 = revenue_FY[1] * statusProbability
                    fy_wRev2022 = revenue_FY[2] * statusProbability
                    fy_wRev2023 = revenue_FY[3] * statusProbability
                    fy_wRev2024 = revenue_FY[4] * statusProbability
                    fy_wRev2025 = revenue_FY[5] * statusProbability
                    fy_wRev2026 = revenue_FY[6] * statusProbability
                    fy_wRev2027 = revenue_FY[7] * statusProbability
                    fy_wRev2028 = revenue_FY[8] * statusProbability
                    fy_wRev2029 = revenue_FY[9] * statusProbability
                    fy_wRev2030 = revenue_FY[10] * statusProbability
                    fy_wRev2031 = revenue_FY[11] * statusProbability
                    fy_wRev2032 = revenue_FY[12] * statusProbability
                    fy_wRev2033 = revenue_FY[13] * statusProbability
                    fy_wRev2034 = revenue_FY[14] * statusProbability
                    fy_wRev2035 = revenue_FY[15] * statusProbability
                    fy_wRev2036 = revenue_FY[16] * statusProbability
                    fy_wRev2037 = revenue_FY[17] * statusProbability
                    fy_wRev2038 = revenue_FY[18] * statusProbability
                    fy_wRev2039 = revenue_FY[19] * statusProbability
                    fy_wRev2040 = revenue_FY[20] * statusProbability
                    fy_wRev2041 = revenue_FY[21] * statusProbability
                    fy_wRev2042 = revenue_FY[22] * statusProbability
                    fy_wRev2043 = revenue_FY[23] * statusProbability
                    fy_wRev2044 = 0.0  # revenue_FY[24]* statusProbability

                # setup output dictiona

                outputDict["projectReviewed"] = project.projectReviewed
                outputDict["reviewDate"] = project.reviewDate

                outputDict["salesContact"] = project.salesContact
                outputDict["idApp"] = project.pk
                outputDict["applicationLine"] = applicationLine
                outputDict["productMarketer"] = productMarketer.__str__()
                outputDict["hfg"] = hfg
                outputDict["ppos"] = ppos
                outputDict["spNumber"] = spNumber
                outputDict["applicationMain"] = applicationMain.__str__()
                outputDict["applicationDetail"] = applicationDetail.__str__()
                outputDict["rfp"] = rfp.__str__()
                outputDict["salesName"] = salesName.__str__()
                outputDict["priceSource"] = priceSource
                outputDict["familyPriceApplicable"] = familyPriceApplicable
                outputDict["familyPriceHelper"] = familyPriceHelper
                outputDict["priceType"] = project.priceType

                outputDict["currency"] = currency
                outputDict["fxRate"] = fxRate
                outputDict["comments"] = comments
                outputDict["region"] = region
                outputDict["projectName"] = projectName
                ###
                if not project.oem:
                    outputDict["oem"] = ""
                else:
                    outputDict["oem"] = project.oem.oemName

                if not project.distributor:
                    outputDict["distributor"] = ""
                else:
                    outputDict["distributor"] = project.distributor.distributorName

                if not project.tier1:
                    outputDict["tierOne"] = ""
                else:
                    outputDict["tierOne"] = project.tier1.tierOneName

                outputDict["mainCustomer"] = project.mainCustomer.customerName
                outputDict["endCustomer"] = project.finalCustomer.finalCustomerName
                outputDict["ems"] = project.ems
                outputDict["vpaCustomer"] = project.vpaCustomer

                outputDict["dragonId"] = dragonId
                outputDict["salesContact"] = salesContact
                outputDict["statusProbability"] = statusProbability
                outputDict["Probability"] = Probability
                outputDict["sop"] = sop
                outputDict["pposAvailablePgs"] = pposAvailablePgs
                outputDict["modifiedBy"] = modifiedBy
                outputDict["modifiedDate"] = modifiedDate
                outputDict["creationDate"] = creationDate

                outputDict["timeBottomUp"] = timeBottomUp
                outputDict["basicType"] = basicType
                outputDict["package"] = package
                outputDict["series"] = series
                outputDict["gen"] = gen
                outputDict["seriesLong"] = seriesLong
                outputDict["genDetail"] = genDetail
                outputDict["gmLifeTime"] = gmLifeTime
                outputDict["revEurLifeTime"] = revEurLifeTime
                outputDict["volLifeTime"] = volLifeTime
                outputDict["volWeightedLifeTime"] = volWeightedLifeTime

                if allData == True:
                    outputDict["vol2020"] = vol2020
                    outputDict["vol2021"] = vol2021
                    outputDict["vol2022"] = vol2022
                    outputDict["vol2023"] = vol2023
                    outputDict["vol2024"] = vol2024
                    outputDict["vol2025"] = vol2025
                    outputDict["vol2026"] = vol2026
                    outputDict["vol2027"] = vol2027
                    outputDict["vol2028"] = vol2028
                    outputDict["vol2029"] = vol2029
                    outputDict["vol2030"] = vol2030
                    outputDict["vol2031"] = vol2031
                    outputDict["vol2032"] = vol2032
                    outputDict["vol2033"] = vol2033
                    outputDict["vol2034"] = vol2034
                    outputDict["vol2035"] = vol2035
                    outputDict["vol2036"] = vol2036
                    outputDict["vol2037"] = vol2037
                    outputDict["vol2038"] = vol2038
                    outputDict["vol2039"] = vol2039
                    outputDict["vol2040"] = vol2040
                    outputDict["vol2041"] = vol2041
                    outputDict["vol2042"] = vol2042
                    outputDict["vol2043"] = vol2043
                    outputDict["vol2044"] = vol2044

                    outputDict["volumesCustomer"] = volumesCustomer
                    outputDict["volCustomer2020"] = volCustomer2020
                    outputDict["volCustomer2021"] = volCustomer2021
                    outputDict["volCustomer2022"] = volCustomer2022
                    outputDict["volCustomer2023"] = volCustomer2023
                    outputDict["volCustomer2024"] = volCustomer2024
                    outputDict["volCustomer2025"] = volCustomer2025
                    outputDict["volCustomer2026"] = volCustomer2026
                    outputDict["volCustomer2027"] = volCustomer2027
                    outputDict["volCustomer2028"] = volCustomer2028
                    outputDict["volCustomer2029"] = volCustomer2029
                    outputDict["volCustomer2030"] = volCustomer2030
                    outputDict["volCustomer2031"] = volCustomer2031
                    outputDict["volCustomer2032"] = volCustomer2032
                    outputDict["volCustomer2033"] = volCustomer2033
                    outputDict["volCustomer2034"] = volCustomer2034
                    outputDict["volCustomer2035"] = volCustomer2035
                    outputDict["volCustomer2036"] = volCustomer2036
                    outputDict["volCustomer2037"] = volCustomer2037
                    outputDict["volCustomer2038"] = volCustomer2038
                    outputDict["volCustomer2039"] = volCustomer2039
                    outputDict["volCustomer2040"] = volCustomer2040
                    outputDict["volCustomer2041"] = volCustomer2041
                    outputDict["volCustomer2042"] = volCustomer2042
                    outputDict["volCustomer2043"] = volCustomer2043
                    outputDict["volCustomer2044"] = volCustomer2044

                    outputDict["price2020"] = price2020
                    outputDict["price2021"] = price2021
                    outputDict["price2022"] = price2022
                    outputDict["price2023"] = price2023
                    outputDict["price2024"] = price2024
                    outputDict["price2025"] = price2025
                    outputDict["price2026"] = price2026
                    outputDict["price2027"] = price2027
                    outputDict["price2028"] = price2028
                    outputDict["price2029"] = price2029
                    outputDict["price2030"] = price2030
                    outputDict["price2031"] = price2031
                    outputDict["price2032"] = price2032
                    outputDict["price2033"] = price2033
                    outputDict["price2034"] = price2034
                    outputDict["price2035"] = price2035
                    outputDict["price2036"] = price2036
                    outputDict["price2037"] = price2037
                    outputDict["price2038"] = price2038
                    outputDict["price2039"] = price2039
                    outputDict["price2040"] = price2040
                    outputDict["price2041"] = price2041
                    outputDict["price2042"] = price2042
                    outputDict["price2043"] = price2043
                    outputDict["price2044"] = 0.0  # price2044

                    outputDict["vhk2020"] = vhk2020
                    outputDict["vhk2021"] = vhk2021
                    outputDict["vhk2022"] = vhk2022
                    outputDict["vhk2023"] = vhk2023
                    outputDict["vhk2024"] = vhk2024
                    outputDict["vhk2025"] = vhk2025
                    outputDict["vhk2026"] = vhk2026
                    outputDict["vhk2027"] = vhk2027
                    outputDict["vhk2028"] = vhk2028
                    outputDict["vhk2029"] = vhk2029
                    outputDict["vhk2030"] = vhk2030
                    outputDict["vhk2031"] = vhk2031
                    outputDict["vhk2032"] = vhk2032
                    outputDict["vhk2033"] = vhk2033
                    outputDict["vhk2034"] = vhk2034
                    outputDict["vhk2035"] = vhk2035
                    outputDict["vhk2036"] = vhk2036
                    outputDict["vhk2037"] = vhk2037
                    outputDict["vhk2038"] = vhk2038
                    outputDict["vhk2039"] = vhk2039
                    outputDict["vhk2040"] = vhk2040
                    outputDict["vhk2041"] = vhk2041
                    outputDict["vhk2042"] = vhk2042
                    outputDict["vhk2043"] = vhk2043
                    outputDict["vhk2044"] = vhk2044

                    outputDict["gm2020"] = gm2020
                    outputDict["gm2021"] = gm2021
                    outputDict["gm2022"] = gm2022
                    outputDict["gm2023"] = gm2023
                    outputDict["gm2024"] = gm2024
                    outputDict["gm2025"] = gm2025
                    outputDict["gm2026"] = gm2026
                    outputDict["gm2027"] = gm2027
                    outputDict["gm2028"] = gm2028
                    outputDict["gm2029"] = gm2029
                    outputDict["gm2030"] = gm2030
                    outputDict["gm2031"] = gm2031
                    outputDict["gm2032"] = gm2032
                    outputDict["gm2033"] = gm2033
                    outputDict["gm2034"] = gm2034
                    outputDict["gm2035"] = gm2035
                    outputDict["gm2036"] = gm2036
                    outputDict["gm2037"] = gm2037
                    outputDict["gm2038"] = gm2038
                    outputDict["gm2039"] = gm2039
                    outputDict["gm2040"] = gm2040
                    outputDict["gm2041"] = gm2041
                    outputDict["gm2042"] = gm2042
                    outputDict["gm2043"] = gm2043
                    outputDict["gm2044"] = gm2044

                    outputDict["wVol2020"] = wVol2020
                    outputDict["wVol2021"] = wVol2021
                    outputDict["wVol2022"] = wVol2022
                    outputDict["wVol2023"] = wVol2023
                    outputDict["wVol2024"] = wVol2024
                    outputDict["wVol2025"] = wVol2025
                    outputDict["wVol2026"] = wVol2026
                    outputDict["wVol2027"] = wVol2027
                    outputDict["wVol2028"] = wVol2028
                    outputDict["wVol2029"] = wVol2029
                    outputDict["wVol2030"] = wVol2030
                    outputDict["wVol2031"] = wVol2031
                    outputDict["wVol2032"] = wVol2032
                    outputDict["wVol2033"] = wVol2033
                    outputDict["wVol2034"] = wVol2034
                    outputDict["wVol2035"] = wVol2035
                    outputDict["wVol2036"] = wVol2036
                    outputDict["wVol2037"] = wVol2037
                    outputDict["wVol2038"] = wVol2038
                    outputDict["wVol2039"] = wVol2039
                    outputDict["wVol2040"] = wVol2040
                    outputDict["wVol2041"] = wVol2041
                    outputDict["wVol2042"] = wVol2042
                    outputDict["wVol2043"] = wVol2043
                    outputDict["wVol2044"] = wVol2044

                    outputDict["wRev2020"] = wRev2020
                    outputDict["wRev2021"] = wRev2021
                    outputDict["wRev2022"] = wRev2022
                    outputDict["wRev2023"] = wRev2023
                    outputDict["wRev2024"] = wRev2024
                    outputDict["wRev2025"] = wRev2025
                    outputDict["wRev2026"] = wRev2026
                    outputDict["wRev2027"] = wRev2027
                    outputDict["wRev2028"] = wRev2028
                    outputDict["wRev2029"] = wRev2029
                    outputDict["wRev2030"] = wRev2030
                    outputDict["wRev2031"] = wRev2031
                    outputDict["wRev2032"] = wRev2032
                    outputDict["wRev2033"] = wRev2033
                    outputDict["wRev2034"] = wRev2034
                    outputDict["wRev2035"] = wRev2035
                    outputDict["wRev2036"] = wRev2036
                    outputDict["wRev2037"] = wRev2037
                    outputDict["wRev2038"] = wRev2038
                    outputDict["wRev2039"] = wRev2039
                    outputDict["wRev2040"] = wRev2040
                    outputDict["wRev2041"] = wRev2041
                    outputDict["wRev2042"] = wRev2042
                    outputDict["wRev2043"] = wRev2043
                    outputDict["wRev2044"] = wRev2044

                    # month stuff
                    outputDict["fy_vol2020"] = fy_vol2020
                    outputDict["fy_vol2021"] = fy_vol2021
                    outputDict["fy_vol2022"] = fy_vol2022
                    outputDict["fy_vol2023"] = fy_vol2023
                    outputDict["fy_vol2024"] = fy_vol2024
                    outputDict["fy_vol2025"] = fy_vol2025
                    outputDict["fy_vol2026"] = fy_vol2026
                    outputDict["fy_vol2027"] = fy_vol2027
                    outputDict["fy_vol2028"] = fy_vol2028
                    outputDict["fy_vol2029"] = fy_vol2029
                    outputDict["fy_vol2030"] = fy_vol2030
                    outputDict["fy_vol2031"] = fy_vol2031
                    outputDict["fy_vol2032"] = fy_vol2032
                    outputDict["fy_vol2033"] = fy_vol2033
                    outputDict["fy_vol2034"] = fy_vol2034
                    outputDict["fy_vol2035"] = fy_vol2035
                    outputDict["fy_vol2036"] = fy_vol2036
                    outputDict["fy_vol2037"] = fy_vol2037
                    outputDict["fy_vol2038"] = fy_vol2038
                    outputDict["fy_vol2039"] = fy_vol2039
                    outputDict["fy_vol2040"] = fy_vol2040
                    outputDict["fy_vol2041"] = fy_vol2041
                    outputDict["fy_vol2042"] = fy_vol2042
                    outputDict["fy_vol2043"] = fy_vol2043
                    outputDict["fy_vol2044"] = fy_vol2044

                    outputDict["fy_gm2020"] = fy_gm2020
                    outputDict["fy_gm2021"] = fy_gm2021
                    outputDict["fy_gm2022"] = fy_gm2022
                    outputDict["fy_gm2023"] = fy_gm2023
                    outputDict["fy_gm2024"] = fy_gm2024
                    outputDict["fy_gm2025"] = fy_gm2025
                    outputDict["fy_gm2026"] = fy_gm2026
                    outputDict["fy_gm2027"] = fy_gm2027
                    outputDict["fy_gm2028"] = fy_gm2028
                    outputDict["fy_gm2029"] = fy_gm2029
                    outputDict["fy_gm2030"] = fy_gm2030
                    outputDict["fy_gm2031"] = fy_gm2031
                    outputDict["fy_gm2032"] = fy_gm2032
                    outputDict["fy_gm2033"] = fy_gm2033
                    outputDict["fy_gm2034"] = fy_gm2034
                    outputDict["fy_gm2035"] = fy_gm2035
                    outputDict["fy_gm2036"] = fy_gm2036
                    outputDict["fy_gm2037"] = fy_gm2037
                    outputDict["fy_gm2038"] = fy_gm2038
                    outputDict["fy_gm2039"] = fy_gm2039
                    outputDict["fy_gm2040"] = fy_gm2040
                    outputDict["fy_gm2041"] = fy_gm2041
                    outputDict["fy_gm2042"] = fy_gm2042
                    outputDict["fy_gm2043"] = fy_gm2043
                    outputDict["fy_gm2044"] = fy_gm2044

                    outputDict["fy_wVol2020"] = fy_wVol2020
                    outputDict["fy_wVol2021"] = fy_wVol2021
                    outputDict["fy_wVol2022"] = fy_wVol2022
                    outputDict["fy_wVol2023"] = fy_wVol2023
                    outputDict["fy_wVol2024"] = fy_wVol2024
                    outputDict["fy_wVol2025"] = fy_wVol2025
                    outputDict["fy_wVol2026"] = fy_wVol2026
                    outputDict["fy_wVol2027"] = fy_wVol2027
                    outputDict["fy_wVol2028"] = fy_wVol2028
                    outputDict["fy_wVol2029"] = fy_wVol2029
                    outputDict["fy_wVol2030"] = fy_wVol2030
                    outputDict["fy_wVol2031"] = fy_wVol2031
                    outputDict["fy_wVol2032"] = fy_wVol2032
                    outputDict["fy_wVol2033"] = fy_wVol2033
                    outputDict["fy_wVol2034"] = fy_wVol2034
                    outputDict["fy_wVol2035"] = fy_wVol2035
                    outputDict["fy_wVol2036"] = fy_wVol2036
                    outputDict["fy_wVol2037"] = fy_wVol2037
                    outputDict["fy_wVol2038"] = fy_wVol2038
                    outputDict["fy_wVol2039"] = fy_wVol2039
                    outputDict["fy_wVol2040"] = fy_wVol2040
                    outputDict["fy_wVol2041"] = fy_wVol2041
                    outputDict["fy_wVol2042"] = fy_wVol2042
                    outputDict["fy_wVol2043"] = fy_wVol2043
                    outputDict["fy_wVol2044"] = fy_wVol2044

                    outputDict["fy_wRev2020"] = fy_wRev2020
                    outputDict["fy_wRev2021"] = fy_wRev2021
                    outputDict["fy_wRev2022"] = fy_wRev2022
                    outputDict["fy_wRev2023"] = fy_wRev2023
                    outputDict["fy_wRev2024"] = fy_wRev2024
                    outputDict["fy_wRev2025"] = fy_wRev2025
                    outputDict["fy_wRev2026"] = fy_wRev2026
                    outputDict["fy_wRev2027"] = fy_wRev2027
                    outputDict["fy_wRev2028"] = fy_wRev2028
                    outputDict["fy_wRev2029"] = fy_wRev2029
                    outputDict["fy_wRev2030"] = fy_wRev2030
                    outputDict["fy_wRev2031"] = fy_wRev2031
                    outputDict["fy_wRev2032"] = fy_wRev2032
                    outputDict["fy_wRev2033"] = fy_wRev2033
                    outputDict["fy_wRev2034"] = fy_wRev2034
                    outputDict["fy_wRev2035"] = fy_wRev2035
                    outputDict["fy_wRev2036"] = fy_wRev2036
                    outputDict["fy_wRev2037"] = fy_wRev2037
                    outputDict["fy_wRev2038"] = fy_wRev2038
                    outputDict["fy_wRev2039"] = fy_wRev2039
                    outputDict["fy_wRev2040"] = fy_wRev2040
                    outputDict["fy_wRev2041"] = fy_wRev2041
                    outputDict["fy_wRev2042"] = fy_wRev2042
                    outputDict["fy_wRev2043"] = fy_wRev2043
                    outputDict["fy_wRev2044"] = fy_wRev2044

                outputArray.append(outputDict)

            else:
                print("project user", project.user)
                print("project", project)
                print("rfp", project.sales_name.rfp)
                idApp = project.pk
                applicationLine = project.productMarketer.applicationLine
                productMarketer = project.productMarketer.__str__()
                hfg = project.sales_name.rfp.hfg
                ppos = project.sales_name.rfp.ppos
                spNumber = project.spNumber
                applicationMain = project.applicationMain.__str__()
                applicationDetail = project.applicationDetail.__str__()
                rfp = project.sales_name.rfp.__str__()
                salesName = project.sales_name.__str__()
                priceSource = project.priceType.priceType
                familyPriceApplicable = project.familyPriceApplicable
                familyPriceHelper = project.familyPriceDetails
                currency = "EUR"
                fxRate = 1.0
                comments = project.comment
                region = project.region
                projectName = project.projectName
                dragonId = project.salesOpportunity.dragonId
                salesContact = project.salesContact
                statusProbability = project.status.statusDisplay
                Probability = project.status
                sop = project.estimatedSop
                pposAvailablePgs = "fm"
                modifiedBy = project.user.username
                modifiedDate = project.modifiedDate
                creationDate = project.creationDate
                timeBottomUp = 0
                basicType = project.sales_name.rfp.basicType
                package = project.sales_name.rfp.packageHelper
                series = project.sales_name.rfp.seriesHelper
                gen = project.sales_name.rfp.familyHelper
                seriesLong = project.sales_name.rfp.package.series.description
                genDetail = project.sales_name.rfp.package.series.family.family_name
                gmLifeTime = cummulativeGrossMargin
                revEurLifeTime = cummulativeRevenue
                volLifeTime = cummulativeVolume
                volWeightedLifeTime = cummulativeWeightedVolume

                print("failing routine")
                outputDict = dict()

                print(
                    "type reviewed",
                    project.projectReviewed,
                    type(project.projectReviewed),
                )
                outputDict["projectReviewed"] = project.projectReviewed
                outputDict["reviewDate"] = project.reviewDate

                outputDict["idApp"] = project.pk
                outputDict["applicationLine"] = applicationLine
                outputDict["productMarketer"] = productMarketer
                outputDict["salesContact"] = project.salesContact

                outputDict["hfg"] = hfg
                outputDict["ppos"] = ppos
                outputDict["spNumber"] = spNumber
                outputDict["applicationMain"] = applicationMain
                outputDict["applicationDetail"] = applicationDetail
                outputDict["rfp"] = rfp
                outputDict["salesName"] = salesName
                outputDict["priceSource"] = priceSource
                outputDict["familyPriceApplicable"] = familyPriceApplicable
                outputDict["familyPriceHelper"] = familyPriceHelper
                outputDict["priceType"] = project.priceType

                outputDict["currency"] = currency
                outputDict["fxRate"] = fxRate
                outputDict["comments"] = comments
                outputDict["region"] = region
                outputDict["projectName"] = projectName
                if not project.oem:
                    outputDict["oem"] = ""
                else:
                    outputDict["oem"] = project.oem.oemName

                if not project.distributor:
                    outputDict["distributor"] = ""
                else:
                    outputDict["distributor"] = project.distributor.distributorName

                if not project.tier1:
                    outputDict["tierOne"] = ""
                else:
                    outputDict["tierOne"] = project.tier1.tierOneName

                outputDict["mainCustomer"] = project.mainCustomer.customerName
                outputDict["endCustomer"] = project.finalCustomer.finalCustomerName

                if not project.ems:
                    outputDict["ems"] = ""
                else:
                    outputDict["ems"] = project.ems.emsName

                outputDict["vpaCustomer"] = project.vpaCustomer
                outputDict["dragonId"] = dragonId
                outputDict["salesContact"] = salesContact
                outputDict["statusProbability"] = statusProbability
                outputDict["Probability"] = Probability
                outputDict["sop"] = sop
                outputDict["pposAvailablePgs"] = pposAvailablePgs
                outputDict["modifiedBy"] = modifiedBy
                outputDict["modifiedDate"] = modifiedDate
                outputDict["creationDate"] = creationDate

                outputDict["timeBottomUp"] = timeBottomUp
                outputDict["basicType"] = basicType
                outputDict["package"] = package
                outputDict["series"] = series
                outputDict["gen"] = gen
                outputDict["seriesLong"] = seriesLong
                outputDict["genDetail"] = genDetail
                outputDict["gmLifeTime"] = gmLifeTime
                outputDict["revEurLifeTime"] = revEurLifeTime
                outputDict["volLifeTime"] = volLifeTime
                outputDict["volWeightedLifeTime"] = volWeightedLifeTime

                outputDict["vol2020"] = 0.0
                outputDict["vol2021"] = 0.0
                outputDict["vol2022"] = 0.0
                outputDict["vol2023"] = 0.0
                outputDict["vol2024"] = 0.0
                outputDict["vol2025"] = 0.0
                outputDict["vol2026"] = 0.0
                outputDict["vol2027"] = 0.0
                outputDict["vol2028"] = 0.0
                outputDict["vol2029"] = 0.0
                outputDict["vol2030"] = 0.0
                outputDict["vol2031"] = 0.0
                outputDict["vol2032"] = 0.0
                outputDict["vol2033"] = 0.0
                outputDict["vol2034"] = 0.0
                outputDict["vol2035"] = 0.0
                outputDict["vol2036"] = 0.0
                outputDict["vol2037"] = 0.0
                outputDict["vol2038"] = 0.0
                outputDict["vol2039"] = 0.0
                outputDict["vol2040"] = 0.0
                outputDict["vol2041"] = 0.0
                outputDict["vol2042"] = 0.0
                outputDict["vol2043"] = 0.0
                outputDict["vol2044"] = 0.0

                outputDict["volumesCustomer"] = 0.0
                outputDict["volCustomer2020"] = 0.0
                outputDict["volCustomer2021"] = 0.0
                outputDict["volCustomer2022"] = 0.0
                outputDict["volCustomer2023"] = 0.0
                outputDict["volCustomer2024"] = 0.0
                outputDict["volCustomer2025"] = 0.0
                outputDict["volCustomer2026"] = 0.0
                outputDict["volCustomer2027"] = 0.0
                outputDict["volCustomer2028"] = 0.0
                outputDict["volCustomer2029"] = 0.0
                outputDict["volCustomer2030"] = 0.0
                outputDict["volCustomer2031"] = 0.0
                outputDict["volCustomer2032"] = 0.0
                outputDict["volCustomer2033"] = 0.0
                outputDict["volCustomer2034"] = 0.0
                outputDict["volCustomer2035"] = 0.0
                outputDict["volCustomer2036"] = 0.0
                outputDict["volCustomer2037"] = 0.0
                outputDict["volCustomer2038"] = 0.0
                outputDict["volCustomer2039"] = 0.0
                outputDict["volCustomer2040"] = 0.0
                outputDict["volCustomer2041"] = 0.0
                outputDict["volCustomer2042"] = 0.0
                outputDict["volCustomer2043"] = 0.0
                outputDict["volCustomer2044"] = 0.0

                outputDict["price2020"] = 0.0
                outputDict["price2021"] = 0.0
                outputDict["price2022"] = 0.0
                outputDict["price2023"] = 0.0
                outputDict["price2024"] = 0.0
                outputDict["price2025"] = 0.0
                outputDict["price2026"] = 0.0
                outputDict["price2027"] = 0.0
                outputDict["price2028"] = 0.0
                outputDict["price2029"] = 0.0
                outputDict["price2030"] = 0.0
                outputDict["price2031"] = 0.0
                outputDict["price2032"] = 0.0
                outputDict["price2033"] = 0.0
                outputDict["price2034"] = 0.0
                outputDict["price2035"] = 0.0
                outputDict["price2036"] = 0.0
                outputDict["price2037"] = 0.0
                outputDict["price2038"] = 0.0
                outputDict["price2039"] = 0.0
                outputDict["price2040"] = 0.0
                outputDict["price2041"] = 0.0
                outputDict["price2042"] = 0.0
                outputDict["price2043"] = 0.0
                outputDict["price2044"] = 0.0

                outputDict["vhk2020"] = 0.0
                outputDict["vhk2021"] = 0.0
                outputDict["vhk2022"] = 0.0
                outputDict["vhk2023"] = 0.0
                outputDict["vhk2024"] = 0.0
                outputDict["vhk2025"] = 0.0
                outputDict["vhk2026"] = 0.0
                outputDict["vhk2027"] = 0.0
                outputDict["vhk2028"] = 0.0
                outputDict["vhk2029"] = 0.0
                outputDict["vhk2030"] = 0.0
                outputDict["vhk2031"] = 0.0
                outputDict["vhk2032"] = 0.0
                outputDict["vhk2033"] = 0.0
                outputDict["vhk2034"] = 0.0
                outputDict["vhk2035"] = 0.0
                outputDict["vhk2036"] = 0.0
                outputDict["vhk2037"] = 0.0
                outputDict["vhk2038"] = 0.0
                outputDict["vhk2039"] = 0.0
                outputDict["vhk2040"] = 0.0
                outputDict["vhk2041"] = 0.0
                outputDict["vhk2042"] = 0.0
                outputDict["vhk2043"] = 0.0
                outputDict["vhk2044"] = 0.0

                outputDict["gm2020"] = 0.0
                outputDict["gm2021"] = 0.0
                outputDict["gm2022"] = 0.0
                outputDict["gm2023"] = 0.0
                outputDict["gm2024"] = 0.0
                outputDict["gm2025"] = 0.0
                outputDict["gm2026"] = 0.0
                outputDict["gm2027"] = 0.0
                outputDict["gm2028"] = 0.0
                outputDict["gm2029"] = 0.0
                outputDict["gm2030"] = 0.0
                outputDict["gm2031"] = 0.0
                outputDict["gm2032"] = 0.0
                outputDict["gm2033"] = 0.0
                outputDict["gm2034"] = 0.0
                outputDict["gm2035"] = 0.0
                outputDict["gm2036"] = 0.0
                outputDict["gm2037"] = 0.0
                outputDict["gm2038"] = 0.0
                outputDict["gm2039"] = 0.0
                outputDict["gm2040"] = 0.0
                outputDict["gm2041"] = 0.0
                outputDict["gm2042"] = 0.0
                outputDict["gm2043"] = 0.0
                outputDict["gm2044"] = 0.0

                outputDict["wVol2020"] = 0.0
                outputDict["wVol2021"] = 0.0
                outputDict["wVol2022"] = 0.0
                outputDict["wVol2023"] = 0.0
                outputDict["wVol2024"] = 0.0
                outputDict["wVol2025"] = 0.0
                outputDict["wVol2026"] = 0.0
                outputDict["wVol2027"] = 0.0
                outputDict["wVol2028"] = 0.0
                outputDict["wVol2029"] = 0.0
                outputDict["wVol2030"] = 0.0
                outputDict["wVol2031"] = 0.0
                outputDict["wVol2032"] = 0.0
                outputDict["wVol2033"] = 0.0
                outputDict["wVol2034"] = 0.0
                outputDict["wVol2035"] = 0.0
                outputDict["wVol2036"] = 0.0
                outputDict["wVol2037"] = 0.0
                outputDict["wVol2038"] = 0.0
                outputDict["wVol2039"] = 0.0
                outputDict["wVol2040"] = 0.0
                outputDict["wVol2041"] = 0.0
                outputDict["wVol2042"] = 0.0
                outputDict["wVol2043"] = 0.0
                outputDict["wVol2044"] = 0.0

                outputDict["wRev2020"] = 0.0
                outputDict["wRev2021"] = 0.0
                outputDict["wRev2022"] = 0.0
                outputDict["wRev2023"] = 0.0
                outputDict["wRev2024"] = 0.0
                outputDict["wRev2025"] = 0.0
                outputDict["wRev2026"] = 0.0
                outputDict["wRev2027"] = 0.0
                outputDict["wRev2028"] = 0.0
                outputDict["wRev2029"] = 0.0
                outputDict["wRev2030"] = 0.0
                outputDict["wRev2031"] = 0.0
                outputDict["wRev2032"] = 0.0
                outputDict["wRev2033"] = 0.0
                outputDict["wRev2034"] = 0.0
                outputDict["wRev2035"] = 0.0
                outputDict["wRev2036"] = 0.0
                outputDict["wRev2037"] = 0.0
                outputDict["wRev2038"] = 0.0
                outputDict["wRev2039"] = 0.0
                outputDict["wRev2040"] = 0.0
                outputDict["wRev2041"] = 0.0
                outputDict["wRev2042"] = 0.0
                outputDict["wRev2043"] = 0.0
                outputDict["wRev2044"] = 0.0

                # month stuff
                outputDict["fy_vol2020"] = 0.0
                outputDict["fy_vol2021"] = 0.0
                outputDict["fy_vol2022"] = 0.0
                outputDict["fy_vol2023"] = 0.0
                outputDict["fy_vol2024"] = 0.0
                outputDict["fy_vol2025"] = 0.0
                outputDict["fy_vol2026"] = 0.0
                outputDict["fy_vol2027"] = 0.0
                outputDict["fy_vol2028"] = 0.0
                outputDict["fy_vol2029"] = 0.0
                outputDict["fy_vol2030"] = 0.0
                outputDict["fy_vol2031"] = 0.0
                outputDict["fy_vol2032"] = 0.0
                outputDict["fy_vol2033"] = 0.0
                outputDict["fy_vol2034"] = 0.0
                outputDict["fy_vol2035"] = 0.0
                outputDict["fy_vol2036"] = 0.0
                outputDict["fy_vol2037"] = 0.0
                outputDict["fy_vol2038"] = 0.0
                outputDict["fy_vol2039"] = 0.0
                outputDict["fy_vol2040"] = 0.0
                outputDict["fy_vol2041"] = 0.0
                outputDict["fy_vol2042"] = 0.0
                outputDict["fy_vol2043"] = 0.0
                outputDict["fy_vol2044"] = 0.0

                outputDict["fy_gm2020"] = 0.0
                outputDict["fy_gm2021"] = 0.0
                outputDict["fy_gm2022"] = 0.0
                outputDict["fy_gm2023"] = 0.0
                outputDict["fy_gm2024"] = 0.0
                outputDict["fy_gm2025"] = 0.0
                outputDict["fy_gm2026"] = 0.0
                outputDict["fy_gm2027"] = 0.0
                outputDict["fy_gm2028"] = 0.0
                outputDict["fy_gm2029"] = 0.0
                outputDict["fy_gm2030"] = 0.0
                outputDict["fy_gm2031"] = 0.0
                outputDict["fy_gm2032"] = 0.0
                outputDict["fy_gm2033"] = 0.0
                outputDict["fy_gm2034"] = 0.0
                outputDict["fy_gm2035"] = 0.0
                outputDict["fy_gm2036"] = 0.0
                outputDict["fy_gm2037"] = 0.0
                outputDict["fy_gm2038"] = 0.0
                outputDict["fy_gm2039"] = 0.0
                outputDict["fy_gm2040"] = 0.0
                outputDict["fy_gm2041"] = 0.0
                outputDict["fy_gm2042"] = 0.0
                outputDict["fy_gm2043"] = 0.0
                outputDict["fy_gm2044"] = 0.0

                outputDict["fy_wVol2020"] = 0.0
                outputDict["fy_wVol2021"] = 0.0
                outputDict["fy_wVol2022"] = 0.0
                outputDict["fy_wVol2023"] = 0.0
                outputDict["fy_wVol2024"] = 0.0
                outputDict["fy_wVol2025"] = 0.0
                outputDict["fy_wVol2026"] = 0.0
                outputDict["fy_wVol2027"] = 0.0
                outputDict["fy_wVol2028"] = 0.0
                outputDict["fy_wVol2029"] = 0.0
                outputDict["fy_wVol2030"] = 0.0
                outputDict["fy_wVol2031"] = 0.0
                outputDict["fy_wVol2032"] = 0.0
                outputDict["fy_wVol2033"] = 0.0
                outputDict["fy_wVol2034"] = 0.0
                outputDict["fy_wVol2035"] = 0.0
                outputDict["fy_wVol2036"] = 0.0
                outputDict["fy_wVol2037"] = 0.0
                outputDict["fy_wVol2038"] = 0.0
                outputDict["fy_wVol2039"] = 0.0
                outputDict["fy_wVol2040"] = 0.0
                outputDict["fy_wVol2041"] = 0.0
                outputDict["fy_wVol2042"] = 0.0
                outputDict["fy_wVol2043"] = 0.0
                outputDict["fy_wVol2044"] = 0.0

                outputDict["fy_wRev2020"] = 0.0
                outputDict["fy_wRev2021"] = 0.0
                outputDict["fy_wRev2022"] = 0.0
                outputDict["fy_wRev2023"] = 0.0
                outputDict["fy_wRev2024"] = 0.0
                outputDict["fy_wRev2025"] = 0.0
                outputDict["fy_wRev2026"] = 0.0
                outputDict["fy_wRev2027"] = 0.0
                outputDict["fy_wRev2028"] = 0.0
                outputDict["fy_wRev2029"] = 0.0
                outputDict["fy_wRev2030"] = 0.0
                outputDict["fy_wRev2031"] = 0.0
                outputDict["fy_wRev2032"] = 0.0
                outputDict["fy_wRev2033"] = 0.0
                outputDict["fy_wRev2034"] = 0.0
                outputDict["fy_wRev2035"] = 0.0
                outputDict["fy_wRev2036"] = 0.0
                outputDict["fy_wRev2037"] = 0.0
                outputDict["fy_wRev2038"] = 0.0
                outputDict["fy_wRev2039"] = 0.0
                outputDict["fy_wRev2040"] = 0.0
                outputDict["fy_wRev2041"] = 0.0
                outputDict["fy_wRev2042"] = 0.0
                outputDict["fy_wRev2043"] = 0.0
                outputDict["fy_wRev2044"] = 0.0

                outputArray.append(outputDict)

    # pack everything into a dictionary together with the project
    result_list = list(
        Project.objects.all().values(
            "projectName",
            "sales_name",
            "region",
            "status",
        )
    )

    """
    print("############")
    print("result list", type(outputArray))
    print(outputArray)
    print("############ result END")
    """

    # now average prices
    totalAsps = [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    ]
    totalAspsWeighted = [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    ]

    for index in range(len(years)):
        try:
            totalAsps[index] = totalRevenues[index] / totalVolumes[index]
            totalAspsWeighted[index] = (
                totalRevenuesWeighted[index] / totalVolumesWeighted[index]
            )
        except:
            print("division failed", index)

    return (
        outputArray,
        totalVolumes,
        totalVolumesWeighted,
        totalRevenues,
        totalRevenuesWeighted,
        totalMargin,
        totalMarginWeighted,
        totalAsps,
        totalAspsWeighted,
        years,
    )


def getBoupData(request, allData):

    # why needed?
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
    ]
    totalVolumes = [
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
    ]
    totalVolumesWeighted = [
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
    ]
    totalMargin = [
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
    ]
    totalMarginWeighted = [
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
    ]
    totalRevenues = [
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
    ]
    totalRevenuesWeighted = [
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
    ]
    totalAsps = [
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
    ]
    totalAspsWeighted = [
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
    ]

    # tbd - one view for the own department (to reduce query), and then one view for atv mc

    # get BoUp entry
    BoUps = BoUp.objects.all()
    print("---> BoUps", type(BoUps))

    outputArray = []

    if BoUps.count() > 0:
        print("Start")
        for BoUpObject in BoUps:
            print("Object: ", BoUpObject)
            outputDict = dict()  # ["dummy 12346778"]

            # setup output dictiona

            outputDict["projectReviewed"] = BoUpObject.Reviewed
            outputDict["reviewDate"] = BoUpObject.reviewDate

            outputDict["salesContact"] = BoUpObject.salesContact
            outputDict["idApp"] = BoUpObject.pk  # ID_APP.__str__()
            outputDict["applicationLine"] = BoUpObject.applicationLine
            outputDict["productMarketer"] = BoUpObject.productMarketer.__str__()
            outputDict["hfg"] = BoUpObject.hfg
            outputDict["ppos"] = BoUpObject.ppos
            outputDict["spNumber"] = BoUpObject.spNumber
            outputDict["applicationMain"] = BoUpObject.applicationMain.__str__()
            outputDict["applicationDetail"] = BoUpObject.applicationDetail.__str__()
            outputDict["rfp"] = BoUpObject.rfp.__str__()
            outputDict["salesName"] = BoUpObject.salesName.__str__()
            outputDict["priceSource"] = BoUpObject.priceSource
            outputDict["familyPriceApplicable"] = BoUpObject.familyPriceApplicable
            outputDict["familyPriceHelper"] = BoUpObject.familyPriceDetails
            outputDict["priceType"] = BoUpObject.priceType

            outputDict["currency"] = BoUpObject.currency
            outputDict["fxRate"] = BoUpObject.fxRate
            outputDict["comments"] = BoUpObject.comment
            outputDict["region"] = BoUpObject.region
            outputDict["projectName"] = BoUpObject.projectName
            ###
            if not BoUpObject.oem:
                outputDict["oem"] = ""
            else:
                outputDict["oem"] = BoUpObject.oem.oemName

            if not BoUpObject.plHfg:
                outputDict["plHfg"] = ""
            else:
                outputDict["plHfg"] = BoUpObject.plHfg

            outputDict["distributor"] = BoUpObject.distributor
            outputDict["tierOne"] = BoUpObject.tier1
            outputDict["mainCustomer"] = BoUpObject.mainCustomer.customerName
            outputDict["endCustomer"] = BoUpObject.endCustomer.finalCustomerName
            outputDict["ems"] = BoUpObject.ems
            outputDict["vpaCustomer"] = BoUpObject.vpaCustomer

            outputDict["dragonId"] = BoUpObject.dragonId
            outputDict["salesContact"] = BoUpObject.salesContact
            outputDict["statusProbability"] = BoUpObject.statusProbability
            outputDict["Probability"] = BoUpObject.probability
            outputDict["sop"] = BoUpObject.sop
            outputDict["pposAvailablePgs"] = BoUpObject.availablePGS
            outputDict["modifiedBy"] = BoUpObject.modifiedBy.username
            outputDict["modifiedDate"] = BoUpObject.modifiedDate
            outputDict["creationDate"] = BoUpObject.creationDate

            outputDict["timeBottomUp"] = BoUpObject.timeBottomUp
            outputDict["basicType"] = BoUpObject.basicType
            outputDict["package"] = BoUpObject.package
            outputDict["series"] = BoUpObject.series
            outputDict["gen"] = BoUpObject.gen
            outputDict["seriesLong"] = BoUpObject.seriesLong
            outputDict["genDetail"] = BoUpObject.genDetail
            outputDict["gmLifeTime"] = BoUpObject.gmLifeTime
            outputDict["revEurLifeTime"] = BoUpObject.revEurLifeTime
            outputDict["volLifeTime"] = BoUpObject.volLifeTime
            outputDict["volWeightedLifeTime"] = BoUpObject.volWeightedLifeTime
            outputDict["contractualCurrency"] = BoUpObject.contractualCurrency

            print("added generic data")
            if allData == True:
                outputDict["vol2020"] = BoUpObject.vol2020
                outputDict["vol2021"] = BoUpObject.vol2021
                outputDict["vol2022"] = BoUpObject.vol2022
                outputDict["vol2023"] = BoUpObject.vol2023
                outputDict["vol2024"] = BoUpObject.vol2024
                outputDict["vol2025"] = BoUpObject.vol2025
                outputDict["vol2026"] = BoUpObject.vol2026
                outputDict["vol2027"] = BoUpObject.vol2027
                outputDict["vol2028"] = BoUpObject.vol2028
                outputDict["vol2029"] = BoUpObject.vol2029
                outputDict["vol2030"] = BoUpObject.vol2030
                outputDict["vol2031"] = BoUpObject.vol2031
                outputDict["vol2032"] = BoUpObject.vol2032
                outputDict["vol2033"] = BoUpObject.vol2033
                outputDict["vol2034"] = BoUpObject.vol2034
                outputDict["vol2035"] = BoUpObject.vol2035
                outputDict["vol2036"] = BoUpObject.vol2036
                outputDict["vol2037"] = BoUpObject.vol2037
                outputDict["vol2038"] = BoUpObject.vol2038
                outputDict["vol2039"] = BoUpObject.vol2039
                outputDict["vol2040"] = BoUpObject.vol2040
                outputDict["vol2041"] = BoUpObject.vol2041
                outputDict["vol2042"] = BoUpObject.vol2042
                outputDict["vol2043"] = BoUpObject.vol2043
                outputDict["vol2044"] = BoUpObject.vol2044

                outputDict["volCustomer2020"] = BoUpObject.volCustomer2020
                outputDict["volCustomer2021"] = BoUpObject.volCustomer2021
                outputDict["volCustomer2022"] = BoUpObject.volCustomer2022
                outputDict["volCustomer2023"] = BoUpObject.volCustomer2023
                outputDict["volCustomer2024"] = BoUpObject.volCustomer2024
                outputDict["volCustomer2025"] = BoUpObject.volCustomer2025
                outputDict["volCustomer2026"] = BoUpObject.volCustomer2026
                outputDict["volCustomer2027"] = BoUpObject.volCustomer2027
                outputDict["volCustomer2028"] = BoUpObject.volCustomer2028
                outputDict["volCustomer2029"] = BoUpObject.volCustomer2029
                outputDict["volCustomer2030"] = BoUpObject.volCustomer2030
                outputDict["volCustomer2031"] = BoUpObject.volCustomer2031
                outputDict["volCustomer2032"] = BoUpObject.volCustomer2032
                outputDict["volCustomer2033"] = BoUpObject.volCustomer2033
                outputDict["volCustomer2034"] = BoUpObject.volCustomer2034
                outputDict["volCustomer2035"] = BoUpObject.volCustomer2035
                outputDict["volCustomer2036"] = BoUpObject.volCustomer2036
                outputDict["volCustomer2037"] = BoUpObject.volCustomer2037
                outputDict["volCustomer2038"] = BoUpObject.volCustomer2038
                outputDict["volCustomer2039"] = BoUpObject.volCustomer2039
                outputDict["volCustomer2040"] = BoUpObject.volCustomer2040
                outputDict["volCustomer2041"] = BoUpObject.volCustomer2041
                outputDict["volCustomer2042"] = BoUpObject.volCustomer2042
                outputDict["volCustomer2043"] = BoUpObject.volCustomer2043
                outputDict["volCustomer2044"] = BoUpObject.volCustomer2044

                outputDict["price2020"] = BoUpObject.price2020
                outputDict["price2021"] = BoUpObject.price2021
                outputDict["price2022"] = BoUpObject.price2022
                outputDict["price2023"] = BoUpObject.price2023
                outputDict["price2024"] = BoUpObject.price2024
                outputDict["price2025"] = BoUpObject.price2025
                outputDict["price2026"] = BoUpObject.price2026
                outputDict["price2027"] = BoUpObject.price2027
                outputDict["price2028"] = BoUpObject.price2028
                outputDict["price2029"] = BoUpObject.price2029
                outputDict["price2030"] = BoUpObject.price2030
                outputDict["price2031"] = BoUpObject.price2031
                outputDict["price2032"] = BoUpObject.price2032
                outputDict["price2033"] = BoUpObject.price2033
                outputDict["price2034"] = BoUpObject.price2034
                outputDict["price2035"] = BoUpObject.price2035
                outputDict["price2036"] = BoUpObject.price2036
                outputDict["price2037"] = BoUpObject.price2037
                outputDict["price2038"] = BoUpObject.price2038
                outputDict["price2039"] = BoUpObject.price2039
                outputDict["price2040"] = BoUpObject.price2040
                outputDict["price2041"] = BoUpObject.price2041
                outputDict["price2042"] = BoUpObject.price2042
                outputDict["price2043"] = BoUpObject.price2043
                outputDict["price2044"] = 0.0

                outputDict["vhk2020"] = BoUpObject.vhk2020
                outputDict["vhk2021"] = BoUpObject.vhk2021
                outputDict["vhk2022"] = BoUpObject.vhk2022
                outputDict["vhk2023"] = BoUpObject.vhk2023
                outputDict["vhk2024"] = BoUpObject.vhk2024
                outputDict["vhk2025"] = BoUpObject.vhk2025
                outputDict["vhk2026"] = BoUpObject.vhk2026
                outputDict["vhk2027"] = BoUpObject.vhk2027
                outputDict["vhk2028"] = BoUpObject.vhk2028
                outputDict["vhk2029"] = BoUpObject.vhk2029
                outputDict["vhk2030"] = BoUpObject.vhk2030
                outputDict["vhk2031"] = BoUpObject.vhk2031
                outputDict["vhk2032"] = BoUpObject.vhk2032
                outputDict["vhk2033"] = BoUpObject.vhk2033
                outputDict["vhk2034"] = BoUpObject.vhk2034
                outputDict["vhk2035"] = BoUpObject.vhk2035
                outputDict["vhk2036"] = BoUpObject.vhk2036
                outputDict["vhk2037"] = BoUpObject.vhk2037
                outputDict["vhk2038"] = BoUpObject.vhk2038
                outputDict["vhk2039"] = BoUpObject.vhk2039
                outputDict["vhk2040"] = BoUpObject.vhk2040
                outputDict["vhk2041"] = BoUpObject.vhk2041
                outputDict["vhk2042"] = BoUpObject.vhk2042
                outputDict["vhk2043"] = BoUpObject.vhk2043
                outputDict["vhk2044"] = BoUpObject.vhk2044

                outputDict["gm2020"] = BoUpObject.gm2020
                outputDict["gm2021"] = BoUpObject.gm2021
                outputDict["gm2022"] = BoUpObject.gm2022
                outputDict["gm2023"] = BoUpObject.gm2023
                outputDict["gm2024"] = BoUpObject.gm2024
                outputDict["gm2025"] = BoUpObject.gm2025
                outputDict["gm2026"] = BoUpObject.gm2026
                outputDict["gm2027"] = BoUpObject.gm2027
                outputDict["gm2028"] = BoUpObject.gm2028
                outputDict["gm2029"] = BoUpObject.gm2029
                outputDict["gm2030"] = BoUpObject.gm2030
                outputDict["gm2031"] = BoUpObject.gm2031
                outputDict["gm2032"] = BoUpObject.gm2032
                outputDict["gm2033"] = BoUpObject.gm2033
                outputDict["gm2034"] = BoUpObject.gm2034
                outputDict["gm2035"] = BoUpObject.gm2035
                outputDict["gm2036"] = BoUpObject.gm2036
                outputDict["gm2037"] = BoUpObject.gm2037
                outputDict["gm2038"] = BoUpObject.gm2038
                outputDict["gm2039"] = BoUpObject.gm2039
                outputDict["gm2040"] = BoUpObject.gm2040
                outputDict["gm2041"] = BoUpObject.gm2041
                outputDict["gm2042"] = BoUpObject.gm2042
                outputDict["gm2043"] = BoUpObject.gm2043
                outputDict["gm2044"] = BoUpObject.gm2044

                outputDict["wVol2020"] = BoUpObject.wVol2020
                outputDict["wVol2021"] = BoUpObject.wVol2021
                outputDict["wVol2022"] = BoUpObject.wVol2022
                outputDict["wVol2023"] = BoUpObject.wVol2023
                outputDict["wVol2024"] = BoUpObject.wVol2024
                outputDict["wVol2025"] = BoUpObject.wVol2025
                outputDict["wVol2026"] = BoUpObject.wVol2026
                outputDict["wVol2027"] = BoUpObject.wVol2027
                outputDict["wVol2028"] = BoUpObject.wVol2028
                outputDict["wVol2029"] = BoUpObject.wVol2029
                outputDict["wVol2030"] = BoUpObject.wVol2030
                outputDict["wVol2031"] = BoUpObject.wVol2031
                outputDict["wVol2032"] = BoUpObject.wVol2032
                outputDict["wVol2033"] = BoUpObject.wVol2033
                outputDict["wVol2034"] = BoUpObject.wVol2034
                outputDict["wVol2035"] = BoUpObject.wVol2035
                outputDict["wVol2036"] = BoUpObject.wVol2036
                outputDict["wVol2037"] = BoUpObject.wVol2037
                outputDict["wVol2038"] = BoUpObject.wVol2038
                outputDict["wVol2039"] = BoUpObject.wVol2039
                outputDict["wVol2040"] = BoUpObject.wVol2040
                outputDict["wVol2041"] = BoUpObject.wVol2041
                outputDict["wVol2042"] = BoUpObject.wVol2042
                outputDict["wVol2043"] = BoUpObject.wVol2043
                outputDict["wVol2044"] = BoUpObject.wVol2044

                outputDict["wRev2020"] = BoUpObject.wRev2020
                outputDict["wRev2021"] = BoUpObject.wRev2021
                outputDict["wRev2022"] = BoUpObject.wRev2022
                outputDict["wRev2023"] = BoUpObject.wRev2023
                outputDict["wRev2024"] = BoUpObject.wRev2024
                outputDict["wRev2025"] = BoUpObject.wRev2025
                outputDict["wRev2026"] = BoUpObject.wRev2026
                outputDict["wRev2027"] = BoUpObject.wRev2027
                outputDict["wRev2028"] = BoUpObject.wRev2028
                outputDict["wRev2029"] = BoUpObject.wRev2029
                outputDict["wRev2030"] = BoUpObject.wRev2030
                outputDict["wRev2031"] = BoUpObject.wRev2031
                outputDict["wRev2032"] = BoUpObject.wRev2032
                outputDict["wRev2033"] = BoUpObject.wRev2033
                outputDict["wRev2034"] = BoUpObject.wRev2034
                outputDict["wRev2035"] = BoUpObject.wRev2035
                outputDict["wRev2036"] = BoUpObject.wRev2036
                outputDict["wRev2037"] = BoUpObject.wRev2037
                outputDict["wRev2038"] = BoUpObject.wRev2038
                outputDict["wRev2039"] = BoUpObject.wRev2039
                outputDict["wRev2040"] = BoUpObject.wRev2040
                outputDict["wRev2041"] = BoUpObject.wRev2041
                outputDict["wRev2042"] = BoUpObject.wRev2042
                outputDict["wRev2043"] = BoUpObject.wRev2043
                outputDict["wRev2044"] = BoUpObject.wRev2044

                # month stuff
                outputDict["fy_vol2020"] = BoUpObject.fy_vol2020
                outputDict["fy_vol2021"] = BoUpObject.fy_vol2021
                outputDict["fy_vol2022"] = BoUpObject.fy_vol2022
                outputDict["fy_vol2023"] = BoUpObject.fy_vol2023
                outputDict["fy_vol2024"] = BoUpObject.fy_vol2024
                outputDict["fy_vol2025"] = BoUpObject.fy_vol2025
                outputDict["fy_vol2026"] = BoUpObject.fy_vol2026
                outputDict["fy_vol2027"] = BoUpObject.fy_vol2027
                outputDict["fy_vol2028"] = BoUpObject.fy_vol2028
                outputDict["fy_vol2029"] = BoUpObject.fy_vol2029
                outputDict["fy_vol2030"] = BoUpObject.fy_vol2030
                outputDict["fy_vol2031"] = BoUpObject.fy_vol2031
                outputDict["fy_vol2032"] = BoUpObject.fy_vol2032
                outputDict["fy_vol2033"] = BoUpObject.fy_vol2033
                outputDict["fy_vol2034"] = BoUpObject.fy_vol2034
                outputDict["fy_vol2035"] = BoUpObject.fy_vol2035
                outputDict["fy_vol2036"] = BoUpObject.fy_vol2036
                outputDict["fy_vol2037"] = BoUpObject.fy_vol2037
                outputDict["fy_vol2038"] = BoUpObject.fy_vol2038
                outputDict["fy_vol2039"] = BoUpObject.fy_vol2039
                outputDict["fy_vol2040"] = BoUpObject.fy_vol2040
                outputDict["fy_vol2041"] = BoUpObject.fy_vol2041
                outputDict["fy_vol2042"] = BoUpObject.fy_vol2042
                outputDict["fy_vol2043"] = BoUpObject.fy_vol2043
                outputDict["fy_vol2044"] = BoUpObject.fy_vol2044

                outputDict["fy_gm2020"] = BoUpObject.fy_gm2020
                outputDict["fy_gm2021"] = BoUpObject.fy_gm2021
                outputDict["fy_gm2022"] = BoUpObject.fy_gm2022
                outputDict["fy_gm2023"] = BoUpObject.fy_gm2023
                outputDict["fy_gm2024"] = BoUpObject.fy_gm2024
                outputDict["fy_gm2025"] = BoUpObject.fy_gm2025
                outputDict["fy_gm2026"] = BoUpObject.fy_gm2026
                outputDict["fy_gm2027"] = BoUpObject.fy_gm2027
                outputDict["fy_gm2028"] = BoUpObject.fy_gm2028
                outputDict["fy_gm2029"] = BoUpObject.fy_gm2029
                outputDict["fy_gm2030"] = BoUpObject.fy_gm2030
                outputDict["fy_gm2031"] = BoUpObject.fy_gm2031
                outputDict["fy_gm2032"] = BoUpObject.fy_gm2032
                outputDict["fy_gm2033"] = BoUpObject.fy_gm2033
                outputDict["fy_gm2034"] = BoUpObject.fy_gm2034
                outputDict["fy_gm2035"] = BoUpObject.fy_gm2035
                outputDict["fy_gm2036"] = BoUpObject.fy_gm2036
                outputDict["fy_gm2037"] = BoUpObject.fy_gm2037
                outputDict["fy_gm2038"] = BoUpObject.fy_gm2038
                outputDict["fy_gm2039"] = BoUpObject.fy_gm2039
                outputDict["fy_gm2040"] = BoUpObject.fy_gm2040
                outputDict["fy_gm2041"] = BoUpObject.fy_gm2041
                outputDict["fy_gm2042"] = BoUpObject.fy_gm2042
                outputDict["fy_gm2043"] = BoUpObject.fy_gm2043
                outputDict["fy_gm2044"] = BoUpObject.fy_gm2044

                outputDict["fy_wVol2020"] = BoUpObject.fy_wVol2020
                outputDict["fy_wVol2021"] = BoUpObject.fy_wVol2021
                outputDict["fy_wVol2022"] = BoUpObject.fy_wVol2022
                outputDict["fy_wVol2023"] = BoUpObject.fy_wVol2023
                outputDict["fy_wVol2024"] = BoUpObject.fy_wVol2024
                outputDict["fy_wVol2025"] = BoUpObject.fy_wVol2025
                outputDict["fy_wVol2026"] = BoUpObject.fy_wVol2026
                outputDict["fy_wVol2027"] = BoUpObject.fy_wVol2027
                outputDict["fy_wVol2028"] = BoUpObject.fy_wVol2028
                outputDict["fy_wVol2029"] = BoUpObject.fy_wVol2029
                outputDict["fy_wVol2030"] = BoUpObject.fy_wVol2030
                outputDict["fy_wVol2031"] = BoUpObject.fy_wVol2031
                outputDict["fy_wVol2032"] = BoUpObject.fy_wVol2032
                outputDict["fy_wVol2033"] = BoUpObject.fy_wVol2033
                outputDict["fy_wVol2034"] = BoUpObject.fy_wVol2034
                outputDict["fy_wVol2035"] = BoUpObject.fy_wVol2035
                outputDict["fy_wVol2036"] = BoUpObject.fy_wVol2036
                outputDict["fy_wVol2037"] = BoUpObject.fy_wVol2037
                outputDict["fy_wVol2038"] = BoUpObject.fy_wVol2038
                outputDict["fy_wVol2039"] = BoUpObject.fy_wVol2039
                outputDict["fy_wVol2040"] = BoUpObject.fy_wVol2040
                outputDict["fy_wVol2041"] = BoUpObject.fy_wVol2041
                outputDict["fy_wVol2042"] = BoUpObject.fy_wVol2042
                outputDict["fy_wVol2043"] = BoUpObject.fy_wVol2043
                outputDict["fy_wVol2044"] = BoUpObject.fy_wVol2044

                outputDict["fy_wRev2020"] = BoUpObject.fy_wRev2020
                outputDict["fy_wRev2021"] = BoUpObject.fy_wRev2021
                outputDict["fy_wRev2022"] = BoUpObject.fy_wRev2022
                outputDict["fy_wRev2023"] = BoUpObject.fy_wRev2023
                outputDict["fy_wRev2024"] = BoUpObject.fy_wRev2024
                outputDict["fy_wRev2025"] = BoUpObject.fy_wRev2025
                outputDict["fy_wRev2026"] = BoUpObject.fy_wRev2026
                outputDict["fy_wRev2027"] = BoUpObject.fy_wRev2027
                outputDict["fy_wRev2028"] = BoUpObject.fy_wRev2028
                outputDict["fy_wRev2029"] = BoUpObject.fy_wRev2029
                outputDict["fy_wRev2030"] = BoUpObject.fy_wRev2030
                outputDict["fy_wRev2031"] = BoUpObject.fy_wRev2031
                outputDict["fy_wRev2032"] = BoUpObject.fy_wRev2032
                outputDict["fy_wRev2033"] = BoUpObject.fy_wRev2033
                outputDict["fy_wRev2034"] = BoUpObject.fy_wRev2034
                outputDict["fy_wRev2035"] = BoUpObject.fy_wRev2035
                outputDict["fy_wRev2036"] = BoUpObject.fy_wRev2036
                outputDict["fy_wRev2037"] = BoUpObject.fy_wRev2037
                outputDict["fy_wRev2038"] = BoUpObject.fy_wRev2038
                outputDict["fy_wRev2039"] = BoUpObject.fy_wRev2039
                outputDict["fy_wRev2040"] = BoUpObject.fy_wRev2040
                outputDict["fy_wRev2041"] = BoUpObject.fy_wRev2041
                outputDict["fy_wRev2042"] = BoUpObject.fy_wRev2042
                outputDict["fy_wRev2043"] = BoUpObject.fy_wRev2043
                outputDict["fy_wRev2044"] = BoUpObject.fy_wRev2044

                outputArray.append(outputDict)

            else:

                outputDict["vol2020"] = 0.0
                outputDict["vol2021"] = 0.0
                outputDict["vol2022"] = 0.0
                outputDict["vol2023"] = 0.0
                outputDict["vol2024"] = 0.0
                outputDict["vol2025"] = 0.0
                outputDict["vol2026"] = 0.0
                outputDict["vol2027"] = 0.0
                outputDict["vol2028"] = 0.0
                outputDict["vol2029"] = 0.0
                outputDict["vol2030"] = 0.0
                outputDict["vol2031"] = 0.0
                outputDict["vol2032"] = 0.0
                outputDict["vol2033"] = 0.0
                outputDict["vol2034"] = 0.0
                outputDict["vol2035"] = 0.0
                outputDict["vol2036"] = 0.0
                outputDict["vol2037"] = 0.0
                outputDict["vol2038"] = 0.0
                outputDict["vol2039"] = 0.0
                outputDict["vol2040"] = 0.0
                outputDict["vol2041"] = 0.0
                outputDict["vol2042"] = 0.0
                outputDict["vol2043"] = 0.0
                outputDict["vol2044"] = 0.0

                outputDict["volumesCustomer"] = 0.0
                outputDict["volCustomer2020"] = 0.0
                outputDict["volCustomer2021"] = 0.0
                outputDict["volCustomer2022"] = 0.0
                outputDict["volCustomer2023"] = 0.0
                outputDict["volCustomer2024"] = 0.0
                outputDict["volCustomer2025"] = 0.0
                outputDict["volCustomer2026"] = 0.0
                outputDict["volCustomer2027"] = 0.0
                outputDict["volCustomer2028"] = 0.0
                outputDict["volCustomer2029"] = 0.0
                outputDict["volCustomer2030"] = 0.0
                outputDict["volCustomer2031"] = 0.0
                outputDict["volCustomer2032"] = 0.0
                outputDict["volCustomer2033"] = 0.0
                outputDict["volCustomer2034"] = 0.0
                outputDict["volCustomer2035"] = 0.0
                outputDict["volCustomer2036"] = 0.0
                outputDict["volCustomer2037"] = 0.0
                outputDict["volCustomer2038"] = 0.0
                outputDict["volCustomer2039"] = 0.0
                outputDict["volCustomer2040"] = 0.0
                outputDict["volCustomer2041"] = 0.0
                outputDict["volCustomer2042"] = 0.0
                outputDict["volCustomer2043"] = 0.0
                outputDict["volCustomer2044"] = 0.0

                outputDict["price2020"] = 0.0
                outputDict["price2021"] = 0.0
                outputDict["price2022"] = 0.0
                outputDict["price2023"] = 0.0
                outputDict["price2024"] = 0.0
                outputDict["price2025"] = 0.0
                outputDict["price2026"] = 0.0
                outputDict["price2027"] = 0.0
                outputDict["price2028"] = 0.0
                outputDict["price2029"] = 0.0
                outputDict["price2030"] = 0.0
                outputDict["price2031"] = 0.0
                outputDict["price2032"] = 0.0
                outputDict["price2033"] = 0.0
                outputDict["price2034"] = 0.0
                outputDict["price2035"] = 0.0
                outputDict["price2036"] = 0.0
                outputDict["price2037"] = 0.0
                outputDict["price2038"] = 0.0
                outputDict["price2039"] = 0.0
                outputDict["price2040"] = 0.0
                outputDict["price2041"] = 0.0
                outputDict["price2042"] = 0.0
                outputDict["price2043"] = 0.0
                outputDict["price2044"] = 0.0

                outputDict["vhk2020"] = 0.0
                outputDict["vhk2021"] = 0.0
                outputDict["vhk2022"] = 0.0
                outputDict["vhk2023"] = 0.0
                outputDict["vhk2024"] = 0.0
                outputDict["vhk2025"] = 0.0
                outputDict["vhk2026"] = 0.0
                outputDict["vhk2027"] = 0.0
                outputDict["vhk2028"] = 0.0
                outputDict["vhk2029"] = 0.0
                outputDict["vhk2030"] = 0.0
                outputDict["vhk2031"] = 0.0
                outputDict["vhk2032"] = 0.0
                outputDict["vhk2033"] = 0.0
                outputDict["vhk2034"] = 0.0
                outputDict["vhk2035"] = 0.0
                outputDict["vhk2036"] = 0.0
                outputDict["vhk2037"] = 0.0
                outputDict["vhk2038"] = 0.0
                outputDict["vhk2039"] = 0.0
                outputDict["vhk2040"] = 0.0
                outputDict["vhk2041"] = 0.0
                outputDict["vhk2042"] = 0.0
                outputDict["vhk2043"] = 0.0
                outputDict["vhk2044"] = 0.0

                outputDict["gm2020"] = 0.0
                outputDict["gm2021"] = 0.0
                outputDict["gm2022"] = 0.0
                outputDict["gm2023"] = 0.0
                outputDict["gm2024"] = 0.0
                outputDict["gm2025"] = 0.0
                outputDict["gm2026"] = 0.0
                outputDict["gm2027"] = 0.0
                outputDict["gm2028"] = 0.0
                outputDict["gm2029"] = 0.0
                outputDict["gm2030"] = 0.0
                outputDict["gm2031"] = 0.0
                outputDict["gm2032"] = 0.0
                outputDict["gm2033"] = 0.0
                outputDict["gm2034"] = 0.0
                outputDict["gm2035"] = 0.0
                outputDict["gm2036"] = 0.0
                outputDict["gm2037"] = 0.0
                outputDict["gm2038"] = 0.0
                outputDict["gm2039"] = 0.0
                outputDict["gm2040"] = 0.0
                outputDict["gm2041"] = 0.0
                outputDict["gm2042"] = 0.0
                outputDict["gm2043"] = 0.0
                outputDict["gm2044"] = 0.0

                outputDict["wVol2020"] = 0.0
                outputDict["wVol2021"] = 0.0
                outputDict["wVol2022"] = 0.0
                outputDict["wVol2023"] = 0.0
                outputDict["wVol2024"] = 0.0
                outputDict["wVol2025"] = 0.0
                outputDict["wVol2026"] = 0.0
                outputDict["wVol2027"] = 0.0
                outputDict["wVol2028"] = 0.0
                outputDict["wVol2029"] = 0.0
                outputDict["wVol2030"] = 0.0
                outputDict["wVol2031"] = 0.0
                outputDict["wVol2032"] = 0.0
                outputDict["wVol2033"] = 0.0
                outputDict["wVol2034"] = 0.0
                outputDict["wVol2035"] = 0.0
                outputDict["wVol2036"] = 0.0
                outputDict["wVol2037"] = 0.0
                outputDict["wVol2038"] = 0.0
                outputDict["wVol2039"] = 0.0
                outputDict["wVol2040"] = 0.0
                outputDict["wVol2041"] = 0.0
                outputDict["wVol2042"] = 0.0
                outputDict["wVol2043"] = 0.0
                outputDict["wVol2044"] = 0.0

                outputDict["wRev2020"] = 0.0
                outputDict["wRev2021"] = 0.0
                outputDict["wRev2022"] = 0.0
                outputDict["wRev2023"] = 0.0
                outputDict["wRev2024"] = 0.0
                outputDict["wRev2025"] = 0.0
                outputDict["wRev2026"] = 0.0
                outputDict["wRev2027"] = 0.0
                outputDict["wRev2028"] = 0.0
                outputDict["wRev2029"] = 0.0
                outputDict["wRev2030"] = 0.0
                outputDict["wRev2031"] = 0.0
                outputDict["wRev2032"] = 0.0
                outputDict["wRev2033"] = 0.0
                outputDict["wRev2034"] = 0.0
                outputDict["wRev2035"] = 0.0
                outputDict["wRev2036"] = 0.0
                outputDict["wRev2037"] = 0.0
                outputDict["wRev2038"] = 0.0
                outputDict["wRev2039"] = 0.0
                outputDict["wRev2040"] = 0.0
                outputDict["wRev2041"] = 0.0
                outputDict["wRev2042"] = 0.0
                outputDict["wRev2043"] = 0.0
                outputDict["wRev2044"] = 0.0

                # month stuff
                outputDict["fy_vol2020"] = 0.0
                outputDict["fy_vol2021"] = 0.0
                outputDict["fy_vol2022"] = 0.0
                outputDict["fy_vol2023"] = 0.0
                outputDict["fy_vol2024"] = 0.0
                outputDict["fy_vol2025"] = 0.0
                outputDict["fy_vol2026"] = 0.0
                outputDict["fy_vol2027"] = 0.0
                outputDict["fy_vol2028"] = 0.0
                outputDict["fy_vol2029"] = 0.0
                outputDict["fy_vol2030"] = 0.0
                outputDict["fy_vol2031"] = 0.0
                outputDict["fy_vol2032"] = 0.0
                outputDict["fy_vol2033"] = 0.0
                outputDict["fy_vol2034"] = 0.0
                outputDict["fy_vol2035"] = 0.0
                outputDict["fy_vol2036"] = 0.0
                outputDict["fy_vol2037"] = 0.0
                outputDict["fy_vol2038"] = 0.0
                outputDict["fy_vol2039"] = 0.0
                outputDict["fy_vol2040"] = 0.0
                outputDict["fy_vol2041"] = 0.0
                outputDict["fy_vol2042"] = 0.0
                outputDict["fy_vol2043"] = 0.0
                outputDict["fy_vol2044"] = 0.0

                outputDict["fy_gm2020"] = 0.0
                outputDict["fy_gm2021"] = 0.0
                outputDict["fy_gm2022"] = 0.0
                outputDict["fy_gm2023"] = 0.0
                outputDict["fy_gm2024"] = 0.0
                outputDict["fy_gm2025"] = 0.0
                outputDict["fy_gm2026"] = 0.0
                outputDict["fy_gm2027"] = 0.0
                outputDict["fy_gm2028"] = 0.0
                outputDict["fy_gm2029"] = 0.0
                outputDict["fy_gm2030"] = 0.0
                outputDict["fy_gm2031"] = 0.0
                outputDict["fy_gm2032"] = 0.0
                outputDict["fy_gm2033"] = 0.0
                outputDict["fy_gm2034"] = 0.0
                outputDict["fy_gm2035"] = 0.0
                outputDict["fy_gm2036"] = 0.0
                outputDict["fy_gm2037"] = 0.0
                outputDict["fy_gm2038"] = 0.0
                outputDict["fy_gm2039"] = 0.0
                outputDict["fy_gm2040"] = 0.0
                outputDict["fy_gm2041"] = 0.0
                outputDict["fy_gm2042"] = 0.0
                outputDict["fy_gm2043"] = 0.0
                outputDict["fy_gm2044"] = 0.0

                outputDict["fy_wVol2020"] = 0.0
                outputDict["fy_wVol2021"] = 0.0
                outputDict["fy_wVol2022"] = 0.0
                outputDict["fy_wVol2023"] = 0.0
                outputDict["fy_wVol2024"] = 0.0
                outputDict["fy_wVol2025"] = 0.0
                outputDict["fy_wVol2026"] = 0.0
                outputDict["fy_wVol2027"] = 0.0
                outputDict["fy_wVol2028"] = 0.0
                outputDict["fy_wVol2029"] = 0.0
                outputDict["fy_wVol2030"] = 0.0
                outputDict["fy_wVol2031"] = 0.0
                outputDict["fy_wVol2032"] = 0.0
                outputDict["fy_wVol2033"] = 0.0
                outputDict["fy_wVol2034"] = 0.0
                outputDict["fy_wVol2035"] = 0.0
                outputDict["fy_wVol2036"] = 0.0
                outputDict["fy_wVol2037"] = 0.0
                outputDict["fy_wVol2038"] = 0.0
                outputDict["fy_wVol2039"] = 0.0
                outputDict["fy_wVol2040"] = 0.0
                outputDict["fy_wVol2041"] = 0.0
                outputDict["fy_wVol2042"] = 0.0
                outputDict["fy_wVol2043"] = 0.0
                outputDict["fy_wVol2044"] = 0.0

                outputDict["fy_wRev2020"] = 0.0
                outputDict["fy_wRev2021"] = 0.0
                outputDict["fy_wRev2022"] = 0.0
                outputDict["fy_wRev2023"] = 0.0
                outputDict["fy_wRev2024"] = 0.0
                outputDict["fy_wRev2025"] = 0.0
                outputDict["fy_wRev2026"] = 0.0
                outputDict["fy_wRev2027"] = 0.0
                outputDict["fy_wRev2028"] = 0.0
                outputDict["fy_wRev2029"] = 0.0
                outputDict["fy_wRev2030"] = 0.0
                outputDict["fy_wRev2031"] = 0.0
                outputDict["fy_wRev2032"] = 0.0
                outputDict["fy_wRev2033"] = 0.0
                outputDict["fy_wRev2034"] = 0.0
                outputDict["fy_wRev2035"] = 0.0
                outputDict["fy_wRev2036"] = 0.0
                outputDict["fy_wRev2037"] = 0.0
                outputDict["fy_wRev2038"] = 0.0
                outputDict["fy_wRev2039"] = 0.0
                outputDict["fy_wRev2040"] = 0.0
                outputDict["fy_wRev2041"] = 0.0
                outputDict["fy_wRev2042"] = 0.0
                outputDict["fy_wRev2043"] = 0.0
                outputDict["fy_wRev2044"] = 0.0

                outputArray.append(outputDict)

            print("added KPI data")

    # now average prices
    """
    for index in range(len(years)):
        try:
            totalAsps[index] = totalRevenues[index] / totalVolumes[index]
            totalAspsWeighted[index] = totalRevenuesWeighted[index] / totalVolumesWeighted[index]
        except:
            print("division failed", index)
    """
    return (
        outputArray,
        totalVolumes,
        totalVolumesWeighted,
        totalRevenues,
        totalRevenuesWeighted,
        totalMargin,
        totalMarginWeighted,
        totalAsps,
        totalAspsWeighted,
        years,
    )
