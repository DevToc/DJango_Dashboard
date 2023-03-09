# Francisco Falise, copyright 01/10/2022
# for each row get the rfp of the salesname, lookup in the Product.rfp table. if exist, set as foreign key and save salesname.
# if no rfp exist, create the rfp. then generate the respective entry

import pandas as pd
from ..models import *


def runSalesNameImport():
    df1 = pd.read_csv(
        "./persistentLayer/importJobs/salesNameImport.csv", sep=";", decimal=","
    )
    length = len(df1.index)
    index = 0
    print("### input")
    print(df1)
    print("####")
    for i in range(0, length, 1):

        rfpImport = df1.loc[i, "rfp"]
        salesNameImport = df1.loc[i, "salesName"]

        products = Product.objects.filter(rfp=rfpImport)
        print("inputs", salesNameImport, rfpImport, "products", products)
        if products.count() > 0:
            print("found more than 0 rps!")

            # what with sales name daisy chain wafer?

            if products.count() == 1:
                product = products[0]

                salesNameObj, created = SalesName.objects.get_or_create(salesName=salesNameImport
                                                                        )

                salesNameObj.rfp = product
                if created == True:
                    print(index, "created", salesNameObj)
                else:
                    print(index, "retrieved", salesNameObj)

            else:
                # tbd
                print("found more than one matching product!!!")
                # either warning, automated email and then manual import or call support

        else:
            print("rfp did not exist! problem at PGS!?")

        # i = i + 1

    return True


def runProductImportNew():
    df1 = pd.read_csv(
        "./productMarketing/importJobs/rpfListExtended.csv", sep=";", decimal=","
    )
    print("running product import!")
    length = len(df1.index)
    index = 0

    for i in range(0, length, 1):

        rfpImport = df1.loc[i, "rfp"]
        pposImport = df1.loc[i, "ppos"]
        hfgImport = df1.loc[i, "hfg"]
        familydescription = df1.loc[i, "familydescription"]
        familyfull = df1.loc[i, "familyfull"]
        series = df1.loc[i, "series"]
        package = df1.loc[i, "package"]
        seriesDescription = df1.loc[i, "seriesDescription"]
        packageDescription = df1.loc[i, "packageDescription"]

        # retrieve or create HFG
        hfgList = ProductHFG.objects.filter(productHFG=hfgImport)
        hfgObj = ""

        if hfgList.count() > 0:
            hfgObj = hfgList[0]
        else:
            print("creating hfg!")
            hfgObj, created = ProductHFG.objects.get_or_create(
                productHFG=hfgImport)

        # retrieve or create PPOS
        pposList = ProductPPOS.objects.filter(
            productPPOS=pposImport, productHFG=hfgObj)
        pposObj = ""

        if pposList.count() > 0:
            pposObj = pposList[0]
        else:
            print("creating hfg!")
            pposObj, created = productPPOS.objects.get_or_create(
                productPPOS=pposImport, productHFG=hfgObj
            )

        products = Product.objects.filter(rfp=rfpImport)

        if products.count() > 0:
            print("found more than 0 products!")
            if products.count() == 1:
                product = products[0]

                productObj, created = Product.objects.get_or_create(
                    rfp=rfpImport)
                if created == True:
                    print(index, "created", productObj)
                    productObj.ppos = pposObj
                    productObj.hfg = hfgObj
                    productObj.familydescription = familydescription
                    productObj.familyfull = familyfull
                    productObj.series = series
                    productObj.package = package
                    productObj.seriesDescription = seriesDescription
                    productObj.packageDescription = packageDescription
                    productObj.save()
                else:
                    print(index, "retrieved and updating attributes", productObj)
                    productObj.ppos = pposObj
                    productObj.hfg = hfgObj
                    productObj.familydescription = familydescription
                    productObj.familyfull = familyfull
                    productObj.series = series
                    productObj.package = package
                    productObj.seriesDescription = seriesDescription
                    productObj.packageDescription = packageDescription
                    productObj.save()

            else:
                # tbd
                print("found more than one matching product!!!")
                # either warning, automated email and then manual import or call support

        else:
            productObj, created = Product.objects.get_or_create(rfp=rfpImport)
            productObj.ppos = pposObj
            productObj.hfg = hfgObj
            productObj.familydescription = familydescription
            productObj.familyfull = familyfull
            productObj.series = series
            productObj.package = package
            productObj.seriesDescription = seriesDescription
            productObj.packageDescription = packageDescription
            print("rfp did not exist! problem at PGS!?")
            productObj.save()
    return True


# products
def runProductImport():
    df1 = pd.read_csv(
        "./productMarketing/importJobs/rpfListExtended.csv", sep=";", decimal=","
    )
    print("running product import!")
    length = len(df1.index)
    index = 0
    print("### input")
    print(df1)
    print("####")
    for i in range(0, length, 1):

        rfpImport = df1.loc[i, "rfp"]
        pposImport = df1.loc[i, "ppos"]
        hfgImport = df1.loc[i, "hfg"]
        familydescription = df1.loc[i, "familydescription"]
        familyfull = df1.loc[i, "familyfull"]
        series = df1.loc[i, "series"]
        package = df1.loc[i, "package"]
        seriesDescription = df1.loc[i, "seriesDescription"]
        packageDescription = df1.loc[i, "packageDescription"]

        products = Product.objects.filter(rfp=rfpImport)

        if products.count() > 0:
            print("found more than 0 products!")
            if products.count() == 1:
                product = products[0]

                productObj, created = Product.objects.get_or_create(
                    rfp=rfpImport)
                if created == True:
                    print(index, "created", productObj)
                    productObj.ppos = pposImport
                    productObj.hfg = hfgImport
                    productObj.familydescription = familydescription
                    productObj.familyfull = familyfull
                    productObj.series = series
                    productObj.package = package
                    productObj.seriesDescription = seriesDescription
                    productObj.packageDescription = packageDescription
                    productObj.save()
                else:
                    print(index, "retrieved and updating attributes", productObj)
                    productObj.ppos = pposImport
                    productObj.hfg = hfgImport
                    productObj.familydescription = familydescription
                    productObj.familyfull = familyfull
                    productObj.series = series
                    productObj.package = package
                    productObj.seriesDescription = seriesDescription
                    productObj.packageDescription = packageDescription
                    productObj.save()

            else:
                # tbd
                print("found more than one matching product!!!")
                # either warning, automated email and then manual import or call support

        else:
            productObj, created = Product.objects.get_or_create(rfp=rfpImport)
            productObj.ppos = pposImport
            productObj.hfg = hfgImport
            productObj.familydescription = familydescription
            productObj.familyfull = familyfull
            productObj.series = series
            productObj.package = package
            productObj.seriesDescription = seriesDescription
            productObj.packageDescription = packageDescription
            print("rfp did not exist! problem at PGS!?")
            productObj.save()

    return True
