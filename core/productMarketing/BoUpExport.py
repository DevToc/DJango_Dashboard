import pandas as pd
import xlsxwriter
from .models import SalesName, MainCustomers, FinalCustomers, ApplicationMain, ApplicationDetail, marketerMetadata
from core.project.models import ProjectStatus
import datetime
import numpy as np
from .queryJobs.SQL_query import *
from django.utils import timezone


def excelExport(inputParams, team, marketer, df):
    runDate = datetime.datetime.today().strftime('%Y-%m-%d')

    filePath = "./persistentLayer/temp/" + "m_" + \
        str(marketer) + "_" + str(runDate) + "_BoUpExport.xlsx"
    workbook = xlsxwriter.Workbook(filePath)
    worksheet = workbook.add_worksheet()
    column_headers = list(df.columns.values)
    unlocked = workbook.add_format({'locked': False})

    for idx, column in enumerate(column_headers):
        worksheet.write(0, idx, column_headers[idx])

    for idx, column in enumerate(column_headers):
        #print("Column", column)
        if column in column_headers[49:]:
            used_format = unlocked
            for row in range(len(df.index)):
                if isinstance(df.iloc[row, idx], datetime.datetime):
                    worksheet.write(
                        row+1, idx, str(df.iloc[row, idx]), used_format)
                elif pd.isnull(df.iloc[row, idx]):
                    worksheet.write(row+1, idx, "", used_format)
                else:
                    worksheet.write(
                        row+1, idx, df.iloc[row, idx], used_format)

    print("file done", filePath)
    workbook.close()
    return filePath


def protectCellsInExcel(inputParams, team, marketer):
    runDate = datetime.datetime.today().strftime('%Y-%m-%d')

    filePath = "/persistentLayer/temp/" + "m_" + \
        str(marketer) + "_" + str(runDate) + "_BoUpExport.xlsx"
    filePath = "m_" + \
        str(marketer) + "_" + str(runDate) + "_BoUpExport.xlsx"

    # xlsxwriter.Workbook('BoUp.xlsx')
    workbook = xlsxwriter.Workbook(filePath)
    worksheet = workbook.add_worksheet()

    boup_df = None

    # BoUp.objects.all()  # restructure_whole()
    if inputParams == "all":
        boup_df = pd.DataFrame(
            list(BoUp.objects.select_related().all().values()))
    elif inputParams == "boupTemplateMyTeamProjects":
        boup_df = pd.DataFrame(
            list(BoUp.objects.select_related().all().values()))
    else:
        boup_df = pd.DataFrame(
            list(BoUp.objects.select_related().filter(productMarketer=marketer).values()))

    # Turn worksheet protection on.
    worksheet.protect()
    column_headers = list(boup_df.columns.values)

    Marketer = marketerMetadata.objects.all()
    allMarketers = []
    for item in Marketer:
        allMarketers.append(item.name)

    MainCustomer = MainCustomers.objects.all()
    allMainCustomers = []
    for item in MainCustomer:
        allMainCustomers.append(item.customerName)

    FinalCustomer = FinalCustomers.objects.all()
    allFinalCustomer = []
    for item in FinalCustomer:
        allFinalCustomer.append(item.finalCustomerName)

    ApplicationMains = ApplicationMain.objects.all()
    allApplicationMain = []
    for item in ApplicationMains:
        allApplicationMain.append(item.appMainDescription)

    ApplicationDetails = ApplicationDetail.objects.all()
    allApplicationDetail = []
    for item in ApplicationDetails:
        allApplicationDetail.append(item.appDetailDescription)

    vpaCustomerDetails = VPACustomers.objects.all()
    allvpaCustomerDetails = []
    for item in vpaCustomerDetails:
        allvpaCustomerDetails.append(item.customerName)

    distributorDetails = Distributors.objects.all()
    allDistributorDetails = []
    for item in distributorDetails:
        allDistributorDetails.append(item.distributorName)

    tier1Details = Tier1.objects.all()
    alltier1Details = []
    for item in tier1Details:
        alltier1Details.append(item.tierOneName)

    oemDetails = OEM.objects.all()
    alloemDetails = []
    for item in oemDetails:
        alloemDetails.append(item.oemName)

    emsDetails = EMS.objects.all()
    allemsDetails = []
    for item in emsDetails:
        allemsDetails.append(item.emsName)

    products = Product.objects.all()
    allProductDetails = []
    for item in products:
        allProductDetails.append(item.rfp)

    Salesnames = SalesName.objects.all()
    allSalesName = []
    for item in Salesnames:
        allSalesName.append(item.name)


    distributorDetails = Distributors.objects.all()
    allDistributorDetails = []
    for item in distributorDetails:
        allDistributorDetails.append(item.distributorName)

    tier1Details = Tier1.objects.all()
    alltier1Details = []
    for item in tier1Details:
        alltier1Details.append(item.tierOneName)

    oemDetails = OEM.objects.all()
    alloemDetails = []
    for item in oemDetails:
        alloemDetails.append(item.oemName)

    emsDetails = EMS.objects.all()
    allemsDetails = []
    for item in emsDetails:
        allemsDetails.append(item.emsName)

    products = Product.objects.all()
    allProductDetails = []
    for item in products:
        allProductDetails.append(item.rfp)

    vpaCustomerDetails = VPACustomers.objects.all()
    allvpaCustomerDetails = []
    for item in vpaCustomerDetails:
        allvpaCustomerDetails.append(item.customerName)

    marketerDetails = marketerMetadata.objects.all()
    allmarketerDetails = []
    for item in marketerDetails:
        allmarketerDetails.append(item.name + "_" + item.familyName)

    """
    # status probability
    statusDetails = ProjectStatus.objects.all()
    allstatusDetails = []
    for item in statusDetails:
        allstatusDetails.append(item.statusDisplay)
    """

    # dragon id

    ##

    unlocked = workbook.add_format({'locked': False, 'num_format': '#,##0.00'}) 
    locked = workbook.add_format({'locked': True, 'num_format': '#,##0.00'})
    locked.set_pattern(1)
    locked.set_bg_color('gray')
    dropDown = workbook.add_format({'locked': False, 'num_format': '#,##0.00'})
    dropDown.set_pattern(1)
    dropDown.set_bg_color('yellow')

    currencyUnlocked = workbook.add_format({'locked': False, 'num_format': '$#,##0.00'})
    currencyLocked = workbook.add_format({'locked': True, 'num_format': '$#,##0.00'})
    currencyLocked.set_pattern(1)
    currencyLocked.set_bg_color('gray')   
    for idx, column in enumerate(column_headers):
        worksheet.write(0, idx, column_headers[idx])
    #print("added headers")
    #print(column_headers)

    dropDownColumns = ["productMarketer_id"]
    changeableColumns = [ "vol2020", "vol2021", "vol2022", "vol2023", "vol2024", "vol2025", "vol2026", "vol2027", "vol2028", "vol2029", "vol2030", "vol2031", "vol2032", "vol2033", "vol2034", "vol2035", "vol2036", "vol2037", "vol2038", "vol2039", "vol2040", "vol2041", "vol2042", "vol2043", "vol2044",
                           "price2020", "price2021", "price2022", "price2023", "price2024", "price2025", "price2026", "price2027", "price2028", "price2029", "price2030", "price2031", "price2032", "price2033", "price2034", "price2035", "price2036", "price2037", "price2038", "price2039", "price2040", "price2041", "price2042", "price2043", "price2044"]
    currencyColumns = ["revEurLifeTime",
                       "price2020", "price2021", "price2022", "price2023", "price2024", "price2025", "price2026", "price2027", "price2028", "price2029", "price2030", "price2031", "price2032", "price2033", "price2034", "price2035", "price2036", "price2037", "price2038", "price2039", "price2040", "price2041", "price2042", "price2043", "price2044",
                       "vhk2020", "vhk2021", "vhk2022", "vhk2023", "vhk2024", "vhk2025", "vhk2026", "vhk2027", "vhk2028", "vhk2029", "vhk2030", "vhk2031", "vhk2032", "vhk2033", "vhk2034", "vhk2035", "vhk2036", "vhk2037", "vhk2038", "vhk2039", "vhk2040", "vhk2041", "vhk2042", "vhk2043", "vhk2044",
                       "gm2020", "gm2021", "gm2022", "gm2023", "gm2024", "gm2025", "gm2026", "gm2027", "gm2028", "gm2029", "gm2030", "gm2031", "gm2032", "gm2033", "gm2034", "gm2035", "gm2036", "gm2037", "gm2038", "gm2039", "gm2040", "gm2041", "gm2042", "gm2043", "gm2044",
                       "wRev2020", "wRev2021", "wRev2022", "wRev2023", "wRev2024", "wRev2025", "wRev2026", "wRev2027", "wRev2028", "wRev2029", "wRev2030", "wRev2031", "wRev2032", "wRev2033", "wRev2034", "wRev2035", "wRev2036", "wRev2037", "wRev2038", "wRev2039", "wRev2040", "wRev2041", "wRev2042", "wRev2043", "wRev2044",
                       "wGrossMargin2020", "wGrossMargin2021", "wGrossMargin2022", "wGrossMargin2023", "wGrossMargin2024", "wGrossMargin2025", "wGrossMargin2026", "wGrossMargin2027", "wGrossMargin2028", "wGrossMargin2029", "wGrossMargin2030", "wGrossMargin2031", "wGrossMargin2032", "wGrossMargin2033", "wGrossMargin2034", "wGrossMargin2035", "wGrossMargin2036", "wGrossMargin2037", "wGrossMargin2038", "wGrossMargin2039", "wGrossMargin2040", "wGrossMargin2041", "wGrossMargin2042", "wGrossMargin2043", "wGrossMargin2044",
                       "asp2020", "asp2021", "asp2022", "asp2023", "asp2024", "asp2025", "asp2026", "asp2027", "asp2028", "asp2029", "asp2030", "asp2031", "asp2032", "asp2033", "asp2034", "asp2035", "asp2036", "asp2037", "asp2038", "asp2039", "asp2040", "asp2041", "asp2042", "asp2043", "asp2044",
                       "fy_gm2020", "fy_gm2021", "fy_gm2022", "fy_gm2023", "fy_gm2024", "fy_gm2025", "fy_gm2026", "fy_gm2027", "fy_gm2028", "fy_gm2029", "fy_gm2030", "fy_gm2031", "fy_gm2032", "fy_gm2033", "fy_gm2034", "fy_gm2035", "fy_gm2036", "fy_gm2037", "fy_gm2038", "fy_gm2039", "fy_gm2040", "fy_gm2041", "fy_gm2042", "fy_gm2043", "fy_gm2044",
                       "fy_wRev2020", "fy_wRev2021", "fy_wRev2022", "fy_wRev2023", "fy_wRev2024", "fy_wRev2025", "fy_wRev2026", "fy_wRev2027", "fy_wRev2028", "fy_wRev2029", "fy_wRev2030", "fy_wRev2031", "fy_wRev2032", "fy_wRev2033", "fy_wRev2034", "fy_wRev2035", "fy_wRev2036", "fy_wRev2037", "fy_wRev2038", "fy_wRev2039", "fy_wRev2040", "fy_wRev2041", "fy_wRev2042", "fy_wRev2043", "fy_wRev2044"
                       ]
    used_format = locked
    for idx, column in enumerate(column_headers):
        #print("Column", column)
        width = 10
        if len(column) > 10:
            width = len(column) +5
        worksheet.set_column(idx, idx, width)
        if column in changeableColumns:
            if column in currencyColumns:
                used_format = currencyUnlocked
            else:
                used_format = unlocked
        elif column in dropDownColumns:
            used_format = dropDown
        elif column in currencyColumns:
            used_format = currencyLocked
        if column == "productMarketer_id":
            for row in range(len(boup_df.index)):
                entry = marketerMetadata.objects.get(id = boup_df.iloc[row,idx])
                worksheet.write(row+1, idx, entry.name, used_format)  
                worksheet.data_validation( 1,idx,1048575,idx, {'validate': 'list', 
                                         'source': allMarketers})

        elif column == "salesName_id":
            for row in range(len(boup_df.index)):
                entry = Salesnames.get(id=boup_df.iloc[row, idx])
                worksheet.write(row+1, idx, entry.name, used_format)
                worksheet.data_validation(1, idx, 1048575, idx, {'validate': 'list',
                                                                    'source': allSalesName})
        elif column == "mainCustomer_id":
            for row in range(len(boup_df.index)):
                entry = MainCustomer.get(
                    id=boup_df.iloc[row, idx])
                worksheet.write(
                    row+1, idx, entry.customerName, used_format)
                worksheet.data_validation(1, idx, 1048575, idx, {'validate': 'list',
                                                                    'source': allMainCustomers})
        elif column == "endCustomer_id":
            for row in range(len(boup_df.index)):
                entry = FinalCustomer.get(
                    id=boup_df.iloc[row, idx])
                worksheet.write(
                    row+1, idx, entry.finalCustomerName, used_format)
                worksheet.data_validation(1, idx, 1048575, idx, {'validate': 'list',
                                                                    'source': allFinalCustomer})
        elif column == "applicationMain_id":
            for row in range(len(boup_df.index)):
                entry = ApplicationMains.get(
                    id=boup_df.iloc[row, idx])
                worksheet.write(
                    row+1, idx, entry.appMainDescription, used_format)
                worksheet.data_validation(1, idx, 1048575, idx, {'validate': 'list',
                                                                    'source': allApplicationMain})
        elif column == "applicationDetail_id":
            for row in range(len(boup_df.index)):
                entry = ApplicationDetails.get(
                    id=boup_df.iloc[row, idx])
                worksheet.write(
                    row+1, idx, entry.appDetailDescription, used_format)
                worksheet.data_validation(1, idx, 1048575, idx, {'validate': 'list',
                                                                    'source': allApplicationDetail})

        # rfp, ems, disti, tier1, oem, vpa without dropdown
        elif column == "rfp_id":
            for row in range(len(boup_df.index)):
                entry = products.get(
                    id=boup_df.iloc[row, idx])
                worksheet.write(
                    row+1, idx, entry.rfp, used_format)

        elif column == "tier1_id":
            for row in range(len(boup_df.index)):
                try:
                    entry = tier1Details.get(
                        id=boup_df.iloc[row, idx])
                    worksheet.write(
                        row+1, idx, entry.tierOneName, used_format)
                except:
                    pass

        elif column == "ems_id":
            for row in range(len(boup_df.index)):
                try:
                    entry = emsDetails.get(
                        id=boup_df.iloc[row, idx])
                    worksheet.write(
                        row+1, idx, entry.emsName, used_format)
                except:
                    pass

        elif column == "oem_id":
            for row in range(len(boup_df.index)):
                try:
                    entry = oemDetails.get(
                        id=boup_df.iloc[row, idx])
                    worksheet.write(
                        row+1, idx, entry.oemName, used_format)
                except:
                    pass

        elif column == "vpaCustomer_id":
            for row in range(len(boup_df.index)):
                try:
                    entry = vpaCustomerDetails.get(
                        id=boup_df.iloc[row, idx])
                    worksheet.write(
                        row+1, idx, entry.customerName, used_format)
                except:
                    pass

        elif column == "distributor_id":
            for row in range(len(boup_df.index)):
                try:
                    entry = distributorDetails.get(
                        id=boup_df.iloc[row, idx])
                    worksheet.write(
                        row+1, idx, entry.distributorName, used_format)
                except:
                    pass

                                  
        else:
            # if column == 'modifiedDate':
            for row in range(len(boup_df.index)):
                if isinstance(boup_df.iloc[row, idx], datetime.datetime):
                    worksheet.write(
                        row+1, idx, str(boup_df.iloc[row, idx]), used_format)
                elif pd.isnull(boup_df.iloc[row, idx]):
                    worksheet.write(row+1, idx, "", used_format)
                else:
                    worksheet.write(
                        row+1, idx, boup_df.iloc[row, idx], used_format)

        used_format = locked

    print("BoUp export done", filePath)
    workbook.close()
    return filePath
