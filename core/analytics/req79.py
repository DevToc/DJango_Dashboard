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
import datetime

import json

def req79(total_df,this_year): #same customer, same faimly, different prices  Values: silicon or package level, different customers.  Y: ASP in EUR, X: year.

    keyQuery = """
    SELECT
    series, endCustomer_id, endCustomerHelper
    FROM
    total_df
    GROUP BY
    series, endCustomer_id
    ;
    """

    keyDf = ps.sqldf(keyQuery, locals())
    keyDf = keyDf.reset_index()


    jsonResult = {}
    for index, row in keyDf.iterrows(): #count /45 because for each project we have 45 entries (45 years)
        #print(row['series'],row['endCustomer_id'])
        end_5year = str(int(this_year) + 5)
        end_10year = str(int(this_year) + 10)
        end_20year = str(int(this_year) + 20)
        valueQuery = "                                  \
        SELECT *           \
        FROM(                                           \
            SELECT                                      \
            series, endCustomer_id, SUM(gm) as CYgm , SUM(wVol) as CYwvol, SUM(fy_gm) as FYgm , SUM(fy_wVol) as FYwvol, SUM(wRev) as CY_wRev, SUM(fy_wRev) as FY_wRev     \
            FROM                                        \
            total_df                                    \
            WHERE                                       \
            year >=" + this_year + " and year <= " + end_5year + " and series = '" + str(row['series']) + "'and endCustomer_id = " + str(row['endCustomer_id']) + " \
            GROUP BY                                    \
            series, endCustomer_id                      \
            )                                          \
        UNION ALL                                         \
        SELECT *                                       \
        FROM(                                           \
            SELECT                                      \
            series, endCustomer_id, SUM(gm) as CYgm , SUM(wVol) as CYwvol, SUM(fy_gm) as FYgm , SUM(fy_wVol) as FYwvol, SUM(wRev) as CY_wRev, SUM(fy_wRev) as FY_wRev     \
            FROM                                        \
            total_df                                    \
            WHERE                                       \
            year >=" + this_year + " and year <= " + end_10year + " and series = '" + str(row['series']) + "'and endCustomer_id = " + str(row['endCustomer_id']) + "\
            GROUP BY  series, endCustomer_id )       \
        UNION ALL                                     \
        SELECT *                                       \
        FROM(                                           \
            SELECT                                      \
            series, endCustomer_id, SUM(gm) as CYgm , SUM(wVol) as CYwvol, SUM(fy_gm) as FYgm , SUM(fy_wVol) as FYwvol, SUM(wRev) as CY_wRev, SUM(fy_wRev) as FY_wRev     \
            FROM                                        \
            total_df                                    \
            WHERE                                       \
            year >=" + this_year + " and year <= " + end_20year + " and series = '" + str(row['series']) + "'and endCustomer_id = " + str(row['endCustomer_id']) + "\
            GROUP BY series, endCustomer_id )        \
        ;                                           \
        "
        valueDf = ps.sqldf(valueQuery, locals())
        yearIntervalls = [5,10,20]
        CYgmList = valueDf['CYgm'].tolist()
        CYvolList = valueDf['CYwvol'].tolist()
        FYgmList = valueDf['FYgm'].tolist()
        FYvolList = valueDf['FYwvol'].tolist()
        CYwrevList = valueDf['CY_wRev'].tolist()
        FYwrevList = valueDf['FY_wRev'].tolist()
        jsonElement = {'series':row['series'],'endCustomer_id':row['endCustomer_id'], 'endCustomerHelper':row['endCustomerHelper'], 'yearIntervall':yearIntervalls, 'CYgm5_10_20':CYgmList, 'CYvol5_10_20': CYvolList, 'FYgm5_10_20':FYgmList, 'FYvol5_10_20': FYvolList, 'CYRev5_10_20':CYwrevList, 'FYRev5_10_20':FYwrevList}

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


class KPIDashboard7(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def get(self, request):
        print("getting KPI Dashboard7")

        ###
        today = datetime.date.today()
        year = today.strftime("%Y")

        total_df = restructure_whole()
        json = req79(total_df,year)
        filterJson = basicFilter()

        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print("getting json",json)
        return JsonResponse({"req79_data": json, "filter":filterJson}, safe=True)


#print(req73(restructure_whole(pd.read_excel('BoUp.xlsx'))))
