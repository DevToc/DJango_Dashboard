from productMarketing.queryJobs.SQL_query import *
from core.project.models import *
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
import datetime
#import pandasql as ps
#import duckdb
import math
import numpy as np
from currencies.models import Currency

"""
new set of dashboards (req 106, 109, 112, 115)
API endpoint: /productMarketing/ManagerDashboard
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



def Dashboard9(): #year grouping in frontend because too much possibilities

    jsonResult = {}

    valueQuery = "                              \
    SELECT                                      \
    gen, series, package, endCustomer_id, mainCustomer_id,               \
    SUM(wVol2020) as wVol2020, SUM(wVol2021) as wVol2021, SUM(wVol2022) as wVol2022, SUM(wVol2023) as wVol2023, SUM(wVol2024) as wVol2024, SUM(wVol2025) as wVol2025, SUM(wVol2026) as wVol2026, SUM(wVol2027) as wVol2027, SUM(wVol2028) as wVol2028, SUM(wVol2029) as wVol2029, SUM(wVol2030) as wVol2030, SUM(wVol2031) as wVol2031, SUM(wVol2032) as wVol2032, SUM(wVol2033) as wVol2033, SUM(wVol2034) as wVol2034, SUM(wVol2035) as wVol2035, SUM(wVol2036) as wVol2036, SUM(wVol2037) as wVol2037, SUM(wVol2038) as wVol2038, SUM(wVol2039) as wVol2039, SUM(wVol2040) as wVol2040, SUM(wVol2041) as wVol2041, SUM(wVol2042) as wVol2042, SUM(wVol2043) as wVol2043, SUM(wVol2044) as wVol2044, SUM(wVol2045) as wVol2045, SUM(wVol2046) as wVol2046, SUM(wVol2047) as wVol2047, SUM(wVol2048) as wVol2048, SUM(wVol2049) as wVol2049, \
    SUM(fy_wVol2020) as FY_wVol2020, SUM(fy_wVol2021) as FY_wVol2021, SUM(fy_wVol2022) as FY_wVol2022, SUM(fy_wVol2023) as FY_wVol2023, SUM(fy_wVol2024) as FY_wVol2024, SUM(fy_wVol2025) as FY_wVol2025, SUM(fy_wVol2026) as FY_wVol2026, SUM(fy_wVol2027) as FY_wVol2027, SUM(fy_wVol2028) as FY_wVol2028, SUM(fy_wVol2029) as FY_wVol2029, SUM(fy_wVol2030) as FY_wVol2030, SUM(fy_wVol2031) as FY_wVol2031, SUM(fy_wVol2032) as FY_wVol2032, SUM(fy_wVol2033) as FY_wVol2033, SUM(fy_wVol2034) as FY_wVol2034, SUM(fy_wVol2035) as FY_wVol2035, SUM(fy_wVol2036) as FY_wVol2036, SUM(fy_wVol2037) as FY_wVol2037, SUM(fy_wVol2038) as FY_wVol2038, SUM(fy_wVol2039) as FY_wVol2039, SUM(fy_wVol2040) as FY_wVol2040, SUM(fy_wVol2041) as FY_wVol2041, SUM(fy_wVol2042) as FY_wVol2042, SUM(fy_wVol2043) as FY_wVol2043, SUM(fy_wVol2044) as FY_wVol2044, SUM(fy_wVol2045) as FY_wVol2045, SUM(fy_wVol2046) as FY_wVol2046, SUM(fy_wVol2047) as FY_wVol2047, SUM(fy_wVol2048) as FY_wVol2048, SUM(fy_wVol2049) as FY_wVol2049, \
    SUM(wRev2020) as wRev2020, SUM(wRev2021) as wRev2021, SUM(wRev2022) as wRev2022, SUM(wRev2023) as wRev2023, SUM(wRev2024) as wRev2024, SUM(wRev2025) as wRev2025, SUM(wRev2026) as wRev2026, SUM(wRev2027) as wRev2027, SUM(wRev2028) as wRev2028, SUM(wRev2029) as wRev2029, SUM(wRev2030) as wRev2030, SUM(wRev2031) as wRev2031, SUM(wRev2032) as wRev2032, SUM(wRev2033) as wRev2033, SUM(wRev2034) as wRev2034, SUM(wRev2035) as wRev2035, SUM(wRev2036) as wRev2036, SUM(wRev2037) as wRev2037, SUM(wRev2038) as wRev2038, SUM(wRev2039) as wRev2039, SUM(wRev2040) as wRev2040, SUM(wRev2041) as wRev2041, SUM(wRev2042) as wRev2042, SUM(wRev2043) as wRev2043, SUM(wRev2044) as wRev2044, SUM(wRev2045) as wRev2045, SUM(wRev2046) as wRev2046, SUM(wRev2047) as wRev2047, SUM(wRev2048) as wRev2048, SUM(wRev2049) as wRev2049, \
    SUM(fy_wRev2020) as FY_wRev2020, SUM(fy_wRev2021) as FY_wRev2021, SUM(fy_wRev2022) as FY_wRev2022, SUM(fy_wRev2023) as FY_wRev2023, SUM(fy_wRev2024) as FY_wRev2024, SUM(fy_wRev2025) as FY_wRev2025, SUM(fy_wRev2026) as FY_wRev2026, SUM(fy_wRev2027) as FY_wRev2027, SUM(fy_wRev2028) as FY_wRev2028, SUM(fy_wRev2029) as FY_wRev2029, SUM(fy_wRev2030) as FY_wRev2030, SUM(fy_wRev2031) as FY_wRev2031, SUM(fy_wRev2032) as FY_wRev2032, SUM(fy_wRev2033) as FY_wRev2033, SUM(fy_wRev2034) as FY_wRev2034, SUM(fy_wRev2035) as FY_wRev2035, SUM(fy_wRev2036) as FY_wRev2036, SUM(fy_wRev2037) as FY_wRev2037, SUM(fy_wRev2038) as FY_wRev2038, SUM(fy_wRev2039) as FY_wRev2039, SUM(fy_wRev2040) as FY_wRev2040, SUM(fy_wRev2041) as FY_wRev2041, SUM(fy_wRev2042) as FY_wRev2042, SUM(fy_wRev2043) as FY_wRev2043, SUM(fy_wRev2044) as FY_wRev2044,SUM(fy_wRev2045) as FY_wRev2045, SUM(fy_wRev2046) as FY_wRev2046, SUM(fy_wRev2047) as FY_wRev2047, SUM(fy_wRev2048) as FY_wRev2048, SUM(fy_wRev2049) as FY_wRev2049, \
    SUM(gm2020) as gm2020, SUM(gm2021) as gm2021, SUM(gm2022) as gm2022, SUM(gm2023) as gm2023, SUM(gm2024) as gm2024, SUM(gm2025) as gm2025, SUM(gm2026) as gm2026, SUM(gm2027) as gm2027, SUM(gm2028) as gm2028, SUM(gm2029) as gm2029, SUM(gm2030) as gm2030, SUM(gm2031) as gm2031, SUM(gm2032) as gm2032, SUM(gm2033) as gm2033, SUM(gm2034) as gm2034, SUM(gm2035) as gm2035, SUM(gm2036) as gm2036, SUM(gm2037) as gm2037, SUM(gm2038) as gm2038, SUM(gm2039) as gm2039, SUM(gm2040) as gm2040, SUM(gm2041) as gm2041, SUM(gm2042) as gm2042, SUM(gm2043) as gm2043, SUM(gm2044) as gm2044, SUM(gm2045) as gm2045, SUM(gm2046) as gm2046, SUM(gm2047) as gm2047, SUM(gm2048) as gm2048, SUM(gm2049) as gm2049, \
    SUM(fy_gm2020) as fy_gm2020, SUM(fy_gm2021) as fy_gm2021, SUM(fy_gm2022) as fy_gm2022, SUM(fy_gm2023) as fy_gm2023, SUM(fy_gm2024) as fy_gm2024, SUM(fy_gm2025) as fy_gm2025, SUM(fy_gm2026) as fy_gm2026, SUM(fy_gm2027) as fy_gm2027, SUM(fy_gm2028) as fy_gm2028, SUM(fy_gm2029) as fy_gm2029, SUM(fy_gm2030) as fy_gm2030, SUM(fy_gm2031) as fy_gm2031, SUM(fy_gm2032) as fy_gm2032, SUM(fy_gm2033) as fy_gm2033, SUM(fy_gm2034) as fy_gm2034, SUM(fy_gm2035) as fy_gm2035, SUM(fy_gm2036) as fy_gm2036, SUM(fy_gm2037) as fy_gm2037, SUM(fy_gm2038) as fy_gm2038, SUM(fy_gm2039) as fy_gm2039, SUM(fy_gm2040) as fy_gm2040, SUM(fy_gm2041) as fy_gm2041, SUM(fy_gm2042) as fy_gm2042, SUM(fy_gm2043) as fy_gm2043, SUM(fy_gm2044) as fy_gm2044, SUM(fy_gm2045) as fy_gm2045, SUM(fy_gm2046) as fy_gm2046, SUM(fy_gm2047) as fy_gm2047, SUM(fy_gm2048) as fy_gm2048, SUM(fy_gm2049) as fy_gm2049, \
    endCustomerHelper, mainCustomerHelper\
    FROM                                        \
    productMarketingDwh_boup                                 \
    GROUP BY                                    \
    gen, series, package, endCustomer_id, mainCustomer_id, endCustomerHelper, mainCustomerHelper  \
    ORDER BY                                    \
    gen, series, package, endCustomer_id, mainCustomer_id, endCustomerHelper, mainCustomerHelper \
    ;                                           \
    "
    #valueDf = duckdb.query(valueQuery).to_df()
    valueDfRaw = rawSqlPerformer(valueQuery)
    valueDf = pd.DataFrame(valueDfRaw)

    #need to make sure, that there are no 0's inserted in the list
    count = 0
    for row in valueDf.values:
        yearList = []
        wVolList = []
        FY_wVolList = []

    count = 0
    for row in valueDf.values:
        yearList = []
        wVolList = []
        FY_wVolList = []
        wRevList = []
        FY_wRevList = []
        gmList = []
        FY_gmList = []
        for i in range(0,30):
            if type(row[5+i]) == type(None):
                row[5+i] = 0.0
            if type(row[35+i]) == type(None):
                row[35+i] = 0.0
            if type(row[65+i]) == type(None):
                row[65+i] = 0.0
            if type(row[95+i]) == type(None):
                row[95+i] = 0.0
            if (row[5+i] != 0 and not math.isnan(row[5+i])) or (row[35+i] != 0 and not math.isnan(row[35+i])) or (row[65+i] != 0 and not math.isnan(row[65+i])) or (row[95+i] != 0 and not math.isnan(row[95+i])):
                yearList.append(str(2020+i))
                wVolList.append(row[5+i])
                FY_wVolList.append(row[35+i])
                wRevList.append(row[65+i])
                FY_wRevList.append(row[95+i])
                gmList.append(row[125+i])
                FY_gmList.append(row[155+i])

        CYaspList = []
        for i in range(0, (len(wVolList)), 1):
            wVol = float(wVolList[i])
            wRev = wRevList[i]
            asp = 0.0

            try:
                asp = wRev / wVol
            except:
                pass

            CYaspList.append(asp)

        FYaspList = []
        for i in range(0, (len(FY_wRevList)), 1):
            FYVol = float(FY_wVolList[i])
            FYRev = FY_wRevList[i]
            asp = 0.0

            try:
                asp = FYRev / FYVol
            except:
                pass

            FYaspList.append(asp)

        jsonElement = {'gen':row[0], 'series':row[1], 'package':row[2], 'endCustomer_id':row[4], 'endCustomerHelper':row[-2], 'mainCustomer_id':row[5], 'mainCustomerHelper':row[-1], 'year':yearList, 'CYwVol':wVolList, 'FYwVol':FY_wVolList, 'CYwRev':wRevList, 'FYwRev':FY_wRevList, 'CYgm':gmList, 'FYgm':FY_gmList, 'CYasp':CYaspList, 'FYasp':FYaspList}

        jsonResult[str(count)]=jsonElement
        count = count +1

    return jsonResult





def Dashboard12(): #and 16

    jsonResult = {}

    valueQuery = "                              \
    SELECT                                      \
    applicationLine,                        \
    SUM(wRev2020) as wRev2020, SUM(wRev2021) as wRev2021, SUM(wRev2022) as wRev2022, SUM(wRev2023) as wRev2023, SUM(wRev2024) as wRev2024, SUM(wRev2025) as wRev2025, SUM(wRev2026) as wRev2026, SUM(wRev2027) as wRev2027, SUM(wRev2028) as wRev2028, SUM(wRev2029) as wRev2029, SUM(wRev2030) as wRev2030, SUM(wRev2031) as wRev2031, SUM(wRev2032) as wRev2032, SUM(wRev2033) as wRev2033, SUM(wRev2034) as wRev2034, SUM(wRev2035) as wRev2035, SUM(wRev2036) as wRev2036, SUM(wRev2037) as wRev2037, SUM(wRev2038) as wRev2038, SUM(wRev2039) as wRev2039, SUM(wRev2040) as wRev2040, SUM(wRev2041) as wRev2041, SUM(wRev2042) as wRev2042, SUM(wRev2043) as wRev2043, SUM(wRev2044) as wRev2044, SUM(wRev2045) as wRev2045, SUM(wRev2046) as wRev2046, SUM(wRev2047) as wRev2047, SUM(wRev2048) as wRev2048, SUM(wRev2049) as wRev2049, \
    SUM(fy_wRev2020) as FY_wRev2020, SUM(fy_wRev2021) as FY_wRev2021, SUM(fy_wRev2022) as FY_wRev2022, SUM(fy_wRev2023) as FY_wRev2023, SUM(fy_wRev2024) as FY_wRev2024, SUM(fy_wRev2025) as FY_wRev2025, SUM(fy_wRev2026) as FY_wRev2026, SUM(fy_wRev2027) as FY_wRev2027, SUM(fy_wRev2028) as FY_wRev2028, SUM(fy_wRev2029) as FY_wRev2029, SUM(fy_wRev2030) as FY_wRev2030, SUM(fy_wRev2031) as FY_wRev2031, SUM(fy_wRev2032) as FY_wRev2032, SUM(fy_wRev2033) as FY_wRev2033, SUM(fy_wRev2034) as FY_wRev2034, SUM(fy_wRev2035) as FY_wRev2035, SUM(fy_wRev2036) as FY_wRev2036, SUM(fy_wRev2037) as FY_wRev2037, SUM(fy_wRev2038) as FY_wRev2038, SUM(fy_wRev2039) as FY_wRev2039, SUM(fy_wRev2040) as FY_wRev2040, SUM(fy_wRev2041) as FY_wRev2041, SUM(fy_wRev2042) as FY_wRev2042, SUM(fy_wRev2043) as FY_wRev2043, SUM(fy_wRev2044) as FY_wRev2044,SUM(fy_wRev2045) as FY_wRev2045, SUM(fy_wRev2046) as FY_wRev2046, SUM(fy_wRev2047) as FY_wRev2047, SUM(fy_wRev2048) as FY_wRev2048, SUM(fy_wRev2049) as FY_wRev2049 \
    FROM                                        \
    productMarketingDwh_boup                                   \
    GROUP BY                                    \
    applicationLine                       \
    ORDER BY    \
    applicationLine  \
    ;                                           \
    "
    #valueDf = duckdb.query(valueQuery).to_df()

    valueDfRaw = rawSqlPerformer(valueQuery)
    valueDf = pd.DataFrame(valueDfRaw)
    #need to make sure, that there are no 0's inserted in the list
    count = 0
    for row in valueDf.values:
        yearList = []
        wRevList = []
        FY_wRevList = []
        #print("row")
        #print(row)
        for i in range(0,30):
            if type(row[1+i]) == type(None):
                row[1+i] = 0.0
            if type(row[31+i]) == type(None):
                row[31+i] = 0.0
            if (row[1+i] != 0 and not math.isnan(row[1+i])) or (row[31+i] != 0 and not math.isnan(row[31+i])) :
                yearList.append(str(2020+i))
                wRevList.append(row[1+i])
                FY_wRevList.append(row[31+i])




        jsonElement = {'applicationLine':row[0], 'year':yearList, 'CYwRev':wRevList, 'FYwRev': FY_wRevList}
        jsonResult[str(count)]=jsonElement
        count = count +1
    return jsonResult


def Dashboard13():

    jsonResult = {}

    valueQuery = "                              \
    SELECT                                      \
    applicationMain_id,                        \
    SUM(wRev2020) as wRev2020, SUM(wRev2021) as wRev2021, SUM(wRev2022) as wRev2022, SUM(wRev2023) as wRev2023, SUM(wRev2024) as wRev2024, SUM(wRev2025) as wRev2025, SUM(wRev2026) as wRev2026, SUM(wRev2027) as wRev2027, SUM(wRev2028) as wRev2028, SUM(wRev2029) as wRev2029, SUM(wRev2030) as wRev2030, SUM(wRev2031) as wRev2031, SUM(wRev2032) as wRev2032, SUM(wRev2033) as wRev2033, SUM(wRev2034) as wRev2034, SUM(wRev2035) as wRev2035, SUM(wRev2036) as wRev2036, SUM(wRev2037) as wRev2037, SUM(wRev2038) as wRev2038, SUM(wRev2039) as wRev2039, SUM(wRev2040) as wRev2040, SUM(wRev2041) as wRev2041, SUM(wRev2042) as wRev2042, SUM(wRev2043) as wRev2043, SUM(wRev2044) as wRev2044, SUM(wRev2045) as wRev2045, SUM(wRev2046) as wRev2046, SUM(wRev2047) as wRev2047, SUM(wRev2048) as wRev2048, SUM(wRev2049) as wRev2049, \
    SUM(fy_wRev2020) as FY_wRev2020, SUM(fy_wRev2021) as FY_wRev2021, SUM(fy_wRev2022) as FY_wRev2022, SUM(fy_wRev2023) as FY_wRev2023, SUM(fy_wRev2024) as FY_wRev2024, SUM(fy_wRev2025) as FY_wRev2025, SUM(fy_wRev2026) as FY_wRev2026, SUM(fy_wRev2027) as FY_wRev2027, SUM(fy_wRev2028) as FY_wRev2028, SUM(fy_wRev2029) as FY_wRev2029, SUM(fy_wRev2030) as FY_wRev2030, SUM(fy_wRev2031) as FY_wRev2031, SUM(fy_wRev2032) as FY_wRev2032, SUM(fy_wRev2033) as FY_wRev2033, SUM(fy_wRev2034) as FY_wRev2034, SUM(fy_wRev2035) as FY_wRev2035, SUM(fy_wRev2036) as FY_wRev2036, SUM(fy_wRev2037) as FY_wRev2037, SUM(fy_wRev2038) as FY_wRev2038, SUM(fy_wRev2039) as FY_wRev2039, SUM(fy_wRev2040) as FY_wRev2040, SUM(fy_wRev2041) as FY_wRev2041, SUM(fy_wRev2042) as FY_wRev2042, SUM(fy_wRev2043) as FY_wRev2043, SUM(fy_wRev2044) as FY_wRev2044,SUM(fy_wRev2045) as FY_wRev2045, SUM(fy_wRev2046) as FY_wRev2046, SUM(fy_wRev2047) as FY_wRev2047, SUM(fy_wRev2048) as FY_wRev2048, SUM(fy_wRev2049) as FY_wRev2049 \
    FROM                                        \
    productMarketingDwh_boup                                   \
    GROUP BY                                    \
    applicationMain_id                       \
    ORDER BY    \
    applicationMain_id  \
    ;                                           \
    "
    #valueDf = duckdb.query(valueQuery).to_df()

    valueDfRaw = rawSqlPerformer(valueQuery)
    valueDf = pd.DataFrame(valueDfRaw)
    #need to make sure, that there are no 0's inserted in the list
    count = 0
    for row in valueDf.values:
        yearList = []
        wRevList = []
        FY_wRevList = []
        #print("row")
        #print(row)
        for i in range(0,30):
            if type(row[1+i]) == type(None):
                row[1+i] = 0.0
            if type(row[31+i]) == type(None):
                row[31+i] = 0.0
            if (row[1+i] != 0 and not math.isnan(row[1+i])) or (row[31+i] != 0 and not math.isnan(row[31+i])) :
                yearList.append(str(2020+i))
                wRevList.append(row[1+i])
                FY_wRevList.append(row[31+i])




        jsonElement = {'applicationMain_id':row[0], 'year':yearList, 'CYwRev':wRevList, 'FYwRev': FY_wRevList}
        jsonResult[str(count)]=jsonElement
        count = count +1
    return jsonResult

def Dashboard15():

    jsonResult = {}

    valueQuery = "                              \
    SELECT                                      \
    applicationMain_id, applicationDetail_id,   \
    SUM(wRev2020) as wRev2020, SUM(wRev2021) as wRev2021, SUM(wRev2022) as wRev2022, SUM(wRev2023) as wRev2023, SUM(wRev2024) as wRev2024, SUM(wRev2025) as wRev2025, SUM(wRev2026) as wRev2026, SUM(wRev2027) as wRev2027, SUM(wRev2028) as wRev2028, SUM(wRev2029) as wRev2029, SUM(wRev2030) as wRev2030, SUM(wRev2031) as wRev2031, SUM(wRev2032) as wRev2032, SUM(wRev2033) as wRev2033, SUM(wRev2034) as wRev2034, SUM(wRev2035) as wRev2035, SUM(wRev2036) as wRev2036, SUM(wRev2037) as wRev2037, SUM(wRev2038) as wRev2038, SUM(wRev2039) as wRev2039, SUM(wRev2040) as wRev2040, SUM(wRev2041) as wRev2041, SUM(wRev2042) as wRev2042, SUM(wRev2043) as wRev2043, SUM(wRev2044) as wRev2044, SUM(wRev2045) as wRev2045, SUM(wRev2046) as wRev2046, SUM(wRev2047) as wRev2047, SUM(wRev2048) as wRev2048, SUM(wRev2049) as wRev2049, \
    SUM(fy_wRev2020) as FY_wRev2020, SUM(fy_wRev2021) as FY_wRev2021, SUM(fy_wRev2022) as FY_wRev2022, SUM(fy_wRev2023) as FY_wRev2023, SUM(fy_wRev2024) as FY_wRev2024, SUM(fy_wRev2025) as FY_wRev2025, SUM(fy_wRev2026) as FY_wRev2026, SUM(fy_wRev2027) as FY_wRev2027, SUM(fy_wRev2028) as FY_wRev2028, SUM(fy_wRev2029) as FY_wRev2029, SUM(fy_wRev2030) as FY_wRev2030, SUM(fy_wRev2031) as FY_wRev2031, SUM(fy_wRev2032) as FY_wRev2032, SUM(fy_wRev2033) as FY_wRev2033, SUM(fy_wRev2034) as FY_wRev2034, SUM(fy_wRev2035) as FY_wRev2035, SUM(fy_wRev2036) as FY_wRev2036, SUM(fy_wRev2037) as FY_wRev2037, SUM(fy_wRev2038) as FY_wRev2038, SUM(fy_wRev2039) as FY_wRev2039, SUM(fy_wRev2040) as FY_wRev2040, SUM(fy_wRev2041) as FY_wRev2041, SUM(fy_wRev2042) as FY_wRev2042, SUM(fy_wRev2043) as FY_wRev2043, SUM(fy_wRev2044) as FY_wRev2044,SUM(fy_wRev2045) as FY_wRev2045, SUM(fy_wRev2046) as FY_wRev2046, SUM(fy_wRev2047) as FY_wRev2047, SUM(fy_wRev2048) as FY_wRev2048, SUM(fy_wRev2049) as FY_wRev2049, \
    SUM(gm2020) as gm2020, SUM(gm2021) as gm2021, SUM(gm2022) as gm2022, SUM(gm2023) as gm2023, SUM(gm2024) as gm2024, SUM(gm2025) as gm2025, SUM(gm2026) as gm2026, SUM(gm2027) as gm2027, SUM(gm2028) as gm2028, SUM(gm2029) as gm2029, SUM(gm2030) as gm2030, SUM(gm2031) as gm2031, SUM(gm2032) as gm2032, SUM(gm2033) as gm2033, SUM(gm2034) as gm2034, SUM(gm2035) as gm2035, SUM(gm2036) as gm2036, SUM(gm2037) as gm2037, SUM(gm2038) as gm2038, SUM(gm2039) as gm2039, SUM(gm2040) as gm2040, SUM(gm2041) as gm2041, SUM(gm2042) as gm2042, SUM(gm2043) as gm2043, SUM(gm2044) as gm2044, SUM(gm2045) as gm2045, SUM(gm2046) as gm2046, SUM(gm2047) as gm2047, SUM(gm2048) as gm2048, SUM(gm2049) as gm2049, \
    SUM(fy_gm2020) as fy_gm2020, SUM(fy_gm2021) as fy_gm2021, SUM(fy_gm2022) as fy_gm2022, SUM(fy_gm2023) as fy_gm2023, SUM(fy_gm2024) as fy_gm2024, SUM(fy_gm2025) as fy_gm2025, SUM(fy_gm2026) as fy_gm2026, SUM(fy_gm2027) as fy_gm2027, SUM(fy_gm2028) as fy_gm2028, SUM(fy_gm2029) as fy_gm2029, SUM(fy_gm2030) as fy_gm2030, SUM(fy_gm2031) as fy_gm2031, SUM(fy_gm2032) as fy_gm2032, SUM(fy_gm2033) as fy_gm2033, SUM(fy_gm2034) as fy_gm2034, SUM(fy_gm2035) as fy_gm2035, SUM(fy_gm2036) as fy_gm2036, SUM(fy_gm2037) as fy_gm2037, SUM(fy_gm2038) as fy_gm2038, SUM(fy_gm2039) as fy_gm2039, SUM(fy_gm2040) as fy_gm2040, SUM(fy_gm2041) as fy_gm2041, SUM(fy_gm2042) as fy_gm2042, SUM(fy_gm2043) as fy_gm2043, SUM(fy_gm2044) as fy_gm2044, SUM(fy_gm2045) as fy_gm2045, SUM(fy_gm2046) as fy_gm2046, SUM(fy_gm2047) as fy_gm2047, SUM(fy_gm2048) as fy_gm2048, SUM(fy_gm2049) as fy_gm2049 \
    FROM                                        \
    productMarketingDwh_boup                    \
    GROUP BY                                    \
    applicationMain_id, applicationDetail_id    \
    ORDER BY                                    \
    applicationMain_id, applicationDetail_id      \
    ;                                           \
    "
    #valueDf = duckdb.query(valueQuery).to_df()

    valueDfRaw = rawSqlPerformer(valueQuery)
    valueDf = pd.DataFrame(valueDfRaw)
    #need to make sure, that there are no 0's inserted in the list
    count = 0
    for row in valueDf.values:
        yearList = []
        wRevList = []
        FY_wRevList = []
        gmList = []
        FY_gmList = []
        #print("row")
        #print(row)
        for i in range(0,30):
            if type(row[2+i]) == type(None):
                row[2+i] = 0.0
            if type(row[32+i]) == type(None):
                row[32+i] = 0.0
            if type(row[62+i]) == type(None):
                row[62+i] = 0.0
            if type(row[92+i]) == type(None):
                row[92+i] = 0.0
            if (row[2+i] != 0 and not math.isnan(row[2+i])) or (row[32+i] != 0 and not math.isnan(row[32+i])) or (row[62+i] != 0 and not math.isnan(row[62+i])) or (row[92+i] != 0 and not math.isnan(row[92+i])):
                yearList.append(str(2020+i))
                wRevList.append(row[2+i])
                FY_wRevList.append(row[32+i])
                gmList.append(row[62+i])
                FY_gmList.append(row[92+i])




        jsonElement = {'applicationMain_id':row[0], 'applicationDetail_id':row[1],'year':yearList, 'CYwRev':wRevList, 'FYwRev': FY_wRevList, 'CYgm':gmList, 'FYgm':FY_gmList}
        jsonResult[str(count)]=jsonElement
        count = count +1
    return jsonResult

def DashboardTBD():

    jsonResult = {}

    valueQuery = "                              \
    SELECT                                      \
    gen, series, package, endCustomer_id, mainCustomer_id,               \
    SUM(wVol2020) as wVol2020, SUM(wVol2021) as wVol2021, SUM(wVol2022) as wVol2022, SUM(wVol2023) as wVol2023, SUM(wVol2024) as wVol2024, SUM(wVol2025) as wVol2025, SUM(wVol2026) as wVol2026, SUM(wVol2027) as wVol2027, SUM(wVol2028) as wVol2028, SUM(wVol2029) as wVol2029, SUM(wVol2030) as wVol2030, SUM(wVol2031) as wVol2031, SUM(wVol2032) as wVol2032, SUM(wVol2033) as wVol2033, SUM(wVol2034) as wVol2034, SUM(wVol2035) as wVol2035, SUM(wVol2036) as wVol2036, SUM(wVol2037) as wVol2037, SUM(wVol2038) as wVol2038, SUM(wVol2039) as wVol2039, SUM(wVol2040) as wVol2040, SUM(wVol2041) as wVol2041, SUM(wVol2042) as wVol2042, SUM(wVol2043) as wVol2043, SUM(wVol2044) as wVol2044, SUM(wVol2045) as wVol2045, SUM(wVol2046) as wVol2046, SUM(wVol2047) as wVol2047, SUM(wVol2048) as wVol2048, SUM(wVol2049) as wVol2049, \
    SUM(fy_wVol2020) as FY_wVol2020, SUM(fy_wVol2021) as FY_wVol2021, SUM(fy_wVol2022) as FY_wVol2022, SUM(fy_wVol2023) as FY_wVol2023, SUM(fy_wVol2024) as FY_wVol2024, SUM(fy_wVol2025) as FY_wVol2025, SUM(fy_wVol2026) as FY_wVol2026, SUM(fy_wVol2027) as FY_wVol2027, SUM(fy_wVol2028) as FY_wVol2028, SUM(fy_wVol2029) as FY_wVol2029, SUM(fy_wVol2030) as FY_wVol2030, SUM(fy_wVol2031) as FY_wVol2031, SUM(fy_wVol2032) as FY_wVol2032, SUM(fy_wVol2033) as FY_wVol2033, SUM(fy_wVol2034) as FY_wVol2034, SUM(fy_wVol2035) as FY_wVol2035, SUM(fy_wVol2036) as FY_wVol2036, SUM(fy_wVol2037) as FY_wVol2037, SUM(fy_wVol2038) as FY_wVol2038, SUM(fy_wVol2039) as FY_wVol2039, SUM(fy_wVol2040) as FY_wVol2040, SUM(fy_wVol2041) as FY_wVol2041, SUM(fy_wVol2042) as FY_wVol2042, SUM(fy_wVol2043) as FY_wVol2043, SUM(fy_wVol2044) as FY_wVol2044, SUM(fy_wVol2045) as FY_wVol2045, SUM(fy_wVol2046) as FY_wVol2046, SUM(fy_wVol2047) as FY_wVol2047, SUM(fy_wVol2048) as FY_wVol2048, SUM(fy_wVol2049) as FY_wVol2049, \
    endCustomerHelper, mainCustomerHelper\
    FROM                                        \
    productMarketingDwh_boup                                 \
    GROUP BY                                    \
    gen, series, package, endCustomer_id, mainCustomer_id, endCustomerHelper, mainCustomerHelper  \
    ORDER BY                                    \
    gen, series, package, endCustomer_id, mainCustomer_id, endCustomerHelper, mainCustomerHelper \
    ;                                           \
    "
    #valueDf = duckdb.query(valueQuery).to_df()
    valueDfRaw = rawSqlPerformer(valueQuery)
    valueDf = pd.DataFrame(valueDfRaw)

    #need to make sure, that there are no 0's inserted in the list
    count = 0
    for row in valueDf.values:
        yearList = []
        wVolList = []
        FY_wVolList = []

    count = 0
    for row in valueDf.values:
        yearList = []
        wVolList = []
        FY_wVolList = []
        for i in range(0,30):
            if (row[5+i] != 0 and not math.isnan(row[5+i])) or (row[35+i] != 0 and not math.isnan(row[35+i])):
                yearList.append(str(2020+i))
                wVolList.append(row[5+i])
                FY_wVolList.append(row[35+i])

        jsonElement = {'gen':row[0], 'series':row[1], 'package':row[2], 'endCustomer_id':row[4], 'endCustomerHelper':row[-2], 'mainCustomer_id':row[5], 'mainCustomerHelper':row[-1], 'year':yearList, 'CYwVol':wVolList, 'FYwVol':FY_wVolList}

        jsonResult[str(count)]=jsonElement
        count = count +1

    return jsonResult


def basicFilter():

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

    """

    1te Linie: EUR - € - 1.0000
    2te Line: USD - $ - 1.0005
    3te Line: JPY - J - 10.0000
    """
    CurrencyExRates = Currency.objects.filter(is_active = 1)
    #print(CurrencyExRates)

    if CurrencyExRates: #if entries exists
        currencies = {}
        for currency in CurrencyExRates:
            currencyName = currency.code
            currencies[currencyName] = currency.factor
            #print(CurrencyExRates[0].rate)

            """
            ...
            currencies: {
                "EUR": 1.0000,
                "USD": 1.0005,
            }
            ....
            """
        jsonDic["currencies"] = currencies
    else:
        jsonDic["currencyRate"] = 1.0

    """
    heute ist das hardcoded -> 1 einzeige
    """

    return jsonDic

import time

class ManagerialDashboardCar(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def get(self, request):

        print("getting Analytics Dashboard")
        # get the start time
        st = time.time()
        ###
        #today = datetime.date.today()
        #year = today.strftime("%Y")

        filterJson = basicFilter()

        TBDnumber = DashboardTBD()
        nine = Dashboard9()
        twelve = Dashboard12()
        thirteen = Dashboard13()
        fiveteen = Dashboard15()
        #sixteen = twelve   #same data

        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        # get the end time
        et = time.time()
        elapsed_time = et - st
        print('Execution time:', elapsed_time, 'seconds')
        return JsonResponse({"TBD":TBDnumber,
                             "nine": nine,
                             "twelve":twelve,
                             "thirteen":thirteen,
                             "sixteen":twelve,
                             "fiveteen":fiveteen,
                             "filter":filterJson
                              }, safe=True)
