""" Patric Gudis, copyright 12 Oct 2022
The Goal is to import the entries from the vhkRfp.xlsx into the vhkl table while checking if the entry already exists.
At first unpivot the excel into an usable data frame.
Then go through each row to get the rfp of the salesname and the used currency.
Look up in the respective tables if exaclty one entry exists.
If more entries exists throw an error message. If no entry exist create the entry.
"""
import pandas as pd
from ..models import *
from core.project.models import Project
from productMarketing.models import ProjectVolumeMonthLog
from core.project.bulkProcessing import bulkUpdaterBoUpTable, bulkErrorUpdateEntrypoint
from datetime import datetime
from django.utils import timezone
from currencies.models import Currency

def runvhklImport(request):

    """
    Bring the data in the wanted form with unpivoting and creating the needed columns.
    """

    df1 = pd.read_excel("./persistentLayer/importJobs/vhkRfp.xlsx")
    index = 0
    print("### input")
    print(df1)
    print("####")

    df_unpivot = pd.melt(
        df1, id_vars=["RFP", "MC_Product"], var_name="YEAR_CURRENCY", value_name="COST"
    )
    df_unpivot["YEAR"] = [int("20" + x[2:4]) for x in df_unpivot["YEAR_CURRENCY"]]
    df_unpivot["CURRENY"] = [x[-1] for x in df_unpivot["YEAR_CURRENCY"]]
    dic = {"€": "EUR", "$": "USD"}
    df_unpivot = df_unpivot.replace({"CURRENY": dic})
    df_unpivot = df_unpivot.drop("YEAR_CURRENCY", axis=1)
    length = len(df_unpivot.index)
    """
    Go through each row to check if an entry exists already exists or if we need to create it.
    For that lookup in the currencies and product table, if the referenced object exists there.
    If we have more than one entry referenced, then we need to throw an error.
    """
    # set all to false before continuing. 
    VhkCy.objects.update(valid=False)

    for i in range(0, length, 1):

        rfpImport = df_unpivot.loc[i, "RFP"]
        currencyImport = df_unpivot.loc[i, "CURRENY"]
        #currencies = Currencies.objects.filter(currency=currencyImport)
        fxObject = Currency.objects.get(code=currencyImport, is_active=True)
        fx = float(fxObject.factor)

        products = Product.objects.filter(rfp=rfpImport)

        calendarYear = df_unpivot.loc[i, "YEAR"]
        cost = df_unpivot.loc[i, "COST"]


        if products.count() > 0:
            print("found more than 0 rps!")

            ## what with sales name daisy chain wafer?

            if (
                products.count() == 1
            ):  # currency count not chekced we assume that there will always be only 1 currency
                product = products[0]
                #currency = currencies[0]
                if pd.isna(cost):
                    cost = 0.0
                """
                vhkcyObj, created = VhkCy.objects.get_or_create(RFP = product, calendarYear = calendarYear, currency = currency, cost = cost)
                if created == True:
                    print(index, "created", vhkcyObj)
                else:
                    print(index, "retrieved", vhkcyObj)
                """
                #### new implementation, pivot table
                """
                vhkcyObjBis, created = VhkCy.objects.get_or_create(
                    RFP=product, currency=currency, valid=True
                )
                """

                vhkcyObjBis, created = VhkCy.objects.get_or_create(
                    RFP=product, currency=fxObject, valid=True
                )

                varName = "cy" + str(calendarYear)
                costValue = setattr(vhkcyObjBis, varName, cost)
                vhkcyObjBis.save()
                #if we have multiple entries for same RFP we need to set forthe older one valid=0
                vhkcyObjects =  VhkCy.objects.filter(RFP = product, currency = fxObject, valid=True).order_by('date')
                if vhkcyObjects.count() > 1:
                    length = vhkcyObjects.count()
                    for i in range(0,length): #the last one is excluded here because it shoudl keep valid = 1
                        vhkcyObjects[i].valid = 0
                        vhkcyObjects[i].save()
                        
            else:
                # tbd
                print(
                    "no too mny products for the VHK / RFP is duplicated / triplicated!!!!!"
                )
                ## either warning, automated email and then manual import or call support

        else:
            print("rfp not found! skipping")

        # i = i + 1


    runDate = datetime.now(tz=timezone.utc)

    # bulk update BoUp table with new VHKs
    bulkUpdaterBoUpTable(vhkUpdate = True, runDate = runDate, mode= 0, projectDtoArray=None)

    # generate a snapshot and store accordingly
    from snapshots.snapshotCreator import snapshotCreator

    runDateB = datetime.datetime.today().strftime('%Y-%m-%d')

    snapshotName = "Snapshot_VHK_Import_" + str(runDateB)
    snapshotComments = "Snapshot created on VHK import."
    snapshotCreator(request, snapshotName, snapshotComments, None)

    # bulk update project errors
    bulkErrorUpdateEntrypoint(request)
    return True
