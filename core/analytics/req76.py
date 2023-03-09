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

def req76right(total_df): #same customer, same faimly, different prices  Values: silicon or package level, different customers.  Y: ASP in EUR, X: year.

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
    for index, row in keyDf.iterrows():
        #print(row['gen'], row['series'],row['package'],row['endCustomer_id'])

        valueQuery = "                              \
        SELECT                                      \
        year, vhk, SUM(wRev) as CY_wRev, SUM(wVol) as CY_wVol, SUM(gm) as CY_gm, SUM(fy_wRev) as FY_wRev, SUM(fy_wVol) as FY_wVol, SUM(fy_gm) as FY_gm  \
        FROM                                        \
        total_df                                    \
        WHERE                                       \
        wRev != 0 and gm != 0 and gen = '" + str(row['gen']) + "' and series = '" + str(row['series']) + "'and package = '" + str(row['package']) + "' and endCustomer_id = " + str(row['endCustomer_id']) + " \
        GROUP BY                                    \
        gen, series, package, endCustomer_id, year  \
        ;                                           \
        "
        valueDf = ps.sqldf(valueQuery, locals())

        yearList = valueDf['year'].tolist()
        vhkList = valueDf['vhk'].tolist()
        CYwrevList = valueDf['CY_wRev'].tolist()
        CYwVolList = valueDf['CY_wVol'].tolist()
        CYgmList = valueDf['CY_gm'].tolist()
        FYwrevList = valueDf['FY_wRev'].tolist()
        FYwVolList = valueDf['FY_wVol'].tolist()
        FYgmList = valueDf['FY_gm'].tolist()
        jsonElement = {'gen':row['gen'], 'series':row['series'],'package':row['package'], 'endCustomer_id':row['endCustomer_id'], 'year':yearList, 'vhk':vhkList, 'CYRev':CYwrevList, 'CYwVol':CYwVolList, 'CYgm':CYgmList, 'FYRev':FYwrevList, 'FYwVol':FYwVolList, 'FYgm':FYgmList}

        jsonResult[str(index)]=jsonElement

    return jsonResult

def req76lefttop(total_df): #same customer, same faimly, different prices  Values: silicon or package level, different customers.  Y: ASP in EUR, X: year.

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
    for index, row in keyDf.iterrows():
        #print(row['gen'], row['series'],row['package'],row['endCustomer_id'])

        valueQuery = "                              \
        SELECT                                      \
        year, SUM(wRev) as CY_wRevSum, SUM(wVol) as CY_wVolSum, SUM(fy_wRev) as FY_wRevSum, SUM(fy_wVol) as FY_wVolSum             \
        FROM                                        \
        total_df                                    \
        WHERE                                       \
        price != 0 and gen = '" + str(row['gen']) + "' and series = '" + str(row['series']) + "' and package = '" + str(row['package']) + "' and endCustomer_id = " + str(row['endCustomer_id']) + " \
        GROUP BY                                    \
        gen, series, package, endCustomer_id, year  \
        ;                                           \
        "
        valueDf = ps.sqldf(valueQuery, locals())
        yearList = valueDf['year'].tolist()
        CYwVolList = valueDf['CY_wVolSum'].tolist()
        CYwRevList = valueDf['CY_wRevSum'].tolist()
        FYwVolList = valueDf['FY_wVolSum'].tolist()
        FYwRevList = valueDf['FY_wRevSum'].tolist()

        CYaspList = []
        for i in range(0, (len(CYwRevList)), 1):            
            wVol = float(CYwVolList[i])
            wRev = CYwRevList[i]
            asp = 0.0

            try:
                asp = wRev / wVol
            except:
                pass

            CYaspList.append(asp)

        FYaspList = []
        for i in range(0, (len(FYwRevList)), 1):            
            wVol = float(FYwVolList[i])
            wRev = FYwRevList[i]
            asp = 0.0

            try:
                asp = wRev / wVol
            except:
                pass

            FYaspList.append(asp)

        jsonElement = {'gen':row['gen'], 'series':row['series'], 'package':row['package'], 'endCustomer_id':row['endCustomer_id'], 'endCustomerHelper':row['endCustomerHelper'], 'year':yearList, 'CYasp':CYaspList, 'FYasp': FYaspList}

        jsonResult[str(index)]=jsonElement

    return jsonResult

def req76leftbottom(total_df): #same customer, same faimly, different prices  Values: silicon or package level, different customers.  Y: ASP in EUR, X: year.

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
    for index, row in keyDf.iterrows():
        #print(row['gen'], row['series'],row['package'],row['endCustomer_id'])

        valueQuery = "                              \
        SELECT                                      \
        year, SUM(vhk) as sum_vhk               \
        FROM                                        \
        total_df                                    \
        WHERE                                       \
        vhk != 0 and gen = '" + str(row['gen']) + "' and series = '" + str(row['series']) + "'and package = '" + str(row['package']) + "' and endCustomer_id = " + str(row['endCustomer_id']) + " \
        GROUP BY                                    \
        gen, series, package, endCustomer_id, year  \
        ;                                           \
        "
        valueDf = ps.sqldf(valueQuery, locals())
        yearList = valueDf['year'].tolist()
        vhkList = valueDf['sum_vhk'].tolist()
        jsonElement = {'gen':row['gen'], 'series':row['series'],'package':row['package'], 'endCustomer_id':row['endCustomer_id'], 'endCustomerHelper':row['endCustomerHelper'], 'year':yearList, 'wVol':vhkList}

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



class KPIDashboard4(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def get(self, request):
        print("getting KPI Dashboard4")

        ###
        total_df = restructure_whole()
        right = req76right(total_df)
        lefttop = req76lefttop(total_df)
        leftbottom = req76leftbottom(total_df)
        filterJson = basicFilter()
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print("getting json",lefttop, right)
        return JsonResponse({"req76_data_right": right, "req76_data_lefttop": lefttop, "req76_data_leftbottom":leftbottom, "filter":filterJson}, safe=True)


#print(req73(restructure_whole(pd.read_excel('BoUp.xlsx'))))
