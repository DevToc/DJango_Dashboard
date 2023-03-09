import pandas as pd

from sqlite3 import Error
import pandasql as ps
from productMarketingDwh.models import *


#first split into to budle and not to bundle, then bundle the ones needed to and after that join those two
#also create entries in a table which links the bundled entry to the small ones and send the joined table to frontend, so when clicking on the extend tab you see the inenr join between those two tables with the key(like a filter)

#or just create a new column which indicates into which group there are joined together and on frontend show whole agg. table and after clickign on extend show the original table filtered on the id

#this function gives the aggregated version, send this and boup to frontend and filter there with the bundleKey
def bundleCustomer(df):
    print("this df is having the SQL statement:", df)
    df_res = restructure_whole(df)
    df_fil = df_res[(df_res['vol'] > 0)] # to get only the rows which have entries 

    #bundle condition
    df_prep = df_fil.groupby(['reviewDate','ID_APP','applicationLine','productMarketer','hfg','ppos','spNumber','applicationMain','applicationDetail','rfp','salesName','priceSource','familyPriceApplicable','familyPriceDetails','priceType','currency','fxRate','comment','region','projectName','mainCustomer','endCustomer','distributor','tier1','oem','ems','vpaCustomer','dragonId','salesContact','probability','statusProbability','sop','availablePGS','modifiedBy','modifiedDate','creationDate','timeBottomUp','basicType','package','series','gen','seriesLong','genDetail','gmLifeTime','revEurLifeTime','volLifeTime','volWeightedLifeTime'])['fy_wVol' ,'fy_wRev', 'fy_vol', 'fy_gm', 'wVol', 'wRev', 'vhk', 'gm', 'volCustomer', 'price', 'vol'].sum()
    df_reduc = df_prep[(df_prep['vol'] < 500)] #this is the condition to bundle

    #propably the PKs
    #df_bundle = df_reduc[["ID_APP", "applicationLine","applicationMain","applicationDetail","rfp","salesName","mainCustomer","endCustomer"]]

    #group them by mainCustomer and endCustomer (boundleKey)
    df_bundle = df_reduc.groupby(["mainCustomer","endCustomer"])['fy_wVol' ,'fy_wRev', 'fy_vol', 'fy_gm', 'wVol', 'wRev', 'vhk', 'gm', 'volCustomer', 'price', 'vol'].sum()



    '''
    queryAggDf = """

    """

    queryResult = ps.sqldf(queryAggDf, locals())
    '''

    #print("SQL result:",query_result_family)

    return  df_bundle 

