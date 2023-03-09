# Francisco Falise, copyright 01/10/2022
# new way using adolphs List

import pandas as pd
from ..models import *
from core.project.models import ProductFamily, Product, ProductSeries, ProductPackage, SalesName, DummyCustomerExceptionProductFamilies
from datetime import datetime
from django.utils import timezone
import pandasql as ps
from enum import Enum
from typing import (
    Iterable,
    TypeVar,
    MutableSequence,
    MutableSequence,
    MutableSequence,
    Any,
)


def getSeriesPl58(df):
    seriesList = []
    dfpl58 = df.loc[((df["PL"] == "58")), :]

    # if RFP is in TCx... get the series
    queryUniqueRfp = """SELECT DISTINCT RFPProduct FROM df ORDER BY RFPProduct ASC;"""

    queryResultUniqueRfp = ps.sqldf(queryUniqueRfp, locals())[
        "RFPProduct"].tolist()

    for rfp in queryResultUniqueRfp:
        if ("TC1" in rfp) | ("TC2" in rfp) | ("TC3" in rfp) | ("TC4" in rfp):
            if len(rfp) > 3:
                tcName = rfp[4:7]
                stringName = rfp[7]
                thisdict = {
                    "tcName": tcName,
                    "series": stringName,
                }

                seriesList.append(thisdict)
                print(rfp, "adding series", stringName)

    seriesList = [i for n, i in enumerate(
        seriesList) if i not in seriesList[n + 1:]]
    print("----> final series list")
    print(seriesList)

    return seriesList


def adolfRun(fileUpload: bool, uploadPath: str) -> bool:
    now = datetime.now()
    date = now.strftime("%Y%m%d")
    totalImportErrors = []
    df1 = None
    csv = False
    # Block A: loading, cleaning job
    if fileUpload == False:
        df1 = pd.read_csv(
            "./persistentLayer/importJobs/adolphList_full.csv",
            sep=";",
            decimal=",",
            low_memory=False,
            skiprows=7,
        )
    else:
        filePath = "." + uploadPath
        if uploadPath[-3:] == "csv":
            csv = True

        df1 = pd.read_csv(
            filePath,
            sep=";",
            decimal=",",
            low_memory=False,
            skiprows=7,
        )

    # df1 = pd.read_csv("./adolphList.csv", sep = ';', decimal=",", low_memory=False, skiprows=7)
    df1 = df1.drop([0])
    df1 = df1.fillna("None")

    # df1 = df1.reset_index(drop=True)

    # df1 = pd.read_csv("./productMarketing/importJobs/adolphList.csv", sep = ';', decimal=",")
    # df1 = df1.drop([0, 1, 2, 3, 4, 5, 6])
    # df1 = df1.reset_index(drop=True)

    # rename PPOS match (its an empty column)
    cols = pd.Series(df1.columns)
    dup_count = cols.value_counts()
    for dup in cols[cols.duplicated()].unique():
        cols[cols[cols == dup].index.values.tolist()] = [
            dup + str(i) for i in range(1, dup_count[dup] + 1)
        ]

    df1.columns = cols
    # df1.to_csv("./test3.csv", sep = ";", decimal=",", header=True)
    # for now everything handled as strings, PPOS is duplicated! we need PPOS.1
    df1 = df1[
        [
            "DIV",
            "BL",
            "PL",
            "PL Desc",
            "PL_HFG",
            "HFG",
            "HFG Description",
            "Marketing Contact",
            "Basic Type (max)",
            "RFP Product",
            "Product Maturity",
            "Product Family *",
            "Main Family *",
            "Sales Product Name",
            "SP#",
            "Package (PPOS)",
            "Package (CRM)",
            "PPOS.1",
            "Quality Requirement Category",
        ]
    ]

    # rename PPOS.1 to PPOS
    df1 = df1.rename(columns={"PPOS.1": "PPOS"})

    """
    comment für Patric: ab hier kann man einen Flow machen. Oberhalb von diesem Punkt kann man Daten aus Denodo ziehen. und im obigen format überführen. 
    """

    # keep only pl hfg 58_x or 90_x
    df1 = df1.loc[((df1["PL_HFG"].str.contains("58_")) |
                   (df1["PL_HFG"].str.contains("90_"))), :]

    # remove HFG 9 (pl58) and S (both pls)
    df1 = df1.loc[
        (((df1["PL"] == "58") & (df1["HFG"] != "9")) | (df1["PL"] == "90")), :
    ]
    # df1 = df1.loc[(((df1['PL'] =='58') & (df1['HFG'] != '9')) ), :]

    df1 = df1[df1["HFG"] != "S"]

    df1.sort_values("PL")

    # remove dummy products
    df1 = df1[df1["Quality Requirement Category"] != "NOT APPLICABLE"]

    df1 = df1[df1["Sales Product Name"].str.contains("DAISY") == False]

    # wenn package blank ist, das ist samples -> todo

    df1 = df1.rename(columns={"Product Family *": "ProductFamily"})
    df1 = df1.rename(columns={"HFG Description *": "HFGDescription"})
    df1 = df1.rename(columns={"Basic Type (max)": "BasicTypeMax"})
    df1 = df1.rename(columns={"RFP Product": "RFPProduct"})
    df1 = df1.rename(columns={"Product Maturity": "ProductMaturity"})
    df1 = df1.rename(columns={"Sales Product Name": "SalesName"})
    df1 = df1.rename(columns={"SP#": "SPNumber"})
    df1 = df1.rename(columns={"Package (PPOS)": "PackagePPOS"})
    df1 = df1.rename(columns={"Package (CRM)": "PackageCRM"})
    df1 = df1.rename(
        columns={"Quality Requirement Category": "QualityRequirementCategory"}
    )
    df1 = df1.rename(columns={"Main Family *": "MainFamily"})

    df1 = df1[df1["ProductFamily"] != None]
    df1 = df1[df1["ProductFamily"] != "None"]
    df1 = df1[df1["ProductFamily"] != ""]
    df1 = df1.reset_index(drop=True)
    length = len(df1.index)

    df1.to_csv("./filteredProductList1.csv", sep=";", decimal=",", header=True)

    for index in range(0, length, 1):
        uncasted = df1.loc[index, "ProductFamily"]
        rfpProduct = df1.loc[index, "RFPProduct"]

        value = str(df1.loc[index, "ProductFamily"])

        if len(value) == 0:
            df1.loc[index, "ProductFamily"] = "delete"
            print(
                "evaluating",
                value,
                "type",
                type(value),
                "len",
                len(value),
                "isspace",
                value.isspace(),
            )

        if value.isspace() == True:
            df1.loc[index, "ProductFamily"] = "delete"
            print(
                "evaluating",
                value,
                "type",
                type(value),
                "len",
                len(value),
                "isspace",
                value.isspace(),
            )

        if value == "None":
            df1.loc[index, "ProductFamily"] = "delete"
            print(
                "evaluating",
                value,
                "type",
                type(value),
                "len",
                len(value),
                "isspace",
                value.isspace(),
            )

        if value == "":
            df1.loc[index, "ProductFamily"] = "delete"
            print(
                "evaluating",
                value,
                "type",
                type(value),
                "len",
                len(value),
                "isspace",
                value.isspace(),
            )

    # df1 = df1[df1.apply(lambda x : "delete" if (len(str(x['ProductFamily'])) == 0) else x,axis=1)]

    df1 = df1[df1["ProductFamily"] != "delete"]
    df1 = df1.reset_index(drop=True)
    # df1 = df1[len(df1['ProductFamily']).values > 0]
    # df1 = df1[(df1['ProductFamily']).values.isspace() == False]

    # df1 = df1[df1['Sales Product Name'] not in "DAISY"]
    df1 = df1.reset_index(drop=True)
    print("df 1")
    print(df1)

    # generate family names
    familyNames: MutableSequence[str] = []

    queryFamilyNames = (
        """SELECT DISTINCT MainFamily FROM df1 ORDER BY MainFamily ASC;"""
    )
    queryResultFamilyNames = ps.sqldf(queryFamilyNames, locals())[
        "MainFamily"].tolist()
    (print("##### queryResultFamilyNames", queryResultFamilyNames))

    #currentProductFamilyObjects = ProductFamily.objects.update(valid=False)

    """
    new code FF for bulk updates of product families.

    existing_values_list_families = list(
        currentProductFamilyObjects.objects.values_list(
            "family_name"
        ).order_by("id")
    )
    existing_qs_families = list(
        currentProductFamilyObjects.all().order_by("id"))

    existing_dict_families = dict(
        zip(existing_values_list_families, existing_qs_families))
    # existing_dict {(3, "AUTOPSOC"): <ProductFamily: ID: 21 - etc> ... left side: id and name; right: full object
    existingFamilies = []  # could be used for bulk update
    newFamilies = []  # will be used for bulk create

    for family in queryResultFamilyNames:
        if value in existing_dict_families:
            existing_db_value = existing_dict_families.get(value)
            existingFamilies.append(existing_db_value)
        else:
            # will append the family name to an array as a string
            newFamilies.append(value[1])

        if "AURIX3G" in family:
            exceptionObj, created = DummyCustomerExceptionProductFamilies.objects.get_or_create(
                exceptedFamily=obj)

    # assigning new values to existing queryset.
    for obj in existingFamilies:
        obj.importDate = datetime.now(tz=timezone.utc)
        obj.valid = True

    # bulk update values that we added new values above
    ProductFamily.objects.bulk_update(
        existingFamilies, ["importDate", "valid"]
    )

    # now bulk creation based on the array of new names
    instance_objs = [
        ProductFamily(
            family_name=newFamily,
            importDate=datetime.now(tz=timezone.utc),
            valid=True
        )
        for newFamily in newFamilies
    ]

    # queryset of newly created newly_created_families
    newly_created_families = ProductFamily.objects.bulk_create(
        instance_objs
    )
    """

    # old code FF
    # create entries of product family tables
    # this is still used for some dropdowns... did not figure out a quick way yet to remove these

    for family in queryResultFamilyNames:
        # print("creating family", family)
        obj, created = ProductFamily.objects.get_or_create(
            family_name=str(family))
        obj.importDate = datetime.now(tz=timezone.utc)
        obj.valid = True
        obj.save()

        # Req. 141: add to exemption list if aurix tc4 or aureo
        """
        if "AURIX3G" in family:
            exceptionObj, created = DummyCustomerExceptionProductFamilies.objects.get_or_create(
                exceptedFamily=obj)
        """

    # create entries of product family tables
    for family in queryResultFamilyNames:
        if "AURIX3G" in family:
            exceptionObj, created = DummyCustomerExceptionProductFamilies.objects.get_or_create(
                exceptedFamily=family)

    # now we need to generate the series, if possible
    length = len(df1.index)

    for index in range(0, length, 1):
        seriesValue = ""
        familyName = df1.loc[index, "ProductFamily"]
        if "AURIX_TC" in str(familyName):
            seriesValue = familyName[-1]
            df1.loc[index, "Series"] = seriesValue
            df1.loc[index, "PackageShortName"] = df1.loc[index, "RFPProduct"][8]
        else:
            seriesValue = str(familyName)
            df1.loc[index, "Series"] = seriesValue
            df1.loc[index, "PackageShortName"] = ""

    queryPackages = """SELECT DISTINCT MainFamily, Series, PackagePPOS, PackageShortName FROM df1 ORDER BY PackagePPOS ASC;"""
    """
    queryResultPackages = ps.sqldf(
        queryPackages, locals())  # ['PackagePPOS'].tolist()
    """
    # remove duplicates
    queryResultFamilyNames = list(dict.fromkeys(queryResultFamilyNames))
    # queryResultPackages = list(dict.fromkeys(queryResultPackages))

    # generate product series for PL58, microcontrollers
    # seriesList = getSeriesPl58(df1)

    querySeries = (
        """SELECT DISTINCT MainFamily, Series FROM df1 ORDER BY MainFamily ASC;"""
    )
    # ['PackagePPOS'].tolist()
    """

    querySeriesResult = ps.sqldf(querySeries, locals())

    # update only non dummy objects
    nonDummySeries = ProductSeries.objects.filter(dummy=False)
    try:
        nonDummySeries.objects.update(valid=False)
    except:
        print("non dummy series empty")
    """

    """
    old code Francisco for series creation
    """
    """
    for index in range(0, len(querySeriesResult.index), 1):
        familyName = querySeriesResult.loc[index, "MainFamily"]
        familyObject = ProductFamily.objects.get(family_name=familyName)
        series = querySeriesResult.loc[index, "Series"]
        seriesObj, created = ProductSeries.objects.get_or_create(
            family=familyObject, series=series
        )
        seriesObj.dummy = False
        seriesObj.importDate = datetime.now(tz=timezone.utc)
        seriesObj.valid = True
        seriesObj.save()
        print(index, "creating series", familyName,
              "--", series, "obj", seriesObj)
    """
    """
    # create packages
    nonDummyPackages = ProductPackage.objects.filter(dummy=False)
    try:
        nonDummyPackages.objects.update(valid=False)
    except:
        print("no non dummy packages")
    productSeriesObjects = ProductSeries.objects.all()
    queryResultPackages.to_csv(
        "./queryResultPackages.csv", sep=";", decimal=",", header=True
    )

    # series and package dummy are strictly limited, so no possible conflicts here
    for index in range(0, len(queryResultPackages.index), 1):
        series = queryResultPackages.loc[index, "Series"]
        packagePpos = queryResultPackages.loc[index, "PackagePPOS"]
        family = queryResultPackages.loc[index, "MainFamily"]
        # print("product family", family, "type", type(family), "len", len(str(family)), "package", packagePpos)
        packageDescription = queryResultPackages.loc[index, "PackageShortName"]
        familyObj = ProductFamily.objects.get(family_name=family)
        seriesObj = ProductSeries.objects.get(
            series=series, family=familyObj)
        packageObj, created = ProductPackage.objects.get_or_create(
            package=packagePpos, series=seriesObj
        )
        packageObj.valid = True
        packageObj.importDate = datetime.now(tz=timezone.utc)
        packageObj.dummy = False
        # if aurix line, add the shortname for package
        packageObj.description = packageDescription
        packageObj.save()
    """

    # these queries were used to generate stats when analyzing the input data

    queryProducts = """SELECT DISTINCT RFPProduct, Series, MainFamily, BasicTypeMax, PackagePPOS, HFG, PPOS, SalesName FROM df1 ORDER BY MainFamily ASC;"""
    """
    queryResultProducts = ps.sqldf(
        queryProducts, locals()
    )
    """

    querSalesNameCount = """SELECT COUNT(DISTINCT SalesName) FROM df1;"""
    """
    queryResultSalesNameCount = ps.sqldf(
        querSalesNameCount, locals()
    )
    """

    querySalesNameDuplicates = """SELECT * FROM df1 WHERE SalesName in (SELECT SalesName FROM ( SELECT SalesName, RFPProduct FROM df1 GROUP BY  SalesName, RFPProduct) GROUP BY SalesName HAVING COUNT(*) > 1);"""
    queryResultSalesNameDuplicates = ps.sqldf(
        querySalesNameDuplicates, locals()
    )

    queryResultSalesNameDuplicates.to_csv("./df1TestSalesNamesUniqueReport.csv",
                                          sep=";", decimal=",", header=True)

    duplicatedSalesNames = []

    for index in range(0, len(queryResultSalesNameDuplicates.index), 1):
        duplicatedSalesNames.append(
            queryResultSalesNameDuplicates.loc[index, "SalesName"])

    duplicatedSalesNames = list(dict.fromkeys(duplicatedSalesNames))

    """
    Handling of existing dummy products:

    Before running the final import, all real entries are set to valid = False. This way, dummys are kept with valid = True.
    
    Keep in mind, that there IS NO unique together constraint for RFP + Series + Package + Family. This allows for quick update of dummy values, when the real entry comes from PGS+,
    assuming that the dummy RFP and Sales Name match exactly the PGS+ identifiers.

    If a dummy was crated with real series, real package, real family, then if the new RFP matches the existing dummy RFP name, then the dummy entry will be updated
    and set to non-dummy (real). The match is done based on RFP name. If the user entered dummy package, dummy series, then the dummy entry will also be updated automatically, since the rfp matching is done solely on RFP string.

    Handling of existing dummy sales names (which are based on real RFPs): they will be also updated automatically, since matching is done based on RFP name and sales name at a string level.

    """
    print("$$$$$$$$$$$$$$$$$$$$$$$ starting to create products")

    df1 = df1.reset_index(drop=True)

    # first deal with duplicated sales names
    for index in range(0, len(df1.index), 1):
        # so if sales name in duplicated list, append "dupl" and the SPNumber for uniqueness
        salesName = df1.loc[index, "SalesName"]
        if salesName in duplicatedSalesNames:
            df1.loc[index, "SalesName"] = salesName + \
                "-dupl-" + str(df1.loc[index, "SPNumber"])[-4:]

    processedRfps = []
    rfpObjects = []
    # deactivate all non dummy products
    nonDummyProducts = Product.objects.filter(dummy=False)
    # nonDummyProducts.update(valid=False) # removed due to faulty logic
    nonDummySalesNames = SalesName.objects.filter(dummy=False)
    # nonDummySalesNames.update(valid=False) # removed due to faulty logic

    """
    here begins the new code for bulk creation / update
    """
    existing_values_list_products = list(
        nonDummyProducts.values_list(
            "rfp"
        ).order_by("id")
    )

    existing_qs_products = list(
        nonDummyProducts.order_by("id"))
    existing_dict_product = dict(
        zip(existing_values_list_products, existing_qs_products))

    # existing_dict_product {(3, sak-tc4-xxx): <ProjectVolumePrices: ID: 21 - QTY: 0 - YR: 2025> ... left side: year and project ID; full object

    alreadyExistingProducts = []
    newProducts = []

    # following arrays are used either to update or bulk create properties
    newProdSeries = []
    newProdFam = []
    newProdPackage = []
    newProdHfg = []
    newProdPpos = []
    newProdFamilyDetail = []
    newProdBasicType = []
    newProdPlHfg = []

    existingProducts = []
    existingProdSeries = []
    existingProdFam = []
    existingProdPackage = []
    existingProdHfg = []
    existingProdPpos = []
    existingProdFamilyDetail = []
    existingProdBasicType = []
    existingProdPlHfg = []

    for index in range(0, len(df1.index), 1):
        rfp = df1.loc[index, "RFPProduct"]

        # if the rfp object already exists, add it to the existing products array.
        # else add the rfp string to the newProductsArray, as well as all necessary attributes
        # the statement "rfp not in existingProducts" if to avoid duplicate entries
        if (rfp in existing_dict_product) and (rfp not in existingProducts):
            existing_dict_value = existing_dict_product.get(rfp)
            alreadyExistingProducts.append(existing_dict_value)
            existingProducts.append(rfp)
            existingProdSeries.append(df1.loc[index, "Series"])
            existingProdFam.append(df1.loc[index, "MainFamily"])
            existingProdPackage.append(df1.loc[index, "PackagePPOS"])
            existingProdHfg.append(df1.loc[index, "HFG"])
            existingProdPpos.append(df1.loc[index, "PPOS"])
            existingProdFamilyDetail.append(df1.loc[index, "ProductFamily"])
            existingProdBasicType.append(df1.loc[index, "BasicTypeMax"])
            existingProdPlHfg.append(df1.loc[index, "PL_HFG"])

        elif (rfp not in existing_dict_product) and (rfp not in newProducts):
            newProducts.append(rfp)
            newProdSeries.append(df1.loc[index, "Series"])
            newProdFam.append(df1.loc[index, "MainFamily"])
            newProdPackage.append(df1.loc[index, "PackagePPOS"])
            newProdHfg.append(df1.loc[index, "HFG"])
            newProdPpos.append(df1.loc[index, "PPOS"])
            newProdFamilyDetail.append(df1.loc[index, "ProductFamily"])
            newProdBasicType.append(df1.loc[index, "BasicTypeMax"])
            newProdPlHfg.append(df1.loc[index, "PL_HFG"])

        else:
            pass

    # assigning new values to existing queryset. years with volume is the user input.
    # this will update existing entries for an RFP, e.g. if the HFG or basic type is changed in PGS+.
    for index in range(0, len(alreadyExistingProducts), 1):
        productObject = alreadyExistingProducts[index]
        productObject.hfg = existingProdHfg[index]
        productObject.ppos = existingProdPpos[index]
        productObject.basicType = existingProdBasicType[index]
        productObject.availablePGS = True
        productObject.familyHelper = existingProdFam[index]
        productObject.packageHelper = existingProdPackage[index]
        productObject.seriesHelper = existingProdSeries[index]
        productObject.valid = True
        productObject.familyDetailHelper = existingProdFamilyDetail[index]
        productObject.plHfg = existingProdPlHfg[index]

        # productObject.save()
        rfpObjects.append(productObject)

    # bulk update values that we added new values above
    Product.objects.bulk_update(
        alreadyExistingProducts, ["hfg", "ppos", "basicType", "availablePGS",
                                  "familyHelper", "packageHelper", "seriesHelper", "valid", "familyDetailHelper", "plHfg"]
    )

    # creating new instances
    instance_objs = []
    for index in range(0, len(newProducts), 1):
        newProduct = Product(
            rfp=newProducts[index],
            hfg=newProdHfg[index],
            ppos=newProdPpos[index],
            basicType=newProdBasicType[index],
            availablePGS=True,
            familyHelper=newProdFam[index],
            packageHelper=newProdPackage[index],
            seriesHelper=newProdSeries[index],
            plHfg=newProdPlHfg[index],
            valid=True,
            familyDetailHelper=newProdFamilyDetail[index],
            dummy=False
        )
        instance_objs.append(newProduct)

    # queryset of newly created volumes
    newly_created_products = Product.objects.bulk_create(
        instance_objs
    )

    rfpObjects = Product.objects.filter(dummy=False, valid=True)
    print("$$$$$$$$$$$$$$$$$$$$$$$ finished creating products")

    """
    now repeat the procedure with salesnames...
    """
    alreadyExistingSalesNames = []
    newSalesNames = []
    allSalesNames = SalesName.objects.all()
    existing_values_list_salesNames = list(
        allSalesNames.values_list(
            "name"
        ).order_by("id")
    )

    existing_qs_salesNames = list(
        allSalesNames.all().order_by("id"))
    existing_dict_salesName = dict(
        zip(existing_values_list_salesNames, existing_qs_salesNames))
    # left hand is sales name as string, right hand the object

    for index in range(0, len(df1.index), 1):
        rfp = df1.loc[index, "RFPProduct"]
        productObject = rfpObjects.get(rfp=rfp)
        basicTypeMax = df1.loc[index, "BasicTypeMax"]
        salesName = df1.loc[index, "SalesName"]

        if (len(basicTypeMax) > 0) and (basicTypeMax.isspace() == False):
            if salesName in existing_dict_salesName:
                existing_dict_value = existing_dict_salesName.get(salesName)
                existing_dict_value.rfp = productObject
                existing_dict_value.dummy = False
                alreadyExistingSalesNames.append(existing_dict_value)

            else:
                # else create
                newSalesName = SalesName(
                    name=salesName,
                    rfp=productObject,
                    dummy=False
                )
                newSalesNames.append(newSalesName)

    # bulk update values that we added new values above
    SalesName.objects.bulk_update(
        alreadyExistingSalesNames, ["rfp", "dummy"]
    )

    newly_created_salesNames = SalesName.objects.bulk_create(
        newSalesNames
    )

    """
    # old code begin
    for index in range(0, len(df1.index), 1):
        rfp = df1.loc[index, "RFPProduct"]
        if rfp not in processedRfps:
            series = df1.loc[index, "Series"]
            packagePpos = df1.loc[index, "PackagePPOS"]
            family = df1.loc[index, "MainFamily"]

            processedRfps.append(rfp)

            basicTypeMax = df1.loc[index, "BasicTypeMax"]
            productObject, created = Product.objects.get_or_create(rfp=rfp)
            productObject.hfg = df1.loc[index, "HFG"]
            productObject.ppos = df1.loc[index, "PPOS"]
            productObject.basicType = basicTypeMax
            productObject.availablePGS = True
            productObject.familyHelper = df1.loc[index, "MainFamily"]
            productObject.packageHelper = df1.loc[index, "PackagePPOS"]
            productObject.seriesHelper = df1.loc[index, "Series"]
            productObject.valid = True
            productObject.familyDetailHelper = df1.loc[index, "ProductFamily"]
            # productObject.package =
            productObject.save()
            rfpObjects.append(productObject)

            salesName = df1.loc[index, "SalesName"]
            if (len(basicTypeMax) > 0) and (basicTypeMax.isspace() == False):
                salesNameObj, created = SalesName.objects.get_or_create(
                    name=salesName)
                salesNameObj.rfp = productObject
                salesNameObj.dummy = False
                salesNameObj.save()

        else:
            indexA = processedRfps.index(rfp)
            productObject = rfpObjects[indexA]
            salesName = df1.loc[index, "SalesName"]
            if (len(basicTypeMax) > 0) and (basicTypeMax.isspace() == False):
                salesNameObj, created = SalesName.objects.get_or_create(
                    name=salesName)
                salesNameObj.rfp = productObject
                salesNameObj.dummy = False
                salesNameObj.save()

        if len(processedRfps) > 100:
            processedRfps = processedRfps[:100]
            rfpObjects = rfpObjects[:100]

    """
    ####
    """
    querySalesNames = 'SELECT DISTINCT RFPProduct, SalesName FROM df1 WHERE RFPProduct = '+ '"' + rfp + '"' + ' ORDER BY RFPProduct ASC;'
    print("executing query:", querySalesNames )
    queryResultSalesNames= ps.sqldf(querySalesNames, locals()) #['ProductFamily'].tolist()

    for index in range(0, len(queryResultSalesNames.index) , 1):
    """

    print("################# FINISHED IMPORTING SALES NAMES AND PRODUCTS")
    # clean buffer
    processedRfps = []
    rfpObjects = []

    return True


# adolfRun()
