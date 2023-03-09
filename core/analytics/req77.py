import pandas as pd
import pandasql as ps
from productMarketing.queryJobs.SQL_query import *

from core.project.models import *
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from django.contrib.auth.decorators import login_required

from core.project.helperFunctions import *

import json

def req77(total_df): #same customer, same faimly, different prices  Values: silicon or package level, different customers.  Y: ASP in EUR, X: year.

    keyQuery = """
    SELECT
    gen, series, package, endCustomer_id, endCustomerHelper
    FROM
    total_df
    GROUP BY
    gen, series, package, endCustomer_id
    ;
    """

    keyDf = ps.sqldf(keyQuery, locals())
    keyDf = keyDf.reset_index()


    jsonResult = {}
    for index, row in keyDf.iterrows(): #count /45 because for each project we have 45 entries (45 years)
        #print(row['gen'], row['series'],row['package'],row['endCustomer_id'])

        valueQuery = "                              \
        SELECT                                      \
        year, COUNT(*) / 45 as project_count, vhk, SUM(wRev) as CY_wRev, SUM(wVol) as CY_wVol, SUM(gm) as CY_gm, MIN(gm) as CYmin_gm, MAX(gm) as CYmax_gm, SUM(fy_wRev) as FY_wRev, SUM(fy_wVol) as FY_wVol, SUM(fy_gm) as FY_gm, MIN(fy_gm) as FYmin_gm, MAX(fy_gm) as FYmax_gm              \
        FROM                                        \
        total_df                                    \
        WHERE                                       \
        gm != 0 and gen = '" + str(row['gen']) + "' and series = '" + str(row['series']) + "'and package = '" + str(row['package']) + "' and endCustomer_id = " + str(row['endCustomer_id']) + " \
        GROUP BY                                    \
        gen, series, package, endCustomer_id, year  \
        ;                                           \
        "
        valueDf = ps.sqldf(valueQuery, locals())
        yearList = valueDf['year'].tolist()
        projectList = valueDf['project_count'].tolist()
        vhkList = valueDf['vhk'].tolist()
        CYwrevList = valueDf['CY_wRev'].tolist()
        CYwVolList = valueDf['CY_wVol'].tolist()
        CYgmList = valueDf['CY_gm'].tolist()
        FYwrevList = valueDf['FY_wRev'].tolist()
        FYwVolList = valueDf['FY_wVol'].tolist()
        FYgmList = valueDf['FY_gm'].tolist()
        CYminGmList = valueDf['CYmin_gm'].tolist()
        CYmaxGmList = valueDf['CYmax_gm'].tolist()
        FYminGmList = valueDf['FYmin_gm'].tolist()
        FYmaxGmList = valueDf['FYmax_gm'].tolist()
        jsonElement = {'gen':row['gen'], 'series':row['series'],'package':row['package'], 'endCustomerHelper':row['endCustomerHelper'], 'endCustomer_id':row['endCustomer_id'], 'year':yearList, 'projectCount':projectList, 'vhk':vhkList, 'CYRev':CYwrevList, 'CYwVol':CYwVolList, 'CYgm':CYgmList, 'CYpmin_gm': CYminGmList, 'CYpmax_gm':CYmaxGmList, 'FYRev':FYwrevList, 'FYwVol':FYwVolList, 'FYgm':FYgmList, 'FYpmin_gm': FYminGmList, 'FYpmax_gm':FYmaxGmList}

        jsonResult[str(index)]=jsonElement

    return jsonResult

def basicFilter(): #same customer, same faimly, different prices  Values: silicon or package level, different customers.  Y: ASP in EUR, X: year.

    FinalCustomer = FinalCustomers.objects.all()
    allFinalCustomer = [(-1,"fieldMissing")]
    for item in FinalCustomer:
        if item.finalCustomerName not in allFinalCustomer:
            id = FinalCustomers.objects.filter(finalCustomerName=item.finalCustomerName).values('id')[0]['id']
            allFinalCustomer.append((id, item.finalCustomerName))

    ProductFam = ProductFamily.objects.all()
    allProductFamily = ["fieldMissing"]
    for item in ProductFam:
        if item.family_name not in allProductFamily:
            allProductFamily.append(item.family_name)

    ProductSerie = ProductSeries.objects.all()
    allProductSeries = ["fieldMissing"]
    for item in ProductSerie:
        if item.series not in allProductSeries:
            allProductSeries.append(item.series)

    ProductPack = ProductPackage.objects.all()
    allProductPackage = ["fieldMissing"]
    for item in ProductPack:
        if item.package not in allProductPackage:
            allProductPackage.append(item.package)

    jsonDic = {'finalCustomer': allFinalCustomer, 'family': allProductFamily, 'series': allProductSeries, 'package': allProductPackage}

    CurrencyExRates = ExchangeRates.objects.filter(currency_id = 1, valid = 1)
    #print(CurrencyExRates)
    if CurrencyExRates: #if entries exists
        jsonDic["currencyRate"] = CurrencyExRates[0].rate
        #print(CurrencyExRates[0].rate)
    else:
        jsonDic["currencyRate"] = 1.0

    return jsonDic


class KPIDashboard5(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def get(self, request):
        print("getting KPI Dashboard5")

        ###
        total_df = restructure_whole()
        json = req77(total_df)
        filterJson = basicFilter()

        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print("getting json",json)
        return JsonResponse({"req77_data": json, "filter":filterJson}, safe=True)


#print(req73(restructure_whole(pd.read_excel('BoUp.xlsx'))))
