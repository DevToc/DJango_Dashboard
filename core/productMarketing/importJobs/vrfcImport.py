"""
Infineon Technologies AG
With this file we import data from the csv based VRFC extracts. In order to generate this input file, the Cube_VRFC.xlsb file has to be saved as a plain CSV with UTF-8 encoding.
Before saving the CSV, the rows 1 to 9 (inclusive) have to be deleted in the .xlsb file. So the first row is the one with "PM_FC_VIST_QTY...." etc in column F.
The header has to have this format:

Having identity keys in the first column will lead to a rejected import job.

Then, the sales forecast has to be separated form marketing forecast and orders on hand.
After import of this file, first the combination of main and end customers is stored as binding in our database for new entries.

Then, cross checks with the fields suggestedMainCustomerVrfc and suggestedEndCustomerVrfc of t_project are done. Errors are dumped into the table vrfcCrossCheck

If existing entries of t_project do not match the allowable combinations of main+end customer a given batch date, warnings are generated. By no means objects of t_project should be deleted.
Again, keep in mind that the checks are done at the suggestedMainCustomerVrfc level due to the fuzziness of the supply chain.
"""

import gc
from decimal import *
from cmath import nan
import pandas as pd
import numpy as np
from typing import (
    Iterable,
    TypeVar,
    MutableSequence,
    MutableSequence,
    MutableSequence,
    Any,
)
from datetime import datetime
# from productMarketingDwh.models import *
# from productMarketing.models import Project
# from ..models import *
from enum import Enum
from sqlite3 import Error
import pandasql as ps
# from productMarketing.models import MainCustomers, FinalCustomers  # , CustomerRelation
from productMarketingDwh.models import *
from core.project.models import MainCustomers, FinalCustomers, Project, MissingOrders, SalesPlanWithNoProject, OrdersWithNoProject, ProjectError, MissingSalesPlan
from django.db import connection


def getQuarter(fiscalQuarter):
    fiscalQuarter = int(fiscalQuarter)
    if fiscalQuarter == 1:
        return 4
    elif fiscalQuarter == 2:
        return 1
    elif fiscalQuarter == 3:
        return 2
    elif fiscalQuarter == 4:
        return 3


def getYear(fiscalQuarter, fiscalYear):
    fiscalYears = ["20_21", "21_22", "22_23", "23_24",
                   "24_25", "25_26", "26_27", "27_28", "28_29", "29_30"]
    years = ["2020", "2021", "2022", "2023", "2024",
             "2025", "2026", "2027", "2028", "2029", "2030"]

    indexFiscalYear = fiscalYears.index(fiscalYear)
    yearIndex = indexFiscalYear

    if int(fiscalQuarter) == 1:
        return years[yearIndex]
    else:
        return years[yearIndex + 1]


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def rawSqlPerformer(sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)
        row = dictfetchall(cursor)
    return row


# fill the available error types first


class ErrorTypesVrfcOohValidation(Enum):
    # high level checks
    rfpMissing: int = 0
    # can happen when an entry in BoUp must be updated to match an updated combination in OoH. otherwise, since OoH is the source of truth for BoUp Main and End Customers, it cannot happen in the other direction.
    endCustomerMissing: int = 1
    # can happen when an entry in BoUp must be updated to match an updated combination in OoH, since OoH is the source of truth for BoUp Main and End Customers, it cannot happen in the other direction.
    mainCustomerMissing: int = 2
    mainEndCustomerMissingBoUp: int = 3
    mainEndCustomerMissingOoh: int = 4

    # low level checks, at main and end customer level (OoH row level check )
    volumeDeltaOverFive: int = 5
    volumeMissingInOoh: int = 6
    volumeMissingInBoUp: int = 7
    aspDeltaOverFive: int = 8
    priceMissingInOoh: int = 9
    priceMissingInBoUp: int = 10

    def __str__(self) -> str:
        # python < v3.10 does not support switch statements...

        if self.value == 0:
            return "RFP Missing in Bottom Up tool."
        elif self.value == 1:
            return "End customer missing completely in OoH."
        elif self.value == 2:
            return "Main customer missing completely in OoH."
        elif self.value == 3:
            return "Combination of main and end customer missing in Bottom Up tool."
        elif self.value == 4:
            return "Combination of main and end customer missing in Orders on Hand."
        elif self.value == 5:
            return "Delta of volumes between OoH and BoUp is over 5%."
        elif self.value == 6:
            return "Volume is missing in OoH."
        elif self.value == 7:
            return "Volume is missing in BoUp."
        elif self.value == 8:
            return "Delta of ASP between OoH and BoUp is over 5%."
        elif self.value == 9:
            return "Price is missing in OoH."
        elif self.value == 10:
            return "Price is zero or missing in BoUp."


class ErrorsVrfcImport(Enum):
    # high level checks
    rfpMissing: int = 0
    quantityError: int = 1
    priceError: int = 2
    revenueError: int = 3
    objectCreationError: int = 4
    priceLengthChar: int = 5

    def __str__(self) -> str:
        # python < v3.10 does not support switch statements...

        if self.value == 0:
            return "RFP Missing in Bottom Up tool."
        elif self.value == 1:
            return "Quantity error (character, formatting)."
        elif self.value == 2:
            return "Price error (character, formatting)."
        elif self.value == 3:
            return "Revenue error (character, formatting)."
        elif self.value == 4:
            return "Miscelaneous import error."
        elif self.value == 5:
            return "ASP unplausible (more than 15 characters) or wrong character."


def importVrfcOohCsv(fileUpload: bool, uploadPath: str) -> bool:
    # datetime.datetime.now()
    now = datetime.now()
    date = now.strftime("%Y%m%d")
    totalImportErrors = []
    missingRfps = []
    filePath = "./persistentLayer/importJobs/marketingCube_full_test.csv"
    csv = False

    writeObjects = True
    importOoh = True
    importSfc = True

    if writeObjects == True:
        if fileUpload == True:
            filePath = "." + uploadPath
            if uploadPath[-3:] == "csv":
                csv = True

        """
        #####################################################################################
        Block A: data import, cleaning and normalization
        #####################################################################################
        """
        df1 = None

        if csv == True:
            df1 = pd.read_csv(
                filePath, sep=";", decimal=",", thousands='.'
            )
        else:
            df1 = pd.read_excel(filePath, decimal=',', thousands=".")
            df1 = df1.drop([0, 1, 2, 3, 4, 5, 6, 7])
            df1.to_csv("./tempVrfcA.csv", sep=";",
                       decimal=",", header=True, index=False)
            df1 = pd.read_csv(
                "./tempVrfcA.csv", sep=";", decimal=",", skiprows=[0]
            )

        # print("### input")
        # print(df1)
        # print("####")
        # df1 = pd.read_csv("./marketingCube_cleaned_ooh_test.csv", sep = ';', decimal=",")
        length = len(df1.index)
        index = 0
        df1 = df1.fillna(0.0)
        df1 = df1.drop([0, 1])
        df1 = df1.reset_index(drop=True)

        header = df1.columns.values.tolist()
        #print("len header", len(header))
        # now remove the headers and the rows 0 and 1. the 21_22, 21_22, etc should now be the row 0.
        df1.to_csv("./test1.csv", sep=";", decimal=",", header=True)

        # 0 is the 21_22, etc.. also the fiscal year. if Total as keyword, the field is the yearly sum of FY.
        firstRow = df1.iloc[0].array
        # 1 is the label for the quarter. if 0.0, this is the yearly sum. adjust label accordingly.
        secondRow = df1.iloc[1].array
        #print("second row pre import", len(secondRow))
        # print(secondRow)
        # print("####")

        # REV+UC = revenue and potential orders microcontrollers
        # REV+UC_POT_QTY = volumes microcontrollers
        # REV+UC_POT_ASP = asp microcontrollers

        # rename headers to a for us functionally meaningfull value
        for index in range(0, (len(secondRow)), 1):
            fieldName: str = ""
            headerValue: str = str(header[index])
            #print("header -->", headerValue)
            # add the type of information (revenue, asp, quantity) depending on the
            if ("_QTY" in str(headerValue)) and ("PM_" in str(headerValue)):
                fieldName = "pmfc_qty_"
            elif ("ASP" in str(headerValue)) and ("PM_" in str(headerValue)):
                # print("found price pm")
                fieldName = "pmfc_asp_"
            elif "PM_" in str(headerValue):
                # print("found revenue pm!")
                fieldName = "pmfc_rev_"
            elif ("_QTY" in str(headerValue)) and ("S_FC" in str(headerValue)):
                # print("found qty sfc")
                fieldName = "sfc_qty_"
            elif ("ASP" in str(headerValue)) and ("S_FC" in str(headerValue)):
                # print("found price sfc")
                fieldName = "sfc_asp_"
            elif "S_FC_VIST" in str(headerValue):
                # print("found revenue sfc!")
                fieldName = "sfc_rev_"
            elif "_QTY" in str(headerValue):
                # print("found qty ooh", firstRow[index])
                fieldName = "ooh_qty_"
            elif "ASP" in str(headerValue):
                # print("found price ooh", firstRow[index])
                fieldName = "ooh_asp_"
            elif "REV+UC_POT" in str(headerValue):
                # print("found revenue ooh!", firstRow[index])
                fieldName = "ooh_rev_"
            else:
                print("not a relevant field", headerValue)

            # if a yearly total
            if str(secondRow[index]) == str(0.0):
                secondRow[index] = fieldName + \
                    str(firstRow[index]).replace(" ", "_")
            else:
                secondRow[index] = fieldName + str(secondRow[index])

        # df1.iloc[2,:] = secondRow

        # remove the first two rows in order to keep only the for us relevant rows
        df1.columns = secondRow
        df1 = df1.drop([0, 1])
        df1 = df1.reset_index(drop=True)

        # for field HFG_DESRIPTION we remove software and others 58_S, 58_9 tbd HFG_DESC
        df1 = df1[df1["HFG_DESC"] != "58_S"]
        df1 = df1[df1["HFG_DESC"] != "58_9"]

        # df1.to_csv("./test1.csv", mode="a", sep=";", decimal=",", header=True)

        """
        #####################################################################################

        Block B: data persistence customers.
        Take care of main and end customer combinations first, as well as of the respective entries in FInal and MainCustomer tables.
        #####################################################################################

        """
        # set all possible combinations to false first
        MainCustomers.objects.filter(dummy=False).update(valid=False)
        FinalCustomers.objects.filter(dummy=False).update(valid=False)

        # get the main customers, final customers and the respective combinations. load into FinalCustomers, MainCustomers, CustomerRelation
        uniqueMainCustomers: MutableSequence[str] = []
        uniqueFinalCustomer: MutableSequence[str] = []
        uniqueCustomerCombinations: MutableSequence[str] = []

        queryMainCustomers = """SELECT DISTINCT MC_NAME FROM df1;"""
        queryFinalCustomers = """SELECT DISTINCT EC_NAME FROM df1;"""
        queryCustomerCombinations = (
            """SELECT DISTINCT MC_NAME, EC_NAME FROM df1 ORDER BY MC_NAME ASC;"""
        )

        queryResultMainCustomers = ps.sqldf(queryMainCustomers, locals())
        queryResultFinalCustomers = ps.sqldf(queryFinalCustomers, locals())
        queryResultCustomerCombinations = ps.sqldf(
            queryCustomerCombinations, locals())

        """
        print("main customers", type(queryResultMainCustomers))
        print(queryResultMainCustomers)
        print("end customers")
        print(queryResultFinalCustomers)
        print("end queryResultFinalCustomers2")
        print(queryResultCustomerCombinations)
        """
        queryResultCustomerCombinations["date"] = date

        filename1 = date + "_MainEndCustomerCombinations.csv"
        path1 = "./persistentLayer/logs/" + filename1
        """
        queryResultCustomerCombinations.to_csv(
            path1, mode="a", sep=";", decimal=",", header=False
        )
        """

        # unique combinations
        uniqueMainCustomers = queryResultMainCustomers["MC_NAME"].tolist()
        uniqueFinalCustomer = queryResultFinalCustomers["EC_NAME"].tolist()

        # both arrays will have the same length
        uniqueCombiMc: MutableSequence[str] = queryResultCustomerCombinations[
            "MC_NAME"
        ].tolist()

        uniqueCombiEc: MutableSequence[str] = queryResultCustomerCombinations[
            "EC_NAME"
        ].tolist()

        for index in range(0, len(uniqueMainCustomers), 1):
            obj, created = MainCustomers.objects.get_or_create(
                customerName=uniqueMainCustomers[index]
            )

            obj.valid = True
            # reset the M2M relation to final customers
            obj.finalCustomers.clear()
            obj.save()

        for index in range(0, len(uniqueFinalCustomer), 1):
            obj, created = FinalCustomers.objects.get_or_create(
                finalCustomerName=uniqueFinalCustomer[index]
            )
            """
            if created == True:
                print("created final customer", obj)
            else:
                print("retrieved final cust obj", obj)
            """
            obj.valid = True
            obj.save()

        lengthA = len(queryResultCustomerCombinations.index)

        allMainCustomers = MainCustomers.objects.all()
        allFinalCustomers = FinalCustomers.objects.all()

        # now connect the main and end customers. note 18/1/23: added many to many relation.
        for index in range(0, lengthA, 1):
            mainCustName = queryResultCustomerCombinations.loc[index, "MC_NAME"]
            mainCustObject = allMainCustomers.get(customerName=mainCustName)
            finalCustStr = queryResultCustomerCombinations.loc[index, "EC_NAME"]
            fincalCustObject = allFinalCustomers.get(
                finalCustomerName=finalCustStr
            )

            # generate the main - end customer relation and save. this will be only used for filtering and controls.
            mainCustObject.finalCustomers.add(fincalCustObject)

            """
            if created == True:
                print("created final customer", fincalCustObject)
            else:
                print("retrieved final custo obj", fincalCustObject)
            """
            obj.valid = True
            obj.save()

        """
        for index in range (0, len(uniqueFinalCustomer), 1):
            obj, created = FinalCustomers.objects.get_or_create(finalCustomerName = uniqueFinalCustomer[index])
        """
        # set all previous combinations to false
        # CustomerRelation.objects.raw('UPDATE productMarketing_customerrelation SET valid = False')
        """
        CustomerRelation.objects.update(valid=False)

        # tbd how to optimize this step, limit number of DB calls, if it's nesteable within the two previous for loops
        for index in range (0, len(uniqueCombiMc), 1):
            mcObj = MainCustomers.objects.filter(customerName = uniqueCombiMc[index])[0]
            ecObj = FinalCustomers.objects.filter(finalCustomerName = uniqueCombiEc[index])[0]
            obj, created = CustomerRelation.objects.get_or_create(mainCustomer = mcObj, finalCustomer = ecObj, valid = True)
            obj.save()

        """
        """
        #####################################################################################
        Block C: data persistence of VRFC core Data.

        Errors are related to missing RFPs in product master data, data type errors (eg floats instead of ints, etc...) or high level DB errors (IO errors)
        
        #####################################################################################
        """
        newHeader = df1.columns.values.tolist()

        # orders on hand, quantities (prices seem to be wrong)

        # truncate first??

        fiscalYears = [
            "19_20",
            "20_21",
            "21_22",
            "22_23",
            "23_24",
            "24_25",
            "25_26",
            "27_28",
            "28_29",
            "29_30",
        ]

        quarters = ["Q1", "Q2", "Q3", "Q4"]
        length = len(df1.index)

        """
        this read write step is done to circumvene errors on data types (decimals, thousands separators)
        """
        if csv == True:
            """
            df1.to_csv("./test2.csv", sep=";", decimal=",",
                    header=True, index=False)
            """
            df1 = pd.read_csv(
                "./test2.csv", sep=";", decimal=",", thousands='.'
            )

        """
        # cast selectively. if format used is dots for thousands separators and imported from CSV
        for index in range(0, length, 1):

            if index > 0:
                break
            rowValues = df1.iloc[index].array
            lengthRow = len(rowValues)

            for indexA in range(0, lengthRow, 1):
                headerValue = newHeader[indexA]

                if "ooh_qty_" in str(headerValue):
                    df1[headerValue].str.replace('.', '', regex=True)
                    df1.astype({headerValue: 'int32'}).dtypes

                elif "ooh_asp_" in str(headerValue):
                    df1[headerValue].str.replace('.', '', regex=True)
                    df1.astype({headerValue: 'float'}).dtypes

                elif "ooh_rev_" in str(headerValue):
                    df1[headerValue].str.replace('.', '', regex=True)
                    df1.astype({headerValue: 'float'}).dtypes

                # sales forecast, quantities (prices seem to be wrong)
                elif "sfc_asp_" in str(headerValue):
                    df1[headerValue].str.replace('.', '', regex=True)
                    df1.astype({headerValue: 'float'}).dtypes

                elif "sfc_qty_" in str(headerValue):
                    df1[headerValue].str.replace('.', '', regex=True)
                    df1.astype({headerValue: 'int32'}).dtypes

                elif "sfc_rev_" in str(headerValue):
                    df1[headerValue].str.replace('.', '', regex=True)
                    df1.astype({headerValue: 'float'}).dtypes

                elif "pmfc_qty_" in str(headerValue):
                    print(df1[headerValue])
                    df1[headerValue].str.replace('.', '', regex=True)
                    df1.astype({headerValue: 'int32'}).dtypes

                elif "pmfc_asp_" in str(headerValue):
                    df1[headerValue].str.replace('.', '', regex=True)
                    df1.astype({headerValue: 'float'}).dtypes

                elif "pmfc_rev_" in str(headerValue):
                    df1[headerValue].str.replace('.', '', regex=True)
                    df1.astype({headerValue: 'float'}).dtypes

                else:
                    print("field seems not relevant", headerValue)
        """
        # helper arrays
        allProducts = Product.objects.all()
        # VrfcOrdersOnHand.objects.all().delete()

        """
        ###########################
        Block B
        Import of Orders on Hand
        ###########################
        """

        # orders on hand
        allVrfcOrdersOnHand = VrfcOrdersOnHand.objects.all()
        alreadyExistingVrfcOoh = []
        newVrfcOoh = []

        existing_values_list_VrfcOoh = list(
            allVrfcOrdersOnHand.values_list(
                "rfp", "mainCustomerVrfc", "endCustomerVrfc", "fiscalYear", "fiscalQuarter"
            ).order_by("id")
        )

        # (2649, 234, 234, '23_24', 0),
        existing_qs_VrfcOoh = list(
            allVrfcOrdersOnHand.all().order_by("id"))
        existing_dict_VrfcOoh = dict(
            zip(existing_values_list_VrfcOoh, existing_qs_VrfcOoh))

        df1.to_csv("./test2.csv", sep=";", decimal=",",
                   header=True, index=False)

        df_unpivot = pd.melt(
            df1, id_vars=["RFP", "MC_NAME", "EC_NAME"]
        )

        df_ooh = df_unpivot[df_unpivot["variable"].str.contains(
            "ooh_") == True]
        df_ooh_part = df_ooh[df_ooh["variable"].str.contains(
            "_Total") == False]

        df_pmfc = df_unpivot[df_unpivot["variable"].str.contains(
            "pmfc_") == True]
        df_sfc = df_unpivot[df_unpivot["variable"].str.contains(
            "sfc_") == True]

        """
        df_unpivot["YEAR"] = [int("20" + x[2:4])
                            for x in df_unpivot["YEAR_CURRENCY"]]
        df_unpivot["CURRENY"] = [x[-1] for x in df_unpivot["YEAR_CURRENCY"]]
        df_unpivot = df_unpivot.drop("YEAR_CURRENCY", axis=1)
        """

        # create helper columns
        df_ooh["quarter"] = df_ooh.variable.str[8:]
        df_ooh["dataType"] = df_ooh.variable.str[:7]

        df_ooh = df_ooh.drop(['variable'], axis=1)
        try:
            df_ooh.to_csv("./df_ooh.csv", sep=";", decimal=",",
                          header=True, index=False)
        except:
            pass

        df_ooh = df_ooh.pivot(
            index=["RFP", "MC_NAME", "EC_NAME", "quarter"], columns=["dataType"], values=["value"]).reset_index()

        # now we just need to fix the headers. the order is: RFP, MC, EC, Quarter, ooh_asp, ooh_qty, ooh_rev
        # drop(index=df_ooh.index[0], axis=0, inplace=True)

        df_ooh = df_ooh.rename(
            columns={'MC_NAME': 'mainCustomer', 'EC_NAME': 'endCustomer'})

        try:
            df_ooh.to_csv("./unmelted0.csv", sep=";", decimal=",",
                          header=True, index=False)
        except:
            pass

        df_ooh.columns = ['RFP', 'mainCustomer', 'endCustomer',
                          'quarter', 'ooh_asp', 'ooh_qty', 'ooh_rev']

        df_ooh = df_ooh.iloc[0:, :]
        try:
            df_ooh.to_csv("./unmeltedA.csv", sep=";", decimal=",",
                          header=True, index=False)
        except:
            pass

        df_ooh.to_csv("./unmeltedA.csv", sep=";",
                      decimal=",", header=True, index=False)

        """
        df_ooh.columns.values[0] = "rfp"
        df_ooh.columns.values[1] = "mainCustomer"
        df_ooh.columns.values[2] = "endCustomer"
        df_ooh.columns.values[3] = "quarter"
        """

        length = len(df_ooh.index)
        print("$$$$$$$$$$$$ preparing bulk create")

        if importOoh == True:
            # now check for errors
            for index in range(0, length, 1):

                errorDict = {
                    "row": index,
                    "errors": "",
                }

                if index % 1000 == 0:
                    print(index, "%% still processing, out of", length)

                rowValues = df_ooh.iloc[index].array
                rfpString: str = rowValues[0]
                lengthRow = len(rowValues)
                lineLevelErrors: MutableSequence[ErrorsVrfcImport] = []
                mainCustomerObj = allMainCustomers.filter(
                    customerName=rowValues[1], valid=True
                )[0]

                finalCustomerObj = allFinalCustomers.filter(
                    finalCustomerName=rowValues[2], valid=True
                )[0]

                product = None
                try:
                    product = allProducts.filter(rfp=rfpString)[0]
                except:
                    # handle error
                    lineLevelErrors.append(ErrorsVrfcImport.rfpMissing)
                    missingRfps.append(rfpString)

                period = rowValues[3]
                fiscalYear = period[:5]
                fiscalQuarter = period[6:]

                # we skip total values
                if (len(lineLevelErrors) == 0) and ("Total" not in fiscalQuarter):
                    year = getYear(fiscalQuarter=fiscalQuarter,
                                   fiscalYear=str(fiscalYear))
                    quarter = getQuarter(fiscalQuarter)
                    rowAsp = round(float(rowValues[4]), 5)
                    rowQty = int(rowValues[5])
                    rowRev = round(float(rowValues[6]), 5)

                    try:
                        floatVal = Decimal(rowAsp)
                    except:
                        lineLevelErrors.append(ErrorsVrfcImport.priceError)
                        print(index, "invalid decimal asp", rowAsp)
                    try:
                        floatVal = Decimal(rowRev)
                    except:
                        lineLevelErrors.append(ErrorsVrfcImport.revenueError)
                        print(index, "invalid decimal rowrev", rowRev)
                    try:
                        floatVal = int(rowQty)
                    except:
                        lineLevelErrors.append(ErrorsVrfcImport.quantityError)

                    if len(str(rowAsp)) > 15:
                        print(index, "spurious ASP", rowAsp)
                        lineLevelErrors.append(
                            ErrorsVrfcImport.priceLengthChar)

                    if (len(lineLevelErrors) == 0):
                        thisKey = (product.id, mainCustomerObj.id,
                                   finalCustomerObj.id, fiscalYear, int(fiscalQuarter))

                        if thisKey in existing_dict_VrfcOoh:
                            existing_dict_value = existing_dict_VrfcOoh.get(
                                thisKey)
                            existing_dict_value.rfp = product
                            existing_dict_value.mainCustomerVrfc = mainCustomerObj
                            existing_dict_value.endCustomerVrfc = finalCustomerObj
                            existing_dict_value.fiscalYear = fiscalYear
                            existing_dict_value.fiscalQuarter = int(
                                fiscalQuarter)
                            existing_dict_value.quantity = rowQty
                            existing_dict_value.asp = rowAsp
                            existing_dict_value.revenue = rowRev
                            existing_dict_value.year = year
                            existing_dict_value.quarter = int(quarter)
                            alreadyExistingVrfcOoh.append(
                                existing_dict_value)

                        else:
                            # else create
                            newVrfcOohEntry = VrfcOrdersOnHand(
                                rfp=product,
                                mainCustomerVrfc=mainCustomerObj,
                                endCustomerVrfc=finalCustomerObj,
                                fiscalYear=fiscalYear,
                                fiscalQuarter=fiscalQuarter,
                                quantity=rowQty,
                                asp=rowAsp,
                                revenue=rowRev,
                                year=year,
                                quarter=quarter
                            )

                            newVrfcOoh.append(newVrfcOohEntry)

                """
                # sales forecast, quantities (prices seem to be wrong)
                elif "sfc_asp_" in str(headerValue):
                    print("found sfc_asp_")
                    fieldName = "sfc_asp_"
                    # will not be used
                elif "sfc_qty_" in str(headerValue):
                    print("found sfc_qty_!")
                    fieldName = "sfc_qty_"
                    # will not be used
                elif "sfc_rev_" in str(headerValue):
                    print("found sfc_rev_!")
                    fieldName = "sfc_rev_"
                    # will not be used
                elif "pmfc_qty_" in str(headerValue):
                    print("found pmfc_qty_!")
                    fieldName = "pmfc_qty_"
                elif "pmfc_asp_" in str(headerValue):
                    print("found pmfc_asp_")
                    fieldName = "pmfc_asp_"

                elif "pmfc_rev_" in str(headerValue):
                    print("found pmfc_rev_")
                    fieldName = "pmfc_rev_"
                else:
                    # print("field seems not relevant", headerValue)
                    pass
                """

                errorDict = {
                    "row": index,
                    "errors": list(dict.fromkeys(lineLevelErrors)),
                }

                totalImportErrors.append(errorDict)

            print("######## starting bulk create", len(
                alreadyExistingVrfcOoh), "new obj len", len(newVrfcOoh))
            # create chunks of 1000 objects for memory handling

            # bulk update values that we added new values above
            VrfcOrdersOnHand.objects.bulk_update(
                alreadyExistingVrfcOoh, ["rfp", "mainCustomerVrfc", "endCustomerVrfc",
                                         "fiscalYear", "quarter", "quantity", "asp", "revenue"], batch_size=1000
            )
            alreadyExistingVrfcOoh = None
            gc.collect()

            print("######### finished with bulk update")

            newly_created_VrfcOoh = VrfcOrdersOnHand.objects.bulk_create(
                newVrfcOoh, batch_size=1000
            )

            print("######### finished with bulk create of OOH")

        """
        ######################################################
        Block C
        Import of Sales Forecast
        ######################################################
        """

        if importSfc == True:
            allVrfcSalesForecast = VrfcSalesForecast.objects.all()
            alreadyExistingVrfcSfc = []
            newVrfcSfc = []
            totalImportErrorsSFC = []

            existing_values_list_VrfcSfc = list(
                allVrfcSalesForecast.values_list(
                    "rfp", "mainCustomerVrfc", "endCustomerVrfc", "fiscalYear", "fiscalQuarter"
                ).order_by("id")
            )

            existing_qs_VrfcSfc = list(
                allVrfcSalesForecast.all().order_by("id"))
            existing_dict_VrfcSfc = dict(
                zip(existing_values_list_VrfcSfc, existing_qs_VrfcSfc))

            # create helper columns
            df_sfc["quarter"] = df_sfc.variable.str[8:]
            df_sfc["dataType"] = df_sfc.variable.str[:7]

            df_sfc = df_sfc.drop(['variable'], axis=1)
            try:
                df_sfc.to_csv("./df_sfc.csv", sep=";", decimal=",",
                              header=True, index=False)
            except:
                pass

            df_sfc = df_sfc.pivot(
                index=["RFP", "MC_NAME", "EC_NAME", "quarter"], columns=["dataType"], values=["value"]).reset_index()

            df_sfc = df_sfc.rename(
                columns={'MC_NAME': 'mainCustomer', 'EC_NAME': 'endCustomer'})

            df_sfc.columns = ['RFP', 'mainCustomer', 'endCustomer',
                              'quarter', 'sfc_asp', 'sfc_qty', 'sfc_rev']

            df_sfc = df_sfc.iloc[0:, :]
            lengthSfc = len(df_sfc.index)
            print("$$$$$$$$$$$$ preparing bulk create sales forecast")

            # now check for errors
            for index in range(0, lengthSfc, 1):

                errorDict = {
                    "row": index,
                    "errors": "",
                }

                if index % 1000 == 0:
                    print(index, "%% still processing SFC, out of", lengthSfc)

                rowValues = df_sfc.iloc[index].array
                rfpString: str = rowValues[0]
                lengthSfcRow = len(rowValues)
                lineLevelErrors: MutableSequence[ErrorsVrfcImport] = []
                mainCustomerObj = allMainCustomers.filter(
                    customerName=rowValues[1], valid=True
                )[0]

                finalCustomerObj = allFinalCustomers.filter(
                    finalCustomerName=rowValues[2], valid=True
                )[0]

                product = None
                try:
                    product = allProducts.filter(rfp=rfpString)[0]
                except:
                    # handle error
                    lineLevelErrors.append(ErrorsVrfcImport.rfpMissing)
                    missingRfps.append(rfpString)

                period = rowValues[3]
                fiscalYear = period[:5]
                fiscalQuarter = period[6:]
                # calenderYear

                # we skip total values
                if (len(lineLevelErrors) == 0) and ("Total" not in fiscalQuarter):
                    year = getYear(fiscalQuarter=fiscalQuarter,
                                   fiscalYear=str(fiscalYear))
                    quarter = getQuarter(fiscalQuarter)
                    rowAsp = round(float(rowValues[4]), 5)
                    rowQty = int(rowValues[5])
                    rowRev = round(float(rowValues[6]), 5)

                    try:
                        floatVal = Decimal(rowAsp)
                    except:
                        lineLevelErrors.append(ErrorsVrfcImport.priceError)
                        print(index, "invalid decimal asp", rowAsp)
                    try:
                        floatVal = Decimal(rowRev)
                    except:
                        lineLevelErrors.append(ErrorsVrfcImport.revenueError)
                        print(index, "invalid decimal rowrev", rowRev)
                    try:
                        floatVal = int(rowQty)
                    except:
                        lineLevelErrors.append(ErrorsVrfcImport.quantityError)

                    if len(str(rowAsp)) > 15:
                        print(index, "spurious ASP", rowAsp)
                        lineLevelErrors.append(
                            ErrorsVrfcImport.pricelengthSfcChar)

                    if (len(lineLevelErrors) == 0):
                        thisKey = (product.id, mainCustomerObj.id,
                                   finalCustomerObj.id, fiscalYear, int(fiscalQuarter))

                        if thisKey in existing_dict_VrfcSfc:
                            existing_dict_value = existing_dict_VrfcSfc.get(
                                thisKey)
                            existing_dict_value.rfp = product
                            existing_dict_value.mainCustomerVrfc = mainCustomerObj
                            existing_dict_value.endCustomerVrfc = finalCustomerObj
                            existing_dict_value.fiscalYear = fiscalYear
                            existing_dict_value.fiscalQuarter = int(
                                fiscalQuarter)
                            existing_dict_value.quantity = rowQty
                            existing_dict_value.asp = rowAsp
                            existing_dict_value.revenue = rowRev
                            existing_dict_value.year = year
                            existing_dict_value.quarter = int(quarter)
                            alreadyExistingVrfcSfc.append(
                                existing_dict_value)

                        else:
                            # else create
                            newVrfcSfcEntry = VrfcSalesForecast(
                                rfp=product,
                                mainCustomerVrfc=mainCustomerObj,
                                endCustomerVrfc=finalCustomerObj,
                                fiscalYear=fiscalYear,
                                fiscalQuarter=fiscalQuarter,
                                quantity=rowQty,
                                asp=rowAsp,
                                revenue=rowRev,
                                year=year,
                                quarter=quarter
                            )

                            newVrfcSfc.append(newVrfcSfcEntry)

                errorDict = {
                    "row": index,
                    "errors": list(dict.fromkeys(lineLevelErrors)),
                }

                totalImportErrorsSFC.append(errorDict)

            print("######## starting bulk update sales forecast", len(
                alreadyExistingVrfcSfc), "new obj len", len(newVrfcSfc))

            # create chunks of 1000 objects for memory handling
            # bulk update values that we added new values above
            VrfcSalesForecast.objects.bulk_update(
                alreadyExistingVrfcSfc, ["rfp", "mainCustomerVrfc", "endCustomerVrfc",
                                         "fiscalYear", "quarter", "quantity", "asp", "revenue"], batch_size=1000
            )
            alreadyExistingVrfcSfc = None
            gc.collect()

            print("######### finished with bulk update sales forecast")

            newly_created_VrfcSfc = VrfcSalesForecast.objects.bulk_create(
                newVrfcSfc, batch_size=1000
            )

            newly_created_VrfcSfc = None
            gc.collect()
            print("######### finished with bulk create sales forecast")

        """
        ######################################################
        Block D
        Import of PM Forecast
        ######################################################
        """

        """
        ######################################################
        Block C
        Error handling
        ######################################################
        """

        # now iterate through the input Df and add columns with all errors...
        # if fileUpload == True:
        if True and (importOoh == True):

            df_ooh["To Be Corrected"] = ""
            df_ooh["outputId"] = ""
            df_ooh["errors"] = ""
            df_ooh["conflictingProjectsDbLevel"] = ""
            df_ooh["conflictingProjectsFileLevel"] = ""

            for index, row in df_ooh.iterrows():
                errorDict = totalImportErrors[index]
                errorString = ""
                conflictProjectsInDb = ""
                conflictProjectsInFile = ""

                for error in errorDict["errors"]:
                    errorString = errorString + error.__str__() + " "
                    df_ooh.loc[index, "To Be Corrected"] = True

                rowValues = df_ooh.iloc[index].array
                #print(index, "row values", rowValues, "errors", errorString)

                """
                for project in errorDict["conflictingProjectsDb"]:
                    conflictProjectsInDb = conflictProjectsInDb + \
                        str(project) + ". "

                for project in errorDict["conflictingRowsFile"]:
                    conflictProjectsInFile = conflictProjectsInFile + \
                        str(project) + ". "
                """

                # df.loc[index, "outputId"] = errorDict["projectId"]
                df_ooh.loc[index, "errors"] = errorString
                # df.loc[index, "conflictingProjectsDbLevel"] = conflictProjectsInDb
                # df.loc[index, "conflictingProjectsFileLevel"] = conflictProjectsInFile

            # remove duplicates
            missingRfps = list(dict.fromkeys(missingRfps))
            df_ooh.to_csv("./reportVRFC.csv", sep=";", decimal=",",
                          header=True, index=False)
            print("#######################################%%%%%%%%%%%%%%%%%%%%%%%")
            print("%%%%% error report %%%%%%%%")
            # print(totalImportErrors)
            print("%%%%% missingRfps %%%%%")
            print(missingRfps)
            print("#######################################%%%%%%%%%%%%%%%%%%%%%%%")

        if importSfc == True:

            df_sfc["To Be Corrected"] = ""
            df_sfc["outputId"] = ""
            df_sfc["errors"] = ""
            df_sfc["conflictingProjectsDbLevel"] = ""
            df_sfc["conflictingProjectsFileLevel"] = ""

            for index, row in df_sfc.iterrows():
                errorDict = totalImportErrorsSFC[index]
                errorString = ""
                conflictProjectsInDb = ""
                conflictProjectsInFile = ""

                for error in errorDict["errors"]:
                    errorString = errorString + error.__str__() + " "
                    df_sfc.loc[index, "To Be Corrected"] = True

                rowValues = df_sfc.iloc[index].array
                #print(index, "row values", rowValues, "errors", errorString)

                """
                for project in errorDict["conflictingProjectsDb"]:
                    conflictProjectsInDb = conflictProjectsInDb + \
                        str(project) + ". "

                for project in errorDict["conflictingRowsFile"]:
                    conflictProjectsInFile = conflictProjectsInFile + \
                        str(project) + ". "
                """

                # df.loc[index, "outputId"] = errorDict["projectId"]
                df_sfc.loc[index, "errors"] = errorString
                # df.loc[index, "conflictingProjectsDbLevel"] = conflictProjectsInDb
                # df.loc[index, "conflictingProjectsFileLevel"] = conflictProjectsInFile

            # remove duplicates
            missingRfps = list(dict.fromkeys(missingRfps))
            df_sfc.to_csv("./reportVRFC.csv", sep=";", decimal=",",
                          header=True, index=False)
            print("#######################################%%%%%%%%%%%%%%%%%%%%%%%")
            print("%%%%% error report %%%%%%%%")
            # print(totalImportErrors)
            print("%%%%% missingRfps %%%%%")
            print(missingRfps)
            print("#######################################%%%%%%%%%%%%%%%%%%%%%%%")

    """
    #####################################################################################
    Block D: sanity checks against projects.
    # D1: rfp planned at main and end customer level in BoUp for a given combination of VRFC mc+ec+rfp
    # D2: func key planned in boup but missing in vrfc
    # D3: planned volume differs too much from OoH or sales forecast. tbd who to warn due to missing salesname.
    # D4: planned asp differs too much from sales forecast (ooh price is not useful). tbd who to warn due to missing salesname.
    #####################################################################################
    """
    # D1
    """
    sqlDistinctOohMcEcRfpCombinations = VrfcOrdersOnHand.objects.raw(
        'SELECT DISTINCT rfp, mainCustomerVrfc, endCustomerVrfc  FROM productmarketingdwh_vrfcordersonhand')
    """
    sqlDistinctOohMcEcRfpCombinations = 'SELECT DISTINCT rfp_id, mainCustomerVrfc_id, endCustomerVrfc_id  FROM productmarketingdwh_vrfcordersonhand'
    distinctOohMcEcRfpCombinations = rawSqlPerformer(
        sqlDistinctOohMcEcRfpCombinations)

    sqlDistinctBoUpMcEcRfpCombinations = "SELECT DISTINCT sales_name_id, mainCustomer_id, finalCustomer_id FROM project_project"

    #sqlDistinctBoUpMcEcRfpCombinations = "SELECT DISTINCT sales_name_id, mainCustomer_id, finalCustomer_id FROM project_project OUTER JOIN project_salesname ON (project_project.sales_name_id = project_salesname.id)"
#    sqlDistinctBoUpMcEcRfpCombinations = "SELECT DISTINCT rfpHlp, mcHlp, ecHlp FROM productmarketingdwh_boup"
#    sql = "SELECT DISTINCT rfp, mainCustomer, endCustomer FROM productmarketingdwh_boup LEFT OUTER JOIN project_sales_name ON (productmarketingdwh_boup.salesName = project_sales_name.name)"
    distinctBoUpMcEcRfpCombinations = rawSqlPerformer(
        sqlDistinctBoUpMcEcRfpCombinations)

    allSalesNames = SalesName.objects.all()

    # the next steps are done to deal with problems on Joins in order to get rfp information at project level
    dfDistinct = pd.DataFrame(distinctBoUpMcEcRfpCombinations)
    dfDistinct["rfp_id"] = ""
    try:
        for index in range(0, len(dfDistinct.index), 1):
            salesname = dfDistinct.loc[index, "sales_name_id"]
            rfpValue = allSalesNames.get(id=salesname).rfp_id
            dfDistinct.loc[index, "rfp_id"] = rfpValue

        print("dfdistinct", len(dfDistinct.index))
        print(dfDistinct)
        # remove sales_name_id column, convert back to dictionary
        dfDistinct.drop('sales_name_id', inplace=True, axis=1)
        dfDistinct.columns = ['mainCustomer_id', 'endCustomer_id', 'rfp_id']
        distinctBoUpMcEcRfpCombinations = dfDistinct.to_dict('records')

    except:
        pass

    # now check if we are missing a project for each OOH combination
    missingProjectKeysRfpLevel = []
    missingOrdersKeysRfpLevel = []

    for index in range(0, len(distinctOohMcEcRfpCombinations), 1):
        rowItem = distinctOohMcEcRfpCombinations[index]
        checker = {"rfp_id": rowItem["rfp_id"], 'mainCustomer_id': rowItem["mainCustomerVrfc_id"],
                   'endCustomer_id': rowItem["endCustomerVrfc_id"]}

        if checker not in distinctBoUpMcEcRfpCombinations:
            missingProjectKeysRfpLevel.append(checker)

    for index in range(0, len(distinctBoUpMcEcRfpCombinations), 1):
        rowItem = distinctBoUpMcEcRfpCombinations[index]
        checker = {"rfp_id": rowItem["rfp_id"], 'mainCustomerVrfc_id': rowItem["mainCustomer_id"],
                   'endCustomerVrfc_id': rowItem["endCustomer_id"]}

        if checker not in distinctOohMcEcRfpCombinations:
            missingOrdersKeysRfpLevel.append(checker)

    """
    print("results missing projects")
    print(missingProjectKeysRfpLevel)
    print("results missing orders")
    print(missingOrdersKeysRfpLevel)
    """
    """
    for each project where orders are missing, mark the project as order missing
    first retrieve all relevant projects 
    this also has a counterpart in helperFunctions.py where MissingOrders are also checked
    """

    allProjects = Project.objects.all()
    projectsWithMissingOrders = []

    for index in range(0, len(missingOrdersKeysRfpLevel), 1):
        rowItem = missingOrdersKeysRfpLevel[index]
        rfpId = rowItem["rfp_id"]
        mcId = rowItem["mainCustomerVrfc_id"]
        ecId = rowItem["endCustomerVrfc_id"]
        relevantProjects = allProjects.filter(
            sales_name__rfp=rfpId, mainCustomer=mcId, finalCustomer=ecId)
        # add to table for missing orders
        if relevantProjects.count() > 0:
            for index in range(0, len(relevantProjects), 1):
                projectsWithMissingOrders.append(relevantProjects[index].id)
        else:
            print("no rel proj found", rfpId, mcId, ecId)

    #print("--> projects boup with missing orders", projectsWithMissingOrders)

    """
    clean the missing orders table
    """
    MissingOrders.objects.all().delete()
    missingOrdersObjsArr = []

    for project in projectsWithMissingOrders:
        newMissingOrderEntry = MissingOrders(project_id=project)
        missingOrdersObjsArr.append(newMissingOrderEntry)

    missingOrdersObjs = MissingOrders.objects.bulk_create(
        missingOrdersObjsArr, batch_size=1000
    )

    # update the ProjectError table accordingly
    allProjectErrors = ProjectError.objects.all()
    projectErrorsUpdate = []
    projectErrorsCreate = []

    allProjectErrorsProjectIds = allProjectErrors.values_list(
        "project", flat=True
    ).order_by("project")

    #print("allProjectErrorsProjectIds", allProjectErrorsProjectIds)
    # create new objects if required
    for projectWithNoOrder in projectsWithMissingOrders:
        if projectWithNoOrder not in allProjectErrorsProjectIds:
            item = ProjectError(project_id=projectWithNoOrder, error_ids="21")
            projectErrorsCreate.append(item)

    # check the existing project errors and remove / add error 21 acoordingly
    for projectErrorRow in allProjectErrors:
        # so if this error row is affected by not having an order
        if projectErrorRow.project_id in projectsWithMissingOrders:
            if "21" in projectErrorRow.error_ids:
                pass
            else:
                projectErrorRow.error_ids = projectErrorRow.error_ids + ",21"
                projectErrorsUpdate.append(projectErrorRow)
        else:
            # check if a project with missing vrfc orcer (Error 21) is stored here. if yes, check if remove
            if "21" in projectErrorRow.error_ids:
                # remove 21
                REPLACEMENTS = [
                    (",21,", ","),
                    (",21", ""),
                    ("21,", ""),
                ]
                for old, new in REPLACEMENTS:
                    projectErrorRow.error_ids = projectErrorRow.error_ids.replace(
                        old, new)
                    # projectErrorRow.save()
                projectErrorsUpdate.append(projectErrorRow)
            else:
                pass

    ProjectError.objects.bulk_update(
        projectErrorsUpdate, ["project", "error_ids"], batch_size=1000
    )

    newly_created_projectErrors = ProjectError.objects.bulk_create(
        projectErrorsCreate, batch_size=1000
    )

    """
    for each order where there is no project, store the ids in the OrdersWithNoProject
    """
    OrdersWithNoProject.objects.all().delete()
    ordersWithNoProjectBulkCreateArray = []

    # for each rfp + mc + ec combination, store this in missingProjects table
    for missingProject in missingProjectKeysRfpLevel:

        item = OrdersWithNoProject(
            rfp_id=missingProject["rfp_id"], mainCustomer_id=missingProject["mainCustomer_id"], endCustomer_id=missingProject["endCustomer_id"])
        ordersWithNoProjectBulkCreateArray.append(item)

    newly_created_projectErrors = OrdersWithNoProject.objects.bulk_create(
        ordersWithNoProjectBulkCreateArray, batch_size=1000
    )

    """
    ************* repeat the above with sales plan
    """

    sqlDistinctSfcMcEcRfpCombinations = 'SELECT DISTINCT rfp_id, mainCustomerVrfc_id, endCustomerVrfc_id  FROM productmarketingdwh_vrfcsalesforecast'
    distinctSfcMcEcRfpCombinations = rawSqlPerformer(
        sqlDistinctSfcMcEcRfpCombinations)

    # now check if we are missing a project for each Sfc combination
    missingProjectKeysRfpLevelSales = []
    missingSalesPlanKeysRfpLevel = []

    for index in range(0, len(distinctSfcMcEcRfpCombinations), 1):
        rowItem = distinctSfcMcEcRfpCombinations[index]
        checker = {"rfp_id": rowItem["rfp_id"], 'mainCustomer_id': rowItem["mainCustomerVrfc_id"],
                   'endCustomer_id': rowItem["endCustomerVrfc_id"]}

        if checker not in distinctBoUpMcEcRfpCombinations:
            missingProjectKeysRfpLevelSales.append(checker)

    for index in range(0, len(distinctBoUpMcEcRfpCombinations), 1):
        rowItem = distinctBoUpMcEcRfpCombinations[index]
        checker = {"rfp_id": rowItem["rfp_id"], 'mainCustomerVrfc_id': rowItem["mainCustomer_id"],
                   'endCustomerVrfc_id': rowItem["endCustomer_id"]}

        if checker not in distinctSfcMcEcRfpCombinations:
            missingSalesPlanKeysRfpLevel.append(checker)

    """
    for each project where orders are missing, mark the project as order missing
    first retrieve all relevant projects 
    this also has a counterpart in helperFunctions.py where missingSalesPlan are also checked
    """

    projectsWithmissingSalesPlan = []

    for index in range(0, len(missingSalesPlanKeysRfpLevel), 1):
        rowItem = missingSalesPlanKeysRfpLevel[index]
        rfpId = rowItem["rfp_id"]
        mcId = rowItem["mainCustomerVrfc_id"]
        ecId = rowItem["endCustomerVrfc_id"]
        relevantProjects = allProjects.filter(
            sales_name__rfp=rfpId, mainCustomer=mcId, finalCustomer=ecId)
        # add to table for missing orders
        if relevantProjects.count() > 0:
            for index in range(0, len(relevantProjects), 1):
                projectsWithmissingSalesPlan.append(relevantProjects[index].id)
        else:
            print("no rel proj found", rfpId, mcId, ecId)

    #print("--> projects boup with missing orders", projectsWithmissingSalesPlan)

    """
    clean the missing orders table
    """
    MissingSalesPlan.objects.all().delete()
    missingSalesPlanObjsArr = []

    for project in projectsWithmissingSalesPlan:
        newMissingOrderEntry = MissingSalesPlan(project_id=project)
        missingSalesPlanObjsArr.append(MissingSalesPlan)

    missingSalesPlanObjs = MissingSalesPlan.objects.bulk_create(
        missingSalesPlanObjsArr, batch_size=1000
    )

    # update the ProjectError table accordingly
    allProjectErrors = ProjectError.objects.all()
    projectErrorsUpdate = []
    projectErrorsCreate = []

    allProjectErrorsProjectIds = allProjectErrors.values_list(
        "project", flat=True
    ).order_by("project")

    #print("allProjectErrorsProjectIds", allProjectErrorsProjectIds)
    # create new objects if required
    for projectWithNoOrder in projectsWithmissingSalesPlan:
        if projectWithNoOrder not in allProjectErrorsProjectIds:
            item = ProjectError(project_id=projectWithNoOrder, error_ids="29")
            projectErrorsCreate.append(item)

    # check the existing project errors and remove / add error 21 acoordingly
    for projectErrorRow in allProjectErrors:
        # so if this error row is affected by not having an order
        if projectErrorRow.project_id in projectsWithmissingSalesPlan:
            if "29" in projectErrorRow.error_ids:
                pass
            else:
                projectErrorRow.error_ids = projectErrorRow.error_ids + ",29"
                projectErrorsUpdate.append(projectErrorRow)
        else:
            # check if a project with missing vrfc orcer (Error 21) is stored here. if yes, check if remove
            if "29" in projectErrorRow.error_ids:
                # remove 21
                REPLACEMENTS = [
                    (",29,", ","),
                    (",29", ""),
                    ("29,", ""),
                ]
                for old, new in REPLACEMENTS:
                    projectErrorRow.error_ids = projectErrorRow.error_ids.replace(
                        old, new)
                    # projectErrorRow.save()
                projectErrorsUpdate.append(projectErrorRow)
            else:
                pass

    ProjectError.objects.bulk_update(
        projectErrorsUpdate, ["project", "error_ids"], batch_size=1000
    )

    newly_created_projectErrors = ProjectError.objects.bulk_create(
        projectErrorsCreate, batch_size=1000
    )

    """
    for each sales plan where there is no project, store the ids in the SalesPlanWithNoProject
    """
    SalesPlanWithNoProject.objects.all().delete()
    SalesPlanWithNoProjectBulkCreateArray = []

    # for each rfp + mc + ec combination, store this in missingProjects table
    for missingProject in missingProjectKeysRfpLevelSales:

        item = SalesPlanWithNoProject(
            rfp_id=missingProject["rfp_id"], mainCustomer_id=missingProject["mainCustomer_id"], endCustomer_id=missingProject["endCustomer_id"])
        SalesPlanWithNoProjectBulkCreateArray.append(item)

    newly_created_projectErrors = SalesPlanWithNoProject.objects.bulk_create(
        SalesPlanWithNoProjectBulkCreateArray, batch_size=1000
    )

    """
    now repeat the procedure above and 
    check for all projects if the combination of main and end customer exists, as well as the absolute values
    """

    # check if main and end customers are still valid
    allFinalCustomers = FinalCustomers.objects.all()
    allMainCustomers = MainCustomers.objects.all()
    validFinalCustomers = allFinalCustomers.filter(valid=True)
    validMainCustomers = allMainCustomers.filter(valid=True)

    projectErrorsCustomersCreate = []
    projectErrorsCustomersModify = []
    allProjectErrors = None
    allProjectErrors = ProjectError.objects.all()
    allProjectErrorsProjectIds = allProjectErrors.values_list(
        "project", flat=True
    ).order_by("project")

    for project in allProjects:
        print("%% checking", project)
        projectLevelErrors = ""

        if validFinalCustomers.filter(finalCustomerName=project.finalCustomer.finalCustomerName).count() == 0:
            projectLevelErrors = projectLevelErrors + ",23"

        if validMainCustomers.filter(customerName=project.mainCustomer.customerName).count() == 0:
            projectLevelErrors = projectLevelErrors + ",24"
        else:
            mainCustomer = validMainCustomers.get(
                customerName=project.mainCustomer.customerName)

            if mainCustomer.finalCustomers.filter(id=project.finalCustomer_id).exists():
                pass
            else:
                projectLevelErrors = projectLevelErrors + ",22"

        print("%% projectLevelErrors", projectLevelErrors)

        if len(projectLevelErrors) > 0:
            # if project has no error, create a new error entry. else retrieve and modify accordingly.
            if project.id not in allProjectErrorsProjectIds:
                # remove leading comma first
                projectLevelErrors = projectLevelErrors[1:]
                item = ProjectError(
                    project_id=projectWithNoOrder, error_ids=projectLevelErrors)
                projectErrorsCustomersCreate.append(item)
            else:
                print("editing project errors")
                currentProjectErrorObject = allProjectErrors.get(
                    project=project.id)
                # check if a project with missing vrfc orcer (Error 21) is stored here. if yes, check if remove
                if "22" in currentProjectErrorObject.error_ids:
                    REPLACEMENTS = [
                        (",22,", ","),
                        (",22", ""),
                        ("22,", ""),
                    ]
                    for old, new in REPLACEMENTS:
                        currentProjectErrorObject.error_ids = currentProjectErrorObject.error_ids.replace(
                            old, new)

                if "23" in currentProjectErrorObject.error_ids:
                    REPLACEMENTS = [
                        (",23,", ","),
                        (",23", ""),
                        ("23,", ""),
                    ]
                    for old, new in REPLACEMENTS:
                        currentProjectErrorObject.error_ids = currentProjectErrorObject.error_ids.replace(
                            old, new)

                if "24" in currentProjectErrorObject.error_ids:
                    REPLACEMENTS = [
                        (",24,", ","),
                        (",24", ""),
                        ("24,", ""),
                    ]
                    for old, new in REPLACEMENTS:
                        currentProjectErrorObject.error_ids = currentProjectErrorObject.error_ids.replace(
                            old, new)

                currentProjectErrorObject.error_ids = currentProjectErrorObject.error_ids + \
                    projectLevelErrors
                projectErrorsCustomersModify.append(currentProjectErrorObject)

        else:
            pass

    ProjectError.objects.bulk_update(
        projectErrorsCustomersModify, ["project", "error_ids"], batch_size=1000
    )

    newly_created_projectErrors = ProjectError.objects.bulk_create(
        projectErrorsCustomersCreate, batch_size=1000
    )

    print("projectErrorsCustomersModify")
    print(projectErrorsCustomersModify)
    print("finished running VRFC import")
    return True


# importVrfcOohCsv()


"""

for reference:

    class ErrorTypesVrfcOohConflicts(models.Model):
    errorType = models.SmallIntegerField(blank=True, null=True)
    evaluationDate = models.DateTimeField(default=now, editable=False)

    class vrfcOohConflicts(models.Model):
        vrfcOohEntry = models.ForeignKey(VrfcOrdersOnHand, on_delete=PROTECT, null=True, blank=True)
        errorType = models.ForeignKey(ErrorTypesVrfcOohConflicts, on_delete=PROTECT, null=True, blank=True)
        evaluationDate = models.DateTimeField(default=now, editable=False)


for reference: 

    class VrfcOrdersOnHand(models.Model):
        rfp = models.ForeignKey(Product, on_delete=models.PROTECT, blank=True, null=False)
        mainCustomerVrfc = models.ForeignKey(MainCustomers, on_delete=models.PROTECT, blank=True, null=False)
        endCustomerVrfc = models.ForeignKey(FinalCustomers, on_delete=models.PROTECT, blank=True, null=False)
        year = models.SmallIntegerField(default=0, blank=True, null=True)
        quarter = models.SmallIntegerField(default=0, blank=True, null=True)
        quantity = models.IntegerField(default=0, blank=True, null=True)
        asp = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=4)
        revenue = models.DecimalField(blank=True, null=True, max_digits=15, decimal_places=2)

    class VrfcSalesForecast(models.Model):
        rfp = models.ForeignKey(Product, on_delete=models.PROTECT, blank=True, null=False)
        mainCustomerVrfc = models.ForeignKey(MainCustomers, on_delete=models.PROTECT, blank=True, null=False)
        endCustomerVrfc = models.ForeignKey(FinalCustomers, on_delete=models.PROTECT, blank=True, null=False)
        year = models.SmallIntegerField(default=0, blank=True, null=True)
        quarter = models.SmallIntegerField(default=0, blank=True, null=True)
        quantity = models.IntegerField(default=0, blank=True, null=True)
        asp = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=4)
        revenue = models.DecimalField(blank=True, null=True, max_digits=15, decimal_places=2)

    class VrfcPmForecast(models.Model):
        rfp = models.ForeignKey(Product, on_delete=models.PROTECT, blank=True, null=False)
        mainCustomerVrfc = models.ForeignKey(MainCustomers, on_delete=models.PROTECT, blank=True, null=False)
        endCustomerVrfc = models.ForeignKey(FinalCustomers, on_delete=models.PROTECT, blank=True, null=False)
        year = models.SmallIntegerField(default=0, blank=True, null=True)
        quarter = models.SmallIntegerField(default=0, blank=True, null=True)
        quantity = models.IntegerField(default=0, blank=True, null=True)
        asp = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=4)
        revenue = models.DecimalField(blank=True, null=True, max_digits=15, decimal_places=2)


"""
