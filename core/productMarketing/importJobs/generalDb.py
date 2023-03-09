# tier 1, oems
# missing

import pandas as pd
from .mainCustomer import *
from .vhkl import *
from .salesNames import *
from ..models import *
from .distributorsImport import *
from .emsImport import *
from .tierOneImport import *
from .productImport import adolfRun
from .vpaCustomerImport import *
from datetime import datetime
from django.utils import timezone
from core.project.models import ProjectStatus, LegalEntities, DistributionChannels, Distributors, Regions, SecondRegion
from .applicationsImportNew import runApplicationsImport
import hashlib
import random
from core.project.models import PriceStatus

# oems


def runOemImport():
    df1 = pd.read_csv(
        "./persistentLayer/importJobs/oemList.csv", sep=";", decimal=",")
    length = len(df1.index)
    index = 0
    print("### input")
    print(df1)
    print("####")
    for i in range(0, length, 1):

        oemInput = df1.loc[i, "oemName"]
        oem = OEM.objects.filter(oemName=oemInput)

        print("inputs", oemInput, "products", oem)
        if oem.count() > 0:
            print("found more than 0 rps!")

            # what with sales name daisy chain wafer?

            if oem.count() == 1:

                oemObj, created = OEM.objects.get_or_create(oemName=oemInput)
                if created == True:
                    print(index, "created", oemObj)
                else:
                    print(index, "retrieved", oemObj)

            else:
                # tbd
                print("found more than one matching customer!!!")
                # either warning, automated email and then manual import or call support

        else:
            print("oem did not exist! creating")
            oemObj, created = OEM.objects.get_or_create(oemName=oemInput)
            if created == True:
                print(index, "created", oemObj)
            else:
                print(index, "retrieved", oemObj)

    return True


# application main and app detail
def runAppMainImport():

    ApplicationMain.objects.all().delete()
    df1 = pd.read_csv(
        "./persistentLayer/importJobs/applicationMain.csv", sep=";", decimal=","
    )
    length = len(df1.index)
    index = 0
    print("### AppMain input")
    print(df1)
    print("####")

    for i in range(0, length, 1):
        appMainInput = df1.loc[i, "appMainDescription"]
        appMain = ApplicationMain.objects.filter(
            appMainDescription=appMainInput)

        print("---> App Main inputs", appMainInput, "products", appMain)
        if appMain.count() > 0:
            print("found more than 0 appMains!")

            # what with sales name daisy chain wafer?

            if appMain.count() == 1:

                appMainObj, created = ApplicationMain.objects.get_or_create(
                    appMainDescription=appMainInput
                )
                if created == True:
                    print(index, "created", appMainObj)
                else:
                    print(index, "retrieved, doing nothing", appMainObj)

            else:
                # tbd
                print("found more than one matching app main!!!")
                # either warning, automated email and then manual import or call support

        else:
            print("app main did not exist! creating", appMainInput)
            appMainObj, created = ApplicationMain.objects.get_or_create(
                appMainDescription=appMainInput
            )
            print("got ->", appMainObj)
            if created == True:
                print(index, "created", appMainObj)
            else:
                print(index, "retrieved", appMainObj)

    return True


# application main and app detail
def runAppDetailImport():
    df1 = pd.read_csv(
        "./persistentLayer/importJobs/applicationDetail.csv", sep=";", decimal=","
    )
    length = len(df1.index)
    index = 0
    print("!!!!!!!!!!!!!!!!!!!!!!!11")
    print("all OEMs!", OEM.objects.all())
    print("all app mains", ApplicationMain.objects.all())
    print("!!!!!!!!!!!!!!!!!!!!!!!11")
    appMains = ApplicationMain.objects.all()

    firstPk = appMains[0].pk
    for appMainObj in appMains:
        print("----> app main", appMainObj.pk)

    print("### AppDetail input")
    print(df1)
    print("####")

    for i in range(0, length, 1):
        appDetailInput = df1.loc[i, "appDetailDescription"]
        appDetail = ApplicationDetail.objects.filter(
            appDetailDescription=appDetailInput
        )
        # watchout, DB beings counting at 1!!!
        appDetailFk = int(df1.loc[i, "appMain"]) + 1

        print(
            "-----> inputs AppDetail",
            appDetailInput,
            "app detail",
            appDetail,
            "app detail fk (app main):",
            appDetailFk,
        )
        if appDetail.count() > 0:
            print("found more than 0 app details!")

            if appDetail.count() == 1:
                appMainObj = ApplicationMain.objects.get(pk=appDetailFk)

                appDetailObj, created = ApplicationDetail.objects.get_or_create(
                    appDetailDescription=appDetailInput, appMain=appMainObj
                )
                if created == True:
                    print(index, "created", appDetailObj)
                else:
                    print(index, "retrieved", appDetailObj)

            else:
                # tbd
                print("found more than one matching app detail!!!")
                # either warning, automated email and then manual import or call support

        else:
            appMainId = df1.loc[i, "appMain"] + firstPk
            print(
                "######### appDetail did not exist! creating, testing",
                appDetailFk,
                "app main id",
                appMainId,
            )

            appMainObj = ApplicationMain.objects.get(id=appMainId)
            appDetailObj, created = ApplicationDetail.objects.get_or_create(
                appDetailDescription=appDetailInput, appMain=appMainObj
            )
            if created == True:
                print(index, "created", appDetailObj)
            else:
                print(index, "retrieved", appDetailObj)

    return True


# fx rates
def runFxRatesImport():
    df1 = pd.read_csv(
        "./persistentLayer/importJobs/currencies.csv", sep=";", decimal=","
    )
    length = len(df1.index)
    index = 0
    print("### input fx rates")
    print(df1)
    print("####")

# currencies


def runCurrenciesImport():
    df1 = pd.read_csv(
        "./persistentLayer/importJobs/currencies.csv", sep=";", decimal=","
    )
    length = len(df1.index)
    index = 0
    print("### input currencies")
    print(df1)
    print("####")
    for i in range(0, length, 1):

        currencyInput = df1.loc[i, "currency"]
        currency = Currencies.objects.filter(currency=currencyInput)

        if currency.count() > 0:
            print("found more than 0 currency!")

            # what with sales name daisy chain wafer?

            if currency.count() == 1:

                currencyObj, created = Currencies.objects.get_or_create(
                    currency=currencyInput
                )
                if created == True:
                    print(index, "created", currencyObj)
                else:
                    print(index, "retrieved", currencyObj)

            else:
                # tbd
                print("found more than one currency!!!")
                # either warning, automated email and then manual import or call support

        else:
            print("currency did not exist! creating currency")
            currencyObj, created = Currencies.objects.get_or_create(
                currency=currencyInput
            )
            if created == True:
                print(index, "created", currencyObj)
            else:
                print(index, "retrieved", currencyObj)


def runFxImport():

    # now the exchange rates
    # exchange rates are understood as the excahnge rate from source into EUR

    df2 = pd.read_csv(
        "./persistentLayer/importJobs/fxRates.csv", sep=";", decimal=","
    )
    length2 = len(df2.index)
    index = 0
    print("### input exchange rates")
    print(df2)
    print("####")

    # set all the previous to not valid
    # set all previous where validTo empty is to now

    timeStamp = datetime.now(tz=timezone.utc)
    currentRates = ExchangeRates.objects.filter(valid=True)
    currentRates.update(validTo=timeStamp)
    ExchangeRates.objects.update(valid=False)

    # assumes consistency of currencies file with fx files
    for i in range(0, length2, 1):
        currencyInput = df2.loc[i, "currency"]
        rate = df2.loc[i, "rate"]
        currency = Currencies.objects.get(currency=currencyInput)
        exchangeRate, created = ExchangeRates.objects.get_or_create(
            currency=currency, valid=True)
        exchangeRate.validFrom = timeStamp
        exchangeRate.rate = rate
        exchangeRate.save()

    return True


# insert test marketer


def runTestMarketer():
    legalEntity, created1 = LegalEntities.objects.get_or_create(
        leShortName="IFAG", leLongName="Infineon Technologies AG"
    )

    print("legal entity", legalEntity)
    marketerObj, created = marketerMetadata.objects.get_or_create(
        name="Test",
        familyName="Marketer",
        country="Germany",
        legalEntity=legalEntity,
    )
    # userRole = models.CharField(max_length=15, choices=ALLOWABLE_TYPES_USER_ROLE, blank=True, null=True)


#    businessLine = models.CharField(max_length=15, choices=ALLOWABLE_TYPES_BL, blank=True, null=True, default = "ATV.PSE")

def ProjectStatusImport():

    ALLOWABLE_TYPES_PROJECT_STATUS = (
        ("100", "BW (100%)"),
        ("90", "DW (90%)"),
        ("60", "DI (60%)"),
        ("40", "DI (40%)"),
        ("0", "LO (0%)"),
    )

    """
        ALLOWABLE_TYPES_PROJECT_STATUS = (
        ("100", "BW (100%)"),
        ("90", "DW (90%)"),
        ("60", "DI (60%)"),
        ("40", "DI (40%)"),
        ("10", "OP (10%)"),
        ("0", "LO (0%)"),
    )
    """

    """
    ALLOWABLE_TYPES_PROJECT_STATUS = (

        # direct business
        ("75", "Approved by Approver 1 (75%)"),
        ("100", "Business Loss (100%)"),
        ("100", "Business Win (100%)"),
        ("100", "Business Win Manual (100%)"),
        ("100", "Business Win POS (100%)"),
        ("40", "DesignIN (40%)"),
        ("67", "DesignIN (67%)"),
        ("0", "Design Loss (0%)"),
        ("100", "Design WIN (100%)"),
        ("100", "Validate Business WIN (100%)"),
        ("90", "Design WIN Claim (90%)"),
        ("30", "Design Accepted (30%)"),
        ("30", "DI - In Progress (30%)"),
        ("0", "Disc. at Identification (0%)"),
        ("0", "Disc. at Qualification (0%)"),
        ("0", "Disc. before Design In (0%)"),
        ("13", "Identified (13%)"),
        ("0", "Unknown - Orphan"),

        # distribution business
        ("50", "Dist: Approved by Approver 1 (50%)"),
        ("0", "Dist: Business Loss (0%)"),
        ("100", "Dist: Business Win (100%)"),
        ("100", "Dist: Business Win Manual (100%)"),
        ("100", "Dist: Business Win POS (100%)"),
        ("30", "Dist: DesignIN (30%)"),
        ("50", "Dist: DesignIN (50%)"),
        ("0", "Dist: Design Loss (0%)"),
        ("75", "Dist: Design WIN (75%)"),
        ("90", "Dist: Validate Business WIN (90%)"),
        ("50", "Dist: Design WIN Claim (50%)"),
        ("30", "Dist: Design Accepted (30%)"),
        ("30", "Dist: DI - In Progress (30%)"),
        ("0", "Dist: Disc. at Identification (0%)"),
        ("0", "Dist: Disc. at Qualification (0%)"),
        ("0", "Dist: Disc. before Design In (0%)"),
        ("10", "Dist: Identified (10%)"),
    )
    """

    for key, item in ALLOWABLE_TYPES_PROJECT_STATUS:
        status, created = ProjectStatus.objects.get_or_create(
            status=key, statusDisplay=item)

    return


def otherFields():
    """
    ALLOWABLE_TYPES_PROJECT_STATUS = (
        ("100", "BW (100%)"),
        ("90", "DW (90%)"),
        ("60", "DI (60%)"),
        ("40", "DI (40%)"),
        ("10", "OP (10%)"),
        ("0", "LO (0%)"),
    )
    """

    ALLOWABLE_TYPES_REGION = (
        ("EMEA", "EMEA"),
        ("AMERICAS", "AMERICAS"),
        ("AP", "AP"),
        ("JAPAN", "JAPAN"),
        ("GC", "GC"),
        ("MISC", "MISC"),
    )

    for key, item in ALLOWABLE_TYPES_REGION:
        status, created = Regions.objects.get_or_create(region=key)
        status2, created2 = SecondRegion.objects.get_or_create(
            secondRegion=key)

    ALLOWABLE_TYPES_DCCHANNEL = (
        ("direct", "Direct"),
        ("distribution", "Distribution"),
    )

    for key, item in ALLOWABLE_TYPES_DCCHANNEL:
        status, created = DistributionChannels.objects.get_or_create(
            dcChannel=key, dcChannelDescription=item)

    ALLOWABLE_TYPES_PRICE_STATUS = (
        ("estim", "Estimation"),
        ("quote", "Quotation"),
        ("contr", "Contract"),
    )

    for key, item in ALLOWABLE_TYPES_PRICE_STATUS:
        status, created = PriceStatus.objects.get_or_create(
            priceType=key, priceTypeDisplay=item)

    print("finished with other imports")
    return

# check general import


def runConfigImport(request):
    df1 = pd.read_csv(
        "./persistentLayer/importJobs/config.csv", sep=";", decimal=",")
    length = len(df1.index)
    index = 0
    print("###### config file")
    print(df1)
    print("####")
    for i in range(0, length, 1):
        configInput = df1.loc[i, "configName"]
        valueInput = df1.loc[i, "value"]
        print("inputs", configInput)

        if configInput == "firstImport":
            # so if this is the first import, run the full import
            """
            Due to changes in customer wishes, the ems, tier ones, vpa, main and final customers tables have to be identical. they share the same information. 
            """
            if str(valueInput) == "0":
                """
                to be run manually on first import, eventually

                run python manage.py shell
                then in the terminal write following code
                from productMarketing.models import ProjectVolumeMonth

                objs = ProjectVolumeMonth.objects.all()
                for obj in objs:
                    obj.save()

                ##### update on Feb 2023: do not run currencies import. create them manually in admin panel instead!

                """
                runApplicationsImport() # done test env
                otherFields()  # done test env
                adolfRun(fileUpload=False, uploadPath=None) # done test env
                runTestMarketer()  # done test env

                """
                runDistributorsImport()
                runEmsImport()
                runTierOneImport()
                runVpaCustomerImport()
                runOemImport()

                # no longer required starting 22 feb 2023:
                # runCurrenciesImport()  # done test env
                # runFxImport()  # done test env

                """
                # runvhklImport(request)
                # ProjectStatusImport()
                print("adolf run finished")
                return
