from .models import (
    MainCustomers,
    MissingOrders,
    MissingSalesPlan,
    Project,
    FinalCustomers,
    Product,
    SalesName,
    OrdersWithNoProject,
)
from productMarketing.models import (
    ProjectVolumePrices,
    ProjectVolumeMonth,
    VhkCy,
    CurrenciesArchive,
    ExchangeRatesArchive,
    ProjectVolumePricesLog,
)
from enum import Enum

from productMarketing.queryJobs.warnings import errorDicTableLvl, errorDicProjectLvl
from datetime import datetime
from django.utils import timezone
from datetime import timedelta
from productMarketing.models import VhkCy
import pandas as pd
import xlsxwriter
from productMarketingDwh.models import VrfcOrdersOnHand, VrfcSalesForecast, BoUp
from django.db.models import Sum
import numpy as np
from django.db import connection
from currencies.models import Currency

"""
cleans leading and trailing zeroes

new Feb 2023: clean years and volumes previous to linSmoother... so if user entered 
[2020, 2021, 2022, 2023, 2024] and [100, 200, 0, 0, 0] to avoid misinterpolation -> [2020, 2021], [100, 200]
[2020, 2021, 2022, 2023, 2024] and [0, 200, 100, 0, 0] ->  [2021, 2022] [200, 100]
[2020, 2021, 2022, 2023, 2024] and [200, 200, 0, 100, 100] ->  [2020, 2021, 2022, 2023, 2024] and [200, 200, 0, 100, 100]

assumes that there are no gaps in the input years and that volumes / years have same length
"""
def cleanYearsVolumes(years, volumes):
    if len(years) == len(volumes):

        # remove trailing
        while volumes:
            if volumes[-1] != 0:
                break
            del volumes[-1]
            del years[-1]

        # remove leading
        while volumes:
            if volumes[0] != 0:
                break
            del volumes[0]
            del years[0]

        print("&&& cleanYearsVolumes")
        print("&&& outputs cleaned", years, volumes)

        """
        print("&&& cleanYearsVolumes")
        # get an array with indices that are 0 
        zeroIndices = [i for i, element in enumerate(volumes) if element==0]
        print("&&& zeroIndices", zeroIndices)

        for index in range(0, len(years), 1):
            if index in zeroIndices:
                years[index] = 0

        print("&&& years step 1", years)
        # remove zeroes
        volumes = list(filter(lambda num: num != 0, volumes))
        years = list(filter(lambda num: num != 0, years))
        print("&&& outputs cleaned", years, volumes)
        """

    else:
        print("&&& did not cleanYearsVolumes")
        return [], []

    return years, volumes

class HighLevelProjectProblems(Enum):
    # high level checks
    grossMarginNegative: int = 0
    weightedGrossMarginNegative: int = 1
    volumeIsZero: int = 2
    pricesAreZero: int = 3
    vhkError: int = 4
    fxError: int = 5
    priceTooLowError: int = 6
    aspTooLowVsAvgError: int = 7
    # originally in Patrics warnings.py
    price_over_15_procent_over_family_average = 8
    price_over_30_procent_over_RFP_average = 9
    same_main_end_customer_RFP_and_same_price_avg = 10
    no_gaps_between_sop_eop_volume = 11
    each_vol_has_price = 12
    no_gaps_between_sop_eop_price = 13
    each_price_has_vol = 14
    price_dif_between_year_not_more_than_15_procent = 15
    same_main_end_customer_RFP_and_same_price_yearly = 16
    price_over_15_procent_over_family_average_year = 17
    pricesAndVolumesMissingCompletely = 18
    projectKeyFactsError = 19
    otherProjectIntegrityError = 20
    noOrdersOnHandError = 21
    customersDontMatchSnop = 22
    mainCustomerDoesNotExist = 23
    endCustomerDoesNotExist = 24
    projectHasTobBeUpdated = 25
    salesOpportunityNotFound = 26
    multipleMatchingSalesOpportunities = 27
    defaultedToFirstMatchingSalesname = 28
    noSalesPlanError = 29

    def __str__(self) -> str:
        # python < v3.10 does not support switch statements...
        errors = {
            0: "Gross margin is zero or negative.",
            1: "Weighted gross margin is zero or negative.",
            2: "Volumes are zero or have not been entered into the system.",
            3: "All prices are zero or have not been entered into the system.",
            4: "No profit computation available. Did not find costs (VHKs) for the selected product, please check. If selected product is correct, please contact BPS Team.",
            5: "Error while fetching exchange rates. No profit computation available.",
            6: "All prices are below the minimum VHK.",
            7: "The ASP is below 20% the average for this product.",
            8: "There is at least one price which is above or below 15% of the overall family level average price.",
            9: "There is at least one price which is above or below 30% of the RFP level average.",
            10: "The average price of this project deviates by more than 1% of the average price of this RFP at the same Main and End Customers.",
            11: "There are gaps in the entered volume values.",
            12: "There is at least a year where there is no price for a given volume.",
            13: "There are price gaps between SOP and EOL (year or years missing).",
            14: "There is at least a year with a valid price but no volume.",
            15: "There is at least one year where the price jumps by more than 15% into the next year.",
            16: "The price differs from the RFP level average for this combination of main and end customer by more than 1% for a given year.",
            17: "There is at least one year in which the price is above or below 15% of the family level average for that given year.",
            18: "The project creation is incomplete. Please enter quantities, prices and a project status for this project.",
            19: "You are missing elementary project data. Please complete the key facts, quantities and prices before continuing.",
            20: "A miscelaneous project integrity error happened. Most likely, you are violating unique project constraints.",
            21: "There are no orders placed for this combination of RFP, Main Customer and End Customer within the next 3 calender years and SOP is within the next 3 years.",
            22: "The combination of Main Customer and End Customer don't match the allowable combinations from Sales and Operations Tool.",
            23: "The Main Customer does no longer exist or is not present in Sales and Operations Tool.",
            24: "The End Customer does no longer exist or is not present in Sales and Operations Tool.",
            25: "The project has not been updated in over 6 months.",
            26: "No matching Sales Opportunity found for this project.",
            27: "Multiple matching Sales Opportunity found for this project.",
            28: "Defaulted to first matching Product Sales Name during data migration. Please adjust to the best possible match.",
            29: "There is no Sales Planning for this combination of RFP, Main Customer and End Customer.",

        }

        return errors.get(self.value)


"""
Computes key metrics using ProjectVolumePrices, ProjectVolumePricesMonths and Vhks. BoUp figures are NOT used in this computation, but rather the result of this function.
VHKs are product manufacturing costs.
ProjectVolumePricesMonths are used to compute fiscal year (october - september) values. Our customer has a fiscal year that's different
of the calender year due to financial reasons.

Price values stored in ProjectVolumePrices are in the project's contractual currency. 
Prices are fetched from ProjectVolumePrices and converted from the contractual currency into USD. VHKs (production costs) are fetched from VhkCy table and converted into USD. 
All output revenue, gross margin figures are in USD.
All project values in BoUp are thus stored in USD. USD is the reigning currency in BoUp table.

All this data can then be used to be persisted in BoUp table (persistence is not implemented in this function!) or to show metrics and errors / quality checks in the front end.
Tends to be slow, it would be better to call async (render page and load data via ajax) but this is not implemented yet.
To Do: improve get_or_create queries to bulk actions.
"""


def getProjectOverview(projectId, user, probability, helperObjects):
    # , 2046, 2047, 2048, 2049, 2050]
    # helper arrays. they are used to have arrays for costs, prices, quantities (volumes), revenues, profit of the same length.
    years = [year for year in range(2020, 2046)]
    months = [month for month in range(1, 13)]

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
    totalCost = []
    asp = []
    errors = []
    vhkError = False
    fx = 1.0
    modifiedVhks = []
    VhkCy = []  # to do: what is this used for?
    project = None

    """
    helper Objects:
    0: Project.select_related("sales_name__rfp", "region")
    1: VhkCy.select_related("currency__currency")
    2: ProjectVolumePrices.objects.select_related(
            "project",
        )

    3: VOID / no longer used: currencyObj = Currencies.objects.get(currency=currencyPrices)   
    4 Old: VOID / no longer used: fxObject = ExchangeRates.objects.get(currency=currencyObj.pk, valid=True)
    4 New: Currency.objects (from django_currencies)
    5: ProjectVolumeMonth.objects.select_related().filter(
                project=project
            )
    6: MissingOrders.objects.filter(project=projectId)
    7: allFinalCustomers = FinalCustomers.objects.all()
    8: allMainCustomers = MainCustomers.objects.all()

    """

    if helperObjects == None:
        project = Project.objects.select_related("sales_name__rfp", "region").get(
            id=projectId
        )
    else:
        projObjHelper = helperObjects[0]
        project = helperObjects[0].get(
            id=projectId
        )

    """
    retrieve the costs for this project. this way we can compute a project's profit.
    costs are driven by RFP (= product), while a project is driven by sales_name (product with a different brand name on it).
    one product can have different sales name. It's like selling a Coca-Cola in red, white or green bottles. but in the end it's the same coca-cola
    with the same manufacturing costs (VHKs) and selling prices.
    costs are also uplaoded with an own currency, thus we have to store the cost's currency in order to convert later into EUR.
    all final computations are done in EUR. the official reporting currency is EUR. that's why we have to always check what is the input currency and then convert into EUR.
    you might make a deal with a customer in japanese Yen or swiss francs, but the reporting has to be done in EUR.

    VHK = VorHerstellungsKosten (production costs in German)
    """

    counterVhk = 0
    """
    get the production costs for each unit of this project's product
    for each year (usually starting with 2020...2040 ) we get each year's production cost.
    production costs change due to inflation, wages changing, etc... this is just a customer's forecast.
    we also retrieve the cost's currency, so that later down the road we can convert into EUR
    """
    try:
        costObject = None

        if helperObjects == None:
            costObject = VhkCy.objects.select_related("currency__currency").get(
                RFP=project.sales_name.rfp.pk, valid=True
            )
        else:
            costObject = helperObjects[1].get(
                RFP=project.sales_name.rfp.pk, valid=True
            )

        # my code
        costValue = list(costObject.values_list(
            [f"cy{year}" for year in years]))
        for value in costValue:
            vhk.append(float(value))
        currencyVhk = costObject.currency.currency

    except:
        """
        if no costs found in the database, we store 0 EUR and set vhkError = True (cost error = True)
        """
        for year in years:
            vhk.append(0.0)
        # to avoid error
        currencyVhk = "EUR"
        vhkError = True


    """
    check if defaulted to first matching sales name during migration and mark accordingly
    will be set to False if project is reviewed once (will assume that during review the correct sales name is set)
    """

    if project.salesNameDefaulted == True:
        errors.append(
            HighLevelProjectProblems.defaultedToFirstMatchingSalesname
        )
        
    """
    get the project's prices and the volumes (quantities).
    this way we compute the revenue (quantity * unit price)
    """
    yearCounter = 0
    runDate = datetime.now(tz=timezone.utc)

    projectVolumePricesObjects = None

    if helperObjects == None:
        projectVolumePricesObjects = ProjectVolumePrices.objects.select_related(
            "project",
        ).filter(project=project, calenderYear__in=years)
    else:
        projectVolumePricesObjects = helperObjects[2].filter(
            project=project, calenderYear__in=years)

    print("projectVolumePricesObjects", projectVolumePricesObjects)

    if projectVolumePricesObjects.count() > 0:

        values_tuple = list(
            projectVolumePricesObjects.values_list(
                "price", "quantity", "calenderYear", "currency", "vhkValue"
            )
        )
        priceValues, quantitiesValues, yearsValues, currenciesValues, vhkValues = zip(
            *values_tuple
        )

        for year in years:
            """
            this is like first index in swift
            get the first index matching the input year. if not available, this will throw a Value Error.
            for each year in 2020...2040, we will fill the helper arrays (prices, currencyPrices, volumes) with the information we need to compute revenues.
            meanwhile we will check if the stored costs differ from the most recent costs and we will update if required.
            each update will lead to an entry in the project log table.
            if we find no information, we will append 0.0 to each array.
            """

            try:
                relevantIndex = yearsValues.index(year)
                prices.append(float(priceValues[relevantIndex]))
                currencyPrices = currenciesValues[relevantIndex]
                volumes.append(quantitiesValues[relevantIndex])

                # create a vhk log only if the value changed wrt to this years VHK
                # vhkActual is the official, infineon cost for this product. vhkValues is the vhk used for this project when creating the project.
                # in future this might be obsolete, since we will be updating VHKs (costs) continuously.
                # if the VHK has changed, update the VHK and log into the project history.
                vhkActual = vhk[yearCounter]

                if helperObjects != None:

                    if float(vhkValues[relevantIndex]) != vhkActual:
                        (
                            logobject,
                            logcreated,
                        ) = ProjectVolumePricesLog.objects.get_or_create(
                            project=project, calenderYear=int(year), runTimestamp=runDate
                        )
                        logobject.vhkValue = vhk[yearCounter]
                        if user != None:
                            logobject.user = user

                        logobject.modreason = "vhk"
                        logobject.save()

                        # update the vhks accordingly
                        object = projectVolumePricesObjects.get(
                            calenderYear=year)
                        object.vhkValue = vhkActual
                        object.save()

                yearCounter = yearCounter + 1

            except:
                prices.append(0.0)
                volumes.append(0)
                yearCounter = yearCounter + 1

        """
        retrieve the exchange rate if no errors happened above
        this way, if required, we can convert from source currency into EUR
        to do: change to django_currencies table
        """
        fxErrorPrices = False
        currencyObj = None
        fxObject = None
        projectCurrency = None

        try:
            if helperObjects == None:
                """
                currencyObj = Currencies.objects.get(currency=currencyPrices)
                fxObject = ExchangeRates.objects.get(currency=currencyObj.pk, valid=True)
                """
                fxObject = Currency.objects.get(code=currencyPrices)
            else:
                """
                currencyObj = helperObjects[3].get(currency=currencyPrices)
                fxObject = helperObjects[4].get(currency=currencyObj.pk, valid=True)
                """
                fxObject = helperObjects[4].get(code=currencyPrices, is_active=True) #Currency.objects.get(code=currencyPrices)
        except:
            fxErrorPrices = True

        # check if price currency (project contractual currency) matches cost currency, else batch transform
        # since the currencies in Db have a strange format, we cast into float.
        # exchange rates are understood from source into EUR. multiplying the source price by the fx will yield a value in EUR.
        if (currencyPrices != "EUR") & (fxErrorPrices == False):
            projectCurrency = currencyPrices
            # get current rate
            fx = 1.0
            try:
                #fx = float(fxObject.rate)
                fx = float(fxObject.factor)
            except:
                fxErrorPrices = True

            """
            convert into the target currency (eur)
            we will map the whole price array with the fx-rate
            """
            for index in range((len(years) - 1)):
                prices[index] = prices[index] * float(fx)
        elif fxErrorPrices == False:
            projectCurrency = currencyPrices

        # now check if the VHK's (costs) currency matches EUR. if not, convert to EUR.
        if (currencyVhk != "EUR") & (fxErrorPrices == False):
            # get current rate
            fx = 1.0

            currencyObjVhk = None
            fxObjVhk = None
            fxVhk = 1.0

            try:
                if helperObjects == None:
                    """
                    currencyObjVhk = Currencies.objects.select_related().get(
                        currency=currencyVhk
                    )
                    fxObjVhk = ExchangeRates.objects.get(
                        currency=currencyObjVhk.pk, valid=True
                    )
                    fxVhk = float(fxObjVhk.rate)
                    """

                    fxVhk = float(Currency.objects.get(code=currencyVhk).factor)
                else:
                    """
                    currencyObjVhk = helperObjects[3].select_related().get(
                        currency=currencyVhk
                    )
                    fxObjVhk = helperObjects[4].get(
                        currency=currencyObjVhk.pk, valid=True
                    )
                    fxVhk = float(fxObjVhk.rate)
                    """
                    fxVhk = float(helperObjects[4].get(
                        code=currencyVhk, is_active=True
                    ).factor)

            except:
                fxErrorPrices = True

            """
            convert the vhks into the target currency
            we will map the whole costs array into the target currency (EUR)
            """
            for index in range((len(years) - 1)):
                vhk[index] = vhk[index] * float(fxVhk)

        """
        repeat procedure for monthly values
        first fetch the months and years of this project, create the tuple for each row in ProjectVolumeMonth
        then iterate over all tuples and create volumes accordingly.
        """

        i = 0
        projectVolumeMonthObjects = None
        if helperObjects == None:
            projectVolumeMonthObjects = ProjectVolumeMonth.objects.select_related().filter(
                project=project
            )
        else:
            projectVolumeMonthObjects = helperObjects[5].filter(
                project=project
            )

        calenderYearValues = list(
            projectVolumeMonthObjects.values_list("calenderYear", flat=True)
        )
        monthValues = list(
            projectVolumeMonthObjects.values_list("month", flat=True))
        monthlyQuantityValues = list(
            projectVolumeMonthObjects.values_list("quantity", flat=True)
        )
        monthYearTuples = []

        for indexA in range(len(calenderYearValues)):
            monthYearTuples.append(
                (calenderYearValues[indexA], monthValues[indexA]))

        for year in years:
            for month in months:
                if ((year, month) in monthYearTuples) == True:
                    all_months.append(i + 1)
                    i = i + 1
                    indexB = monthYearTuples.index((year, month))
                    volumesMonth.append(monthlyQuantityValues[indexB])
                else:
                    missing_months.append(i + 1)
                    i = i + 1

        ##################
        for year in years:
            try:
                region.append(project.region)
            except:
                region.append("Not avaiable")
        """
        in this section we will compute revenue and gross margins using the costs, prices and volumes we fetched above.
        we assume that now everything is in EUR.
        if any error happened with currency conversion, we will return zero arrays.
        the formula is easy: gross margin = total revenue - total cost
        Gross margin is a synonym for gross profit.
        total revenue = quantity * price
        total cost = quantity * vhk
        quantity is the same as volume, we use the words interchangeably
        """
        # revenue and gm
        revenue = []
        grossMargin = []
        grossMarginPct = []

        # initialize values
        for index in range((len(years))):
            revenue.append(0.0)
            grossMargin.append(0.0)
            grossMarginPct.append(0.0)

        # FY calculations through month aggregation
        revenue_month = []
        grossMargin_month = []
        grossMarginPct_month = []

        print(projectId, "fxErrorPrices", fxErrorPrices, "vhkError",
              vhkError, "prices", prices, "volumes", volumes)

        """
        so only if no error happened before we will compute profit.
        otherwise we will create arrays with zeros.
        """
        if (fxErrorPrices == False) & (vhkError == False):
            for index in range(len(years)):

                revenueValue = prices[index] * volumes[index]
                cost = vhk[index] * volumes[index]
                grossMarginValue = revenueValue - cost
                revenue[index] = revenueValue  # .append(revenueValue)
                # append(grossMarginValue)
                grossMargin[index] = grossMarginValue
                grossMarginPctValue = 0
                totalCost.append(cost)
                try:
                    grossMarginPctValue = grossMarginValue * 100 / revenueValue
                    grossMarginPct[index] = grossMarginPctValue
                except:
                    grossMarginPct[index] = 0.0
                # print("%%%%%%%%%%% final result, year", years[index], "volume", volumes[index], "price", prices[index], "currency: EUR",
                #     "revenue", revenueValue, "gross margin", grossMarginValue, "cost", vhk[index], "margin pctg", grossMarginPctValue)

            # for monthly calculation aggregated into FY
            for index in range(len(years)):
                for month in months:
                    try:
                        month_value = volumesMonth[(index * 12) + month - 1]
                    except:
                        # since only values until 2024 and not up to 2045(because entry is for 2020 to 2024)
                        month_value = 0
                    revenueMonthValue = prices[index] * month_value

                    if revenueMonthValue == None:
                        revenueMonthValue = 0.0

                    grossMarginMonthValue = revenueMonthValue - (
                        vhk[index] * month_value
                    )
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

        else:
            """
            if there is an error with the currencies conversion, we will create arrays with zeros
            """
            # just add revenue for sake of completeness
            for index in range(len(years) - 1):
                revenueValue = prices[index] * volumes[index]
                revenue[index] = revenueValue
                totalCost.append(0.0)
                grossMarginPct_month.append(0.0)
                # grossMargin.append(0.0)

            # for monthly calculation aggregated into FY
            for index in range(len(years)):
                for month in months:
                    try:
                        month_value = volumesMonth[(index * 12) + month - 1]
                    except:
                        month_value = 0

                    revenueMonthValue = prices[index] * month_value
                    revenue_month.append(revenueMonthValue)

        """
        this will convert our figures into fiscal years.
        The customer uses both a calendar year (jan-dec) and a fiscal year (oct-sept) for reporting.
        thus we will use the monthly figures in order to aggregate accordingly for the fiscal year values.
        there are no database calls involved in this step.
        """
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
                revenue_FY.append(
                    sum(revenue_month[current_start: current_end + 1]))
                grossProfit_FY.append(
                    sum(grossMargin_month[current_start: current_end + 1])
                )
                grossProfitPct_FY.append(
                    sum(grossMarginPct_month[current_start: current_end + 1])
                )
                volumes_FY.append(
                    sum(volumesMonth[current_start: current_end + 1]))

        # process errors. this is later used to populte the errors array used to show in the front end.
        if fxErrorPrices == True:
            errors.append(HighLevelProjectProblems.fxError)
            #    "Error while fetching exchange rates. No profit computation available.")

        if vhkError == True:
            errors.append(HighLevelProjectProblems.vhkError)
            #    "Error while fetching VHKs. No profit computation available.")

        """
        now compute weighted figures
        weighted figures are nothing else than an applying the project's status / probability to the above mentioned figures (revenue, gross margin)
        here the only tricky thing would be to deal with division by 0
        """
        weightedGrossMargin = []
        weightedGrossMarginPct = []
        weightedRevenue = []
        weightedVolume = []
        asp = []

        # this here has to be an &. using pipe just for testing purposes.
        if (fxErrorPrices == False) & (vhkError == False):

            if probability == None:
                errors.append(
                    HighLevelProjectProblems.pricesAndVolumesMissingCompletely
                )

            if (probability != 0.0) and (probability != None):
                for index in range(len(years)):
                    weightedVolumeValue = probability * volumes[index]
                    weightedRevenueValue = weightedVolumeValue * prices[index]
                    weightedGrossMarginValue = (
                        weightedRevenueValue - weightedVolumeValue * vhk[index]
                    )

                    try:
                        aspValue = weightedRevenueValue / weightedVolumeValue
                        weightedGrossMarginPctValue = (
                            weightedGrossMarginValue * 100 / weightedRevenueValue
                        )
                    except:
                        aspValue = 0.0
                        weightedGrossMarginPctValue = 0.0

                    asp.append(aspValue)
                    weightedGrossMargin.append(weightedGrossMarginValue)
                    weightedRevenue.append(weightedRevenueValue)
                    weightedGrossMarginPct.append(weightedGrossMarginPctValue)
                    weightedVolume.append(weightedVolumeValue)
            else:
                for index in range(len(years)):
                    asp.append(0.0)
                    weightedGrossMargin.append(0.0)
                    weightedRevenue.append(0.0)
                    weightedGrossMarginPct.append(0.0)
                    weightedVolume.append(0.0)

        else:
            if probability != 0.0 and (probability != None):
                for index in range(len(years)):
                    #print("prob, year, vol", probability, volumes[index])
                    weightedVolumeValue = probability * volumes[index]
                    weightedRevenueValue = weightedVolumeValue * prices[index]
                    weightedGrossMarginValue = 0.0
                    aspValue = 0.0
                    weightedGrossMarginPctValue = 0.0

                    try:
                        aspValue = weightedRevenueValue / weightedVolumeValue
                        weightedGrossMarginPctValue = (
                            weightedGrossMarginValue * 100 / weightedRevenueValue
                        )
                    except:
                        aspValue = 0.0
                        weightedGrossMarginPctValue = 0.0

                    asp.append(aspValue)
                    weightedGrossMargin.append(weightedGrossMarginValue)
                    weightedRevenue.append(weightedRevenueValue)
                    weightedGrossMarginPct.append(weightedGrossMarginPctValue)
                    weightedVolume.append(weightedVolumeValue)

            else:
                for index in range(len(years)):
                    asp.append(0.0)
                    weightedGrossMargin.append(0.0)
                    weightedRevenue.append(0.0)
                    weightedGrossMarginPct.append(0.0)
                    weightedVolume.append(0.0)

        ######
        """
        we will now compute the sums across the project's lifetime
        """
        sumGrossMargin = sum(grossMargin)
        sumRevenue = sum(revenue)
        sumCost = sum(totalCost)
        sumWeightedVolume = sum(weightedVolume)
        sumWeightedRevenue = sum(weightedRevenue)
        sumWeightedMargin = sum(weightedGrossMargin)
        sumVolume = sum(volumes)
        averageAsp = 0.0

        """
        if len(asp) > 0:
            tempAsp = []
            # for each year where asp is not zero
            for index in range(len(years)):
                if asp[index] > 0.0:
                    tempAsp.append(asp[index])
            try:
                averageAsp = sum(tempAsp) / (len(tempAsp))
            except:
                averageAsp = 0.0
        else:
            averageAsp = 0.0
        """

        if len(weightedVolume) == len(weightedRevenue):
            try:
                averageAsp = sumWeightedRevenue / sumWeightedVolume
            except:
                averageAsp = 0.0
        else:
            averageAsp = 0.0

        # now some high level checks that are used to show errors in the front end.

        if sumGrossMargin < 0:
            errors.append(HighLevelProjectProblems.grossMarginNegative)

        if sumWeightedMargin < 0:
            errors.append(HighLevelProjectProblems.grossMarginNegative)

        if sum(volumes) == 0:
            errors.append(HighLevelProjectProblems.volumeIsZero)

        if len(volumes) > 0:
            if max(volumes) <= 0:
                errors.append(HighLevelProjectProblems.volumeIsZero)

        if sum(prices) == 0:
            errors.append(HighLevelProjectProblems.pricesAreZero)

        if len(prices) > 0:
            if max(prices) <= 0:
                errors.append(HighLevelProjectProblems.pricesAreZero)

        if max(prices) < min(vhk):
            errors.append(HighLevelProjectProblems.priceTooLowError)

        # check avg asp vs. product avg
        # req 59,61,101. originally designed with struct.
        externalErrors, meanPriceRfpLevel, meanPriceSiliconLevel = errorDicTableLvl(
            projectId, helperObjects
        )

        if (
            externalErrors[
                HighLevelProjectProblems.price_over_30_procent_over_RFP_average
            ]
            == True
        ):
            errors.append(
                HighLevelProjectProblems.price_over_30_procent_over_RFP_average
            )

        if (
            externalErrors[
                HighLevelProjectProblems.same_main_end_customer_RFP_and_same_price_avg
            ]
            == True
        ):
            errors.append(
                HighLevelProjectProblems.same_main_end_customer_RFP_and_same_price_avg
            )

        if (
            externalErrors[
                HighLevelProjectProblems.price_over_15_procent_over_family_average
            ]
            == True
        ):
            errors.append(
                HighLevelProjectProblems.price_over_15_procent_over_family_average
            )

        if (
            externalErrors[
                HighLevelProjectProblems.same_main_end_customer_RFP_and_same_price_yearly
            ]
            == True
        ):
            errors.append(
                HighLevelProjectProblems.same_main_end_customer_RFP_and_same_price_yearly
            )

        if (
            externalErrors[
                HighLevelProjectProblems.price_over_15_procent_over_family_average_year
            ]
            == True
        ):
            errors.append(
                HighLevelProjectProblems.price_over_15_procent_over_family_average_year
            )

        # req  45,60,62. originally in warnings.py of Patric.
        intrinsicErrors = errorDicProjectLvl(projectId)

        for key, value in intrinsicErrors.items():
            # watchout, use False here!!!
            if value == False:
                errors.append(key)

        # check against VRFC, Orders
        ordersMissing = 0
        if helperObjects == None:
            ordersMissing = MissingOrders.objects.filter(project=projectId)
        else:
            ordersMissing = helperObjects[6].filter(project=projectId)

        current_year = datetime.now().year
        three_years_after = current_year + 3

        # orders if SOP on short term (Nahzeitraum, 3 years)
        if (ordersMissing.count() > 0) & (abs(three_years_after - project.estimatedSop) < 3):
            errors.append(HighLevelProjectProblems.noOrdersOnHandError)

        # check against VRFC, Sales Plan
        salesPlanMissing = 0
        if helperObjects == None:
            salesPlanMissing = MissingSalesPlan.objects.filter(
                project=projectId)
        else:
            salesPlanMissing = helperObjects[9].filter(project=projectId)

        if (salesPlanMissing.count() > 0):
            errors.append(HighLevelProjectProblems.noSalesPlanError)

        # check if main and end customers are still valid
        allFinalCustomers = None
        allMainCustomers = None

        if helperObjects == None:
            allFinalCustomers = FinalCustomers.objects.all()
            allMainCustomers = MainCustomers.objects.all()
        else:
            allFinalCustomers = helperObjects[7]
            allMainCustomers = helperObjects[8]

        validFinalCustomers = allFinalCustomers.filter(valid=True)
        validMainCustomers = allMainCustomers.filter(valid=True)

        if validFinalCustomers.filter(id=project.finalCustomer_id).count() == 0:
            errors.append(HighLevelProjectProblems.endCustomerDoesNotExist)

        if validMainCustomers.filter(id=project.mainCustomer_id).count() == 0:
            errors.append(HighLevelProjectProblems.mainCustomerDoesNotExist)
        else:
            mainCustomer = validMainCustomers.get(id=project.mainCustomer_id)

            if mainCustomer.finalCustomers.filter(id=project.finalCustomer_id).exists():
                pass
            else:
                errors.append(HighLevelProjectProblems.customersDontMatchSnop)

        # check against Dragon. dragon is the sales opportunities system.
        # is there any matching dragon opportunity, based on sales name, applications, main and end customer?
        # this has not been implemented yet (wip Francisco / Patric)

        # check last update time. of more than 6 months, error / warning.
        if abs(project.modifiedDate - runDate) > (timedelta(days=180)):
            errors.append(HighLevelProjectProblems.projectHasTobBeUpdated)
        print("cc")
        return (
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
            sumWeightedMargin,
            projectCurrency,
            fx
        )

    else:

        errors.append(
            HighLevelProjectProblems.pricesAndVolumesMissingCompletely)

        revenue = []
        volumes = []
        prices = []
        grossMargin = []
        grossMarginPct = []
        revenue_month = []
        grossMargin_month = []
        grossMarginPct_month = []
        vhk = []
        revenue_FY = []
        grossProfit_FY = []
        grossProfitPct_FY = []
        volumes_FY = []
        VhkCy = []
        totalCost = []
        asp = []
        weightedGrossMargin = []
        weightedGrossMarginPct = []
        weightedRevenue = []
        weightedVolume = []

        return (
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
            0,
            0,
            0,
            years,
            errors,
            weightedGrossMargin,
            weightedGrossMarginPct,
            weightedRevenue,
            asp,
            weightedVolume,
            0,
            0,
            0,
            0,
            0,
            None,
            1.0
        )


"""
this function is used to generate yearly aggregated figures for revenues, prices, profit etc...
the values are later stored as a CSV snapshot for further use in future.
"""


def getBoUpKeyMetrics(inputDf):
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

    revenues = []
    volumes = []
    grossMargin = []
    totalCost = []
    weightedVolumes = []
    weightedGrossMargin = []
    weightedRevenues = []
    asp = []

    # for each column where "vol20xx", run the vertical sum. idem for wRev,
    # to be redone via sql query, this is too slow

    for (columnName, columnData) in inputDf.iteritems():
        if ("wVol" in str(columnName)) & ("fy_" not in str(columnName)):
            values = columnData.values
            values = list(map(float, values))
            weightedVolumes.append(sum(values))

        if ("wRev" in str(columnName)) & ("fy_" not in str(columnName)):
            values = columnData.values
            values = list(map(float, values))
            weightedRevenues.append(sum(values))

        if ("wGrossMargin" in str(columnName)) & ("fy_" not in str(columnName)):
            values = columnData.values
            values = list(map(float, values))
            weightedGrossMargin.append(sum(values))

        if "asp" in str(columnName):
            values = columnData.values
            values = list(map(float, values))
            asp.append(sum(values))

        if (
            ("vol" in str(columnName))
            & ("wVol" not in str(columnName))
            & ("fy_" not in str(columnName))
            & ("volWeightedLifeTime" not in str(columnName))
            & ("volCustomer" not in str(columnName))
            & ("volLifeTime" not in str(columnName))
        ):
            #print("colname vol", columnName)
            values = columnData.values
            values = list(map(float, values))
            volumes.append(sum(values))

        if (
            ("gm" in str(columnName))
            & ("wGrossMargin" not in str(columnName))
            & ("fy_gm" not in str(columnName))
            & ("gmLifeTime" not in str(columnName))
        ):
            #print("colname gm", columnName)
            values = columnData.values
            values = list(map(float, values))
            grossMargin.append(sum(values))

        """
        if ("gm" in str(columnName)) & ("wGrossMargin" not in str(columnName)):
            values = columnData.values
            values = list(map(float, values))
            grossMargin.append(sum(values))
        """

    return (
        years,
        weightedVolumes,
        weightedGrossMargin,
        weightedRevenues,
        asp,
        volumes,
        grossMargin,
    )


def missingVhkReport(marketer):
    allProducts = Product.objects.all()
    allVHks = VhkCy.objects.all()
    missingProducts = []
    basicTypes = []
    packages = []

    for product in allProducts:
        if allVHks.filter(RFP=product, valid=True).count() == 0:
            missingProducts.append(product.rfp)
            basicTypes.append(product.basicType)
            packages.append(product.packageHelper)

    dict = {
        "Missing RFP": missingProducts,
        "BasicType": basicTypes,
        "Package": packages,
    }
    df = pd.DataFrame(dict)

    runDate = datetime.today().strftime("%Y-%m-%d")
    filePath = "m_" + str(marketer) + "_" + str(runDate) + "_MissingVHKS.xlsx"

    df.to_excel(filePath)

    return filePath


# vrfcFileExportOoh


def vrfcFileExportOoh(marketer):

    df = pd.DataFrame.from_records(
        VrfcOrdersOnHand.objects.all().values(
            "id",
            "rfp__rfp",  # <-- get the name through the foreign key
            "mainCustomerVrfc__customerName",
            "endCustomerVrfc__finalCustomerName",
            "quarter",
            "year",
            "fiscalQuarter",
            "fiscalYear",
            "quantity",
            "asp",
            "revenue",
        )
    ).rename(
        columns={
            "rfp__rfp": "Product (RFP)",
            "mainCustomerVrfc__customerName": "Main Customer",
            "endCustomerVrfc__finalCustomerName": "End Customer",
        }
    )
    runDate = datetime.today().strftime("%Y-%m-%d")

    filePath = (
        "./persistentLayer/temp/"
        + "m_"
        + str(marketer)
        + "_"
        + str(runDate)
        + "_SalesForecastExport.xlsx"
    )

    df.to_excel(filePath)
    return filePath


def vrfcFileExportSfc(marketer):

    df = pd.DataFrame.from_records(
        VrfcSalesForecast.objects.all().values(
            "id",
            "rfp__rfp",  # <-- get the name through the foreign key
            "mainCustomerVrfc__customerName",
            "endCustomerVrfc__finalCustomerName",
            "quarter",
            "year",
            "fiscalQuarter",
            "fiscalYear",
            "quantity",
            "asp",
            "revenue",
        )
    ).rename(
        columns={
            "rfp__rfp": "Product (RFP)",
            "mainCustomerVrfc__customerName": "Main Customer",
            "endCustomerVrfc__finalCustomerName": "End Customer",
        }
    )

    runDate = datetime.today().strftime("%Y-%m-%d")

    filePath = (
        "./persistentLayer/temp/"
        + "m_"
        + str(marketer)
        + "_"
        + str(runDate)
        + "_SalesForecastExport.xlsx"
    )

    df.to_excel(filePath)

    return filePath


def productMasterDataFile(marketer):

    df = pd.DataFrame.from_records(
        SalesName.objects.filter(valid=True).values(
            "id",
            "dummy",  # <-- get the name through the foreign key
            "name",
            "rfp__rfp",
            "rfp__hfg",
            "rfp__ppos",
            "rfp__familyHelper",
            "rfp__familyDetailHelper",
            "rfp__packageHelper",
            "rfp__seriesHelper",
            "rfp__availablePGS",
            "rfp__basicType",
        )
    ).rename(
        columns={
            "dummy": "Dummy",
            "name": "Product Sales Name",
            "rfp__rfp": "RFP",
            "rfp__hfg": "HFG",
            "rfp__ppos": "PPOS",
            "rfp__familyHelper": "Product Family",
            "rfp__familyDetailHelper": "Family Detail",
            "rfp__packageHelper": "Package",
            "rfp__seriesHelper": "Series",
            "rfp__availablePGS": "Available in PGS+",
            "rfp__basicType": "Basic Type",
        }
    )

    runDate = datetime.today().strftime("%Y-%m-%d")
    filePath = (
        "m_" + str(marketer) + "_" + str(runDate) +
        "_ProductMasterDataExport.xlsx"
    )
    df.to_excel(filePath)

    return filePath


"""
the goal of this report is to download a list of planned projects where there is no order placed
"""


def projectsWithNoOrderReport(marketer):
    df = pd.DataFrame.from_records(
        MissingOrders.objects.all().values(
            "project__id",
            "project__sales_name__rfp__rfp",
            "project__sales_name__name",
            "project__mainCustomer__customerName",
            "project__finalCustomer__finalCustomerName",
            "project__applicationMain__appMainDescription",
            "project__applicationDetail__appDetailDescription",
            "project__productMarketer__name",
            "project__productMarketer__familyName",
            "project__dummy",
            "project__draft",
        )
    ).rename(
        columns={
            "id": "Project ID",
            "project__sales_name__rfp__rfp": "RFP",
            "project__sales_name__name": "Product Sales Name",
            "project__mainCustomer__customerName": "Main Customer",
            "project__finalCustomer__finalCustomerName": "End Customer",
            "project__applicationMain__appMainDescription": "Application Main",
            "project__applicationDetail__appDetailDescription": "Application Detail",
            "project__productMarketer__name": "Marketer Name",
            "project__productMarketer__familyName": "Marketer Surname",
            "project__dummy": "Model Filler?",
            "project__draft": "Draft?",
        })

    runDate = datetime.today().strftime('%Y-%m-%d')
    filePath = "m_" + \
        str(marketer) + "_" + str(runDate) + "_ProjectsWithNoOrdersReport.xlsx"
    df.to_excel(filePath)

    return filePath, df


"""
the goal of this report is to download a list of orders that have no planned project
"""


def ordersWithNoProjectReport(marketer):

    allOrders = VrfcOrdersOnHand.objects.all()
    df = pd.DataFrame.from_records(
        OrdersWithNoProject.objects.all().values(
            "id",
            "rfp__rfp",  # <-- get the name through the foreign key
            "mainCustomer__customerName",
            "endCustomer__finalCustomerName",
            "rfp",  # <-- get the name through the foreign key
            "mainCustomer",
            "endCustomer",
        )
    ).rename(
        columns={
            "rfp__rfp": "RFP",
            "mainCustomer__customerName": "Main Customer",
            "endCustomer__finalCustomerName": "End Customer",
            "rfp": "ProductId",
            "mainCustomer": "MainCustomerId",
            "endCustomer": "EndCustomerId",
        }
    )

    lengthA = len(df.index)

    df["Order Quantity"] = np.nan
    df["Order Revenue"] = np.nan

    for index in range(0, lengthA, 1):
        mainCustomerId = df.loc[index, "MainCustomerId"]
        endCustomerId = df.loc[index, "EndCustomerId"]
        rfpId = df.loc[index, "ProductId"]

        orders = allOrders.filter(
            mainCustomerVrfc=mainCustomerId, endCustomerVrfc=endCustomerId, rfp=rfpId)
        cummulativeRevenue = orders.aggregate(Sum('revenue'))
        cummulativeVolume = orders.aggregate(Sum('quantity'))
        #print("cumrev", cummulativeRevenue)

        df.loc[index, "Order Quantity"] = cummulativeVolume["quantity__sum"]
        df.loc[index, "Order Revenue"] = cummulativeRevenue["revenue__sum"]

        """
        # attempt to append as a single row the orders at a quarterly level, incl asp, revenue, volume
        ordersDf = pd.DataFrame.from_records(
            orders.values("rfp", "mainCustomerVrfc", "endCustomerVrfc", "quarter", "fiscalQuarter", "year", "fiscalYear", "quantity", "asp", "revenue")
        )
        print("ordersdf")
        print(ordersDf)
        pivotDf = ordersDf.pivot(columns=["quarter", "fiscalQuarter"], values=['quantity', 'asp', 'revenue'])
        print("pivot df")
        print(pivotDf)
        """

    runDate = datetime.today().strftime('%Y-%m-%d')
    filePath = "./persistentLayer/importExport/m_" + \
        str(marketer) + "_" + str(runDate) + "_OrdersWithNoProject.xlsx"
    df.to_excel(filePath)

    return filePath, df


"""
The goal of this report is to download daily deltas of BoUp (grouped at RFP level) wrt to VRFC Orders
"""


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def rawSqlPerformer(sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)
        row = dictfetchall(cursor)
    return row

# compare all entries from vfrcoderonhand with projVolmonth


def boupDeltasToOrdersReportQuery():
    valueQuery = "                                  \
        SELECT                                          \
        endCustomerVrfc_id as endCustomer, mainCustomerVrfc_id as mainCustomer, a.rfp_id as rfp, calenderYear, b.quarter,   \
        a.quantity as OoH_quantity, b.quantity as projectAgg_quantity, a.quantity - b.quantity as delta, -1 as projects \
        FROM  \
        productMarketingDwh_vrfcordersonhand as a\
        INNER JOIN                                     \
        (SELECT  \
         finalCustomer_id, mainCustomer_id, rfp_id, calenderYear, quarter, SUM(quantity) as quantity \
         FROM (\
                SELECT                                      \
                proj.finalCustomer_id, proj.mainCustomer_id, sal.rfp_id, volMon.calenderYear, volMon.quarter, volMon.quantity        \
                FROM                                        \
                project_project as proj                                   \
                INNER JOIN                                       \
                project_salesname as sal                                       \
                ON proj.sales_name_id = sal.id        \
                INNER JOIN                                         \
                (SELECT *, CASE WHEN month < 4 THEN 1 \
                            WHEN month > 3 and month < 7 THEN 2   \
                            WHEN month > 6 and month < 10 THEN 3   \
                            WHEN month > 9  THEN 4   \
                            ELSE -1   \
                            END AS quarter                                                         \
                FROM productMarketing_projectvolumemonth  \
                ) as volMon                                       \
                ON proj.id = volMon.project_id  \
              )        \
         GROUP BY        \
         finalCustomer_id, mainCustomer_id, rfp_id, calenderYear, quarter    \
        ) as b\
        ON a.endCustomerVrfc_id=b.finalCustomer_id and a.mainCustomerVrfc_id = b.mainCustomer_id and a.rfp_id = b.rfp_id and a.year = b.calenderYear and a.quarter = b.quarter  \
        ;                                               \
        "

    allDeltaEntries = rawSqlPerformer(valueQuery)
    return allDeltaEntries


def boupDeltasToOrdersReport(marketer):

    #allBoupProjects = BoUp.objects.all()
    #allOrders = VrfcOrdersOnHand.objects.all()

    # ProjectVolumePricesMonth -> aggregate into quarterly level
    # -> group into RFP, Main Customer, End Customer level

    df = pd.DataFrame(boupDeltasToOrdersReportQuery())

    runDate = datetime.today().strftime("%Y-%m-%d")
    filePath = (
        "./persistentLayer/importExport/m_" +
        str(marketer) + "_" + str(runDate) + "_boupDeltasToOrders.xlsx"
    )
    print("df")
    print(df)
    df.to_excel(filePath)

    return filePath, df


"""
from django.db import connection

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def rawSqlPerformer(sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)
        row = dictfetchall(cursor)
    return row


###compare all entries from vfrcoderonhand with projVolmonth
def boupDeltasToOrdersReport ():
    valueQuery = "                                  \
        SELECT                                          \
        endCustomerVrfc_id as endCustomer, mainCustomerVrfc_id as mainCustomer, a.rfp_id as rfp, calenderYear, b.quarter,   \
        a.quantity as OoH_quantity, b.quantity as projectAgg_quantity, a.quantity - b.quantity as delta, -1 as projects \
        FROM  \
        productMarketingDwh_vrfcordersonhand as a\
        INNER JOIN                                     \
        (SELECT  \
         finalCustomer_id, mainCustomer_id, rfp_id, calenderYear, quarter, SUM(quantity) as quantity \
         FROM (\
                SELECT                                      \
                proj.finalCustomer_id, proj.mainCustomer_id, sal.rfp_id, volMon.calenderYear, volMon.quarter, volMon.quantity        \
                FROM                                        \
                project_project as proj                                   \
                INNER JOIN                                       \
                project_salesname as sal                                       \
                ON proj.sales_name_id = sal.id        \
                INNER JOIN                                         \
                (SELECT *, CASE WHEN month < 4 THEN 1 \
                            WHEN month > 3 and month < 7 THEN 2   \
                            WHEN month > 6 and month < 10 THEN 3   \
                            WHEN month > 9  THEN 4   \
                            ELSE -1   \
                            END AS quarter                                                         \
                FROM productMarketing_projectvolumemonth  \
                ) as volMon                                       \
                ON proj.id = volMon.project_id  \
              )        \
         GROUP BY        \
         finalCustomer_id, mainCustomer_id, rfp_id, calenderYear, quarter    \
        ) as b\
        ON a.endCustomerVrfc_id=b.finalCustomer_id and a.mainCustomerVrfc_id = b.mainCustomer_id and a.rfp_id = b.rfp_id and a.year = b.calenderYear and a.quarter = b.quarter  \
        ;                                               \
        "

    allDeltaEntries = rawSqlPerformer(valueQuery)


    return allDeltaEntries
"""
