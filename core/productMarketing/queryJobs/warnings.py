# from turtle import position
import numpy as np
from scipy.stats import poisson
import pandas as pd
from scipy.interpolate import interp1d
from ..models import *
from statistics import mean
from enum import Enum
from django.db.models import Avg

# def checkConditionsAtPrice(sop, eop, prices): #check if each year has a price

#     years = list(range(sop,eop)) #False means everything ok and True means there is a missing value
#     check = False
#     for idx, i in enumerate(years):
#         if prices[idx] == 0:
#             check = True

#     return  check


def checkVolumeEntry(projectId):  # gives all years which have a volume entry
    years = []
    volumeObjects = ProjectVolumePrices.objects.filter(project_id=projectId)
    for volObj in volumeObjects:
        if volObj.quantity != 0 and not pd.isna(volObj.quantity):
            years.append(volObj.calenderYear)
            # print(volObj.quantity)

    return years


def checkgapsInYearsEntry(years):  # gives all years which have a volume entry
    int_years = []
    for i in years:
        int_years.append(int(i))
    check = True
    sop = min(int_years)
    eop = max(int_years)
    for i in list(range(sop, eop + 1)):
        if i not in int_years:
            print("missing", i)
            check = False
    return check


"""
projectVolumePrices:
calenderYear
quantity
quantityCustomerEstimation
source
data
user #foreign key
modifiedDate
project #foreign key
valid
priceSource
comment
currency
price
priceValidityUntil
priceSourceComment
"""
# req  45,60,62


def errorDicProjectLvl(p_id):

    from project.helperFunctions import HighLevelProjectProblems

    """
    class Error(Enum):
        no_gaps_between_sop_eop_volume = 1
        each_vol_has_price = 2
        no_gaps_between_sop_eop_price = 3
        each_price_has_vol = 4
        price_dif_between_year_not_more_than_15_procent = 4
    """

    projectsVolPrice = ProjectVolumePrices.objects.filter(project_id=p_id)
    errorDic = {
        HighLevelProjectProblems.no_gaps_between_sop_eop_volume: True,
        HighLevelProjectProblems.each_vol_has_price: True,
        HighLevelProjectProblems.no_gaps_between_sop_eop_price: True,
        HighLevelProjectProblems.each_price_has_vol: True,
        HighLevelProjectProblems.price_dif_between_year_not_more_than_15_procent: True,
    }

    # first check and second:gaps_between_sop_eop_volume & each_vol_has_price

    # list of each year with an entry
    years_vol = []
    for pVolPrice in projectsVolPrice:
        if pVolPrice.quantity != 0:
            years_vol.append(pVolPrice.calenderYear)
            if pVolPrice.price == 0:
                errorDic[HighLevelProjectProblems.each_vol_has_price] = False
    # print(years_vol)

    if len(years_vol) > 0:
        # check if from smallest to largest year, if there is a missing year
        sop_vol = min(years_vol)
        eop_vol = max(years_vol)
        for i in list(range(sop_vol, eop_vol + 1)):
            if i not in years_vol:
                errorDic[
                    HighLevelProjectProblems.no_gaps_between_sop_eop_volume
                ] = False

    # third check and forth: gaps_between_sop_eop_price & each_price_has_vol

    # list of each year with an entry
    years_price = []
    price_list = []

    #print("project vol price -->", projectsVolPrice)
    #print("project vol price count", projectsVolPrice.count())
    for pVolPrice in projectsVolPrice:
        if pVolPrice.price != 0:
            years_price.append(pVolPrice.calenderYear)
            price_list.append(pVolPrice.price)
            if pVolPrice.quantity == 0:
                errorDic[HighLevelProjectProblems.each_price_has_vol] = False
    # print(years_price)
    # print(price_list)

    # check if from smallest to largest year, if there is a missing year
    if len(years_price) > 0:
        sop_price = min(years_price)
        eop_price = max(years_price)
        for i in list(range(sop_price, eop_price + 1)):
            if i not in years_price:
                errorDic[HighLevelProjectProblems.no_gaps_between_sop_eop_price] = False

    # fifth check: price_dif_between_year_not_more_than_15_procent

    d = {"year": years_price, "price": price_list}
    df_price = pd.DataFrame(data=d)

    df_sorted = df_price.sort_values(by=["year"])
    price_values = df_sorted["price"].tolist()
    # print(price_values)
    for idx, price_value in enumerate(price_values):
        if idx == 0:
            continue

        if (
            price_value > float(price_values[idx - 1]) * 1.15
            or price_value < float(price_values[idx - 1]) * 0.85
        ):
            errorDic[
                HighLevelProjectProblems.price_dif_between_year_not_more_than_15_procent
            ] = False

    return errorDic


"""
projectVolumePrices:
calenderYear
quantity
quantityCustomerEstimation
source
data
user #foreign key
modifiedDate
project #foreign key
valid
priceSource
comment
currency
price
priceValidityUntil
priceSourceComment
"""


# reqs,59,61,101
def errorDicTableLvl(p_id, helperObjects):
    from project.helperFunctions import HighLevelProjectProblems

    """
    class Error(Enum):
        no_price_over_15_procent_over_family_average = 1
        no_price_over_30_procent_over_RFP_average = 2
        same_main_end_customer_RFP_and_same_price = 3
    """
    errorDic = {
        HighLevelProjectProblems.price_over_15_procent_over_family_average: False,
        HighLevelProjectProblems.price_over_30_procent_over_RFP_average: False,
        HighLevelProjectProblems.same_main_end_customer_RFP_and_same_price_avg: False,
        HighLevelProjectProblems.same_main_end_customer_RFP_and_same_price_yearly: False,
        HighLevelProjectProblems.price_over_15_procent_over_family_average_year: False
    }

    projects = None
    projectVolumePricesObjects = None

    if helperObjects == None:
        projects = Project.objects.all()
        projectVolumePricesObjects = ProjectVolumePrices.objects.select_related()
    else:
        projects = helperObjects[0]
        projectVolumePricesObjects = helperObjects[2]

    # get a list of all projectsVolPRice with the same series (first seven characters in SalesName are the same)
    needed_project = projects.get(id=p_id)

    projectsVolPrice_family = []
    family = needed_project.sales_name.rfp.familyHelper

    """
    # get projects with the same silicon
    filter_string_silicon = str(needed_project.sales_name)[:8]

    SalesNameSilicon = SalesName.objects.filter(
        salesName__icontains=filter_string_silicon)
    salesname_ids_silicon = SalesNameSilicon.values_list('id', flat=True)
    projectSilicon = []
    for salesname in salesname_ids_silicon:
        for element in Project.objects.filter(salesName_id=salesname):
            #print("element:", element.id)
            projectSilicon.append(element.id)

    """

    projectFamily = []
    meanPriceFamilyLevel = 0.0
    projectsWithSameFamily = Project.objects.select_related().filter(
        sales_name__rfp__familyHelper=family).exclude(id=needed_project.id)

    thisProjectPrices = (
        ProjectVolumePrices.objects.select_related()
        .filter(project_id=needed_project.id)
        .exclude(price=0.0)
    )

    # price list at this project level
    # prices have always to be casted to float
    thisProjectPricesArray = []
    for price in thisProjectPrices:
        thisProjectPricesArray.append(float(price.price))

    # no_price_over_15_procent_over_family_average
    if projectsWithSameFamily.count() > 0:

        # get the non zero prices of projects with the same family
        price_list_family = []
        similarProjectPrices = (
            ProjectVolumePrices.objects.filter(
                project__in=projectsWithSameFamily)
            .exclude(price=0.0)
            .values_list("price", flat=True)
        )
        for price in similarProjectPrices:
            price_list_family.append(float(price))

        if len(price_list_family) > 0:
            meanPriceFamilyLevel = float(mean(price_list_family))

            for price in thisProjectPricesArray:
                if (
                    price > meanPriceFamilyLevel * 1.15
                    or price < meanPriceFamilyLevel * 0.85
                ):
                    errorDic[
                        HighLevelProjectProblems.price_over_15_procent_over_family_average
                    ] = True

        # now repeat at yearly level

        similarProjectPricesObj = (
            ProjectVolumePrices.objects.select_related()
            .filter(project__in=projectsWithSameFamily)
            .exclude(price=0.0)
        )
        calenderYears = thisProjectPrices.values_list(
            "calenderYear", flat=True)
        thisYearRelevantProjects = similarProjectPricesObj.filter(
            calenderYear__in=calenderYears
        ).values_list("price", flat=True)

        if thisYearRelevantProjects.count() > 0:
            helperArray = []

            for price in thisYearRelevantProjects:
                helperArray.append(float(price))

            if len(helperArray) > 0:

                meanPrice = mean(helperArray)

                for price in thisYearRelevantProjects:
                    if (float(price) > meanPrice * 1.15) or (
                        float(price) < meanPrice * 0.85
                    ):
                        errorDic[
                            HighLevelProjectProblems.price_over_15_procent_over_family_average_year
                        ] = True
    else:
        print("no other projectsWithSameFamily, cannot price_over_15_procent_over_family_average_year nor price_over_15_procent_over_family_average")

    #################################
    # no_price_over_30_procent_over_RFP_average   (or under 30pct)
    # all projects with same rfp, excluding the analyzed project.

    projects_rfp = (
        projects.select_related()
        .filter(sales_name__rfp=needed_project.sales_name.rfp)
        .exclude(id=needed_project.id)
    )

    meanPriceRfpLevel: float = 0.0

    if projects_rfp.count() > 0:
        """
        get the prices for this RFP where the price values are not 0
        use the list of projects with the same rfp in order to retrieve each project's average price. (unweighted)
        if the price is not 0.0, it's appended to price_list_rfp.
        then, the average over all projects is built (unweighted).
        using this average, unweighted figure, the current analyzed project is evaluated. if deviation is above the predetermined values, an error is output.

        """
        try:
            meanPriceRfpLevel = float(
                (
                    projectVolumePricesObjects.filter(project__in=projects_rfp)
                    .exclude(price=0.0)
                    .aggregate(Avg("price"))
                    .get("price__avg", 0.0)
                )
            )
        except:
            pass

        for price in thisProjectPrices:
            if (
                (float(price.price) > (meanPriceRfpLevel * 1.30))
                or (float(price.price) < (meanPriceRfpLevel * 0.70))
            ) & (meanPriceRfpLevel != 0.0):
                errorDic[
                    HighLevelProjectProblems.price_over_30_procent_over_RFP_average
                ] = True

    else:
        print(
            "no other projects with same rfp... cannot price_over_30_procent_over_RFP_average"
        )

    if meanPriceRfpLevel == 0.0:
        HighLevelProjectProblems.pricesAreZero

    #####################################
    """
    same_main_end_customer_RFP_and_same_price, deviation of average over 1 pct
    """
    projects_same_customers_and_rfp = projects.filter(
        sales_name__rfp=needed_project.sales_name.rfp,
        mainCustomer=needed_project.mainCustomer,
        finalCustomer=needed_project.finalCustomer,
    ).exclude(id=needed_project.id)

    project_ids_same = projects_same_customers_and_rfp.values_list(
        "id", flat=True)

    projectsVolPrice_same = projectVolumePricesObjects.filter(
        project_id__in=project_ids_same
    ).exclude(price=0.0)

    if projects_same_customers_and_rfp.count() > 0:
        """
        get the prices for the projects that have the same rfp, end customer and main customer
        TODO: replace by raw sql statement? does this bring a performance impovemnet at all?
        """
        try:
            meanPrice = float(
                projectsVolPrice_same.aggregate(
                    Avg("price")).get("price__avg", 0.0)
            )

            if thisProjectPrices.count() > 0:
                for price in thisProjectPrices:
                    if (float(price.price) > (meanPriceRfpLevel * 1.01)) or (
                        float(price.price) < (meanPriceRfpLevel * 0.99)
                    ):
                        errorDic[
                            HighLevelProjectProblems.same_main_end_customer_RFP_and_same_price_avg
                        ] = True
        except:
            pass
    print("aaa")
    ################################
    # same_main_end_customer_RFP_and_same_price, deviation of absolute value at yearly level
    try:
        if thisProjectPrices.count() > 0:
            if projects_same_customers_and_rfp.count() > 0:

                for thisProject in thisProjectPrices:
                    thisYear = thisProject.calenderYear
                    thisYearsPrice = float(thisProject.price)
                    thisYearAveragePriceArray = []
                    """
                    now get all projects that have same rfp, main and end customer
                    for each year where our current price is not 0, try to find a corresponding value and append to the years' array for building the average.
                    """

                    sameRfpCustomerSameYearProjectsPrices = projectsVolPrice_same.filter(
                        calenderYear=thisYear
                    )

                    if sameRfpCustomerSameYearProjectsPrices.count() > 0:
                        for proj in sameRfpCustomerSameYearProjectsPrices:
                            thisYearAveragePriceArray.append(float(proj.price))

                        meanPrice = float(mean(thisYearAveragePriceArray))

                        if (
                            thisYearsPrice > meanPrice * 1.01
                            or thisYearsPrice < meanPrice * 0.99
                        ):
                            errorDic[
                                HighLevelProjectProblems.same_main_end_customer_RFP_and_same_price_yearly
                            ] = True
                        print("this years price", thisYearsPrice,
                              "mean price", meanPrice)
            else:
                print(
                    "no projects_same_customers_and_rfp, cannot same_main_end_customer_RFP_and_same_price_yearly"
                )
    except:
        pass
    print("bb")
    return errorDic, meanPriceRfpLevel, meanPriceFamilyLevel


def checkBoUpEntryGapsVol(df):
    dfFilteredVol = df.loc[df["vol"] != 0]
    groups = dfFilteredVol["id"].unique()
    check_list = []
    for group in groups:
        dfVolGroup = dfFilteredVol.loc[dfFilteredVol["id"] == group]
        check = True
        sop = min(dfVolGroup.year)
        eop = max(dfVolGroup.year)
        for i in list(range(sop, eop + 1)):
            if i not in set(dfVolGroup.year):
                check = False
        check_list.append((group, check))
    print(check_list)
    return check_list


def checkBoUpEntryGapsPrice(df):
    dfFilteredPrice = df.loc[df["price"] != 0]
    groups = dfFilteredPrice["id"].unique()
    check_list = []
    for group in groups:
        dfPriceGroup = dfFilteredPrice.loc[dfFilteredPrice["id"] == group]
        check = True
        sop = min(dfPriceGroup.year)
        eop = max(dfPriceGroup.year)
        for i in list(range(sop, eop + 1)):
            if i not in set(dfPriceGroup.year):
                # print("problem row", i )
                check = False
        check_list.append((group, check))
        # print("years of group just done", dfPriceGroup.year, "project_id", group)
    # print(check_list)
    return check_list
