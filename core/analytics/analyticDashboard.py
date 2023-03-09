import time
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
this file is the first caroussel for business insights
API end point:  /productMarketing/KPIDashboardCar
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


def Dashboard1Left():

    jsonResult = {}

    valueQuery = "                              \
    SELECT                                      \
    gen, endCustomer_id,                        \
    SUM(wVol2020) as wVol2020, SUM(wVol2021) as wVol2021, SUM(wVol2022) as wVol2022, SUM(wVol2023) as wVol2023, SUM(wVol2024) as wVol2024, SUM(wVol2025) as wVol2025, SUM(wVol2026) as wVol2026, SUM(wVol2027) as wVol2027, SUM(wVol2028) as wVol2028, SUM(wVol2029) as wVol2029, SUM(wVol2030) as wVol2030, SUM(wVol2031) as wVol2031, SUM(wVol2032) as wVol2032, SUM(wVol2033) as wVol2033, SUM(wVol2034) as wVol2034, SUM(wVol2035) as wVol2035, SUM(wVol2036) as wVol2036, SUM(wVol2037) as wVol2037, SUM(wVol2038) as wVol2038, SUM(wVol2039) as wVol2039, SUM(wVol2040) as wVol2040, SUM(wVol2041) as wVol2041, SUM(wVol2042) as wVol2042, SUM(wVol2043) as wVol2043, SUM(wVol2044) as wVol2044, SUM(wVol2045) as wVol2045, SUM(wVol2046) as wVol2046, SUM(wVol2047) as wVol2047, SUM(wVol2048) as wVol2048, SUM(wVol2049) as wVol2049, \
    SUM(wRev2020) as wRev2020, SUM(wRev2021) as wRev2021, SUM(wRev2022) as wRev2022, SUM(wRev2023) as wRev2023, SUM(wRev2024) as wRev2024, SUM(wRev2025) as wRev2025, SUM(wRev2026) as wRev2026, SUM(wRev2027) as wRev2027, SUM(wRev2028) as wRev2028, SUM(wRev2029) as wRev2029, SUM(wRev2030) as wRev2030, SUM(wRev2031) as wRev2031, SUM(wRev2032) as wRev2032, SUM(wRev2033) as wRev2033, SUM(wRev2034) as wRev2034, SUM(wRev2035) as wRev2035, SUM(wRev2036) as wRev2036, SUM(wRev2037) as wRev2037, SUM(wRev2038) as wRev2038, SUM(wRev2039) as wRev2039, SUM(wRev2040) as wRev2040, SUM(wRev2041) as wRev2041, SUM(wRev2042) as wRev2042, SUM(wRev2043) as wRev2043, SUM(wRev2044) as wRev2044, SUM(wRev2045) as wRev2045, SUM(wRev2046) as wRev2046, SUM(wRev2047) as wRev2047, SUM(wRev2048) as wRev2048, SUM(wRev2049) as wRev2049, \
    SUM(fy_wVol2020) as FY_wVol2020, SUM(fy_wVol2021) as FY_wVol2021, SUM(fy_wVol2022) as FY_wVol2022, SUM(fy_wVol2023) as FY_wVol2023, SUM(fy_wVol2024) as FY_wVol2024, SUM(fy_wVol2025) as FY_wVol2025, SUM(fy_wVol2026) as FY_wVol2026, SUM(fy_wVol2027) as FY_wVol2027, SUM(fy_wVol2028) as FY_wVol2028, SUM(fy_wVol2029) as FY_wVol2029, SUM(fy_wVol2030) as FY_wVol2030, SUM(fy_wVol2031) as FY_wVol2031, SUM(fy_wVol2032) as FY_wVol2032, SUM(fy_wVol2033) as FY_wVol2033, SUM(fy_wVol2034) as FY_wVol2034, SUM(fy_wVol2035) as FY_wVol2035, SUM(fy_wVol2036) as FY_wVol2036, SUM(fy_wVol2037) as FY_wVol2037, SUM(fy_wVol2038) as FY_wVol2038, SUM(fy_wVol2039) as FY_wVol2039, SUM(fy_wVol2040) as FY_wVol2040, SUM(fy_wVol2041) as FY_wVol2041, SUM(fy_wVol2042) as FY_wVol2042, SUM(fy_wVol2043) as FY_wVol2043, SUM(fy_wVol2044) as FY_wVol2044, SUM(fy_wVol2045) as FY_wVol2045, SUM(fy_wVol2046) as FY_wVol2046, SUM(fy_wVol2047) as FY_wVol2047, SUM(fy_wVol2048) as FY_wVol2048, SUM(fy_wVol2049) as FY_wVol2049, \
    SUM(fy_wRev2020) as FY_wRev2020, SUM(fy_wRev2021) as FY_wRev2021, SUM(fy_wRev2022) as FY_wRev2022, SUM(fy_wRev2023) as FY_wRev2023, SUM(fy_wRev2024) as FY_wRev2024, SUM(fy_wRev2025) as FY_wRev2025, SUM(fy_wRev2026) as FY_wRev2026, SUM(fy_wRev2027) as FY_wRev2027, SUM(fy_wRev2028) as FY_wRev2028, SUM(fy_wRev2029) as FY_wRev2029, SUM(fy_wRev2030) as FY_wRev2030, SUM(fy_wRev2031) as FY_wRev2031, SUM(fy_wRev2032) as FY_wRev2032, SUM(fy_wRev2033) as FY_wRev2033, SUM(fy_wRev2034) as FY_wRev2034, SUM(fy_wRev2035) as FY_wRev2035, SUM(fy_wRev2036) as FY_wRev2036, SUM(fy_wRev2037) as FY_wRev2037, SUM(fy_wRev2038) as FY_wRev2038, SUM(fy_wRev2039) as FY_wRev2039, SUM(fy_wRev2040) as FY_wRev2040, SUM(fy_wRev2041) as FY_wRev2041, SUM(fy_wRev2042) as FY_wRev2042, SUM(fy_wRev2043) as FY_wRev2043, SUM(fy_wRev2044) as FY_wRev2044,SUM(fy_wRev2045) as FY_wRev2045, SUM(fy_wRev2046) as FY_wRev2046, SUM(fy_wRev2047) as FY_wRev2047, SUM(fy_wRev2048) as FY_wRev2048, SUM(fy_wRev2049) as FY_wRev2049, \
    endCustomerHelper\
    FROM                                        \
    productMarketingDwh_boup                                   \
    GROUP BY                                    \
    gen, endCustomer_id  , endCustomerHelper                       \
    ORDER BY    \
    gen, endCustomer_id  , endCustomerHelper  \
    ;                                           \
    "
    #valueDf = duckdb.query(valueQuery).to_df()

    valueDfRaw = rawSqlPerformer(valueQuery)
    valueDf = pd.DataFrame(valueDfRaw)
    # need to make sure, that there are no 0's inserted in the list
    count = 0
    for row in valueDf.values:
        yearList = []
        wVolList = []
        wRevList = []
        FY_wVolList = []
        FY_wRevList = []
        # print("row")
        # print(row)
        for i in range(0, 30):
            """
            ****
            Danger!
            positional based query!
            if we add new fields to the query, we need to adjunst the row[2+i].... accordingly

            ****
            2-26 first wVol, 27-51 second wRef, 52-76 thrid fiscal year wVol, 77-101 forth fiscal year wRef
            """

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
                wVolList.append(row[2+i])
                wRevList.append(row[32+i])
                FY_wVolList.append(row[62+i])
                FY_wRevList.append(row[92+i])

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

        jsonElement = {'gen': row[0], 'endCustomer_id': row[1], 'endCustomerHelper': row[-1],
                       'year': yearList, 'CYasp': CYaspList, 'FYasp': FYaspList}
        jsonResult[str(count)] = jsonElement
        count = count + 1
    return jsonResult

    '''
    keyQuery = """
    SELECT
    gen, endCustomer_id, endCustomerHelper
    FROM
    total_df
    GROUP BY
    gen, endCustomer_id, endCustomerHelper
    ;
    """

    keyDf = ps.sqldf(keyQuery, locals())
    keyDf = keyDf.reset_index()

    jsonResult = {}

    for index, row in keyDf.iterrows():
        #print(row['gen'], row['endCustomer_id'])

        valueQuery = "                              \
        SELECT                                      \
        year, SUM(wRev) as CY_wRevSum, SUM(wVol) as CY_wVolSum, SUM(fy_wRev) as FY_wRevSum, SUM(fy_wVol) as FY_wVolSum               \
        FROM                                        \
        total_df                                    \
        WHERE                                       \
        price != 0 and gen = '" + str(row['gen']) + "' and endCustomer_id = " + str(row['endCustomer_id']) + " \
        GROUP BY                                    \
        gen, endCustomer_id, year  \
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

        jsonElement = {'gen':row['gen'], 'endCustomer_id':row['endCustomer_id'], 'endCustomerHelper':row['endCustomerHelper'], 'year':yearList, 'CYasp':CYaspList, 'FYasp': FYaspList}

        jsonResult[str(index)]=jsonElement

    return jsonResult
    '''


def Dashboard1Middle():

    jsonResult = {}

    valueQuery = "                              \
    SELECT                                      \
    gen, series, endCustomer_id,                \
    SUM(wVol2020) as wVol2020, SUM(wVol2021) as wVol2021, SUM(wVol2022) as wVol2022, SUM(wVol2023) as wVol2023, SUM(wVol2024) as wVol2024, SUM(wVol2025) as wVol2025, SUM(wVol2026) as wVol2026, SUM(wVol2027) as wVol2027, SUM(wVol2028) as wVol2028, SUM(wVol2029) as wVol2029, SUM(wVol2030) as wVol2030, SUM(wVol2031) as wVol2031, SUM(wVol2032) as wVol2032, SUM(wVol2033) as wVol2033, SUM(wVol2034) as wVol2034, SUM(wVol2035) as wVol2035, SUM(wVol2036) as wVol2036, SUM(wVol2037) as wVol2037, SUM(wVol2038) as wVol2038, SUM(wVol2039) as wVol2039, SUM(wVol2040) as wVol2040, SUM(wVol2041) as wVol2041, SUM(wVol2042) as wVol2042, SUM(wVol2043) as wVol2043, SUM(wVol2044) as wVol2044, SUM(wVol2045) as wVol2045, SUM(wVol2046) as wVol2046, SUM(wVol2047) as wVol2047, SUM(wVol2048) as wVol2048, SUM(wVol2049) as wVol2049, \
    SUM(wRev2020) as wRev2020, SUM(wRev2021) as wRev2021, SUM(wRev2022) as wRev2022, SUM(wRev2023) as wRev2023, SUM(wRev2024) as wRev2024, SUM(wRev2025) as wRev2025, SUM(wRev2026) as wRev2026, SUM(wRev2027) as wRev2027, SUM(wRev2028) as wRev2028, SUM(wRev2029) as wRev2029, SUM(wRev2030) as wRev2030, SUM(wRev2031) as wRev2031, SUM(wRev2032) as wRev2032, SUM(wRev2033) as wRev2033, SUM(wRev2034) as wRev2034, SUM(wRev2035) as wRev2035, SUM(wRev2036) as wRev2036, SUM(wRev2037) as wRev2037, SUM(wRev2038) as wRev2038, SUM(wRev2039) as wRev2039, SUM(wRev2040) as wRev2040, SUM(wRev2041) as wRev2041, SUM(wRev2042) as wRev2042, SUM(wRev2043) as wRev2043, SUM(wRev2044) as wRev2044, SUM(wRev2045) as wRev2045, SUM(wRev2046) as wRev2046, SUM(wRev2047) as wRev2047, SUM(wRev2048) as wRev2048, SUM(wRev2049) as wRev2049, \
    SUM(fy_wVol2020) as FY_wVol2020, SUM(fy_wVol2021) as FY_wVol2021, SUM(fy_wVol2022) as FY_wVol2022, SUM(fy_wVol2023) as FY_wVol2023, SUM(fy_wVol2024) as FY_wVol2024, SUM(fy_wVol2025) as FY_wVol2025, SUM(fy_wVol2026) as FY_wVol2026, SUM(fy_wVol2027) as FY_wVol2027, SUM(fy_wVol2028) as FY_wVol2028, SUM(fy_wVol2029) as FY_wVol2029, SUM(fy_wVol2030) as FY_wVol2030, SUM(fy_wVol2031) as FY_wVol2031, SUM(fy_wVol2032) as FY_wVol2032, SUM(fy_wVol2033) as FY_wVol2033, SUM(fy_wVol2034) as FY_wVol2034, SUM(fy_wVol2035) as FY_wVol2035, SUM(fy_wVol2036) as FY_wVol2036, SUM(fy_wVol2037) as FY_wVol2037, SUM(fy_wVol2038) as FY_wVol2038, SUM(fy_wVol2039) as FY_wVol2039, SUM(fy_wVol2040) as FY_wVol2040, SUM(fy_wVol2041) as FY_wVol2041, SUM(fy_wVol2042) as FY_wVol2042, SUM(fy_wVol2043) as FY_wVol2043, SUM(fy_wVol2044) as FY_wVol2044, SUM(fy_wVol2045) as FY_wVol2045, SUM(fy_wVol2046) as FY_wVol2046, SUM(fy_wVol2047) as FY_wVol2047, SUM(fy_wVol2048) as FY_wVol2048, SUM(fy_wVol2049) as FY_wVol2049, \
    SUM(fy_wRev2020) as FY_wRev2020, SUM(fy_wRev2021) as FY_wRev2021, SUM(fy_wRev2022) as FY_wRev2022, SUM(fy_wRev2023) as FY_wRev2023, SUM(fy_wRev2024) as FY_wRev2024, SUM(fy_wRev2025) as FY_wRev2025, SUM(fy_wRev2026) as FY_wRev2026, SUM(fy_wRev2027) as FY_wRev2027, SUM(fy_wRev2028) as FY_wRev2028, SUM(fy_wRev2029) as FY_wRev2029, SUM(fy_wRev2030) as FY_wRev2030, SUM(fy_wRev2031) as FY_wRev2031, SUM(fy_wRev2032) as FY_wRev2032, SUM(fy_wRev2033) as FY_wRev2033, SUM(fy_wRev2034) as FY_wRev2034, SUM(fy_wRev2035) as FY_wRev2035, SUM(fy_wRev2036) as FY_wRev2036, SUM(fy_wRev2037) as FY_wRev2037, SUM(fy_wRev2038) as FY_wRev2038, SUM(fy_wRev2039) as FY_wRev2039, SUM(fy_wRev2040) as FY_wRev2040, SUM(fy_wRev2041) as FY_wRev2041, SUM(fy_wRev2042) as FY_wRev2042, SUM(fy_wRev2043) as FY_wRev2043, SUM(fy_wRev2044) as FY_wRev2044,SUM(fy_wRev2045) as FY_wRev2045, SUM(fy_wRev2046) as FY_wRev2046, SUM(fy_wRev2047) as FY_wRev2047, SUM(fy_wRev2048) as FY_wRev2048, SUM(fy_wRev2049) as FY_wRev2049, \
    endCustomerHelper\
    FROM                                        \
    productMarketingDwh_boup                                     \
    GROUP BY                                    \
    gen, series, endCustomer_id , endCustomerHelper                \
    ORDER BY                                    \
    gen, series, endCustomer_id , endCustomerHelper                \
    ;                                           \
    "
    #valueDf = duckdb.query(valueQuery).to_df()
    valueDfRaw = rawSqlPerformer(valueQuery)
    valueDf = pd.DataFrame(valueDfRaw)

    # need to make sure, that there are no 0's inserted in the list
    count = 0
    for row in valueDf.values:
        yearList = []
        wVolList = []
        wRevList = []
        FY_wVolList = []
        FY_wRevList = []
        # print("row")
        # print(row)
        for i in range(0, 30):
            # 3-27 first, 28-52 second, 53-77 thrid, 78-102 forth

            if type(row[3+i]) == type(None):
                row[3+i] = 0.0
            if type(row[33+i]) == type(None):
                row[33+i] = 0.0
            if type(row[63+i]) == type(None):
                row[63+i] = 0.0
            if type(row[93+i]) == type(None):
                row[93+i] = 0.0

            if (row[3+i] != 0 and not math.isnan(row[3+i])) or (row[33+i] != 0 and not math.isnan(row[33+i])) or (row[63+i] != 0 and not math.isnan(row[63+i])) or (row[93+i] != 0 and not math.isnan(row[93+i])):
                yearList.append(str(2020+i))
                wVolList.append(row[3+i])
                wRevList.append(row[33+i])
                FY_wVolList.append(row[63+i])
                FY_wRevList.append(row[93+i])

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

        jsonElement = {'gen': row[0], 'series': row[1], 'endCustomer_id': row[2],
                       'endCustomerHelper': row[-1], 'year': yearList, 'CYasp': CYaspList, 'FYasp': FYaspList}
        jsonResult[str(count)] = jsonElement
        count = count + 1

    return jsonResult

    '''
    keyQuery = """
    SELECT
    gen, series, endCustomer_id, endCustomerHelper
    FROM
    total_df
    GROUP BY
    gen, series, endCustomer_id, endCustomerHelper
    ;
    """

    keyDf = duckdb.query(keyQuery).to_df()
    #keyDf = ps.sqldf(keyQuery, locals())
    keyDf = keyDf.reset_index()


    jsonResult = {}

    for index, row in keyDf.iterrows():
        #print(row['gen'], row['series'],row['endCustomer_id'])

        valueQuery = "                              \
        SELECT                                      \
        year, SUM(wRev) as CY_wRevSum, SUM(wVol) as CY_wVolSum, SUM(fy_wRev) as FY_wRevSum, SUM(fy_wVol) as FY_wVolSum               \
        FROM                                        \
        total_df                                    \
        WHERE                                       \
        gen = '" + str(row['gen']) + "' and series = '" + str(row['series']) + "' and endCustomer_id = " + str(row['endCustomer_id']) + " \
        GROUP BY                                    \
        gen, series, endCustomer_id, year  \
        ;                                           \
        "

        valueDf = duckdb.query(valueQuery).to_df()
        #valueDf = ps.sqldf(valueQuery, locals())
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

        jsonElement = {'gen':row['gen'], 'series':row['series'], 'endCustomer_id':row['endCustomer_id'], 'endCustomerHelper':row['endCustomerHelper'], 'year':yearList, 'CYasp':CYaspList, 'FYasp': FYaspList}

        jsonResult[str(index)]=jsonElement

    return jsonResult
    '''


def Dashboard1Right():  # req73_data_right req74_data_left req75_data_lefttop req76_data_lefttop

    jsonResult = {}

    valueQuery = "                              \
    SELECT                                      \
    gen, series, package, endCustomer_id,                \
    SUM(wVol2020) as wVol2020, SUM(wVol2021) as wVol2021, SUM(wVol2022) as wVol2022, SUM(wVol2023) as wVol2023, SUM(wVol2024) as wVol2024, SUM(wVol2025) as wVol2025, SUM(wVol2026) as wVol2026, SUM(wVol2027) as wVol2027, SUM(wVol2028) as wVol2028, SUM(wVol2029) as wVol2029, SUM(wVol2030) as wVol2030, SUM(wVol2031) as wVol2031, SUM(wVol2032) as wVol2032, SUM(wVol2033) as wVol2033, SUM(wVol2034) as wVol2034, SUM(wVol2035) as wVol2035, SUM(wVol2036) as wVol2036, SUM(wVol2037) as wVol2037, SUM(wVol2038) as wVol2038, SUM(wVol2039) as wVol2039, SUM(wVol2040) as wVol2040, SUM(wVol2041) as wVol2041, SUM(wVol2042) as wVol2042, SUM(wVol2043) as wVol2043, SUM(wVol2044) as wVol2044, SUM(wVol2045) as wVol2045, SUM(wVol2046) as wVol2046, SUM(wVol2047) as wVol2047, SUM(wVol2048) as wVol2048, SUM(wVol2049) as wVol2049, \
    SUM(wRev2020) as wRev2020, SUM(wRev2021) as wRev2021, SUM(wRev2022) as wRev2022, SUM(wRev2023) as wRev2023, SUM(wRev2024) as wRev2024, SUM(wRev2025) as wRev2025, SUM(wRev2026) as wRev2026, SUM(wRev2027) as wRev2027, SUM(wRev2028) as wRev2028, SUM(wRev2029) as wRev2029, SUM(wRev2030) as wRev2030, SUM(wRev2031) as wRev2031, SUM(wRev2032) as wRev2032, SUM(wRev2033) as wRev2033, SUM(wRev2034) as wRev2034, SUM(wRev2035) as wRev2035, SUM(wRev2036) as wRev2036, SUM(wRev2037) as wRev2037, SUM(wRev2038) as wRev2038, SUM(wRev2039) as wRev2039, SUM(wRev2040) as wRev2040, SUM(wRev2041) as wRev2041, SUM(wRev2042) as wRev2042, SUM(wRev2043) as wRev2043, SUM(wRev2044) as wRev2044, SUM(wRev2045) as wRev2045, SUM(wRev2046) as wRev2046, SUM(wRev2047) as wRev2047, SUM(wRev2048) as wRev2048, SUM(wRev2049) as wRev2049, \
    SUM(fy_wVol2020) as FY_wVol2020, SUM(fy_wVol2021) as FY_wVol2021, SUM(fy_wVol2022) as FY_wVol2022, SUM(fy_wVol2023) as FY_wVol2023, SUM(fy_wVol2024) as FY_wVol2024, SUM(fy_wVol2025) as FY_wVol2025, SUM(fy_wVol2026) as FY_wVol2026, SUM(fy_wVol2027) as FY_wVol2027, SUM(fy_wVol2028) as FY_wVol2028, SUM(fy_wVol2029) as FY_wVol2029, SUM(fy_wVol2030) as FY_wVol2030, SUM(fy_wVol2031) as FY_wVol2031, SUM(fy_wVol2032) as FY_wVol2032, SUM(fy_wVol2033) as FY_wVol2033, SUM(fy_wVol2034) as FY_wVol2034, SUM(fy_wVol2035) as FY_wVol2035, SUM(fy_wVol2036) as FY_wVol2036, SUM(fy_wVol2037) as FY_wVol2037, SUM(fy_wVol2038) as FY_wVol2038, SUM(fy_wVol2039) as FY_wVol2039, SUM(fy_wVol2040) as FY_wVol2040, SUM(fy_wVol2041) as FY_wVol2041, SUM(fy_wVol2042) as FY_wVol2042, SUM(fy_wVol2043) as FY_wVol2043, SUM(fy_wVol2044) as FY_wVol2044, SUM(fy_wVol2045) as FY_wVol2045, SUM(fy_wVol2046) as FY_wVol2046, SUM(fy_wVol2047) as FY_wVol2047, SUM(fy_wVol2048) as FY_wVol2048, SUM(fy_wVol2049) as FY_wVol2049, \
    SUM(fy_wRev2020) as FY_wRev2020, SUM(fy_wRev2021) as FY_wRev2021, SUM(fy_wRev2022) as FY_wRev2022, SUM(fy_wRev2023) as FY_wRev2023, SUM(fy_wRev2024) as FY_wRev2024, SUM(fy_wRev2025) as FY_wRev2025, SUM(fy_wRev2026) as FY_wRev2026, SUM(fy_wRev2027) as FY_wRev2027, SUM(fy_wRev2028) as FY_wRev2028, SUM(fy_wRev2029) as FY_wRev2029, SUM(fy_wRev2030) as FY_wRev2030, SUM(fy_wRev2031) as FY_wRev2031, SUM(fy_wRev2032) as FY_wRev2032, SUM(fy_wRev2033) as FY_wRev2033, SUM(fy_wRev2034) as FY_wRev2034, SUM(fy_wRev2035) as FY_wRev2035, SUM(fy_wRev2036) as FY_wRev2036, SUM(fy_wRev2037) as FY_wRev2037, SUM(fy_wRev2038) as FY_wRev2038, SUM(fy_wRev2039) as FY_wRev2039, SUM(fy_wRev2040) as FY_wRev2040, SUM(fy_wRev2041) as FY_wRev2041, SUM(fy_wRev2042) as FY_wRev2042, SUM(fy_wRev2043) as FY_wRev2043, SUM(fy_wRev2044) as FY_wRev2044,SUM(fy_wRev2045) as FY_wRev2045, SUM(fy_wRev2046) as FY_wRev2046, SUM(fy_wRev2047) as FY_wRev2047, SUM(fy_wRev2048) as FY_wRev2048, SUM(fy_wRev2049) as FY_wRev2049, \
    endCustomerHelper\
    FROM                                        \
    productMarketingDwh_boup                                \
    GROUP BY                                    \
    gen, series, package, endCustomer_id, endCustomerHelper                 \
    ORDER BY                                    \
    gen, series, package, endCustomer_id , endCustomerHelper                \
    ;                                           \
    "
    #valueDf = duckdb.query(valueQuery).to_df()
    valueDfRaw = rawSqlPerformer(valueQuery)
    valueDf = pd.DataFrame(valueDfRaw)

    # need to make sure, that there are no 0's inserted in the list
    count = 0
    for row in valueDf.values:
        yearList = []
        wVolList = []
        wRevList = []
        FY_wVolList = []
        FY_wRevList = []
        # print("row")
        # print(row)
        for i in range(0, 30):
            # 4-28 first, 29-53 second, 54-78thrid, 79-103 forth
            if type(row[4+i]) == type(None):
                row[4+i] = 0.0
            if type(row[34+i]) == type(None):
                row[34+i] = 0.0
            if type(row[64+i]) == type(None):
                row[64+i] = 0.0
            if type(row[94+i]) == type(None):
                row[94+i] = 0.0

            if (row[4+i] != 0 and not math.isnan(row[4+i])) or (row[34+i] != 0 and not math.isnan(row[34+i])) or (row[64+i] != 0 and not math.isnan(row[64+i])) or (row[94+i] != 0 and not math.isnan(row[94+i])):
                yearList.append(str(2020+i))
                wVolList.append(row[4+i])
                wRevList.append(row[34+i])
                FY_wVolList.append(row[64+i])
                FY_wRevList.append(row[94+i])

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

        jsonElement = {'gen': row[0], 'series': row[1], 'package': row[2], 'endCustomer_id': row[3],
                       'endCustomerHelper': row[-1], 'year': yearList, 'CYasp': CYaspList, 'FYasp': FYaspList}
        jsonResult[str(count)] = jsonElement
        count = count + 1

    return jsonResult

    '''
    keyQuery = """
    SELECT
    gen, series, package, endCustomer_id, endCustomerHelper
    FROM
    total_df
    GROUP BY
    gen, series, package, endCustomer_id, endCustomerHelper
    ;
    """

    keyDf = duckdb.query(keyQuery).to_df()
    #keyDf = ps.sqldf(keyQuery, locals())
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
        gen = '" + str(row['gen']) + "' and series = '" + str(row['series']) + "' and package = '" + str(row['package']) + "' and endCustomer_id = " + str(row['endCustomer_id']) + " \
        GROUP BY                                    \
        gen, series, package, endCustomer_id, year  \
        ;                                           \
        "
        valueDf = duckdb.query(valueQuery).to_df()
        #valueDf = ps.sqldf(valueQuery, locals())
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
    '''


def Dashboard2Right():  # same customer, same faimly, different prices  Values: silicon or package level, different customers.  Y: ASP in EUR, X: year.

    jsonResult = {}

    valueQuery = "                              \
    SELECT                                      \
    gen, series, package,                       \
    SUM(wVol2020) as wVol2020, SUM(wVol2021) as wVol2021, SUM(wVol2022) as wVol2022, SUM(wVol2023) as wVol2023, SUM(wVol2024) as wVol2024, SUM(wVol2025) as wVol2025, SUM(wVol2026) as wVol2026, SUM(wVol2027) as wVol2027, SUM(wVol2028) as wVol2028, SUM(wVol2029) as wVol2029, SUM(wVol2030) as wVol2030, SUM(wVol2031) as wVol2031, SUM(wVol2032) as wVol2032, SUM(wVol2033) as wVol2033, SUM(wVol2034) as wVol2034, SUM(wVol2035) as wVol2035, SUM(wVol2036) as wVol2036, SUM(wVol2037) as wVol2037, SUM(wVol2038) as wVol2038, SUM(wVol2039) as wVol2039, SUM(wVol2040) as wVol2040, SUM(wVol2041) as wVol2041, SUM(wVol2042) as wVol2042, SUM(wVol2043) as wVol2043, SUM(wVol2044) as wVol2044, SUM(wVol2045) as wVol2045, SUM(wVol2046) as wVol2046, SUM(wVol2047) as wVol2047, SUM(wVol2048) as wVol2048, SUM(wVol2049) as wVol2049, \
    SUM(wRev2020) as wRev2020, SUM(wRev2021) as wRev2021, SUM(wRev2022) as wRev2022, SUM(wRev2023) as wRev2023, SUM(wRev2024) as wRev2024, SUM(wRev2025) as wRev2025, SUM(wRev2026) as wRev2026, SUM(wRev2027) as wRev2027, SUM(wRev2028) as wRev2028, SUM(wRev2029) as wRev2029, SUM(wRev2030) as wRev2030, SUM(wRev2031) as wRev2031, SUM(wRev2032) as wRev2032, SUM(wRev2033) as wRev2033, SUM(wRev2034) as wRev2034, SUM(wRev2035) as wRev2035, SUM(wRev2036) as wRev2036, SUM(wRev2037) as wRev2037, SUM(wRev2038) as wRev2038, SUM(wRev2039) as wRev2039, SUM(wRev2040) as wRev2040, SUM(wRev2041) as wRev2041, SUM(wRev2042) as wRev2042, SUM(wRev2043) as wRev2043, SUM(wRev2044) as wRev2044, SUM(wRev2045) as wRev2045, SUM(wRev2046) as wRev2046, SUM(wRev2047) as wRev2047, SUM(wRev2048) as wRev2048, SUM(wRev2049) as wRev2049, \
    SUM(fy_wVol2020) as FY_wVol2020, SUM(fy_wVol2021) as FY_wVol2021, SUM(fy_wVol2022) as FY_wVol2022, SUM(fy_wVol2023) as FY_wVol2023, SUM(fy_wVol2024) as FY_wVol2024, SUM(fy_wVol2025) as FY_wVol2025, SUM(fy_wVol2026) as FY_wVol2026, SUM(fy_wVol2027) as FY_wVol2027, SUM(fy_wVol2028) as FY_wVol2028, SUM(fy_wVol2029) as FY_wVol2029, SUM(fy_wVol2030) as FY_wVol2030, SUM(fy_wVol2031) as FY_wVol2031, SUM(fy_wVol2032) as FY_wVol2032, SUM(fy_wVol2033) as FY_wVol2033, SUM(fy_wVol2034) as FY_wVol2034, SUM(fy_wVol2035) as FY_wVol2035, SUM(fy_wVol2036) as FY_wVol2036, SUM(fy_wVol2037) as FY_wVol2037, SUM(fy_wVol2038) as FY_wVol2038, SUM(fy_wVol2039) as FY_wVol2039, SUM(fy_wVol2040) as FY_wVol2040, SUM(fy_wVol2041) as FY_wVol2041, SUM(fy_wVol2042) as FY_wVol2042, SUM(fy_wVol2043) as FY_wVol2043, SUM(fy_wVol2044) as FY_wVol2044, SUM(fy_wVol2045) as FY_wVol2045, SUM(fy_wVol2046) as FY_wVol2046, SUM(fy_wVol2047) as FY_wVol2047, SUM(fy_wVol2048) as FY_wVol2048, SUM(fy_wVol2049) as FY_wVol2049, \
    SUM(fy_wRev2020) as FY_wRev2020, SUM(fy_wRev2021) as FY_wRev2021, SUM(fy_wRev2022) as FY_wRev2022, SUM(fy_wRev2023) as FY_wRev2023, SUM(fy_wRev2024) as FY_wRev2024, SUM(fy_wRev2025) as FY_wRev2025, SUM(fy_wRev2026) as FY_wRev2026, SUM(fy_wRev2027) as FY_wRev2027, SUM(fy_wRev2028) as FY_wRev2028, SUM(fy_wRev2029) as FY_wRev2029, SUM(fy_wRev2030) as FY_wRev2030, SUM(fy_wRev2031) as FY_wRev2031, SUM(fy_wRev2032) as FY_wRev2032, SUM(fy_wRev2033) as FY_wRev2033, SUM(fy_wRev2034) as FY_wRev2034, SUM(fy_wRev2035) as FY_wRev2035, SUM(fy_wRev2036) as FY_wRev2036, SUM(fy_wRev2037) as FY_wRev2037, SUM(fy_wRev2038) as FY_wRev2038, SUM(fy_wRev2039) as FY_wRev2039, SUM(fy_wRev2040) as FY_wRev2040, SUM(fy_wRev2041) as FY_wRev2041, SUM(fy_wRev2042) as FY_wRev2042, SUM(fy_wRev2043) as FY_wRev2043, SUM(fy_wRev2044) as FY_wRev2044,SUM(fy_wRev2045) as FY_wRev2045, SUM(fy_wRev2046) as FY_wRev2046, SUM(fy_wRev2047) as FY_wRev2047, SUM(fy_wRev2048) as FY_wRev2048, SUM(fy_wRev2049) as FY_wRev2049, \
    MIN(asp2020) as minAsp2020, MIN(asp2021) as minAsp2021, MIN(asp2022) as minAsp2022, MIN(asp2023) as minAsp2023, MIN(asp2024) as minAsp2024, MIN(asp2025) as minAsp2025, MIN(asp2026) as minAsp2026, MIN(asp2027) as minAsp2027, MIN(asp2028) as minAsp2028, MIN(asp2029) as minAsp2029, MIN(asp2030) as minAsp2030, MIN(asp2031) as minAsp2031, MIN(asp2032) as minAsp2032, MIN(asp2033) as minAsp2033, MIN(asp2034) as minAsp2034, MIN(asp2035) as minAsp2035, MIN(asp2036) as minAsp2036, MIN(asp2037) as minAsp2037, MIN(asp2038) as minAsp2038, MIN(asp2039) as minAsp2039, MIN(asp2040) as minAsp2040, MIN(asp2041) as minAsp2041, MIN(asp2042) as minAsp2042, MIN(asp2043) as minAsp2043, MIN(asp2044) as minAsp2044, MIN(asp2045) as minAsp2045, MIN(asp2046) as minAsp2046, MIN(asp2047) as minAsp2047, MIN(asp2048) as minAsp2048, MIN(asp2049) as minAsp2049, \
    MAX(asp2020) as maxAsp2020, MAX(asp2021) as maxAsp2021, MAX(asp2022) as maxAsp2022, MAX(asp2023) as maxAsp2023, MAX(asp2024) as maxAsp2024, MAX(asp2025) as maxAsp2025, MAX(asp2026) as maxAsp2026, MAX(asp2027) as maxAsp2027, MAX(asp2028) as maxAsp2028, MAX(asp2029) as maxAsp2029, MAX(asp2030) as maxAsp2030, MAX(asp2031) as maxAsp2031, MAX(asp2032) as maxAsp2032, MAX(asp2033) as maxAsp2033, MAX(asp2034) as maxAsp2034, MAX(asp2035) as maxAsp2035, MAX(asp2036) as maxAsp2036, MAX(asp2037) as maxAsp2037, MAX(asp2038) as maxAsp2038, MAX(asp2039) as maxAsp2039, MAX(asp2040) as maxAsp2040, MAX(asp2041) as maxAsp2041, MAX(asp2042) as maxAsp2042, MAX(asp2043) as maxAsp2043, MAX(asp2044) as maxAsp2044, MAX(asp2045) as maxAsp2045, MAX(asp2046) as maxAsp2046, MAX(asp2047) as maxAsp2047, MAX(asp2048) as maxAsp2048, MAX(asp2049) as maxAsp2049 \
    FROM                                        \
    productMarketingDwh_boup                                   \
    GROUP BY                                    \
    gen, series, package                        \
    ORDER BY                                    \
    gen, series, package                        \
    ;                                           \
    "
    #valueDf = duckdb.query(valueQuery).to_df()
    valueDfRaw = rawSqlPerformer(valueQuery)
    valueDf = pd.DataFrame(valueDfRaw)
    # need to make sure, that there are no 0's inserted in the list
    count = 0
    for row in valueDf.values:
        yearList = []
        wVolList = []
        wRevList = []
        FY_wVolList = []
        FY_wRevList = []
        minAspList = []
        maxAspList = []
        # print("row")
        # print(row)
        for i in range(0, 30):
            # 3-27 first, 28-52 second, 53-77thrid, 78-102 forth
            if type(row[3+i]) == type(None):
                row[3+i] = 0.0
            if type(row[33+i]) == type(None):
                row[33+i] = 0.0
            if type(row[63+i]) == type(None):
                row[63+i] = 0.0
            if type(row[93+i]) == type(None):
                row[93+i] = 0.0

            if (row[3+i] != 0 and not math.isnan(row[3+i])) or (row[33+i] != 0 and not math.isnan(row[33+i])) or (row[63+i] != 0 and not math.isnan(row[63+i])) or (row[93+i] != 0 and not math.isnan(row[93+i])):
                yearList.append(str(2020+i))
                wVolList.append(row[3+i])
                wRevList.append(row[33+i])
                FY_wVolList.append(row[63+i])
                FY_wRevList.append(row[93+i])
                minAspList.append(row[123+i])
                maxAspList.append(row[153+i])
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

        jsonElement = {'gen': row[0], 'series': row[1], 'package': row[2], 'year': yearList,
                       'CYasp': CYaspList, 'FYasp': FYaspList, 'minAsp': minAspList, 'maxAsp': maxAspList}
        jsonResult[str(count)] = jsonElement
        count = count + 1

    return jsonResult

    '''
    keyQuery = """
    SELECT
    gen, series, package
    FROM
    total_df
    GROUP BY
    gen, series, package
    ;
    """

    keyDf = duckdb.query(keyQuery).to_df()
    #keyDf = ps.sqldf(keyQuery, locals())
    keyDf = keyDf.reset_index()

    jsonResult = {}
    for index, row in keyDf.iterrows():
        #print(row['gen'], row['series'],row['package'])

        valueQuery = "                              \
        SELECT                                      \
        year, SUM(wRev) as CY_wRevSum, SUM(wVol) as CY_wVolSum, SUM(fy_wRev) as FY_wRevSum, SUM(fy_wVol) as FY_wVolSum, MIN(asp) as min_Aprice, MAX(asp) as max_Aprice           \
        FROM                                        \
        total_df                                    \
        WHERE                                       \
        gen = '" + str(row['gen']) + "' and series = '" + str(row['series']) + "' and package = '" + str(row['package']) + "'  \
        GROUP BY                                    \
        gen, series, package, year  \
        ;                                           \
        "
        valueDf = duckdb.query(valueQuery).to_df()
        #valueDf = ps.sqldf(valueQuery, locals())
        yearList = valueDf['year'].tolist()
        CYwVolList = valueDf['CY_wVolSum'].tolist()
        CYwRevList = valueDf['CY_wRevSum'].tolist()
        FYwVolList = valueDf['FY_wVolSum'].tolist()
        FYwRevList = valueDf['FY_wRevSum'].tolist()
        minPriceList = valueDf['min_Aprice'].tolist()
        maxPriceList = valueDf['max_Aprice'].tolist()

        aspList = []

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

        jsonElement = {'gen':row['gen'], 'series':row['series'], 'package':row['package'], 'year':yearList, 'CYasp':CYaspList, 'FYasp': FYaspList, 'minAsp':minPriceList, 'maxAsp':maxPriceList}

        jsonResult[str(index)]=jsonElement

    return jsonResult
    '''


# same customer, same faimly, different prices  Values: silicon or package level, different customers.  Y: ASP in EUR, X: year.
def Dashboard3Leftbottom():

    jsonResult = {}

    valueQuery = "                              \
    SELECT                                      \
    gen, series, package, endCustomer_id, \
    SUM(wVol2020) as wVol2020, SUM(wVol2021) as wVol2021, SUM(wVol2022) as wVol2022, SUM(wVol2023) as wVol2023, SUM(wVol2024) as wVol2024, SUM(wVol2025) as wVol2025, SUM(wVol2026) as wVol2026, SUM(wVol2027) as wVol2027, SUM(wVol2028) as wVol2028, SUM(wVol2029) as wVol2029, SUM(wVol2030) as wVol2030, SUM(wVol2031) as wVol2031, SUM(wVol2032) as wVol2032, SUM(wVol2033) as wVol2033, SUM(wVol2034) as wVol2034, SUM(wVol2035) as wVol2035, SUM(wVol2036) as wVol2036, SUM(wVol2037) as wVol2037, SUM(wVol2038) as wVol2038, SUM(wVol2039) as wVol2039, SUM(wVol2040) as wVol2040, SUM(wVol2041) as wVol2041, SUM(wVol2042) as wVol2042, SUM(wVol2043) as wVol2043, SUM(wVol2044) as wVol2044, SUM(wVol2045) as wVol2045, SUM(wVol2046) as wVol2046, SUM(wVol2047) as wVol2047, SUM(wVol2048) as wVol2048, SUM(wVol2049) as wVol2049, \
    SUM(fy_wVol2020) as FY_wVol2020, SUM(fy_wVol2021) as FY_wVol2021, SUM(fy_wVol2022) as FY_wVol2022, SUM(fy_wVol2023) as FY_wVol2023, SUM(fy_wVol2024) as FY_wVol2024, SUM(fy_wVol2025) as FY_wVol2025, SUM(fy_wVol2026) as FY_wVol2026, SUM(fy_wVol2027) as FY_wVol2027, SUM(fy_wVol2028) as FY_wVol2028, SUM(fy_wVol2029) as FY_wVol2029, SUM(fy_wVol2030) as FY_wVol2030, SUM(fy_wVol2031) as FY_wVol2031, SUM(fy_wVol2032) as FY_wVol2032, SUM(fy_wVol2033) as FY_wVol2033, SUM(fy_wVol2034) as FY_wVol2034, SUM(fy_wVol2035) as FY_wVol2035, SUM(fy_wVol2036) as FY_wVol2036, SUM(fy_wVol2037) as FY_wVol2037, SUM(fy_wVol2038) as FY_wVol2038, SUM(fy_wVol2039) as FY_wVol2039, SUM(fy_wVol2040) as FY_wVol2040, SUM(fy_wVol2041) as FY_wVol2041, SUM(fy_wVol2042) as FY_wVol2042, SUM(fy_wVol2043) as FY_wVol2043, SUM(fy_wVol2044) as FY_wVol2044, SUM(fy_wVol2045) as FY_wVol2045, SUM(fy_wVol2046) as FY_wVol2046, SUM(fy_wVol2047) as FY_wVol2047, SUM(fy_wVol2048) as FY_wVol2048, SUM(fy_wVol2049) as FY_wVol2049, \
    endCustomerHelper\
    FROM                                        \
    productMarketingDwh_boup                                 \
    GROUP BY                                    \
    gen, series, package, endCustomer_id, endCustomerHelper                 \
    ORDER BY                                    \
    gen, series, package, endCustomer_id , endCustomerHelper                \
    ;                                           \
    "
    #valueDf = duckdb.query(valueQuery).to_df()
    valueDfRaw = rawSqlPerformer(valueQuery)
    valueDf = pd.DataFrame(valueDfRaw)

    # need to make sure, that there are no 0's inserted in the list
    count = 0
    for row in valueDf.values:
        yearList = []
        wVolList = []
        FY_wVolList = []
        # print("row")
        # print(row)
        for i in range(0, 30):
            # 4-28 first, 29-53 second
            if (row[4+i] != 0 and not math.isnan(row[4+i])) or (row[34+i] != 0 and not math.isnan(row[34+i])):
                yearList.append(str(2020+i))
                wVolList.append(row[4+i])
                FY_wVolList.append(row[34+i])

        jsonElement = {'gen': row[0], 'series': row[1], 'package': row[2], 'endCustomer_id': row[3],
                       'endCustomerHelper': row[-1], 'year': yearList, 'CYwVol': wVolList, 'FYwVol': FY_wVolList}
        jsonResult[str(count)] = jsonElement
        count = count + 1

    return jsonResult

    '''
    keyQuery = """
    SELECT
    gen, series, package, endCustomer_id, endCustomerHelper
    FROM
    total_df
    GROUP BY
    gen, series, package, endCustomer_id, endCustomerHelper
    ;
    """

    keyDf = duckdb.query(keyQuery).to_df()
    #keyDf = ps.sqldf(keyQuery, locals())
    keyDf = keyDf.reset_index()


    jsonResult = {}
    for index, row in keyDf.iterrows():
        #print(row['gen'], row['series'],row['package'],row['endCustomer_id'])

        valueQuery = "                              \
        SELECT                                      \
        year, SUM(wVol) as CYwVol, SUM(fy_wVol) as FYwVol  \
        FROM                                        \
        total_df                                    \
        WHERE                                       \
        wVol != 0 and gen = '" + str(row['gen']) + "' and series = '" + str(row['series']) + "'and package = '" + str(row['package']) + "' and endCustomer_id = " + str(row['endCustomer_id']) + " \
        GROUP BY                                    \
        gen, series, package, endCustomer_id, year  \
        ;                                           \
        "
        valueDf = duckdb.query(valueQuery).to_df()
        #valueDf = ps.sqldf(valueQuery, locals())
        yearList = valueDf['year'].tolist()
        CYwVolList = valueDf['CYwVol'].tolist()
        FYwVolList = valueDf['FYwVol'].tolist()
        jsonElement = {'gen':row['gen'], 'series':row['series'],'package':row['package'], 'endCustomer_id':row['endCustomer_id'], 'endCustomerHelper':row['endCustomerHelper'], 'year':yearList, 'CYwVol':CYwVolList, 'FYwVol':FYwVolList}

        jsonResult[str(index)]=jsonElement

    return jsonResult
    '''

# von hier aus runter


def Dashboard3Right():  # same customer, same faimly, different prices  Values: silicon or package level, different customers.  Y: ASP in EUR, X: year.

    jsonResult = {}

    valueQuery = "                              \
    SELECT                                      \
    gen, series, package, endCustomer_id,                \
    SUM(wVol2020) as wVol2020, SUM(wVol2021) as wVol2021, SUM(wVol2022) as wVol2022, SUM(wVol2023) as wVol2023, SUM(wVol2024) as wVol2024, SUM(wVol2025) as wVol2025, SUM(wVol2026) as wVol2026, SUM(wVol2027) as wVol2027, SUM(wVol2028) as wVol2028, SUM(wVol2029) as wVol2029, SUM(wVol2030) as wVol2030, SUM(wVol2031) as wVol2031, SUM(wVol2032) as wVol2032, SUM(wVol2033) as wVol2033, SUM(wVol2034) as wVol2034, SUM(wVol2035) as wVol2035, SUM(wVol2036) as wVol2036, SUM(wVol2037) as wVol2037, SUM(wVol2038) as wVol2038, SUM(wVol2039) as wVol2039, SUM(wVol2040) as wVol2040, SUM(wVol2041) as wVol2041, SUM(wVol2042) as wVol2042, SUM(wVol2043) as wVol2043, SUM(wVol2044) as wVol2044, SUM(wVol2045) as wVol2045, SUM(wVol2046) as wVol2046, SUM(wVol2047) as wVol2047, SUM(wVol2048) as wVol2048, SUM(wVol2049) as wVol2049, \
    SUM(wRev2020) as wRev2020, SUM(wRev2021) as wRev2021, SUM(wRev2022) as wRev2022, SUM(wRev2023) as wRev2023, SUM(wRev2024) as wRev2024, SUM(wRev2025) as wRev2025, SUM(wRev2026) as wRev2026, SUM(wRev2027) as wRev2027, SUM(wRev2028) as wRev2028, SUM(wRev2029) as wRev2029, SUM(wRev2030) as wRev2030, SUM(wRev2031) as wRev2031, SUM(wRev2032) as wRev2032, SUM(wRev2033) as wRev2033, SUM(wRev2034) as wRev2034, SUM(wRev2035) as wRev2035, SUM(wRev2036) as wRev2036, SUM(wRev2037) as wRev2037, SUM(wRev2038) as wRev2038, SUM(wRev2039) as wRev2039, SUM(wRev2040) as wRev2040, SUM(wRev2041) as wRev2041, SUM(wRev2042) as wRev2042, SUM(wRev2043) as wRev2043, SUM(wRev2044) as wRev2044, SUM(wRev2045) as wRev2045, SUM(wRev2046) as wRev2046, SUM(wRev2047) as wRev2047, SUM(wRev2048) as wRev2048, SUM(wRev2049) as wRev2049, \
    SUM(fy_wVol2020) as FY_wVol2020, SUM(fy_wVol2021) as FY_wVol2021, SUM(fy_wVol2022) as FY_wVol2022, SUM(fy_wVol2023) as FY_wVol2023, SUM(fy_wVol2024) as FY_wVol2024, SUM(fy_wVol2025) as FY_wVol2025, SUM(fy_wVol2026) as FY_wVol2026, SUM(fy_wVol2027) as FY_wVol2027, SUM(fy_wVol2028) as FY_wVol2028, SUM(fy_wVol2029) as FY_wVol2029, SUM(fy_wVol2030) as FY_wVol2030, SUM(fy_wVol2031) as FY_wVol2031, SUM(fy_wVol2032) as FY_wVol2032, SUM(fy_wVol2033) as FY_wVol2033, SUM(fy_wVol2034) as FY_wVol2034, SUM(fy_wVol2035) as FY_wVol2035, SUM(fy_wVol2036) as FY_wVol2036, SUM(fy_wVol2037) as FY_wVol2037, SUM(fy_wVol2038) as FY_wVol2038, SUM(fy_wVol2039) as FY_wVol2039, SUM(fy_wVol2040) as FY_wVol2040, SUM(fy_wVol2041) as FY_wVol2041, SUM(fy_wVol2042) as FY_wVol2042, SUM(fy_wVol2043) as FY_wVol2043, SUM(fy_wVol2044) as FY_wVol2044, SUM(fy_wVol2045) as FY_wVol2045, SUM(fy_wVol2046) as FY_wVol2046, SUM(fy_wVol2047) as FY_wVol2047, SUM(fy_wVol2048) as FY_wVol2048, SUM(fy_wVol2049) as FY_wVol2049, \
    SUM(fy_wRev2020) as FY_wRev2020, SUM(fy_wRev2021) as FY_wRev2021, SUM(fy_wRev2022) as FY_wRev2022, SUM(fy_wRev2023) as FY_wRev2023, SUM(fy_wRev2024) as FY_wRev2024, SUM(fy_wRev2025) as FY_wRev2025, SUM(fy_wRev2026) as FY_wRev2026, SUM(fy_wRev2027) as FY_wRev2027, SUM(fy_wRev2028) as FY_wRev2028, SUM(fy_wRev2029) as FY_wRev2029, SUM(fy_wRev2030) as FY_wRev2030, SUM(fy_wRev2031) as FY_wRev2031, SUM(fy_wRev2032) as FY_wRev2032, SUM(fy_wRev2033) as FY_wRev2033, SUM(fy_wRev2034) as FY_wRev2034, SUM(fy_wRev2035) as FY_wRev2035, SUM(fy_wRev2036) as FY_wRev2036, SUM(fy_wRev2037) as FY_wRev2037, SUM(fy_wRev2038) as FY_wRev2038, SUM(fy_wRev2039) as FY_wRev2039, SUM(fy_wRev2040) as FY_wRev2040, SUM(fy_wRev2041) as FY_wRev2041, SUM(fy_wRev2042) as FY_wRev2042, SUM(fy_wRev2043) as FY_wRev2043, SUM(fy_wRev2044) as FY_wRev2044, SUM(fy_wRev2045) as FY_wRev2045, SUM(fy_wRev2046) as FY_wRev2046, SUM(fy_wRev2047) as FY_wRev2047, SUM(fy_wRev2048) as FY_wRev2048, SUM(fy_wRev2049) as FY_wRev2049, \
    SUM(vhk2020) as vhk2020, SUM(vhk2021) as vhk2021, SUM(vhk2022) as vhk2022, SUM(vhk2023) as vhk2023, SUM(vhk2024) as vhk2024, SUM(vhk2025) as vhk2025, SUM(vhk2026) as vhk2026, SUM(vhk2027) as vhk2027, SUM(vhk2028) as vhk2028, SUM(vhk2029) as vhk2029, SUM(vhk2030) as vhk2030, SUM(vhk2031) as vhk2031, SUM(vhk2032) as vhk2032, SUM(vhk2033) as vhk2033, SUM(vhk2034) as vhk2034, SUM(vhk2035) as vhk2035, SUM(vhk2036) as vhk2036, SUM(vhk2037) as vhk2037, SUM(vhk2038) as vhk2038, SUM(vhk2039) as vhk2039, SUM(vhk2040) as vhk2040, SUM(vhk2041) as vhk2041, SUM(vhk2042) as vhk2042, SUM(vhk2043) as vhk2043, SUM(vhk2044) as vhk2044, SUM(vhk2045) as vhk2045, SUM(vhk2046) as vhk2046, SUM(vhk2047) as vhk2047, SUM(vhk2048) as vhk2048, SUM(vhk2049) as vhk2049, \
    SUM(gm2020) as gm2020, SUM(gm2021) as gm2021, SUM(gm2022) as gm2022, SUM(gm2023) as gm2023, SUM(gm2024) as gm2024, SUM(gm2025) as gm2025, SUM(gm2026) as gm2026, SUM(gm2027) as gm2027, SUM(gm2028) as gm2028, SUM(gm2029) as gm2029, SUM(gm2030) as gm2030, SUM(gm2031) as gm2031, SUM(gm2032) as gm2032, SUM(gm2033) as gm2033, SUM(gm2034) as gm2034, SUM(gm2035) as gm2035, SUM(gm2036) as gm2036, SUM(gm2037) as gm2037, SUM(gm2038) as gm2038, SUM(gm2039) as gm2039, SUM(gm2040) as gm2040, SUM(gm2041) as gm2041, SUM(gm2042) as gm2042, SUM(gm2043) as gm2043, SUM(gm2044) as gm2044, SUM(gm2045) as gm2045, SUM(gm2046) as gm2046, SUM(gm2047) as gm2047, SUM(gm2048) as gm2048, SUM(gm2049) as gm2049, \
    SUM(fy_gm2020) as fy_gm2020, SUM(fy_gm2021) as fy_gm2021, SUM(fy_gm2022) as fy_gm2022, SUM(fy_gm2023) as fy_gm2023, SUM(fy_gm2024) as fy_gm2024, SUM(fy_gm2025) as fy_gm2025, SUM(fy_gm2026) as fy_gm2026, SUM(fy_gm2027) as fy_gm2027, SUM(fy_gm2028) as fy_gm2028, SUM(fy_gm2029) as fy_gm2029, SUM(fy_gm2030) as fy_gm2030, SUM(fy_gm2031) as fy_gm2031, SUM(fy_gm2032) as fy_gm2032, SUM(fy_gm2033) as fy_gm2033, SUM(fy_gm2034) as fy_gm2034, SUM(fy_gm2035) as fy_gm2035, SUM(fy_gm2036) as fy_gm2036, SUM(fy_gm2037) as fy_gm2037, SUM(fy_gm2038) as fy_gm2038, SUM(fy_gm2039) as fy_gm2039, SUM(fy_gm2040) as fy_gm2040, SUM(fy_gm2041) as fy_gm2041, SUM(fy_gm2042) as fy_gm2042, SUM(fy_gm2043) as fy_gm2043, SUM(fy_gm2044) as fy_gm2044, SUM(fy_gm2045) as fy_gm2045, SUM(fy_gm2046) as fy_gm2046, SUM(fy_gm2047) as fy_gm2047, SUM(fy_gm2048) as fy_gm2048, SUM(fy_gm2049) as fy_gm2049, \
    endCustomerHelper \
    FROM                                        \
    productMarketingDwh_boup                                   \
    GROUP BY                                    \
    gen, series, package, endCustomer_id, endCustomerHelper                 \
    ORDER BY                                    \
    gen, series, package, endCustomer_id, endCustomerHelper                \
    ;                                           \
    "
    #valueDf = duckdb.query(valueQuery).to_df()
    valueDfRaw = rawSqlPerformer(valueQuery)
    valueDf = pd.DataFrame(valueDfRaw)

    # need to make sure, that there are no 0's inserted in the list
    count = 0
    for row in valueDf.values:
        yearList = []
        wVolList = []
        wRevList = []
        FY_wVolList = []
        FY_wRevList = []
        vhkList = []
        gmList = []
        FY_gmList = []

        for i in range(0, 30):
            # 4-28 first, 29-53 second, 54-78thrid, 79-103 forth, 104-128 fifth,  129-153 sixth, 154-178 seventh
            if (row[4+i] != 0 and not row[4+i] is None) or (row[34+i] != 0 and not row[34+i] is None) or (row[64+i] != 0 and not row[64+i] is None) or (row[94+i] != 0 and not row[94+i]) is None:
                yearList.append(str(2020+i))
                wVolList.append(row[4+i])
                wRevList.append(row[34+i])
                FY_wVolList.append(row[64+i])
                FY_wRevList.append(row[94+i])
                vhkList.append(row[124+i])
                gmList.append(row[154+i])
                FY_gmList.append(row[184+i])

        jsonElement = {'gen': row[0], 'series': row[1], 'package': row[2], 'endCustomer_id': row[3], 'endCustomerHelper': row[-1], 'year': yearList,
                       'vhk': vhkList, 'CYRev': wRevList, 'CYwVol': wVolList, 'CYgm': gmList, 'FYRev': FY_wRevList, 'FYwVol': FY_wVolList, 'FYgm': FY_gmList}
        jsonResult[str(count)] = jsonElement
        count = count + 1

    return jsonResult

    '''
    keyQuery = """
    SELECT
    gen, series, package, endCustomer_id, endCustomerHelper
    FROM
    total_df
    GROUP BY
    gen, series, package, endCustomer_id, endCustomerHelper
    ;
    """

    keyDf = duckdb.query(keyQuery).to_df()
    #keyDf = ps.sqldf(keyQuery, locals())
    keyDf = keyDf.reset_index()


    jsonResult = {}
    for index, row in keyDf.iterrows():
        #print(row['gen'], row['series'],row['package'],row['endCustomer_id'])

        valueQuery = "                              \
        SELECT                                      \
        year, SUM(vhk) as vhk, SUM(wRev) as CY_wRev, SUM(wVol) as CY_wVol, SUM(gm) as CY_gm, SUM(fy_wRev) as FY_wRev, SUM(fy_wVol) as FY_wVol, SUM(fy_gm) as FY_gm  \
        FROM                                        \
        total_df                                    \
        WHERE                                       \
        wRev != 0 and gm != 0 and gen = '" + str(row['gen']) + "' and series = '" + str(row['series']) + "'and package = '" + str(row['package']) + "' and endCustomer_id = " + str(row['endCustomer_id']) + " \
        GROUP BY                                    \
        gen, series, package, endCustomer_id, year  \
        ;                                           \
        "
        valueDf = duckdb.query(valueQuery).to_df()
        #valueDf = ps.sqldf(valueQuery, locals())

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
    '''


# same customer, same faimly, different prices  Values: silicon or package level, different customers.  Y: ASP in EUR, X: year.
def Dashboard4Leftbottom():

    jsonResult = {}

    valueQuery = "                              \
    SELECT                                      \
    gen, series, package, endCustomer_id,                \
    SUM(vhk2020) as vhk2020, SUM(vhk2021) as vhk2021, SUM(vhk2022) as vhk2022, SUM(vhk2023) as vhk2023, SUM(vhk2024) as vhk2024, SUM(vhk2025) as vhk2025, SUM(vhk2026) as vhk2026, SUM(vhk2027) as vhk2027, SUM(vhk2028) as vhk2028, SUM(vhk2029) as vhk2029, SUM(vhk2030) as vhk2030, SUM(vhk2031) as vhk2031, SUM(vhk2032) as vhk2032, SUM(vhk2033) as vhk2033, SUM(vhk2034) as vhk2034, SUM(vhk2035) as vhk2035, SUM(vhk2036) as vhk2036, SUM(vhk2037) as vhk2037, SUM(vhk2038) as vhk2038, SUM(vhk2039) as vhk2039, SUM(vhk2040) as vhk2040, SUM(vhk2041) as vhk2041, SUM(vhk2042) as vhk2042, SUM(vhk2043) as vhk2043, SUM(vhk2044) as vhk2044, SUM(vhk2045) as vhk2045, SUM(vhk2046) as vhk2046, SUM(vhk2047) as vhk2047, SUM(vhk2048) as vhk2048, SUM(vhk2049) as vhk2049, \
    endCustomerHelper\
    FROM                                        \
    productMarketingDwh_boup                                    \
    GROUP BY                                    \
    gen, series, package, endCustomer_id, endCustomerHelper                 \
    ORDER BY                                    \
    gen, series, package, endCustomer_id, endCustomerHelper                \
    ;                                           \
    "
    #valueDf = duckdb.query(valueQuery).to_df()
    valueDfRaw = rawSqlPerformer(valueQuery)
    valueDf = pd.DataFrame(valueDfRaw)

    # need to make sure, that there are no 0's inserted in the list
    count = 0
    for row in valueDf.values:
        yearList = []
        vhkList = []
        # print("row")
        # print(row)
        for i in range(0, 30):
            if (row[4+i] != 0 and not row[4+i] is None):
                yearList.append(str(2020+i))
                vhkList.append(row[4+i])

        jsonElement = {'gen': row[0], 'series': row[1], 'package': row[2],
                       'endCustomer_id': row[3], 'endCustomerHelper': row[-1], 'year': yearList, 'vhk': vhkList}
        jsonResult[str(count)] = jsonElement
        count = count + 1

    return jsonResult

    '''
    keyQuery = """
    SELECT
    gen, series, package, endCustomer_id, endCustomerHelper
    FROM
    total_df
    GROUP BY
    gen, series, package, endCustomer_id, endCustomerHelper
    ;
    """

    keyDf = duckdb.query(keyQuery).to_df()
    #keyDf = ps.sqldf(keyQuery, locals())
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
        valueDf = duckdb.query(valueQuery).to_df()
        #valueDf = ps.sqldf(valueQuery, locals())
        yearList = valueDf['year'].tolist()
        vhkList = valueDf['sum_vhk'].tolist()
        jsonElement = {'gen':row['gen'], 'series':row['series'],'package':row['package'], 'endCustomer_id':row['endCustomer_id'], 'endCustomerHelper':row['endCustomerHelper'], 'year':yearList, 'wVol':vhkList}

        jsonResult[str(index)]=jsonElement

    return jsonResult
    '''


def Dashboard5():  # same customer, same faimly, different prices  Values: silicon or package level, different customers.  Y: ASP in EUR, X: year.

    jsonResult = {}

    valueQuery = "                              \
    SELECT                                      \
    gen, series, package, endCustomer_id,                \
    SUM(wVol2020) as wVol2020, SUM(wVol2021) as wVol2021, SUM(wVol2022) as wVol2022, SUM(wVol2023) as wVol2023, SUM(wVol2024) as wVol2024, SUM(wVol2025) as wVol2025, SUM(wVol2026) as wVol2026, SUM(wVol2027) as wVol2027, SUM(wVol2028) as wVol2028, SUM(wVol2029) as wVol2029, SUM(wVol2030) as wVol2030, SUM(wVol2031) as wVol2031, SUM(wVol2032) as wVol2032, SUM(wVol2033) as wVol2033, SUM(wVol2034) as wVol2034, SUM(wVol2035) as wVol2035, SUM(wVol2036) as wVol2036, SUM(wVol2037) as wVol2037, SUM(wVol2038) as wVol2038, SUM(wVol2039) as wVol2039, SUM(wVol2040) as wVol2040, SUM(wVol2041) as wVol2041, SUM(wVol2042) as wVol2042, SUM(wVol2043) as wVol2043, SUM(wVol2044) as wVol2044, SUM(wVol2045) as wVol2045, SUM(wVol2046) as wVol2046, SUM(wVol2047) as wVol2047, SUM(wVol2048) as wVol2048, SUM(wVol2049) as wVol2049, \
    SUM(wRev2020) as wRev2020, SUM(wRev2021) as wRev2021, SUM(wRev2022) as wRev2022, SUM(wRev2023) as wRev2023, SUM(wRev2024) as wRev2024, SUM(wRev2025) as wRev2025, SUM(wRev2026) as wRev2026, SUM(wRev2027) as wRev2027, SUM(wRev2028) as wRev2028, SUM(wRev2029) as wRev2029, SUM(wRev2030) as wRev2030, SUM(wRev2031) as wRev2031, SUM(wRev2032) as wRev2032, SUM(wRev2033) as wRev2033, SUM(wRev2034) as wRev2034, SUM(wRev2035) as wRev2035, SUM(wRev2036) as wRev2036, SUM(wRev2037) as wRev2037, SUM(wRev2038) as wRev2038, SUM(wRev2039) as wRev2039, SUM(wRev2040) as wRev2040, SUM(wRev2041) as wRev2041, SUM(wRev2042) as wRev2042, SUM(wRev2043) as wRev2043, SUM(wRev2044) as wRev2044, SUM(wRev2045) as wRev2045, SUM(wRev2046) as wRev2046, SUM(wRev2047) as wRev2047, SUM(wRev2048) as wRev2048, SUM(wRev2049) as wRev2049, \
    SUM(fy_wVol2020) as FY_wVol2020, SUM(fy_wVol2021) as FY_wVol2021, SUM(fy_wVol2022) as FY_wVol2022, SUM(fy_wVol2023) as FY_wVol2023, SUM(fy_wVol2024) as FY_wVol2024, SUM(fy_wVol2025) as FY_wVol2025, SUM(fy_wVol2026) as FY_wVol2026, SUM(fy_wVol2027) as FY_wVol2027, SUM(fy_wVol2028) as FY_wVol2028, SUM(fy_wVol2029) as FY_wVol2029, SUM(fy_wVol2030) as FY_wVol2030, SUM(fy_wVol2031) as FY_wVol2031, SUM(fy_wVol2032) as FY_wVol2032, SUM(fy_wVol2033) as FY_wVol2033, SUM(fy_wVol2034) as FY_wVol2034, SUM(fy_wVol2035) as FY_wVol2035, SUM(fy_wVol2036) as FY_wVol2036, SUM(fy_wVol2037) as FY_wVol2037, SUM(fy_wVol2038) as FY_wVol2038, SUM(fy_wVol2039) as FY_wVol2039, SUM(fy_wVol2040) as FY_wVol2040, SUM(fy_wVol2041) as FY_wVol2041, SUM(fy_wVol2042) as FY_wVol2042, SUM(fy_wVol2043) as FY_wVol2043, SUM(fy_wVol2044) as FY_wVol2044, SUM(fy_wVol2045) as FY_wVol2045, SUM(fy_wVol2046) as FY_wVol2046, SUM(fy_wVol2047) as FY_wVol2047, SUM(fy_wVol2048) as FY_wVol2048, SUM(fy_wVol2049) as FY_wVol2049, \
    SUM(fy_wRev2020) as FY_wRev2020, SUM(fy_wRev2021) as FY_wRev2021, SUM(fy_wRev2022) as FY_wRev2022, SUM(fy_wRev2023) as FY_wRev2023, SUM(fy_wRev2024) as FY_wRev2024, SUM(fy_wRev2025) as FY_wRev2025, SUM(fy_wRev2026) as FY_wRev2026, SUM(fy_wRev2027) as FY_wRev2027, SUM(fy_wRev2028) as FY_wRev2028, SUM(fy_wRev2029) as FY_wRev2029, SUM(fy_wRev2030) as FY_wRev2030, SUM(fy_wRev2031) as FY_wRev2031, SUM(fy_wRev2032) as FY_wRev2032, SUM(fy_wRev2033) as FY_wRev2033, SUM(fy_wRev2034) as FY_wRev2034, SUM(fy_wRev2035) as FY_wRev2035, SUM(fy_wRev2036) as FY_wRev2036, SUM(fy_wRev2037) as FY_wRev2037, SUM(fy_wRev2038) as FY_wRev2038, SUM(fy_wRev2039) as FY_wRev2039, SUM(fy_wRev2040) as FY_wRev2040, SUM(fy_wRev2041) as FY_wRev2041, SUM(fy_wRev2042) as FY_wRev2042, SUM(fy_wRev2043) as FY_wRev2043, SUM(fy_wRev2044) as FY_wRev2044,SUM(fy_wRev2045) as FY_wRev2045, SUM(fy_wRev2046) as FY_wRev2046, SUM(fy_wRev2047) as FY_wRev2047, SUM(fy_wRev2048) as FY_wRev2048, SUM(fy_wRev2049) as FY_wRev2049, \
    SUM(vhk2020) as vhk2020, SUM(vhk2021) as vhk2021, SUM(vhk2022) as vhk2022, SUM(vhk2023) as vhk2023, SUM(vhk2024) as vhk2024, SUM(vhk2025) as vhk2025, SUM(vhk2026) as vhk2026, SUM(vhk2027) as vhk2027, SUM(vhk2028) as vhk2028, SUM(vhk2029) as vhk2029, SUM(vhk2030) as vhk2030, SUM(vhk2031) as vhk2031, SUM(vhk2032) as vhk2032, SUM(vhk2033) as vhk2033, SUM(vhk2034) as vhk2034, SUM(vhk2035) as vhk2035, SUM(vhk2036) as vhk2036, SUM(vhk2037) as vhk2037, SUM(vhk2038) as vhk2038, SUM(vhk2039) as vhk2039, SUM(vhk2040) as vhk2040, SUM(vhk2041) as vhk2041, SUM(vhk2042) as vhk2042, SUM(vhk2043) as vhk2043, SUM(vhk2044) as vhk2044, SUM(vhk2045) as vhk2045, SUM(vhk2046) as vhk2046, SUM(vhk2047) as vhk2047, SUM(vhk2048) as vhk2048, SUM(vhk2049) as vhk2049, \
    SUM(gm2020) as gm2020, SUM(gm2021) as gm2021, SUM(gm2022) as gm2022, SUM(gm2023) as gm2023, SUM(gm2024) as gm2024, SUM(gm2025) as gm2025, SUM(gm2026) as gm2026, SUM(gm2027) as gm2027, SUM(gm2028) as gm2028, SUM(gm2029) as gm2029, SUM(gm2030) as gm2030, SUM(gm2031) as gm2031, SUM(gm2032) as gm2032, SUM(gm2033) as gm2033, SUM(gm2034) as gm2034, SUM(gm2035) as gm2035, SUM(gm2036) as gm2036, SUM(gm2037) as gm2037, SUM(gm2038) as gm2038, SUM(gm2039) as gm2039, SUM(gm2040) as gm2040, SUM(gm2041) as gm2041, SUM(gm2042) as gm2042, SUM(gm2043) as gm2043, SUM(gm2044) as gm2044, SUM(gm2045) as gm2045, SUM(gm2046) as gm2046, SUM(gm2047) as gm2047, SUM(gm2048) as gm2048, SUM(gm2049) as gm2049, \
    SUM(fy_gm2020) as fy_gm2020, SUM(fy_gm2021) as fy_gm2021, SUM(fy_gm2022) as fy_gm2022, SUM(fy_gm2023) as fy_gm2023, SUM(fy_gm2024) as fy_gm2024, SUM(fy_gm2025) as fy_gm2025, SUM(fy_gm2026) as fy_gm2026, SUM(fy_gm2027) as fy_gm2027, SUM(fy_gm2028) as fy_gm2028, SUM(fy_gm2029) as fy_gm2029, SUM(fy_gm2030) as fy_gm2030, SUM(fy_gm2031) as fy_gm2031, SUM(fy_gm2032) as fy_gm2032, SUM(fy_gm2033) as fy_gm2033, SUM(fy_gm2034) as fy_gm2034, SUM(fy_gm2035) as fy_gm2035, SUM(fy_gm2036) as fy_gm2036, SUM(fy_gm2037) as fy_gm2037, SUM(fy_gm2038) as fy_gm2038, SUM(fy_gm2039) as fy_gm2039, SUM(fy_gm2040) as fy_gm2040, SUM(fy_gm2041) as fy_gm2041, SUM(fy_gm2042) as fy_gm2042, SUM(fy_gm2043) as fy_gm2043, SUM(fy_gm2044) as fy_gm2044, SUM(fy_gm2045) as fy_gm2045, SUM(fy_gm2046) as fy_gm2046, SUM(fy_gm2047) as fy_gm2047, SUM(fy_gm2048) as fy_gm2048, SUM(fy_gm2049) as fy_gm2049, \
    MIN(gm2020) as mingm2020, MIN(gm2021) as mingm2021, MIN(gm2022) as mingm2022, MIN(gm2023) as mingm2023, MIN(gm2024) as mingm2024, MIN(gm2025) as mingm2025, MIN(gm2026) as mingm2026, MIN(gm2027) as mingm2027, MIN(gm2028) as mingm2028, MIN(gm2029) as mingm2029, MIN(gm2030) as mingm2030, MIN(gm2031) as mingm2031, MIN(gm2032) as mingm2032, MIN(gm2033) as mingm2033, MIN(gm2034) as mingm2034, MIN(gm2035) as mingm2035, MIN(gm2036) as mingm2036, MIN(gm2037) as mingm2037, MIN(gm2038) as mingm2038, MIN(gm2039) as mingm2039, MIN(gm2040) as mingm2040, MIN(gm2041) as mingm2041, MIN(gm2042) as mingm2042, MIN(gm2043) as mingm2043, MIN(gm2044) as mingm2044,  MIN(gm2045) as mingm2045, MIN(gm2046) as mingm2046, MIN(gm2047) as mingm2047, MIN(gm2048) as mingm2048, MIN(gm2049) as mingm2049, \
    MIN(fy_gm2020) as minFy_gm2020, MIN(fy_gm2021) as minFy_gm2021, MIN(fy_gm2022) as minFy_gm2022, MIN(fy_gm2023) as minFy_gm2023, MIN(fy_gm2024) as minFy_gm2024, MIN(fy_gm2025) as minFy_gm2025, MIN(fy_gm2026) as minFy_gm2026, MIN(fy_gm2027) as minFy_gm2027, MIN(fy_gm2028) as minFy_gm2028, MIN(fy_gm2029) as minFy_gm2029, MIN(fy_gm2030) as minFy_gm2030, MIN(fy_gm2031) as minFy_gm2031, MIN(fy_gm2032) as minFy_gm2032, MIN(fy_gm2033) as minFy_gm2033, MIN(fy_gm2034) as minFy_gm2034, MIN(fy_gm2035) as minFy_gm2035, MIN(fy_gm2036) as minFy_gm2036, MIN(fy_gm2037) as minFy_gm2037, MIN(fy_gm2038) as minFy_gm2038, MIN(fy_gm2039) as minFy_gm2039, MIN(fy_gm2040) as minFy_gm2040, MIN(fy_gm2041) as minFy_gm2041, MIN(fy_gm2042) as minFy_gm2042, MIN(fy_gm2043) as minFy_gm2043, MIN(fy_gm2044) as minFy_gm2044, MIN(fy_gm2045) as minFy_gm2045, MIN(fy_gm2046) as minFy_gm2046, MIN(fy_gm2047) as minFy_gm2047, MIN(fy_gm2048) as minFy_gm2048, MIN(fy_gm2049) as minFy_gm2049, \
    MAX(gm2020) as MAXgm2020, MAX(gm2021) as MAXgm2021, MAX(gm2022) as MAXgm2022, MAX(gm2023) as MAXgm2023, MAX(gm2024) as MAXgm2024, MAX(gm2025) as MAXgm2025, MAX(gm2026) as MAXgm2026, MAX(gm2027) as MAXgm2027, MAX(gm2028) as MAXgm2028, MAX(gm2029) as MAXgm2029, MAX(gm2030) as MAXgm2030, MAX(gm2031) as MAXgm2031, MAX(gm2032) as MAXgm2032, MAX(gm2033) as MAXgm2033, MAX(gm2034) as MAXgm2034, MAX(gm2035) as MAXgm2035, MAX(gm2036) as MAXgm2036, MAX(gm2037) as MAXgm2037, MAX(gm2038) as MAXgm2038, MAX(gm2039) as MAXgm2039, MAX(gm2040) as MAXgm2040, MAX(gm2041) as MAXgm2041, MAX(gm2042) as MAXgm2042, MAX(gm2043) as MAXgm2043, MAX(gm2044) as MAXgm2044, MAX(gm2045) as MAXgm2045, MAX(gm2046) as MAXgm2046, MAX(gm2047) as MAXgm2047, MAX(gm2048) as MAXgm2048, MAX(gm2049) as MAXgm2049, \
    MAX(fy_gm2020) as MAXFy_gm2020, MAX(fy_gm2021) as MAXFy_gm2021, MAX(fy_gm2022) as MAXFy_gm2022, MAX(fy_gm2023) as MAXFy_gm2023, MAX(fy_gm2024) as MAXFy_gm2024, MAX(fy_gm2025) as MAXFy_gm2025, MAX(fy_gm2026) as MAXFy_gm2026, MAX(fy_gm2027) as MAXFy_gm2027, MAX(fy_gm2028) as MAXFy_gm2028, MAX(fy_gm2029) as MAXFy_gm2029, MAX(fy_gm2030) as MAXFy_gm2030, MAX(fy_gm2031) as MAXFy_gm2031, MAX(fy_gm2032) as MAXFy_gm2032, MAX(fy_gm2033) as MAXFy_gm2033, MAX(fy_gm2034) as MAXFy_gm2034, MAX(fy_gm2035) as MAXFy_gm2035, MAX(fy_gm2036) as MAXFy_gm2036, MAX(fy_gm2037) as MAXFy_gm2037, MAX(fy_gm2038) as MAXFy_gm2038, MAX(fy_gm2039) as MAXFy_gm2039, MAX(fy_gm2040) as MAXFy_gm2040, MAX(fy_gm2041) as MAXFy_gm2041, MAX(fy_gm2042) as MAXFy_gm2042, MAX(fy_gm2043) as MAXFy_gm2043, MAX(fy_gm2044) as MAXFy_gm2044, MAX(fy_gm2045) as MAXFy_gm2045, MAX(fy_gm2046) as MAXFy_gm2046, MAX(fy_gm2047) as MAXFy_gm2047, MAX(fy_gm2048) as MAXFy_gm2048, MAX(fy_gm2049) as MAXFy_gm2049 \
   ,COUNT(*) as project_count, endCustomerHelper\
    FROM                                        \
    productMarketingDwh_boup                                 \
    GROUP BY                                    \
    gen, series, package, endCustomer_id, endCustomerHelper                 \
    ORDER BY                                    \
    gen, series, package, endCustomer_id , endCustomerHelper                \
    ;                                           \
    "
    #valueDf = duckdb.query(valueQuery).to_df()
    valueDfRaw = rawSqlPerformer(valueQuery)
    valueDf = pd.DataFrame(valueDfRaw)

    # need to make sure, that there are no 0's inserted in the list
    count = 0
    for row in valueDf.values:
        yearList = []
        wVolList = []
        wRevList = []
        FY_wRevList = []
        FY_wVolList = []
        vhkList = []
        gmList = []
        FY_gmList = []
        minGmList = []
        maxGmList = []
        FY_minGmList = []
        FY_maxGmList = []
        projectCountList = []
        # print("row")
        # print(row)
        for i in range(0, 30):
            # 4-28 first, 29-53 second, 54-78thrid, 79-103 forth
            if (row[4+i] != 0 and not row[4+i] is None) or (row[34+i] != 0 and not row[34+i] is None) or (row[64+i] != 0 and not row[64+i] is None) or (row[94+i] != 0 and not row[94+i]) is None:
                yearList.append(str(2020+i))
                wVolList.append(row[4+i])
                wRevList.append(row[34+i])
                FY_wVolList.append(row[64+i])
                FY_wRevList.append(row[94+i])
                vhkList.append(row[124+i])
                gmList.append(row[154+i])
                FY_gmList.append(row[184+i])
                minGmList.append(row[214+i])
                FY_minGmList.append(row[244+i])
                maxGmList.append(row[274+i])
                FY_maxGmList.append(row[304+i])
        projectCountList.append(row[334])

        jsonElement = {'gen': row[0], 'series': row[1], 'package': row[2], 'endCustomer_id': row[3], 'endCustomerHelper': row[-1], 'year': yearList, 'projectCount': projectCountList, 'vhk': vhkList, 'CYRev': wRevList,
                       'CYwVol': wVolList, 'CYgm': gmList, 'CYpmin_gm': minGmList, 'CYpmax_gm': maxGmList, 'FYRev': FY_wRevList, 'FYwVol': FY_wVolList, 'FYgm': FY_gmList, 'FYpmin_gm': FY_minGmList, 'FYpmax_gm': FY_maxGmList}

        jsonResult[str(count)] = jsonElement
        count = count + 1

    return jsonResult

    '''
    keyQuery = """
    SELECT
    gen, series, package, endCustomer_id, endCustomerHelper
    FROM
    total_df
    GROUP BY
    gen, series, package, endCustomer_id, endCustomerHelper
    ;
    """

    keyDf = duckdb.query(keyQuery).to_df()
    #keyDf = ps.sqldf(keyQuery, locals())
    keyDf = keyDf.reset_index()


    jsonResult = {}
    for index, row in keyDf.iterrows(): #count /45 because for each project we have 45 entries (45 years)
        #print(row['gen'], row['series'],row['package'],row['endCustomer_id'])

        valueQuery = "                              \
        SELECT                                      \
        year, COUNT(*) / 45 as project_count, SUM(vhk) as vhk, SUM(wRev) as CY_wRev, SUM(wVol) as CY_wVol, SUM(gm) as CY_gm, MIN(gm) as CYmin_gm, MAX(gm) as CYmax_gm, SUM(fy_wRev) as FY_wRev, SUM(fy_wVol) as FY_wVol, SUM(fy_gm) as FY_gm, MIN(fy_gm) as FYmin_gm, MAX(fy_gm) as FYmax_gm              \
        FROM                                        \
        total_df                                    \
        WHERE                                       \
        gm != 0 and gen = '" + str(row['gen']) + "' and series = '" + str(row['series']) + "'and package = '" + str(row['package']) + "' and endCustomer_id = " + str(row['endCustomer_id']) + " \
        GROUP BY                                    \
        gen, series, package, endCustomer_id, year  \
        ;                                           \
        "
        valueDf = duckdb.query(valueQuery).to_df()
        #valueDf = ps.sqldf(valueQuery, locals())
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
    '''


def DashboardBubble(this_year):  # for 6,7,8

    jsonResult = {}

    valueQuery = "                                  \
        SELECT                                      \
        series, endCustomer_id, \
        SUM(wVol2020) as wVol2020, SUM(wVol2021) as wVol2021, SUM(wVol2022) as wVol2022, SUM(wVol2023) as wVol2023, SUM(wVol2024) as wVol2024, SUM(wVol2025) as wVol2025, SUM(wVol2026) as wVol2026, SUM(wVol2027) as wVol2027, SUM(wVol2028) as wVol2028, SUM(wVol2029) as wVol2029, SUM(wVol2030) as wVol2030, SUM(wVol2031) as wVol2031, SUM(wVol2032) as wVol2032, SUM(wVol2033) as wVol2033, SUM(wVol2034) as wVol2034, SUM(wVol2035) as wVol2035, SUM(wVol2036) as wVol2036, SUM(wVol2037) as wVol2037, SUM(wVol2038) as wVol2038, SUM(wVol2039) as wVol2039, SUM(wVol2040) as wVol2040, SUM(wVol2041) as wVol2041, SUM(wVol2042) as wVol2042, SUM(wVol2043) as wVol2043, SUM(wVol2044) as wVol2044, SUM(wVol2045) as wVol2045, SUM(wVol2046) as wVol2046, SUM(wVol2047) as wVol2047, SUM(wVol2048) as wVol2048, SUM(wVol2049) as wVol2049, \
        SUM(wRev2020) as wRev2020, SUM(wRev2021) as wRev2021, SUM(wRev2022) as wRev2022, SUM(wRev2023) as wRev2023, SUM(wRev2024) as wRev2024, SUM(wRev2025) as wRev2025, SUM(wRev2026) as wRev2026, SUM(wRev2027) as wRev2027, SUM(wRev2028) as wRev2028, SUM(wRev2029) as wRev2029, SUM(wRev2030) as wRev2030, SUM(wRev2031) as wRev2031, SUM(wRev2032) as wRev2032, SUM(wRev2033) as wRev2033, SUM(wRev2034) as wRev2034, SUM(wRev2035) as wRev2035, SUM(wRev2036) as wRev2036, SUM(wRev2037) as wRev2037, SUM(wRev2038) as wRev2038, SUM(wRev2039) as wRev2039, SUM(wRev2040) as wRev2040, SUM(wRev2041) as wRev2041, SUM(wRev2042) as wRev2042, SUM(wRev2043) as wRev2043, SUM(wRev2044) as wRev2044, SUM(wRev2045) as wRev2045, SUM(wRev2046) as wRev2046, SUM(wRev2047) as wRev2047, SUM(wRev2048) as wRev2048, SUM(wRev2049) as wRev2049, \
        SUM(fy_wVol2020) as FY_wVol2020, SUM(fy_wVol2021) as FY_wVol2021, SUM(fy_wVol2022) as FY_wVol2022, SUM(fy_wVol2023) as FY_wVol2023, SUM(fy_wVol2024) as FY_wVol2024, SUM(fy_wVol2025) as FY_wVol2025, SUM(fy_wVol2026) as FY_wVol2026, SUM(fy_wVol2027) as FY_wVol2027, SUM(fy_wVol2028) as FY_wVol2028, SUM(fy_wVol2029) as FY_wVol2029, SUM(fy_wVol2030) as FY_wVol2030, SUM(fy_wVol2031) as FY_wVol2031, SUM(fy_wVol2032) as FY_wVol2032, SUM(fy_wVol2033) as FY_wVol2033, SUM(fy_wVol2034) as FY_wVol2034, SUM(fy_wVol2035) as FY_wVol2035, SUM(fy_wVol2036) as FY_wVol2036, SUM(fy_wVol2037) as FY_wVol2037, SUM(fy_wVol2038) as FY_wVol2038, SUM(fy_wVol2039) as FY_wVol2039, SUM(fy_wVol2040) as FY_wVol2040, SUM(fy_wVol2041) as FY_wVol2041, SUM(fy_wVol2042) as FY_wVol2042, SUM(fy_wVol2043) as FY_wVol2043, SUM(fy_wVol2044) as FY_wVol2044, SUM(fy_wVol2045) as FY_wVol2045, SUM(fy_wVol2046) as FY_wVol2046, SUM(fy_wVol2047) as FY_wVol2047, SUM(fy_wVol2048) as FY_wVol2048, SUM(fy_wVol2049) as FY_wVol2049, \
        SUM(fy_wRev2020) as FY_wRev2020, SUM(fy_wRev2021) as FY_wRev2021, SUM(fy_wRev2022) as FY_wRev2022, SUM(fy_wRev2023) as FY_wRev2023, SUM(fy_wRev2024) as FY_wRev2024, SUM(fy_wRev2025) as FY_wRev2025, SUM(fy_wRev2026) as FY_wRev2026, SUM(fy_wRev2027) as FY_wRev2027, SUM(fy_wRev2028) as FY_wRev2028, SUM(fy_wRev2029) as FY_wRev2029, SUM(fy_wRev2030) as FY_wRev2030, SUM(fy_wRev2031) as FY_wRev2031, SUM(fy_wRev2032) as FY_wRev2032, SUM(fy_wRev2033) as FY_wRev2033, SUM(fy_wRev2034) as FY_wRev2034, SUM(fy_wRev2035) as FY_wRev2035, SUM(fy_wRev2036) as FY_wRev2036, SUM(fy_wRev2037) as FY_wRev2037, SUM(fy_wRev2038) as FY_wRev2038, SUM(fy_wRev2039) as FY_wRev2039, SUM(fy_wRev2040) as FY_wRev2040, SUM(fy_wRev2041) as FY_wRev2041, SUM(fy_wRev2042) as FY_wRev2042, SUM(fy_wRev2043) as FY_wRev2043, SUM(fy_wRev2044) as FY_wRev2044,SUM(fy_wRev2045) as FY_wRev2045, SUM(fy_wRev2046) as FY_wRev2046, SUM(fy_wRev2047) as FY_wRev2047, SUM(fy_wRev2048) as FY_wRev2048, SUM(fy_wRev2049) as FY_wRev2049, \
        SUM(gm2020) as gm2020, SUM(gm2021) as gm2021, SUM(gm2022) as gm2022, SUM(gm2023) as gm2023, SUM(gm2024) as gm2024, SUM(gm2025) as gm2025, SUM(gm2026) as gm2026, SUM(gm2027) as gm2027, SUM(gm2028) as gm2028, SUM(gm2029) as gm2029, SUM(gm2030) as gm2030, SUM(gm2031) as gm2031, SUM(gm2032) as gm2032, SUM(gm2033) as gm2033, SUM(gm2034) as gm2034, SUM(gm2035) as gm2035, SUM(gm2036) as gm2036, SUM(gm2037) as gm2037, SUM(gm2038) as gm2038, SUM(gm2039) as gm2039, SUM(gm2040) as gm2040, SUM(gm2041) as gm2041, SUM(gm2042) as gm2042, SUM(gm2043) as gm2043, SUM(gm2044) as gm2044, SUM(gm2045) as gm2045, SUM(gm2046) as gm2046, SUM(gm2047) as gm2047, SUM(gm2048) as gm2048, SUM(gm2049) as gm2049, \
        SUM(fy_gm2020) as fy_gm2020, SUM(fy_gm2021) as fy_gm2021, SUM(fy_gm2022) as fy_gm2022, SUM(fy_gm2023) as fy_gm2023, SUM(fy_gm2024) as fy_gm2024, SUM(fy_gm2025) as fy_gm2025, SUM(fy_gm2026) as fy_gm2026, SUM(fy_gm2027) as fy_gm2027, SUM(fy_gm2028) as fy_gm2028, SUM(fy_gm2029) as fy_gm2029, SUM(fy_gm2030) as fy_gm2030, SUM(fy_gm2031) as fy_gm2031, SUM(fy_gm2032) as fy_gm2032, SUM(fy_gm2033) as fy_gm2033, SUM(fy_gm2034) as fy_gm2034, SUM(fy_gm2035) as fy_gm2035, SUM(fy_gm2036) as fy_gm2036, SUM(fy_gm2037) as fy_gm2037, SUM(fy_gm2038) as fy_gm2038, SUM(fy_gm2039) as fy_gm2039, SUM(fy_gm2040) as fy_gm2040, SUM(fy_gm2041) as fy_gm2041, SUM(fy_gm2042) as fy_gm2042, SUM(fy_gm2043) as fy_gm2043, SUM(fy_gm2044) as fy_gm2044, SUM(fy_gm2045) as fy_gm2045, SUM(fy_gm2046) as fy_gm2046, SUM(fy_gm2047) as fy_gm2047, SUM(fy_gm2048) as fy_gm2048, SUM(fy_gm2049) as fy_gm2049, \
        endCustomerHelper\
        FROM                                        \
        productMarketingDwh_boup                               \
        GROUP BY                                    \
        series, endCustomer_id, endCustomerHelper                      \
        ORDER BY                                    \
        series, endCustomer_id, endCustomerHelper                \
        "
    #valueDf = duckdb.query(valueQuery).to_df()
    valueDfRaw = rawSqlPerformer(valueQuery)
    valueDf = pd.DataFrame(valueDfRaw)

    yearIntervalls = [5, 10, 20]

    # need to make sure, that there are no 0's inserted in the list
    count = 0
    for row in valueDf.values:
        yearList = []
        wVolList = []
        wRevList = []
        FY_wRevList = []
        FY_wVolList = []
        gmList = []
        FY_gmList = []

        for i in range(0, 30):
            if (row[2+i] != 0 and not row[2+i] is None) or (row[32+i] != 0 and not row[32+i] is None) or (row[62+i] != 0 and not row[62+i] is None) or (row[92+i] != 0 and not row[92+i]) is None:
                yearList.append(str(2020+i))
                wVolList.append(row[2+i])
                wRevList.append(row[32+i])
                FY_wVolList.append(row[62+i])
                FY_wRevList.append(row[92+i])
                gmList.append(row[122+i])
                FY_gmList.append(row[152+i])

        CYgmList = []
        CYvolList = []
        CYwrevList = []
        FYgmList = []
        FYvolList = []
        FYwrevList = []

        gmSum = 0
        volSum = 0
        revSum = 0
        FYgmSum = 0
        FYvolSum = 0
        FYrevSum = 0
        for i in range(0, 3):
            for idx, year in enumerate(yearList):
                if int(year) <= int(this_year) + yearIntervalls[i] and int(year) >= int(this_year):
                    gmSum = gmSum + gmList[idx]
                    volSum = volSum + wVolList[idx]
                    revSum = revSum + wRevList[idx]
                    FYgmSum = FYgmSum + FY_gmList[idx]
                    FYvolSum = FYvolSum + FY_wVolList[idx]
                    FYrevSum = FYrevSum + FY_wRevList[idx]
            CYgmList.append(gmSum)
            CYvolList.append(volSum)
            CYwrevList.append(revSum)
            FYgmList.append(FYgmSum)
            FYvolList.append(FYvolSum)
            FYwrevList.append(FYrevSum)

        jsonElement = {'series': row[0], 'endCustomer_id': row[1], 'endCustomerHelper': row[-1], 'yearIntervall': yearIntervalls, 'CYgm5_10_20': CYgmList,
                       'CYvol5_10_20': CYvolList, 'FYgm5_10_20': FYgmList, 'FYvol5_10_20': FYvolList, 'CYRev5_10_20': CYwrevList, 'FYRev5_10_20': FYwrevList}
        jsonResult[str(count)] = jsonElement
        count = count + 1

    return jsonResult

    '''
    keyQuery = """
    SELECT
    series, endCustomer_id, endCustomerHelper
    FROM
    total_df
    GROUP BY
    series, endCustomer_id, endCustomerHelper
    ;
    """

    keyDf = duckdb.query(keyQuery).to_df()
    #keyDf = ps.sqldf(keyQuery, locals())
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
            series, endCustomer_id, \
            SUM(gm) as CYgm , SUM(wVol) as CYwvol, SUM(fy_gm) as FYgm , SUM(fy_wVol) as FYwvol, SUM(wRev) as CY_wRev, SUM(fy_wRev) as FY_wRev     \
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
            series, endCustomer_id, \
            SUM(gm) as CYgm , SUM(wVol) as CYwvol, SUM(fy_gm) as FYgm , SUM(fy_wVol) as FYwvol, SUM(wRev) as CY_wRev, SUM(fy_wRev) as FY_wRev     \
            FROM                                        \
            total_df                                    \
            WHERE                                       \
            year >=" + this_year + " and year <= " + end_10year + " and series = '" + str(row['series']) + "'and endCustomer_id = " + str(row['endCustomer_id']) + "\
            GROUP BY  series, endCustomer_id )       \
        UNION ALL                                     \
        SELECT *                                       \
        FROM(                                           \
            SELECT                                      \
            series, endCustomer_id, \
            SUM(gm) as CYgm , SUM(wVol) as CYwvol, SUM(fy_gm) as FYgm , SUM(fy_wVol) as FYwvol, SUM(wRev) as CY_wRev, SUM(fy_wRev) as FY_wRev     \
            FROM                                        \
            total_df                                    \
            WHERE                                       \
            year >=" + this_year + " and year <= " + end_20year + " and series = '" + str(row['series']) + "'and endCustomer_id = " + str(row['endCustomer_id']) + "\
            GROUP BY series, endCustomer_id )        \
        ;                                           \
        "
        valueDf = duckdb.query(valueQuery).to_df()
        #valueDf = ps.sqldf(valueQuery, locals())
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
    '''

def fixReq74Left():

    jsonResult = {}

    valueQuery = "                              \
    SELECT                                      \
    gen, series, package, endCustomer_id,                \
    SUM(wVol2020) as wVol2020, SUM(wVol2021) as wVol2021, SUM(wVol2022) as wVol2022, SUM(wVol2023) as wVol2023, SUM(wVol2024) as wVol2024, SUM(wVol2025) as wVol2025, SUM(wVol2026) as wVol2026, SUM(wVol2027) as wVol2027, SUM(wVol2028) as wVol2028, SUM(wVol2029) as wVol2029, SUM(wVol2030) as wVol2030, SUM(wVol2031) as wVol2031, SUM(wVol2032) as wVol2032, SUM(wVol2033) as wVol2033, SUM(wVol2034) as wVol2034, SUM(wVol2035) as wVol2035, SUM(wVol2036) as wVol2036, SUM(wVol2037) as wVol2037, SUM(wVol2038) as wVol2038, SUM(wVol2039) as wVol2039, SUM(wVol2040) as wVol2040, SUM(wVol2041) as wVol2041, SUM(wVol2042) as wVol2042, SUM(wVol2043) as wVol2043, SUM(wVol2044) as wVol2044, SUM(wVol2045) as wVol2045, SUM(wVol2046) as wVol2046, SUM(wVol2047) as wVol2047, SUM(wVol2048) as wVol2048, SUM(wVol2049) as wVol2049, \
    SUM(wRev2020) as wRev2020, SUM(wRev2021) as wRev2021, SUM(wRev2022) as wRev2022, SUM(wRev2023) as wRev2023, SUM(wRev2024) as wRev2024, SUM(wRev2025) as wRev2025, SUM(wRev2026) as wRev2026, SUM(wRev2027) as wRev2027, SUM(wRev2028) as wRev2028, SUM(wRev2029) as wRev2029, SUM(wRev2030) as wRev2030, SUM(wRev2031) as wRev2031, SUM(wRev2032) as wRev2032, SUM(wRev2033) as wRev2033, SUM(wRev2034) as wRev2034, SUM(wRev2035) as wRev2035, SUM(wRev2036) as wRev2036, SUM(wRev2037) as wRev2037, SUM(wRev2038) as wRev2038, SUM(wRev2039) as wRev2039, SUM(wRev2040) as wRev2040, SUM(wRev2041) as wRev2041, SUM(wRev2042) as wRev2042, SUM(wRev2043) as wRev2043, SUM(wRev2044) as wRev2044, SUM(wRev2045) as wRev2045, SUM(wRev2046) as wRev2046, SUM(wRev2047) as wRev2047, SUM(wRev2048) as wRev2048, SUM(wRev2049) as wRev2049, \
    SUM(fy_wVol2020) as FY_wVol2020, SUM(fy_wVol2021) as FY_wVol2021, SUM(fy_wVol2022) as FY_wVol2022, SUM(fy_wVol2023) as FY_wVol2023, SUM(fy_wVol2024) as FY_wVol2024, SUM(fy_wVol2025) as FY_wVol2025, SUM(fy_wVol2026) as FY_wVol2026, SUM(fy_wVol2027) as FY_wVol2027, SUM(fy_wVol2028) as FY_wVol2028, SUM(fy_wVol2029) as FY_wVol2029, SUM(fy_wVol2030) as FY_wVol2030, SUM(fy_wVol2031) as FY_wVol2031, SUM(fy_wVol2032) as FY_wVol2032, SUM(fy_wVol2033) as FY_wVol2033, SUM(fy_wVol2034) as FY_wVol2034, SUM(fy_wVol2035) as FY_wVol2035, SUM(fy_wVol2036) as FY_wVol2036, SUM(fy_wVol2037) as FY_wVol2037, SUM(fy_wVol2038) as FY_wVol2038, SUM(fy_wVol2039) as FY_wVol2039, SUM(fy_wVol2040) as FY_wVol2040, SUM(fy_wVol2041) as FY_wVol2041, SUM(fy_wVol2042) as FY_wVol2042, SUM(fy_wVol2043) as FY_wVol2043, SUM(fy_wVol2044) as FY_wVol2044, SUM(fy_wVol2045) as FY_wVol2045, SUM(fy_wVol2046) as FY_wVol2046, SUM(fy_wVol2047) as FY_wVol2047, SUM(fy_wVol2048) as FY_wVol2048, SUM(fy_wVol2049) as FY_wVol2049, \
    SUM(fy_wRev2020) as FY_wRev2020, SUM(fy_wRev2021) as FY_wRev2021, SUM(fy_wRev2022) as FY_wRev2022, SUM(fy_wRev2023) as FY_wRev2023, SUM(fy_wRev2024) as FY_wRev2024, SUM(fy_wRev2025) as FY_wRev2025, SUM(fy_wRev2026) as FY_wRev2026, SUM(fy_wRev2027) as FY_wRev2027, SUM(fy_wRev2028) as FY_wRev2028, SUM(fy_wRev2029) as FY_wRev2029, SUM(fy_wRev2030) as FY_wRev2030, SUM(fy_wRev2031) as FY_wRev2031, SUM(fy_wRev2032) as FY_wRev2032, SUM(fy_wRev2033) as FY_wRev2033, SUM(fy_wRev2034) as FY_wRev2034, SUM(fy_wRev2035) as FY_wRev2035, SUM(fy_wRev2036) as FY_wRev2036, SUM(fy_wRev2037) as FY_wRev2037, SUM(fy_wRev2038) as FY_wRev2038, SUM(fy_wRev2039) as FY_wRev2039, SUM(fy_wRev2040) as FY_wRev2040, SUM(fy_wRev2041) as FY_wRev2041, SUM(fy_wRev2042) as FY_wRev2042, SUM(fy_wRev2043) as FY_wRev2043, SUM(fy_wRev2044) as FY_wRev2044,SUM(fy_wRev2045) as FY_wRev2045, SUM(fy_wRev2046) as FY_wRev2046, SUM(fy_wRev2047) as FY_wRev2047, SUM(fy_wRev2048) as FY_wRev2048, SUM(fy_wRev2049) as FY_wRev2049, \
    SUM(price2020) as price2020, SUM(price2021) as price2021, SUM(price2022) as price2022, SUM(price2023) as price2023, SUM(price2024) as price2024, SUM(price2025) as price2025, SUM(price2026) as price2026, SUM(price2027) as price2027, SUM(price2028) as price2028, SUM(price2029) as price2029, SUM(price2030) as price2030, SUM(price2031) as price2031, SUM(price2032) as price2032, SUM(price2033) as price2033, SUM(price2034) as price2034, SUM(price2035) as price2035, SUM(price2036) as price2036, SUM(price2037) as price2037, SUM(price2038) as price2038, SUM(price2039) as price2039, SUM(price2040) as price2040, SUM(price2041) as price2041, SUM(price2042) as price2042, SUM(price2043) as price2043, SUM(price2044) as price2044, SUM(price2045) as price2045, SUM(price2046) as price2046, SUM(price2047) as price2047, SUM(price2048) as price2048, SUM(price2049) as price2049, \
    endCustomerHelper\
    FROM                                        \
    productMarketingDwh_boup                                 \
    GROUP BY                                    \
    gen, series, package, endCustomer_id, endCustomerHelper                 \
    ORDER BY                                    \
    gen, series, package, endCustomer_id , endCustomerHelper                \
    ;                                           \
    "
    #valueDf = duckdb.query(valueQuery).to_df()
    valueDfRaw = rawSqlPerformer(valueQuery)
    valueDf = pd.DataFrame(valueDfRaw)

    # need to make sure, that there are no 0's inserted in the list
    count = 0
    for row in valueDf.values:
        yearList = []
        wVolList = []
        wRevList = []
        FY_wRevList = []
        FY_wVolList = []
        priceList = []

        # print("row")
        # print(row)
        for i in range(0, 30):
            # 4-28 first, 29-53 second, 54-78thrid, 79-103 forth
            if (row[4+i] != 0 and not row[4+i] is None) or (row[34+i] != 0 and not row[34+i] is None) or (row[64+i] != 0 and not row[64+i] is None) or (row[94+i] != 0 and not row[94+i]) is None:
                yearList.append(str(2020+i))
                wVolList.append(row[4+i])
                wRevList.append(row[34+i])
                FY_wVolList.append(row[64+i])
                FY_wRevList.append(row[94+i])
                priceList.append(row[124+i])


        jsonElement = {'gen': row[0], 'series': row[1], 'package': row[2], 'endCustomer_id': row[3], 'endCustomerHelper': row[-1], 'year': yearList, 'CYwRev': wRevList, 'CYwVol': wVolList, 'avg_price': priceList, 'FYwRev': FY_wRevList, 'FYwVol': FY_wVolList}

        jsonResult[str(count)] = jsonElement
        count = count + 1

    return jsonResult



def fixReq75LeftTop():
    jsonResult = {}

    valueQuery = "                              \
    SELECT                                      \
    gen, series, package, endCustomer_id,                \
    SUM(wVol2020) as wVol2020, SUM(wVol2021) as wVol2021, SUM(wVol2022) as wVol2022, SUM(wVol2023) as wVol2023, SUM(wVol2024) as wVol2024, SUM(wVol2025) as wVol2025, SUM(wVol2026) as wVol2026, SUM(wVol2027) as wVol2027, SUM(wVol2028) as wVol2028, SUM(wVol2029) as wVol2029, SUM(wVol2030) as wVol2030, SUM(wVol2031) as wVol2031, SUM(wVol2032) as wVol2032, SUM(wVol2033) as wVol2033, SUM(wVol2034) as wVol2034, SUM(wVol2035) as wVol2035, SUM(wVol2036) as wVol2036, SUM(wVol2037) as wVol2037, SUM(wVol2038) as wVol2038, SUM(wVol2039) as wVol2039, SUM(wVol2040) as wVol2040, SUM(wVol2041) as wVol2041, SUM(wVol2042) as wVol2042, SUM(wVol2043) as wVol2043, SUM(wVol2044) as wVol2044, SUM(wVol2045) as wVol2045, SUM(wVol2046) as wVol2046, SUM(wVol2047) as wVol2047, SUM(wVol2048) as wVol2048, SUM(wVol2049) as wVol2049, \
    SUM(wRev2020) as wRev2020, SUM(wRev2021) as wRev2021, SUM(wRev2022) as wRev2022, SUM(wRev2023) as wRev2023, SUM(wRev2024) as wRev2024, SUM(wRev2025) as wRev2025, SUM(wRev2026) as wRev2026, SUM(wRev2027) as wRev2027, SUM(wRev2028) as wRev2028, SUM(wRev2029) as wRev2029, SUM(wRev2030) as wRev2030, SUM(wRev2031) as wRev2031, SUM(wRev2032) as wRev2032, SUM(wRev2033) as wRev2033, SUM(wRev2034) as wRev2034, SUM(wRev2035) as wRev2035, SUM(wRev2036) as wRev2036, SUM(wRev2037) as wRev2037, SUM(wRev2038) as wRev2038, SUM(wRev2039) as wRev2039, SUM(wRev2040) as wRev2040, SUM(wRev2041) as wRev2041, SUM(wRev2042) as wRev2042, SUM(wRev2043) as wRev2043, SUM(wRev2044) as wRev2044, SUM(wRev2045) as wRev2045, SUM(wRev2046) as wRev2046, SUM(wRev2047) as wRev2047, SUM(wRev2048) as wRev2048, SUM(wRev2049) as wRev2049, \
    SUM(fy_wVol2020) as FY_wVol2020, SUM(fy_wVol2021) as FY_wVol2021, SUM(fy_wVol2022) as FY_wVol2022, SUM(fy_wVol2023) as FY_wVol2023, SUM(fy_wVol2024) as FY_wVol2024, SUM(fy_wVol2025) as FY_wVol2025, SUM(fy_wVol2026) as FY_wVol2026, SUM(fy_wVol2027) as FY_wVol2027, SUM(fy_wVol2028) as FY_wVol2028, SUM(fy_wVol2029) as FY_wVol2029, SUM(fy_wVol2030) as FY_wVol2030, SUM(fy_wVol2031) as FY_wVol2031, SUM(fy_wVol2032) as FY_wVol2032, SUM(fy_wVol2033) as FY_wVol2033, SUM(fy_wVol2034) as FY_wVol2034, SUM(fy_wVol2035) as FY_wVol2035, SUM(fy_wVol2036) as FY_wVol2036, SUM(fy_wVol2037) as FY_wVol2037, SUM(fy_wVol2038) as FY_wVol2038, SUM(fy_wVol2039) as FY_wVol2039, SUM(fy_wVol2040) as FY_wVol2040, SUM(fy_wVol2041) as FY_wVol2041, SUM(fy_wVol2042) as FY_wVol2042, SUM(fy_wVol2043) as FY_wVol2043, SUM(fy_wVol2044) as FY_wVol2044, SUM(fy_wVol2045) as FY_wVol2045, SUM(fy_wVol2046) as FY_wVol2046, SUM(fy_wVol2047) as FY_wVol2047, SUM(fy_wVol2048) as FY_wVol2048, SUM(fy_wVol2049) as FY_wVol2049, \
    SUM(fy_wRev2020) as FY_wRev2020, SUM(fy_wRev2021) as FY_wRev2021, SUM(fy_wRev2022) as FY_wRev2022, SUM(fy_wRev2023) as FY_wRev2023, SUM(fy_wRev2024) as FY_wRev2024, SUM(fy_wRev2025) as FY_wRev2025, SUM(fy_wRev2026) as FY_wRev2026, SUM(fy_wRev2027) as FY_wRev2027, SUM(fy_wRev2028) as FY_wRev2028, SUM(fy_wRev2029) as FY_wRev2029, SUM(fy_wRev2030) as FY_wRev2030, SUM(fy_wRev2031) as FY_wRev2031, SUM(fy_wRev2032) as FY_wRev2032, SUM(fy_wRev2033) as FY_wRev2033, SUM(fy_wRev2034) as FY_wRev2034, SUM(fy_wRev2035) as FY_wRev2035, SUM(fy_wRev2036) as FY_wRev2036, SUM(fy_wRev2037) as FY_wRev2037, SUM(fy_wRev2038) as FY_wRev2038, SUM(fy_wRev2039) as FY_wRev2039, SUM(fy_wRev2040) as FY_wRev2040, SUM(fy_wRev2041) as FY_wRev2041, SUM(fy_wRev2042) as FY_wRev2042, SUM(fy_wRev2043) as FY_wRev2043, SUM(fy_wRev2044) as FY_wRev2044,SUM(fy_wRev2045) as FY_wRev2045, SUM(fy_wRev2046) as FY_wRev2046, SUM(fy_wRev2047) as FY_wRev2047, SUM(fy_wRev2048) as FY_wRev2048, SUM(fy_wRev2049) as FY_wRev2049, \
    SUM(price2020) as price2020, SUM(price2021) as price2021, SUM(price2022) as price2022, SUM(price2023) as price2023, SUM(price2024) as price2024, SUM(price2025) as price2025, SUM(price2026) as price2026, SUM(price2027) as price2027, SUM(price2028) as price2028, SUM(price2029) as price2029, SUM(price2030) as price2030, SUM(price2031) as price2031, SUM(price2032) as price2032, SUM(price2033) as price2033, SUM(price2034) as price2034, SUM(price2035) as price2035, SUM(price2036) as price2036, SUM(price2037) as price2037, SUM(price2038) as price2038, SUM(price2039) as price2039, SUM(price2040) as price2040, SUM(price2041) as price2041, SUM(price2042) as price2042, SUM(price2043) as price2043, SUM(price2044) as price2044, SUM(price2045) as price2045, SUM(price2046) as price2046, SUM(price2047) as price2047, SUM(price2048) as price2048, SUM(price2049) as price2049, \
    endCustomerHelper\
    FROM                                        \
    productMarketingDwh_boup                                 \
    GROUP BY                                    \
    gen, series, package, endCustomer_id, endCustomerHelper                 \
    ORDER BY                                    \
    gen, series, package, endCustomer_id , endCustomerHelper                \
    ;                                           \
    "
    #valueDf = duckdb.query(valueQuery).to_df()
    valueDfRaw = rawSqlPerformer(valueQuery)
    valueDf = pd.DataFrame(valueDfRaw)

    # need to make sure, that there are no 0's inserted in the list
    count = 0
    for row in valueDf.values:
        yearList = []
        wVolList = []
        wRevList = []
        FY_wRevList = []
        FY_wVolList = []
        priceList = []

        # print("row")
        # print(row)
        for i in range(0, 30):
            # 4-28 first, 29-53 second, 54-78thrid, 79-103 forth
            if (row[4+i] != 0 and not row[4+i] is None) or (row[34+i] != 0 and not row[34+i] is None) or (row[64+i] != 0 and not row[64+i] is None) or (row[94+i] != 0 and not row[94+i]) is None:
                yearList.append(str(2020+i))
                wVolList.append(row[4+i])
                wRevList.append(row[34+i])
                FY_wVolList.append(row[64+i])
                FY_wRevList.append(row[94+i])
                priceList.append(row[124+i])


        jsonElement = {'gen': row[0], 'series': row[1], 'package': row[2], 'endCustomer_id': row[3], 'endCustomerHelper': row[-1], 'year': yearList, 'CYwRev': wRevList, 'CYwVol': wVolList, 'avg_price': priceList, 'FYwRev': FY_wRevList, 'FYwVol': FY_wVolList}

        jsonResult[str(count)] = jsonElement
        count = count + 1

    return jsonResult




def basicFilter():  # same customer, same faimly, different prices  Values: silicon or package level, different customers.  Y: ASP in EUR, X: year.

    FinalCustomer = FinalCustomers.objects.all()
    allFinalCustomer = [(-1, "fieldMissing")]
    for item in FinalCustomer:
        if item.finalCustomerName not in allFinalCustomer:
            id = FinalCustomers.objects.filter(
                finalCustomerName=item.finalCustomerName).values('id')[0]['id']
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

    jsonDic = {'finalCustomer': allFinalCustomer, 'family': allProductFamily,
               'series': allProductSeries, 'package': allProductPackage}

    # old code old exchange rates model

    try:
        CurrencyExRates = ExchangeRates.objects.filter(currency_id=1, valid=1)
        # print(CurrencyExRates)
        if CurrencyExRates:  # if entries exists
            jsonDic["currencyRate"] = CurrencyExRates[0].rate
            # print(CurrencyExRates[0].rate)
        else:
            jsonDic["currencyRate"] = 1.0
    except:
        jsonDic["currencyRate"] = 1.0

    """

    1te Linie: EUR - € - 1.0000
    2te Line: USD - $ - 1.0005
    3te Line: JPY - J - 10.0000
    CurrencyExRates = Currency.objects.filter(is_active = 1)
    #print(CurrencyExRates)

    if CurrencyExRates: #if entries exists
        currencies = {}
        for currency in CurrencyExRates:
            currencyName = currency.code
            currencies[currencyName] = currency.factor
            #print(CurrencyExRates[0].rate)


        jsonDic["currencies"] = currencies
    """

    return jsonDic


""""
This function is used starting Feb 23rd
"""


class AnalyticDashboardCar(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def get(self, request):

        print("getting Analytics Dashboard")
        # get the start time
        st = time.time()
        ###
        #total_df = restructure_whole()
        #df_boup = pd.DataFrame(list(BoUp.objects.all().values()))
        today = datetime.date.today()
        year = today.strftime("%Y")

        filterJson = basicFilter()
        # req 73
        one_left = Dashboard1Left()
        one_middle = Dashboard1Middle()
        one_right = Dashboard1Right()

        # req 74
        # two_left = one_right #same data
        two_right = Dashboard2Right()

        # req 75
        # three_lefttop = two_left #same data
        three_leftbottom = Dashboard3Leftbottom()
        three_right = Dashboard3Right()

        # req 76
        # four_lefttop = one_right #same data
        four_leftbottom = Dashboard4Leftbottom()
        # four_right = three_right #same data

        # req 77
        five_json = Dashboard5()

        # req 78
        six_json = DashboardBubble(year)

        """
        req 79, 80 are using the same datasets as req 78
        """

        # req 79
        # seven_json = six_json #same data

        # req 80
        # eight_json = six_json #same data
        #fixes

        Left74 = fixReq74Left()
        leftTop75 = fixReq75LeftTop()
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% finished with analytics dashboard")
        # get the end time
        et = time.time()
        elapsed_time = et - st
        print('Execution time:', elapsed_time, 'seconds')
        return JsonResponse({"first": {"req73_data_right": one_right, "req73_data_middle": one_middle, "req73_data_left": one_left, "filter": filterJson},
                             "second": {"req74_data_right": two_right, "req74_data_left": Left74, "filter": filterJson},
                             "third": {"req75_data_right": three_right, "req75_data_lefttop": leftTop75, "req75_data_leftbottom": three_leftbottom, "filter": filterJson},
                             "forth": {"req76_data_right": three_right, "req76_data_lefttop": one_right, "req76_data_leftbottom": four_leftbottom, "filter": filterJson},
                             "fifth": {"req77_data": five_json, "filter": filterJson},
                             "sixth": {"req78_data": six_json, "filter": filterJson},
                             "seventh": {"req79_data": six_json, "filter": filterJson},
                             "eightth": {"req80_data": six_json, "filter": filterJson}}, safe=True)
