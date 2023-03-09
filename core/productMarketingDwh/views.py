# Francisco Falise, copyright 01/10/2022
from ajax_datatable.views import AjaxDatatableView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import *
from productMarketing.models import *
from django.http import JsonResponse


# import matplotlib as plt
# import matplotlib.pyplot as plt
import io
import base64
from decimal import Decimal
from django.utils import formats

# import seaborn as sns


# from .diagnosis import decode, decodePrivateInsurers
# from .scan import *
# from .ocr import ocrscan
# from .suitability import physioSuitability

from enum import Enum
from productMarketing.queryJobs.boupDataOverview import *
from productMarketing.queryJobs.warnings import *
from productMarketing.queryJobs.SQL_query import *
from .models import VrfcOrdersOnHand


@login_required(login_url="/login/")
def showKPI(request):
    projectNameError = True
    print("Start showKPI")
    if request.method == "POST":

        projectName = request.POST.get("projectName")
        print("Get projects")
        projects = Project.objects.filter(projectName=projectName)
        print("Got projects")
        count = projects.count()
        project = projects[0]
        region1 = project.region
        print(count)
        for i in range(0, count):
            print(i)
            print(projects[i].id)
            print(projects[i].salesName)
            print(projects[i].region)

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
        vhk = []
        volumes = []
        volumesCustomer = []
        prices = []
        currencyPrices = ""
        currencyVhk = ""
        region = []
        print("rfp of project", project.salesName.rfp)

        for year in years:
            try:
                # priceObject = ProjectPrices.objects.get(project = project, calenderYear = int(year), valid = True)
                object = ProjectVolumePrices.objects.get(
                    project=project, calendarYear=year
                )

                # volumeCustObject = ProjectVolumeCustomerEstimation.objects.get(project = project, calenderYear = year)
                # volumeObject = ProjectVolume.objects.get(project = project, calenderYear = year)
                prices.append(float(object.price))
                volumes.append(object.quantity)
                volumesCustomer.append(object.quantityCustomerEstimation)
                currencyPrices = object.currency
            except:
                prices.append(0)
                volumes.append(0)
                volumesCustomer.append(0)

        try:
            costObject = VhkCy.objects.get(
                RFP=project.salesName.rfp.pk, valid=True)

            for year in years:
                varName = "cy" + str(year)
                try:
                    costValue = getattr(costObject, varName)
                    vhk.append(float(costValue))
                    currencyVhk = costObject.currency.currency
                except:
                    vhk.append(0)
        except:
            # empty vhks
            for year in years:
                vhk.append(0)

        for year in years:
            try:
                region.append(project.region)
            except:
                region.append("Not avaiable")

        ##### revenue and gm
        revenue = []
        grossMargin = []
        grossMarginPct = []

        fxErrorPrices = False

        print("prices", prices)
        print("vhk", vhk)
        print("volumes", volumes)
        print("currencies", currencyPrices, currencyVhk)
        """
        ### check if price currency matches cost currency, else batch transform
        if currencyPrices != "EUR":
            print("currencies do not match! converting to EUR")
            ### get current rate
            fx = 1.0
            print("get currency")
            currencyObj = Currencies.objects.get(currency = currencyPrices)
            print("got currency")
            try:
                fxObject = ExchangeRates.objects.get(currency = currencyObj.pk, valid = True)
                fx = fxObject.rate
            except:
                print("failed currency exchange!! aborting!!")
                fxErrorPrices = True

            print("lenghts", len(prices), len(years))
            for index in range((len(years) - 1)):
                prices[index] = prices[index] * float(fx)

        if currencyVhk != "EUR":
            print("currencies vhk do not match! converting to EUR")
            ### get current rate
            fx = 1.0
            currencyObj = Currencies.objects.get(currency = currencyVhk)
            print("currobj", currencyObj.currency)

            try:
                fxObject = ExchangeRates.objects.get(currency = currencyObj.pk, valid = True)
                fx = fxObject.rate
            except:
                print("failed currency exchange!! aborting!!")
                fxErrorPrices = True

            for index in range((len(years) - 1)):
                vhk[index] = vhk[index] * float(fx)

        #### will be first in EUR
        print("------------> final results without considering family prices")

"""
        fxErrorPrices == False
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
                    "%%%%%%%%%%% DWH final result, year",
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

        print("lens", len(years), len(grossMargin), len(revenue))
        print("%%%%%&&&&& gross margins", grossMargin)
        print("%%%%%&&&&& revenue", revenue)
        print("%%%%%&&&&& cumulative gross margin", sum(grossMargin))
        print("%%%%%&&&&& cumulative revenue", sum(grossMargin))

        # plots
        plt.switch_backend("agg")

        sns.set_style("darkgrid")

        rev_margin = sns.lineplot(years, revenue, label="Revenue", marker="o")
        sns.lineplot(years, grossMargin, label="Cost Margin", marker="o")
        rev_margin.set(title="Revenue and Gross Margin",
                       xlabel="Year", ylabel="EUR")

        revenueMarginPlot = io.BytesIO()
        plt.savefig(revenueMarginPlot, format="jpg")
        revenueMarginPlot.seek(0)
        revenueMarginPlotBase64 = base64.b64encode(revenueMarginPlot.read())
        plt.clf()

        encodedrevenueMarginPlotBase64 = str(revenueMarginPlotBase64)
        encodedrevenueMarginPlotBase64 = encodedrevenueMarginPlotBase64[2:]
        encodedrevenueMarginPlotBase64 = encodedrevenueMarginPlotBase64[:-1]

        fig, ax = plt.subplots()
        ax2 = ax.twinx()
        volPrice = sns.lineplot(x=years, y=volumes, ax=ax, marker="o")
        sns.lineplot(years, prices, ax=ax2, color="orange", marker="o")
        ax.legend(handles=[a.lines[0]
                  for a in [ax, ax2]], labels=["Prices", "Volumes"])
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

        fig, ax = plt.subplots()
        ax2 = ax.twinx()
        volCPrice = sns.lineplot(x=years, y=volumesCustomer, ax=ax, marker="o")
        sns.lineplot(years, prices, ax=ax2, color="orange", marker="o")
        ax.legend(
            handles=[a.lines[0] for a in [ax, ax2]],
            labels=["Prices", "CustomerVolumes"],
        )
        ax.set_ylabel("Pieces")
        ax2.set_ylabel("EUR")
        volCPrice.set(title="CustomerVolume and Price")

        volumeCPricePlot = io.BytesIO()
        plt.savefig(volumeCPricePlot, format="jpg")
        volumeCPricePlot.seek(0)
        volumeCPricePlotBase64 = base64.b64encode(volumeCPricePlot.read())
        plt.clf()

        plt.close()

        encodedvolumeCPricePlotBase64 = str(volumeCPricePlotBase64)
        encodedvolumeCPricePlotBase64 = encodedvolumeCPricePlotBase64[2:]
        encodedvolumeCPricePlotBase64 = encodedvolumeCPricePlotBase64[:-1]

    else:
        projectName = ""
        count = 0
        region1 = ""
        projectNameError = ""
        encodedrevenueMarginPlotBase64 = ""
        encodedvolumePricePlotBase64 = ""
        encodedvolumeCPricePlotBase64 = ""
        print("no project name")

    return render(
        request,
        "productMarketing/KPI.html",
        {
            "projectNameError": projectNameError,
            "count": count,
            "region": region1,
            "projectName": projectName,
            "revenueMarginPlotBase64": encodedrevenueMarginPlotBase64,
            "volumePricePlotBase64": encodedvolumePricePlotBase64,
            "SliderPlotBase64": encodedvolumeCPricePlotBase64,
        },
    )


# for the Overviews... the first views return the HTML template. the following are the AJAX endpoints. The slim view shows only the key data of a project.


def boupTableSlim(request):
    return render(request, "productMarketing/boupOverviewSlim.html")


def boupTable(request):
    print("########### running boupTable")

    if request.method == "POST":
        print("post")

    return render(
        request,
        "productMarketing/boupOverview.html",
        {
            "segment": "boupOverviewSlim",
        },
    )


def boupTable_FY(request):
    print("########### running boup table FY")

    if request.method == "POST":
        print("post")

    return render(
        request,
        "productMarketing/boupOverview_FY.html",
        {
            "segment": "boupOverviewSlim",
        },
    )


def boupTableSlimData(request):
    print("running boupTableSlimData")

    (
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
    ) = getBoupTableData(request, False)
    outputDict = dict()
    outputDict["dataForTable"] = outputArray
    outputDict["totalVolumes"] = totalVolumes
    outputDict["totalVolumesWeighted"] = totalVolumesWeighted
    outputDict["totalRevenues"] = totalRevenues
    outputDict["totalRevenuesWeighted"] = totalRevenuesWeighted
    outputDict["totalMargin"] = totalMargin
    outputDict["totalMarginWeighted"] = totalMarginWeighted
    outputDict["totalAsps"] = totalAsps
    outputDict["totalAspsWeighted"] = totalAspsWeighted
    outputDict["years"] = years
    return JsonResponse(outputDict, safe=False)


def boupTableAllData(request):
    print("running boupTableAllData")

    (
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
    ) = getBoupData(request, True)
    outputDict = dict()
    outputDict["dataForTable"] = outputArray
    outputDict["totalVolumes"] = totalVolumes
    outputDict["totalVolumesWeighted"] = totalVolumesWeighted
    outputDict["totalRevenues"] = totalRevenues
    outputDict["totalRevenuesWeighted"] = totalRevenuesWeighted
    outputDict["totalMargin"] = totalMargin
    outputDict["totalMarginWeighted"] = totalMarginWeighted
    outputDict["totalAsps"] = totalAsps
    outputDict["totalAspsWeighted"] = totalAspsWeighted
    outputDict["years"] = years
    return JsonResponse(outputDict, safe=False)


# BOUP Table Data


class boupTableView(AjaxDatatableView):
    model = BoUp
    search_values_separator = "+"
    length_menu = [[10, 20, 50, 100], [10, 20, 50, 100]]
    column_defs = [
        {
            "name": "pk",
            "title": "Edit",
            "searchable": False,
        },
        {
            "name": "ID_APP",
            "title": "ID APP",
            "foreign_field": "ID_APP__id",
        },
        {
            "name": "Reviewed",
            "title": "Reviewed",
            "choices": True,
            "autofilter": True,
        },
        {
            "name": "reviewDate",
            "title": "Review Date",
        },
        {
            "name": "dummy",
            "title": "Dummy",
            "choices": True,
            "autofilter": True,
        },
        {
            "name": "applicationLine",
            "title": "Application Line",
            "choices": True,
            "autofilter": True,
        },
        {
            "name": "applicationMain",
            "title": "Application Main",
            "choices": True,
            "autofilter": True,
            "foreign_field": "applicationMain__appMainDescription",
        },
        {
            "name": "applicationDetail",
            "title": "Application Detail",
            "foreign_field": "applicationDetail__appDetailDescription",
            "choices": True,
            "autofilter": True,
        },
        {
            "name": "productMarketer",
            "title": "Product Marketer",
            "foreign_field": "productMarketer__name",
            "choices": True,
            "autofilter": True,
        },
        {
            "name": "rfp",
            "title": "RFP",
            "foreign_field": "rfp__rfp",
        },
        {
            "name": "salesName",
            "title": "Product Sales Name",
            "foreign_field": "salesName__name",
        },
        {
            "name": "hfg",
            "title": "HFG",
            "choices": True,
            "autofilter": True,
        },
        {
            "name": "plHfg",
            "title": "PL_HFG",
            "choices": True,
            "autofilter": True,
        },
        {
            "name": "ppos",
            "title": "PPOS",
        },
        {
            "name": "region",
            "title": "Region",
            "choices": True,
            "autofilter": True,
        },
        {
            "name": "secondRegion",
            "title": "Second Region",
            "choices": True,
            "autofilter": True,
        },
        {
            "name": "mainCustomer",
            "title": "Main Customer",
            "foreign_field": "mainCustomer__customerName",
            "choices": True,
            "autofilter": True,
        },
        {
            "name": "endCustomer",
            "title": "End Customer",
            "foreign_field": "endCustomer__finalCustomerName",
            "choices": True,
            "autofilter": True,
        },
        {
            "name": "distributor",
            "title": "Distributor",
            "foreign_field": "distributor__distributorName",
            "choices": True,
            "autofilter": True,
        },
        {
            "name": "tier1",
            "title": "Tier One",
            "foreign_field": "tier1__tierOneName",
            "choices": True,
            "autofilter": True,
        },
        {
            "name": "oem",
            "title": "OEM",
            "foreign_field": "oem__oemName",
            "choices": True,
            "autofilter": True,
        },
        {
            "name": "ems",
            "title": "EMS",
            "foreign_field": "ems__emsName",
            "choices": True,
            "autofilter": True,
        },
        {
            "name": "vpaCustomer",
            "title": "VPA Customer",
            "foreign_field": "vpaCustomer__customerName",
            "choices": True,
            "autofilter": True,
        },
        {
            "name": "spNumber",
            "title": "SP Number",
        },
        {
            "name": "probability",
            "title": "Probability",
        },
        {
            "name": "statusProbability",
            "title": "Status Probability",
            "choices": True,
            "autofilter": True,
        },
        {
            "name": "priceSource",
            "title": "Price Source",
        },
        {
            "name": "familyPriceApplicable",
            "title": "Family Price Applicable",
            "choices": True,
            "autofilter": True,
        },
        {
            "name": "familyPriceDetails",
            "title": "Family Price Detail",
        },
        {
            "name": "priceType",
            "title": "Price Type",
            "choices": True,
            "autofilter": True,
        },
        {
            "name": "currency",
            "title": "Currency",
            "choices": True,
            "autofilter": True,
        },
        {
            "name": "contractualCurrency",
            "title": "Contractual Currency",
            "choices": True,
            "autofilter": True,
        },
        {
            "name": "fxRate",
            "title": "FX Rate",
        },
        {
            "name": "comment",
            "title": "Comments",
        },
        {
            "name": "dcChannel",
            "title": "dcChannel",
        },
        {
            "name": "projectName",
            "title": "Project Name",
        },
        {
            "name": "dragonId",
            "title": "Dragon ID",
        },
        {
            "name": "salesContact",
            "title": "Sales Contact",
        },
        {
            "name": "sop",
            "title": "SOP",
        },
        {
            "name": "availablePGS",
            "title": "Available PGS",
        },
        {
            "name": "modifiedBy",
            "title": "Modified By",
            "foreign_field": "modifiedBy__username",
        },
        {
            "name": "modifiedDate",
            "title": "Modified Date",
        },
        {
            "name": "creationDate",
            "title": "Creation Date",
        },
        # {
        #    "name": "timeBottomUp",
        #    "title": "Time Bottom Up",
        # },
        {
            "name": "gen",
            "title": "Gen",
        },
        {
            "name": "genDetail",
            "title": "Gen Detail",
        },
        {
            "name": "basicType",
            "title": "Basic Type",
        },
        {
            "name": "package",
            "title": "Package",
        },
        {
            "name": "series",
            "title": "Series",
        },
        {
            "name": "seriesLong",
            "title": "Series Long",
        },
        {
            "name": "gmLifeTime",
            "title": "GM Lifetime",
        },
        {
            "name": "revEurLifeTime",
            "title": "Rev Eur Lifetime",
        },
        {
            "name": "volLifeTime",
            "title": "Vol Lifetime",
        },
        {
            "name": "volWeightedLifeTime",
            "title": "Vol Weighted Lifetime",
        },
        {"name": "vol2020", "title": "Vol 2020"},
        {"name": "vol2021", "title": "Vol 2021"},
        {"name": "vol2022", "title": "Vol 2022"},
        {"name": "vol2023", "title": "Vol 2023"},
        {"name": "vol2024", "title": "Vol 2024"},
        {"name": "vol2025", "title": "Vol 2025"},
        {"name": "vol2026", "title": "Vol 2026"},
        {"name": "vol2027", "title": "Vol 2027"},
        {"name": "vol2028", "title": "Vol 2028"},
        {"name": "vol2029", "title": "Vol 2029"},
        {"name": "vol2030", "title": "Vol 2030"},
        {"name": "vol2031", "title": "Vol 2031"},
        {"name": "vol2032", "title": "Vol 2032"},
        {"name": "vol2033", "title": "Vol 2033"},
        {"name": "vol2034", "title": "Vol 2034"},
        {"name": "vol2035", "title": "Vol 2035"},
        {"name": "vol2036", "title": "Vol 2036"},
        {"name": "vol2037", "title": "Vol 2037"},
        {"name": "vol2038", "title": "Vol 2038"},
        {"name": "vol2039", "title": "Vol 2039"},
        {"name": "vol2040", "title": "Vol 2040"},
        {"name": "vol2041", "title": "Vol 2041"},
        {"name": "vol2042", "title": "Vol 2042"},
        {"name": "vol2043", "title": "Vol 2043"},
        {"name": "vol2044", "title": "Vol 2044"},
        {"name": "volCustomer2020", "title": "Vol Customer 2020"},
        {"name": "volCustomer2021", "title": "Vol Customer 2021"},
        {"name": "volCustomer2022", "title": "Vol Customer 2022"},
        {"name": "volCustomer2023", "title": "Vol Customer 2023"},
        {"name": "volCustomer2024", "title": "Vol Customer 2024"},
        {"name": "volCustomer2025", "title": "Vol Customer 2025"},
        {"name": "volCustomer2026", "title": "Vol Customer 2026"},
        {"name": "volCustomer2027", "title": "Vol Customer 2027"},
        {"name": "volCustomer2028", "title": "Vol Customer 2028"},
        {"name": "volCustomer2029", "title": "Vol Customer 2029"},
        {"name": "volCustomer2030", "title": "Vol Customer 2030"},
        {"name": "volCustomer2031", "title": "Vol Customer 2031"},
        {"name": "volCustomer2032", "title": "Vol Customer 2032"},
        {"name": "volCustomer2033", "title": "Vol Customer 2033"},
        {"name": "volCustomer2034", "title": "Vol Customer 2034"},
        {"name": "volCustomer2035", "title": "Vol Customer 2035"},
        {"name": "volCustomer2036", "title": "Vol Customer 2036"},
        {"name": "volCustomer2037", "title": "Vol Customer 2037"},
        {"name": "volCustomer2038", "title": "Vol Customer 2038"},
        {"name": "volCustomer2039", "title": "Vol Customer 2039"},
        {"name": "volCustomer2040", "title": "Vol Customer 2040"},
        {"name": "volCustomer2041", "title": "Vol Customer 2041"},
        {"name": "volCustomer2042", "title": "Vol Customer 2042"},
        {"name": "volCustomer2043", "title": "Vol Customer 2043"},
        {"name": "volCustomer2044", "title": "Vol Customer 2044"},
        {"name": "price2020", "title": "Price 2020"},
        {"name": "price2021", "title": "Price 2021"},
        {"name": "price2022", "title": "Price 2022"},
        {"name": "price2023", "title": "Price 2023"},
        {"name": "price2024", "title": "Price 2024"},
        {"name": "price2025", "title": "Price 2025"},
        {"name": "price2026", "title": "Price 2026"},
        {"name": "price2027", "title": "Price 2027"},
        {"name": "price2028", "title": "Price 2028"},
        {"name": "price2029", "title": "Price 2029"},
        {"name": "price2030", "title": "Price 2030"},
        {"name": "price2031", "title": "Price 2031"},
        {"name": "price2032", "title": "Price 2032"},
        {"name": "price2033", "title": "Price 2033"},
        {"name": "price2034", "title": "Price 2034"},
        {"name": "price2035", "title": "Price 2035"},
        {"name": "price2036", "title": "Price 2036"},
        {"name": "price2037", "title": "Price 2037"},
        {"name": "price2038", "title": "Price 2038"},
        {"name": "price2039", "title": "Price 2039"},
        {"name": "price2040", "title": "Price 2040"},
        {"name": "price2041", "title": "Price 2041"},
        {"name": "price2042", "title": "Price 2042"},
        {"name": "price2043", "title": "Price 2043"},
        {"name": "price2044", "title": "Price 2044"},
        {"name": "vhk2020", "title": "VHK 2020"},
        {"name": "vhk2021", "title": "VHK 2021"},
        {"name": "vhk2022", "title": "VHK 2022"},
        {"name": "vhk2023", "title": "VHK 2023"},
        {"name": "vhk2024", "title": "VHK 2024"},
        {"name": "vhk2025", "title": "VHK 2025"},
        {"name": "vhk2026", "title": "VHK 2026"},
        {"name": "vhk2027", "title": "VHK 2027"},
        {"name": "vhk2028", "title": "VHK 2028"},
        {"name": "vhk2029", "title": "VHK 2029"},
        {"name": "vhk2030", "title": "VHK 2030"},
        {"name": "vhk2031", "title": "VHK 2031"},
        {"name": "vhk2032", "title": "VHK 2032"},
        {"name": "vhk2033", "title": "VHK 2033"},
        {"name": "vhk2034", "title": "VHK 2034"},
        {"name": "vhk2035", "title": "VHK 2035"},
        {"name": "vhk2036", "title": "VHK 2036"},
        {"name": "vhk2037", "title": "VHK 2037"},
        {"name": "vhk2038", "title": "VHK 2038"},
        {"name": "vhk2039", "title": "VHK 2039"},
        {"name": "vhk2040", "title": "VHK 2040"},
        {"name": "vhk2041", "title": "VHK 2041"},
        {"name": "vhk2042", "title": "VHK 2042"},
        {"name": "vhk2043", "title": "VHK 2043"},
        {"name": "vhk2044", "title": "VHK 2044"},
        {"name": "gm2020", "title": "GM 2020"},
        {"name": "gm2021", "title": "GM 2021"},
        {"name": "gm2022", "title": "GM 2022"},
        {"name": "gm2023", "title": "GM 2023"},
        {"name": "gm2024", "title": "GM 2024"},
        {"name": "gm2025", "title": "GM 2025"},
        {"name": "gm2026", "title": "GM 2026"},
        {"name": "gm2027", "title": "GM 2027"},
        {"name": "gm2028", "title": "GM 2028"},
        {"name": "gm2029", "title": "GM 2029"},
        {"name": "gm2030", "title": "GM 2030"},
        {"name": "gm2031", "title": "GM 2031"},
        {"name": "gm2032", "title": "GM 2032"},
        {"name": "gm2033", "title": "GM 2033"},
        {"name": "gm2034", "title": "GM 2034"},
        {"name": "gm2035", "title": "GM 2035"},
        {"name": "gm2036", "title": "GM 2036"},
        {"name": "gm2037", "title": "GM 2037"},
        {"name": "gm2038", "title": "GM 2038"},
        {"name": "gm2039", "title": "GM 2039"},
        {"name": "gm2040", "title": "GM 2040"},
        {"name": "gm2041", "title": "GM 2041"},
        {"name": "gm2042", "title": "GM 2042"},
        {"name": "gm2043", "title": "GM 2043"},
        {"name": "gm2044", "title": "GM 2044"},
        {"name": "wVol2020", "title": "W Vol 2020"},
        {"name": "wVol2021", "title": "W Vol 2021"},
        {"name": "wVol2022", "title": "W Vol 2022"},
        {"name": "wVol2023", "title": "W Vol 2023"},
        {"name": "wVol2024", "title": "W Vol 2024"},
        {"name": "wVol2025", "title": "W Vol 2025"},
        {"name": "wVol2026", "title": "W Vol 2026"},
        {"name": "wVol2027", "title": "W Vol 2027"},
        {"name": "wVol2028", "title": "W Vol 2028"},
        {"name": "wVol2029", "title": "W Vol 2029"},
        {"name": "wVol2030", "title": "W Vol 2030"},
        {"name": "wVol2031", "title": "W Vol 2031"},
        {"name": "wVol2032", "title": "W Vol 2032"},
        {"name": "wVol2033", "title": "W Vol 2033"},
        {"name": "wVol2034", "title": "W Vol 2034"},
        {"name": "wVol2035", "title": "W Vol 2035"},
        {"name": "wVol2036", "title": "W Vol 2036"},
        {"name": "wVol2037", "title": "W Vol 2037"},
        {"name": "wVol2038", "title": "W Vol 2038"},
        {"name": "wVol2039", "title": "W Vol 2039"},
        {"name": "wVol2040", "title": "W Vol 2040"},
        {"name": "wVol2041", "title": "W Vol 2041"},
        {"name": "wVol2042", "title": "W Vol 2042"},
        {"name": "wVol2043", "title": "W Vol 2043"},
        {"name": "wVol2044", "title": "W Vol 2044"},
        {"name": "wRev2020", "title": "W Rev 2020"},
        {"name": "wRev2021", "title": "W Rev 2021"},
        {"name": "wRev2022", "title": "W Rev 2022"},
        {"name": "wRev2023", "title": "W Rev 2023"},
        {"name": "wRev2024", "title": "W Rev 2024"},
        {"name": "wRev2025", "title": "W Rev 2025"},
        {"name": "wRev2026", "title": "W Rev 2026"},
        {"name": "wRev2027", "title": "W Rev 2027"},
        {"name": "wRev2028", "title": "W Rev 2028"},
        {"name": "wRev2029", "title": "W Rev 2029"},
        {"name": "wRev2030", "title": "W Rev 2030"},
        {"name": "wRev2031", "title": "W Rev 2031"},
        {"name": "wRev2032", "title": "W Rev 2032"},
        {"name": "wRev2033", "title": "W Rev 2033"},
        {"name": "wRev2034", "title": "W Rev 2034"},
        {"name": "wRev2035", "title": "W Rev 2035"},
        {"name": "wRev2036", "title": "W Rev 2036"},
        {"name": "wRev2037", "title": "W Rev 2037"},
        {"name": "wRev2038", "title": "W Rev 2038"},
        {"name": "wRev2039", "title": "W Rev 2039"},
        {"name": "wRev2040", "title": "W Rev 2040"},
        {"name": "wRev2041", "title": "W Rev 2041"},
        {"name": "wRev2042", "title": "W Rev 2042"},
        {"name": "wRev2043", "title": "W Rev 2043"},
        {"name": "wRev2044", "title": "W Rev 2044"},
        {"name": "wGrossMargin2020", "title": "W Gross Margin 2020"},
        {"name": "wGrossMargin2021", "title": "W Gross Margin 2021"},
        {"name": "wGrossMargin2022", "title": "W Gross Margin 2022"},
        {"name": "wGrossMargin2023", "title": "W Gross Margin 2023"},
        {"name": "wGrossMargin2024", "title": "W Gross Margin 2024"},
        {"name": "wGrossMargin2025", "title": "W Gross Margin 2025"},
        {"name": "wGrossMargin2026", "title": "W Gross Margin 2026"},
        {"name": "wGrossMargin2027", "title": "W Gross Margin 2027"},
        {"name": "wGrossMargin2028", "title": "W Gross Margin 2028"},
        {"name": "wGrossMargin2029", "title": "W Gross Margin 2029"},
        {"name": "wGrossMargin2030", "title": "W Gross Margin 2030"},
        {"name": "wGrossMargin2031", "title": "W Gross Margin 2031"},
        {"name": "wGrossMargin2032", "title": "W Gross Margin 2032"},
        {"name": "wGrossMargin2033", "title": "W Gross Margin 2033"},
        {"name": "wGrossMargin2034", "title": "W Gross Margin 2034"},
        {"name": "wGrossMargin2035", "title": "W Gross Margin 2035"},
        {"name": "wGrossMargin2036", "title": "W Gross Margin 2036"},
        {"name": "wGrossMargin2037", "title": "W Gross Margin 2037"},
        {"name": "wGrossMargin2038", "title": "W Gross Margin 2038"},
        {"name": "wGrossMargin2039", "title": "W Gross Margin 2039"},
        {"name": "wGrossMargin2040", "title": "W Gross Margin 2040"},
        {"name": "wGrossMargin2041", "title": "W Gross Margin 2041"},
        {"name": "wGrossMargin2042", "title": "W Gross Margin 2042"},
        {"name": "wGrossMargin2043", "title": "W Gross Margin 2043"},
        {"name": "wGrossMargin2044", "title": "W Gross Margin 2044"},
        {"name": "asp2020", "title": "ASP 2020"},
        {"name": "asp2021", "title": "ASP 2021"},
        {"name": "asp2022", "title": "ASP 2022"},
        {"name": "asp2023", "title": "ASP 2023"},
        {"name": "asp2024", "title": "ASP 2024"},
        {"name": "asp2025", "title": "ASP 2025"},
        {"name": "asp2026", "title": "ASP 2026"},
        {"name": "asp2027", "title": "ASP 2027"},
        {"name": "asp2028", "title": "ASP 2028"},
        {"name": "asp2029", "title": "ASP 2029"},
        {"name": "asp2030", "title": "ASP 2030"},
        {"name": "asp2031", "title": "ASP 2031"},
        {"name": "asp2032", "title": "ASP 2032"},
        {"name": "asp2033", "title": "ASP 2033"},
        {"name": "asp2034", "title": "ASP 2034"},
        {"name": "asp2035", "title": "ASP 2035"},
        {"name": "asp2036", "title": "ASP 2036"},
        {"name": "asp2037", "title": "ASP 2037"},
        {"name": "asp2038", "title": "ASP 2038"},
        {"name": "asp2039", "title": "ASP 2039"},
        {"name": "asp2040", "title": "ASP 2040"},
        {"name": "asp2041", "title": "ASP 2041"},
        {"name": "asp2042", "title": "ASP 2042"},
        {"name": "asp2043", "title": "ASP 2043"},
        {"name": "asp2044", "title": "ASP 2044"},
        {"name": "fy_vol2020", "title": "FY Vol 2020"},
        {"name": "fy_vol2021", "title": "FY Vol 2021"},
        {"name": "fy_vol2022", "title": "FY Vol 2022"},
        {"name": "fy_vol2023", "title": "FY Vol 2023"},
        {"name": "fy_vol2024", "title": "FY Vol 2024"},
        {"name": "fy_vol2025", "title": "FY Vol 2025"},
        {"name": "fy_vol2026", "title": "FY Vol 2026"},
        {"name": "fy_vol2027", "title": "FY Vol 2027"},
        {"name": "fy_vol2028", "title": "FY Vol 2028"},
        {"name": "fy_vol2029", "title": "FY Vol 2029"},
        {"name": "fy_vol2030", "title": "FY Vol 2030"},
        {"name": "fy_vol2031", "title": "FY Vol 2031"},
        {"name": "fy_vol2032", "title": "FY Vol 2032"},
        {"name": "fy_vol2033", "title": "FY Vol 2033"},
        {"name": "fy_vol2034", "title": "FY Vol 2034"},
        {"name": "fy_vol2035", "title": "FY Vol 2035"},
        {"name": "fy_vol2036", "title": "FY Vol 2036"},
        {"name": "fy_vol2037", "title": "FY Vol 2037"},
        {"name": "fy_vol2038", "title": "FY Vol 2038"},
        {"name": "fy_vol2039", "title": "FY Vol 2039"},
        {"name": "fy_vol2040", "title": "FY Vol 2040"},
        {"name": "fy_vol2041", "title": "FY Vol 2041"},
        {"name": "fy_vol2042", "title": "FY Vol 2042"},
        {"name": "fy_vol2043", "title": "FY Vol 2043"},
        {"name": "fy_vol2044", "title": "FY Vol 2044"},
        {"name": "fy_gm2020", "title": "FY GM 2020"},
        {"name": "fy_gm2021", "title": "FY GM 2021"},
        {"name": "fy_gm2022", "title": "FY GM 2022"},
        {"name": "fy_gm2023", "title": "FY GM 2023"},
        {"name": "fy_gm2024", "title": "FY GM 2024"},
        {"name": "fy_gm2025", "title": "FY GM 2025"},
        {"name": "fy_gm2026", "title": "FY GM 2026"},
        {"name": "fy_gm2027", "title": "FY GM 2027"},
        {"name": "fy_gm2028", "title": "FY GM 2028"},
        {"name": "fy_gm2029", "title": "FY GM 2029"},
        {"name": "fy_gm2030", "title": "FY GM 2030"},
        {"name": "fy_gm2031", "title": "FY GM 2031"},
        {"name": "fy_gm2032", "title": "FY GM 2032"},
        {"name": "fy_gm2033", "title": "FY GM 2033"},
        {"name": "fy_gm2034", "title": "FY GM 2034"},
        {"name": "fy_gm2035", "title": "FY GM 2035"},
        {"name": "fy_gm2036", "title": "FY GM 2036"},
        {"name": "fy_gm2037", "title": "FY GM 2037"},
        {"name": "fy_gm2038", "title": "FY GM 2038"},
        {"name": "fy_gm2039", "title": "FY GM 2039"},
        {"name": "fy_gm2040", "title": "FY GM 2040"},
        {"name": "fy_gm2041", "title": "FY GM 2041"},
        {"name": "fy_gm2042", "title": "FY GM 2042"},
        {"name": "fy_gm2043", "title": "FY GM 2043"},
        {"name": "fy_gm2044", "title": "FY GM 2044"},
        {"name": "fy_wVol2020", "title": "FY W Vol 2020"},
        {"name": "fy_wVol2021", "title": "FY W Vol 2021"},
        {"name": "fy_wVol2022", "title": "FY W Vol 2022"},
        {"name": "fy_wVol2023", "title": "FY W Vol 2023"},
        {"name": "fy_wVol2024", "title": "FY W Vol 2024"},
        {"name": "fy_wVol2025", "title": "FY W Vol 2025"},
        {"name": "fy_wVol2026", "title": "FY W Vol 2026"},
        {"name": "fy_wVol2027", "title": "FY W Vol 2027"},
        {"name": "fy_wVol2028", "title": "FY W Vol 2028"},
        {"name": "fy_wVol2029", "title": "FY W Vol 2029"},
        {"name": "fy_wVol2030", "title": "FY W Vol 2030"},
        {"name": "fy_wVol2031", "title": "FY W Vol 2031"},
        {"name": "fy_wVol2032", "title": "FY W Vol 2032"},
        {"name": "fy_wVol2033", "title": "FY W Vol 2033"},
        {"name": "fy_wVol2034", "title": "FY W Vol 2034"},
        {"name": "fy_wVol2035", "title": "FY W Vol 2035"},
        {"name": "fy_wVol2036", "title": "FY W Vol 2036"},
        {"name": "fy_wVol2037", "title": "FY W Vol 2037"},
        {"name": "fy_wVol2038", "title": "FY W Vol 2038"},
        {"name": "fy_wVol2039", "title": "FY W Vol 2039"},
        {"name": "fy_wVol2040", "title": "FY W Vol 2040"},
        {"name": "fy_wVol2041", "title": "FY W Vol 2041"},
        {"name": "fy_wVol2042", "title": "FY W Vol 2042"},
        {"name": "fy_wVol2043", "title": "FY W Vol 2043"},
        {"name": "fy_wVol2044", "title": "FY W Vol 2044"},
    ]

    # 24308519.000000000000
    def render_column(self, row, column):

        if column in (
            "gmLifeTime",
            "revEurLifeTime",
            "volLifeTime",
            "volWeightedLifeTime",
            "vol2020",
            "vol2021",
            "vol2022",
            "vol2023",
            "vol2024",
            "vol2025",
            "vol2026",
            "vol2027",
            "vol2028",
            "vol2029",
            "vol2030",
            "vol2031",
            "vol2032",
            "vol2033",
            "vol2034",
            "vol2035",
            "vol2036",
            "vol2037",
            "vol2038",
            "vol2039",
            "vol2040",
            "vol2041",
            "vol2042",
            "vol2043",
            "vol2044",
            "volCustomer2020",
            "volCustomer2021",
            "volCustomer2022",
            "volCustomer2023",
            "volCustomer2024",
            "volCustomer2025",
            "volCustomer2026",
            "volCustomer2027",
            "volCustomer2028",
            "volCustomer2029",
            "volCustomer2030",
            "volCustomer2031",
            "volCustomer2032",
            "volCustomer2033",
            "volCustomer2034",
            "volCustomer2035",
            "volCustomer2036",
            "volCustomer2037",
            "volCustomer2038",
            "volCustomer2039",
            "volCustomer2040",
            "volCustomer2041",
            "volCustomer2042",
            "volCustomer2043",
            "volCustomer2044",
            "price2020",
            "price2021",
            "price2022",
            "price2023",
            "price2024",
            "price2025",
            "price2026",
            "price2027",
            "price2028",
            "price2029",
            "price2030",
            "price2031",
            "price2032",
            "price2033",
            "price2034",
            "price2035",
            "price2036",
            "price2037",
            "price2038",
            "price2039",
            "price2040",
            "price2041",
            "price2042",
            "price2043",
            "price2044",
            "vhk2020",
            "vhk2021",
            "vhk2022",
            "vhk2023",
            "vhk2024",
            "vhk2025",
            "vhk2026",
            "vhk2027",
            "vhk2028",
            "vhk2029",
            "vhk2030",
            "vhk2031",
            "vhk2032",
            "vhk2033",
            "vhk2034",
            "vhk2035",
            "vhk2036",
            "vhk2037",
            "vhk2038",
            "vhk2039",
            "vhk2040",
            "vhk2041",
            "vhk2042",
            "vhk2043",
            "vhk2044",
            "gm2020",
            "gm2021",
            "gm2022",
            "gm2023",
            "gm2024",
            "gm2025",
            "gm2026",
            "gm2027",
            "gm2028",
            "gm2029",
            "gm2030",
            "gm2031",
            "gm2032",
            "gm2033",
            "gm2034",
            "gm2035",
            "gm2036",
            "gm2037",
            "gm2038",
            "gm2039",
            "gm2040",
            "gm2041",
            "gm2042",
            "gm2043",
            "gm2044",
            "wVol2020",
            "wVol2021",
            "wVol2022",
            "wVol2023",
            "wVol2024",
            "wVol2025",
            "wVol2026",
            "wVol2027",
            "wVol2028",
            "wVol2029",
            "wVol2030",
            "wVol2031",
            "wVol2032",
            "wVol2033",
            "wVol2034",
            "wVol2035",
            "wVol2036",
            "wVol2037",
            "wVol2038",
            "wVol2039",
            "wVol2040",
            "wVol2041",
            "wVol2042",
            "wVol2043",
            "wVol2044",
            "wRev2020",
            "wRev2021",
            "wRev2022",
            "wRev2023",
            "wRev2024",
            "wRev2025",
            "wRev2026",
            "wRev2027",
            "wRev2028",
            "wRev2029",
            "wRev2030",
            "wRev2031",
            "wRev2032",
            "wRev2033",
            "wRev2034",
            "wRev2035",
            "wRev2036",
            "wRev2037",
            "wRev2038",
            "wRev2039",
            "wRev2040",
            "wRev2041",
            "wRev2042",
            "wRev2043",
            "wRev2044",
            "wGrossMargin2020",
            "wGrossMargin2021",
            "wGrossMargin2022",
            "wGrossMargin2023",
            "wGrossMargin2024",
            "wGrossMargin2025",
            "wGrossMargin2026",
            "wGrossMargin2027",
            "wGrossMargin2028",
            "wGrossMargin2029",
            "wGrossMargin2030",
            "wGrossMargin2031",
            "wGrossMargin2032",
            "wGrossMargin2033",
            "wGrossMargin2034",
            "wGrossMargin2035",
            "wGrossMargin2036",
            "wGrossMargin2037",
            "wGrossMargin2038",
            "wGrossMargin2039",
            "wGrossMargin2040",
            "wGrossMargin2041",
            "wGrossMargin2042",
            "wGrossMargin2043",
            "wGrossMargin2044",
            "asp2020",
            "asp2021",
            "asp2022",
            "asp2023",
            "asp2024",
            "asp2025",
            "asp2026",
            "asp2027",
            "asp2028",
            "asp2029",
            "asp2030",
            "asp2031",
            "asp2032",
            "asp2033",
            "asp2034",
            "asp2035",
            "asp2036",
            "asp2037",
            "asp2038",
            "asp2039",
            "asp2040",
            "asp2041",
            "asp2042",
            "asp2043",
            "asp2044",
            "fy_vol2020",
            "fy_vol2021",
            "fy_vol2022",
            "fy_vol2023",
            "fy_vol2024",
            "fy_vol2025",
            "fy_vol2026",
            "fy_vol2027",
            "fy_vol2028",
            "fy_vol2029",
            "fy_vol2030",
            "fy_vol2031",
            "fy_vol2032",
            "fy_vol2033",
            "fy_vol2034",
            "fy_vol2035",
            "fy_vol2036",
            "fy_vol2037",
            "fy_vol2038",
            "fy_vol2039",
            "fy_vol2040",
            "fy_vol2041",
            "fy_vol2042",
            "fy_vol2043",
            "fy_vol2044",
            "fy_gm2020",
            "fy_gm2021",
            "fy_gm2022",
            "fy_gm2023",
            "fy_gm2024",
            "fy_gm2025",
            "fy_gm2026",
            "fy_gm2027",
            "fy_gm2028",
            "fy_gm2029",
            "fy_gm2030",
            "fy_gm2031",
            "fy_gm2032",
            "fy_gm2033",
            "fy_gm2034",
            "fy_gm2035",
            "fy_gm2036",
            "fy_gm2037",
            "fy_gm2038",
            "fy_gm2039",
            "fy_gm2040",
            "fy_gm2041",
            "fy_gm2042",
            "fy_gm2043",
            "fy_gm2044",
            "fy_wVol2020",
            "fy_wVol2021",
            "fy_wVol2022",
            "fy_wVol2023",
            "fy_wVol2024",
            "fy_wVol2025",
            "fy_wVol2026",
            "fy_wVol2027",
            "fy_wVol2028",
            "fy_wVol2029",
            "fy_wVol2030",
            "fy_wVol2031",
            "fy_wVol2032",
            "fy_wVol2033",
            "fy_wVol2034",
            "fy_wVol2035",
            "fy_wVol2036",
            "fy_wVol2037",
            "fy_wVol2038",
            "fy_wVol2039",
            "fy_wVol2040",
            "fy_wVol2041",
            "fy_wVol2042",
            "fy_wVol2043",
            "fy_wVol2044",
        ):
            value = getattr(row, column)
            if isinstance(value, (int, float, Decimal)):
                value = round(value, 2)
                return formats.localize(value)

        return super().render_column(row, column)

    def customize_row(self, row, obj):
        print("customizing row", row)
        row["pk"] = (
            """
        <div class="d-flex gap-2">
            <a href="/project/projectDeepdive/"""
            + str(row["ID_APP"])
            + """" class="text-secondary"> <i class="mdi mdi-square-edit-outline fs-18"></i></a>
            <a href="#" class="text-secondary"> <i class="mdi mdi-delete-outline fs-18"></i></a>
        </div>
        """
        )


class ProjectAPIView(AjaxDatatableView):
    model = Project
    search_values_separator = "+"
    length_menu = [[10, 20, 50, 100], [10, 20, 50, 100]]
    column_defs = [
        {
            "name": "pk",
            "title": "Edit",
            "placeholder": True,
            "searchable": False,
            "orderable": False,
        },
        {
            "name": "projectReviewed",
            "title": "Reviewed",
        },
        {
            "name": "reviewDate",
            "title": "Review Date",
        },
        {
            "name": "id",
            "title": "ID",
            "lookup_field": "__lte",
        },
        {
            "name": "productMarketer",
            "title": "Product Marketer",
            "foreign_field": "productMarketer__name",
        },
        {
            "name": "sales_name",
            "title": "Sales Name",
            "foreign_field": "sales_name__name",
        },
        {
            "name": "spNumber",
            "title": "SP Number",
        },
        {
            "name": "applicationMain",
            "title": "Application Main",
            "choices": True,
            "autofilter": True,
            "foreign_field": "applicationMain__appMainDescription",
        },
        {
            "name": "applicationDetail",
            "title": "Application Detail",
            "foreign_field": "applicationDetail__appDetailDescription",
        },
        {
            "name": "familyPriceApplicable",
            "title": "Family Price Applicable",
        },
        {
            "name": "priceType",
            "title": "Price Type",
            "foreign_field": "priceType__priceType",
        },
        {
            "name": "projectName",
            "title": "Project Name",
        },
        {
            "name": "mainCustomer",
            "title": "Main Customer",
            "foreign_field": "mainCustomer__customerName",
        },
        {
            "name": "finalCustomer",
            "title": "End Customer",
            "foreign_field": "finalCustomer__finalCustomerName",
        },
        {
            "name": "salesContact",
            "title": "Sales Contact",
        },
        {
            "name": "distributor",
            "title": "Distributor",
            "foreign_field": "distributor__distributorName",
        },
        {
            "name": "tier1",
            "title": "Tier One",
            "foreign_field": "tier1__tierOneName",
        },
        {
            "name": "oem",
            "title": "OEM",
            "foreign_field": "oem__oemName",
        },
        {
            "name": "ems",
            "title": "EMS",
            "foreign_field": "ems__emsName",
        },
        {
            "name": "vpaCustomer",
            "title": "VPA Customer",
            "foreign_field": "vpaCustomer__customerName",
        },
        {
            "name": "estimatedSop",
            "title": "SOP",
        },
        {
            "name": "modifiedDate",
            "title": "Modification Date",
        },
        {
            "name": "creationDate",
            "title": "Creation date",
        },
    ]

    def get_initial_queryset(self, request=None):
        queryset = self.model.objects.select_related(
            "productMarketer",
            "sales_name",
            "applicationMain",
            "applicationDetail",
            "priceType",
            "mainCustomer",
            "finalCustomer",
            "distributor",
            "tier1",
            "oem",
            "ems",
            "vpaCustomer",
        )
        return queryset

    def customize_row(self, row, obj):
        row["pk"] = (
            """
        <div class="d-flex gap-2">
            <a href="/project/projectDeepdive/"""
            + str(row["id"])
            + """" class="text-secondary"> <i class="mdi mdi-square-edit-outline fs-18"></i></a>
            <a href="#" class="text-secondary"> <i class="mdi mdi-delete-outline fs-18"></i></a>
        </div>
        """
        )

        # """
        #     <a href="#" class="btn btn-info btn-edit"
        #        onclick="var id=this.closest('tr').id.substr(4); alert('Editing Artist: ' + id); return false;">
        #        Edit
        #     </a>
        #     <a href="#" class="btn btn-danger btn-edit"
        #        onclick="var id=this.closest('tr').id.substr(4); alert('Deleting Artist: ' + id); return false;">
        #        Delete
        #     </a>
        # """
