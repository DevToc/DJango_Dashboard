import os
from enum import Enum
from typing import Any, Iterable, MutableSequence, TypeVar
import datetime
from .models import *
import pandas as pd
import pandasql as ps
from productMarketingDwh.models import BoUp, VhkCy, CurrenciesArchive, ExchangeRatesArchive
from .bottomUpPersistor import bottomUpPersistor
from productMarketing.interpolator import linSmoother
from core.project.models import Project
from productMarketing.models import ProjectVolumePricesLog, ProjectVolumeMonth, ProjectVolumePrices
from django.utils import timezone
from core.project.helperFunctions import getProjectOverview
import hashlib
import random

from currencies.models import Currency

def isBlank(myString):
    if myString and myString.strip():
        # myString is not None AND myString is not empty or blank
        return False
    # myString is None OR myString is empty or blank
    return True


def testProjecTiming(sop, dummy):
    today = datetime.date.today()
    year = today.year
    pastError = False
    dummyTimingError = False

    if (year - sop) > 2:
        pastError = True

    if (abs(sop - year) <= 2) & (dummy == True):
        dummyTimingError = True

    return pastError, dummyTimingError


# operand: abstraction for volumes or prices
class errorTypesProjectEntryValidation(Enum):
    salesNameDoesNotExist = 0
    mainCustomerDoesNotExist = 1
    finalCustomerDoesNotExist = 2
    vpaCustomerDoesNotExist = 3
    distributorDoesNotExist = 4
    emsDoesNotExist = 5
    tierOneDoesNotExist = 6
    oemDoesNotExist = 7
    projectCreationConflict = 8
    marketerDoesNotExist = 9
    priceStatusIncorrect = 10
    distributionTypeIncorrect = 11
    regionIncorrect = 12
    projectDoesNotExist = 13
    rfpDoesNotExist = 14
    customersNotMatching = 15
    mainApplicationDoesNotExist = 16
    detailApplicationDoesNotExist = 17
    projectCreationConflictFileLevel = 18
    willNotCreateProject = 19
    projectWasDeleted = 20
    projectWasManipulated = 21
    applicationLineDoesNotExist = 22
    regionDidNotExist = 23
    statusDidNotExist = 24

    def __str__(self):
        # python < v3.10 does not support switch statements...

        if self.value == 0:
            return "Sales name does not exist or is empty."
        elif self.value == 1:
            return "Main Customer does not exist or is empty."
        elif self.value == 2:
            return "End Customer does not exist or is empty."
        elif self.value == 3:
            return "VPA Customer does not exist."
        elif self.value == 4:
            return "Distributor does not exist."
        elif self.value == 5:
            return "EMS does not exist."
        elif self.value == 6:
            return "Tier One does not exist."
        elif self.value == 7:
            return "OEM does not exist."
        elif self.value == 8:
            return "Project Creation Conflict. There is already a project in the data base with the same combination of sales name, main customer, end customer, main application and application detail."
        elif self.value == 9:
            return "Product marketer does not Exist"
        elif self.value == 10:
            return "The price status does not match Infineon's guidelines."
        elif self.value == 11:
            return "The entered distribution type is not allowed."
        elif self.value == 12:
            return "The entered region is not allowed."
        elif self.value == 13:
            return "Project does not exist."
        elif self.value == 14:
            return "RFP does not exist."
        elif self.value == 15:
            return "End customer does not match main customer."
        elif self.value == 16:
            return "Main application does not exist or is empty."
        elif self.value == 17:
            return "Application detail does not exist or is empty."
        elif self.value == 18:
            return "Project uniqueness conflict. In this file there is already a project row with the same combination of sales name, main customer, end customer, main application and application detail."
        elif self.value == 19:
            return "Solve conflicts - otherwise will not create project."
        elif self.value == 20:
            return "Project was deleted and does no longer exist in the database."
        elif self.value == 21:
            return "Project was manipulated in the database or in Excel in a way, that it no longer matches the original functional key (combination of main customer, end customer, application main, application detail and product sales name). A reimport is no longer possible."
        elif self.value == 22:
            return "Application Line does not exist."
        elif self.value == 23:
            return "Region did not exist."
        elif self.value == 24:
            return "Status did not exist."


"""
needs:

params = {"name": projectName, "productMarketerFirstName": productMarketerFirstName, "productMarketerLastName": productMarketerLastName,
"applicationMain": appMainDescription, "applicationDetail": appDetailDescription, "mainCustomer": customerName, "finalCustomer": finalCustomerName,
"sales_name": name, "distributor": distributorName, "ems": emsName, "tier1": tierOneName, "oem": oemName, "vpaCustomer": customerName, "salesContact": name, "familyPriceApplicable": familyPriceApplicable,
"familyPriceDetails": familyPriceDetails, "estimatedSop": estimatedSop, "status": status, "region": region, "secondRegion": secondRegion,
"draft": draft, "dummy": dummy, "priceValidUntil": priceValidUntil}
}

Optional params (used elsewhere): volumes, prices

Used to validate each DTO (params dictionary) against the helperQuerysets (the only available values)
Keep in mind: Mode 2 (Elke File) does not have sales names, so we will fetch the first match

"""

def projectCreatorValidator(params: dict, helperQuerySets: dict, mode: int, creationDesired: bool) -> tuple[int, MutableSequence[errorTypesProjectEntryValidation], MutableSequence[int]]:

    errorList: MutableSequence[errorTypesProjectEntryValidation] = []
    projectNameInput = None

    if mode == 2:
        projectNameInput = params["projectName"]

    # projectName = params["name"]
    productMarketerFirstName = params["productMarketerFirstName"]
    productMarketerLastName = params["productMarketerLastName"]
    appMain = params["applicationMain"]
    appDetail = params["applicationDetail"]
    appLine = params["applicationLine"]
    customerName = params["mainCustomer"]
    finalCustomerName = params["finalCustomer"]
    salesName = params["sales_name"]
    dummy = params["dummy"]
    projectId = params["projectId"]
    rfpInput = params["rfp"]
    projectName = params["name"]
    projectDescription = params["projectDescription"]
    spNumber = params["spNumber"]
    comment = params["comment"]
    distributorName = params["distributor"]
    emsName = params["ems"]
    tierOneName = params["tier1"]
    oemName = params["oem"]
    vpacustomerName = params["vpaCustomer"]
    salesContactName = params["salesContact"]  # name related
    familyPriceApplicable = params["familyPriceApplicable"]
    familyPriceDetails = params["familyPriceDetails"]
    estimatedSop = params["estimatedSop"]
    status = params["status"]
    region = params["region"]
    secondRegion = params["secondRegion"]
    draft = params["draft"]
    priceValidUntil = params["priceValidUntil"]
    #dcChannel = params["dcChannel"]
    conflictingProjects = []

    ###
    allowableproductMarketers = helperQuerySets["productMarketers"]
#    allowableproductMarketerFirstName = helperQuerySets["productMarketerFirstName"]
#    allowableproductMarketerLastName = helperQuerySets["productMarketerLastName"]
    allowableappMainDescription = helperQuerySets["applicationMain"]
    allowableappDetailDescription = helperQuerySets["applicationDetail"]
    allowablecustomerName = helperQuerySets["mainCustomer"]
    allowablefinalCustomerName = helperQuerySets["finalCustomer"]
    allowableSalesNames = helperQuerySets["sales_name"]
    allowableProducts = helperQuerySets["products"] 
    allowabledistributorName = helperQuerySets["distributor"]
    allowableemsName = helperQuerySets["ems"]
    allowabletierOneName = helperQuerySets["tier1"]
    allowableoemName = helperQuerySets["oem"]
    allowablevpacustomerName = helperQuerySets["vpaCustomer"]
    allowablesalesContactName = helperQuerySets["salesContact"]  # name related
    allowablestatus = helperQuerySets["status"]
    allowableregion = helperQuerySets["region"]
    allowablesecondRegion = helperQuerySets["secondRegion"]
    allowableProjects = helperQuerySets["projects"]
    allowableRfps = helperQuerySets["products"]
    allowableApplicationLine = helperQuerySets["applicationLine"]

    productFatalError = False
    appMainError = False
    appDetailError = False
    mainCustomerError = False
    finalCustomerError = False
    salesNameError = False
    appLineError = False

    """

    Initialize IDs.
    For mode 0:
    These values require look up from database in order to find the reference objects, which are mandatory.
    If the matching values are not found in the DB, the user should know about this. The user should be able to see the excel reference value,
    and to select a correct value from a dropdown.

    """
    salesNameId = 0
    finalCustomerId = 0
    mainCustomerId = 0
    applicationMainId = 0
    applicationDetailId = 0
    distributorId = 0
    vpaCustomerId = 0
    emsId = 0
    tierOneId = 0
    oemId = 0
    # product marketer id is set to 1 as to default to the default marketer (not null constraint)
    productMarketerId = 1
    statusId = 0
    regionId = 0
    secondRegionId = 0
    dcChannelId = 0
    priceTypeId = 0
    salesContactId = 0
    outputProjectId = 0
    applicationLineId = 0

    attributeIds = {
        "salesNameId": 0,
        "finalCustomerId": 0,
        "mainCustomerId": 0,
        "applicationMainId": 0,
        "applicationDetailId": 0,
        "distributorId": 0,
        "vpaCustomerId": 0,
        "emsId": 0,
        "tierOneId": 0,
        "oemId": 0,
        "productMarketerId": 1,
        "statusId": 0,
        "regionId": 0,
        "secondRegionId": 0,
        "dcChannelId": 0,
        "priceTypeId": 0,
        "salesContactId": 0,
        "outputProjectId": 0,
        "applicationLineId": 0,
        "userId": 1, 
        "salesNameDefaulted": False
    }

    # elke file... first matching sales name for rfp
    if mode == 2:
        rfpObj = allowableProducts.get(rfp=rfpInput)
        try:
            salesNameId = allowableSalesNames.filter(
                rfp=rfpObj).first()
            attributeIds["salesNameId"] = salesNameId.id
            attributeIds["salesNameDefaulted"] = True

        except:
            salesNameError = True
            errorList.append(
                errorTypesProjectEntryValidation.salesNameDoesNotExist)

    else:
        try:
            salesNameId = allowableSalesNames.filter(
                name=salesName).first()
        except:
            salesNameError = True
            errorList.append(
                errorTypesProjectEntryValidation.salesNameDoesNotExist)

    try:
        finalCustomerId = allowablefinalCustomerName.filter(
            finalCustomerName__iexact=finalCustomerName).first()
        attributeIds["finalCustomerId"] = finalCustomerId.id

    except:
        finalCustomerError = True
        errorList.append(
            errorTypesProjectEntryValidation.finalCustomerDoesNotExist)

    print("main customer testing", customerName, "Type", type(customerName))
    try:
        mainCustomerId = allowablecustomerName.filter(
            customerName__iexact=customerName).first()
        attributeIds["mainCustomerId"] = mainCustomerId.id
    except:
        mainCustomerError = True
        errorList.append(
            errorTypesProjectEntryValidation.mainCustomerDoesNotExist)
        
    try:
        applicationLineId = allowableApplicationLine.filter(
            applicationLineShortName__iexact=appLine).first()
        attributeIds["applicationLineId"] = applicationLineId.id

    except:
        appLineError = True
        errorList.append(
            errorTypesProjectEntryValidation.applicationLineDoesNotExist)

    try:
        applicationMainId = allowableappMainDescription.get(
            appMainDescription__iexact=appMain, appLine_id=  applicationLineId)
        attributeIds["applicationMainId"] = applicationMainId.id

    except:
        appMainError = True
        errorList.append(
            errorTypesProjectEntryValidation.mainApplicationDoesNotExist)

    try:
        applicationDetailId = allowableappDetailDescription.get(
            appDetailDescription__iexact=appDetail, appMain_id=applicationMainId)
        attributeIds["applicationDetailId"] = applicationDetailId.id

    except:
        appDetailError = True
        errorList.append(
            errorTypesProjectEntryValidation.detailApplicationDoesNotExist)

    """
    now repeat with tier one, distributor, oem, vpa customers
    only run if not blank, not space, since they are optional values.

    """
    if distributorName:
        try:
            distributorId = allowabledistributorName.get(
                distributorName__iexact=distributorName)
            attributeIds["distributorId"] = distributorId.id

        except:
            errorList.append(
                errorTypesProjectEntryValidation.distributorDoesNotExist)

    if emsName:
        try:
            emsId = allowableemsName.get(
                emsName__iexact=emsName)
            attributeIds["emsId"] = emsId.id

        except:
            errorList.append(
                errorTypesProjectEntryValidation.emsDoesNotExist)

    if tierOneName:
        try:
            tierOneId = allowabletierOneName.get(
                tierOneName__iexact=tierOneName)
            attributeIds["tierOneId"] = tierOneId.id

        except:
            errorList.append(
                errorTypesProjectEntryValidation.tierOneDoesNotExist)

    if oemName:
        try:
            oemId = allowableoemName.get(
                oemName__iexact=oemName)
            attributeIds["oemId"] = oemId.id

        except:
            errorList.append(
                errorTypesProjectEntryValidation.oemDoesNotExist)

    if vpacustomerName:
        try:
            vpaCustomerId = allowablevpacustomerName.get(
                customerName__iexact=vpacustomerName)
            attributeIds["vpaCustomerId"] = vpaCustomerId.id

        except:
            errorList.append(
                errorTypesProjectEntryValidation.vpaCustomerDoesNotExist)

    """
    now with the remaining fields
    """
    if mode == 2:
        if status:
                status = int(status) * 100
                try:
                    statusObj = allowablestatus.filter(
                        status__iexact=status).first()
                    attributeIds["statusId"] = statusObj.id
                except:
                    errorList.append(
                        errorTypesProjectEntryValidation.statusDidNotExist)

        if region:
                try:
                    regionObj = allowableregion.get(
                        region__iexact=region)
                    attributeIds["regionId"] = regionObj.id

                except:
                    errorList.append(
                        errorTypesProjectEntryValidation.regionDidNotExist)

    """
    uniqueness check: salesname, main customer, end customer, main application, application detail for mode 0 (migration)
    in mode 1 (excel flow), just check that the ID was not manipulated (Although the field is frozen in excel)
    in mode 2 (Elke File), use unique key combination
    """

    if (mode == 0) | (mode == 2):

        """
        if no salesName was entered (empty string), try to fetch a matching rfp and map the first matching sales name.
        if this fails, then the routine can be stopped.
        problem with SalesName or RFPs: the import / export process with Excel makes leading zeros disappear (e.g. 00000)
        """
        if not salesName:
            rfpObjects = allowableRfps.filter(rfp=rfpInput)
            #print("rfp objects", rfpObjects, rfpObjects.count())
            if rfpObjects.count() != 1:
                rfpObjects = allowableRfps.filter(rfp__endswith=rfpInput)

            if rfpObjects.count() != 1:
                errorList.append(
                    errorTypesProjectEntryValidation.rfpDoesNotExist)
                productFatalError == True

            # now get the sales name that match this rfp
            if productFatalError != True:

                salesNameObjects = allowableSalesNames.filter(rfp=rfpObjects.first())

                if salesNameObjects.count() > 0:
                    salesNameId = salesNameObjects.first().pk
                else:
                    productFatalError = True
                    errorList.append(
                        errorTypesProjectEntryValidation.rfpDoesNotExist)

        else:
            salesNameObjects = allowableSalesNames.filter(
                name__endswith=salesName)

            if salesNameObjects.count() == 0:
                #print("sales name did not exist!")
                errorList.append(
                    errorTypesProjectEntryValidation.salesNameDoesNotExist)
                productFatalError = True
            else:
                #print("sales names", salesNameObjects)
                salesNameId = salesNameObjects.first().pk

        """
        check that the end customer matches the main customer
        """


        """
        if no errors found, proceed to test uniqueness of project.
        if the project already exists, raise a warning.
        This will test against the existing DB. The test within the import file is done at a level above.
        """

        if mode == 0:

            if (productFatalError == False) & (appMainError == False) & (appDetailError == False) & (mainCustomerError == False) & (finalCustomerError == False):
                #print("testing uniqueness on migration mode", mainCustomerId, finalCustomerId, applicationMainId, applicationDetailId, salesNameId)
                #print("mainCustomerId", mainCustomerId, "finalCustomerId", finalCustomerId, "applicationMainId", applicationMainId, "applicationDetailId", applicationDetailId, "salesNameId", salesNameId)
                countProjects = allowableProjects.filter(mainCustomer=mainCustomerId, finalCustomer=finalCustomerId,
                                                        applicationMain=applicationMainId, applicationDetail=applicationDetailId, sales_name=salesNameId)
                if countProjects.count() > 0:
                    errorList.append(
                        errorTypesProjectEntryValidation.projectCreationConflict)
                    conflictingProjects.append(countProjects.values_list(
                        "id", flat=True
                    ))

            else:
                errorList.append(
                    errorTypesProjectEntryValidation.willNotCreateProject)

        else:
            """
            mode 2 Elke
            we will create here a synthetic project name to test uniqueness....
            """
            print("%%%%%%% checking creation conflict")
            if (productFatalError == False) & (appMainError == False) & (appDetailError == False) & (mainCustomerError == False) & (finalCustomerError == False):
                #print("testing uniqueness on migration mode", mainCustomerId, finalCustomerId, applicationMainId, applicationDetailId, salesNameId)
                #print("mainCustomerId", mainCustomerId, "finalCustomerId", finalCustomerId, "applicationMainId", applicationMainId, "applicationDetailId", applicationDetailId, "salesNameId", salesNameId)
                countProjects = allowableProjects.filter(mainCustomer=mainCustomerId, finalCustomer=finalCustomerId,
                                                        applicationMain=applicationMainId, applicationDetail=applicationDetailId, sales_name=salesNameId, syntheticProjectName=projectNameInput, dummy=dummy, draft=False, productMarketer_id=productMarketerId)
                
                print("inputs:", mainCustomerId, finalCustomerId, "apps", applicationMainId, applicationDetailId,"sn", salesNameId, "dummy", dummy, "pmid", productMarketerId, projectNameInput)
                print("output", countProjects, "count", countProjects.count())
                # this will avoid a bulk creation later down the road
                if countProjects.count() > 0:
                    errorList.append(
                        errorTypesProjectEntryValidation.projectCreationConflict)
                    print("project creation conflict!")

                    conflictingProjects.append(countProjects.values_list(
                        "id", flat=True
                    ))
             
            else:
                errorList.append(
                    errorTypesProjectEntryValidation.willNotCreateProject)

        """
        now check the general inputs: marketer name, comments length, tier 1, oem, region, price source, family price
        """

        # product marketer check
        countProductMarketers = allowableproductMarketers.filter(
            name=productMarketerFirstName, familyName=productMarketerLastName)

        if countProductMarketers.count() == 0:
            errorList.append(
                errorTypesProjectEntryValidation.marketerDoesNotExist)
            #print("marketer does not exist", countProductMarketers)
        else:
            attributeIds["productMarketerId"] = countProductMarketers.first().pk
            productMarketerId = countProductMarketers.first().pk

            # try to set the user
            try:
                userId = countProductMarketers.first().user.id
                attributeIds["productMarketerId"] = userId
            except:
                pass

    else:
        countProjects = allowableProjects.filter(id=projectId)
        if countProjects.count() == 0:
            errorList.append(
                errorTypesProjectEntryValidation.projectDoesNotExist)
            #print("project does not exist! error!")
        else:
            """
            check that project was not manipulated and functional key matches the export. and that no additional rows were added. 
            check that the imported functional key matches the exported one
            """
            exportedProject = None
            exportedProject = allowableProjects.get(id=projectId)

            try:
                exportedProject = allowableProjects.get(id=projectId)
            except:
                errorList.append(
                errorTypesProjectEntryValidation.projectWasDeleted)

            if exportedProject == None:
                errorList.append(
                errorTypesProjectEntryValidation.projectWasDeleted)
            else:
                exportedMainCustomer = exportedProject.mainCustomer.customerName
                exportedFinalCustomer = exportedProject.finalCustomer.finalCustomerName
                exportedApplicationMain = exportedProject.applicationMain.appMainDescription
                exportedApplicationDetail = exportedProject.applicationDetail.appDetailDescription
                exportedSalesName = exportedProject.sales_name.name

                if (str(exportedMainCustomer) != str(mainCustomerId)) or (str(exportedFinalCustomer) != str(finalCustomerId)) or (str(exportedApplicationDetail) != str(applicationDetailId)) or (str(applicationMainId) != str(exportedApplicationMain)) or (str(exportedSalesName) != str(salesNameId)):
                    errorList.append(
                    errorTypesProjectEntryValidation.projectWasManipulated)

    #print("%%%%%%%% all validation errors", errorList)

    """
    mode 0 / migration: create project
    mode 1 / excel workflow: update project
    """

    if (mode == 0) & (creationDesired == True):
        if errorTypesProjectEntryValidation.projectCreationConflict not in errorList:
            projectObj = Project.objects.get_or_create(mainCustomer=mainCustomerId, finalCustomer=finalCustomerId,
                                                       applicationMain=applicationMainId, applicationDetail=applicationDetailId, sales_name=salesNameId)

            outputProjectId = projectObj.pk
            # now update all fields
            projectObj.productMarketer = productMarketerId if productMarketerId != 0 else projectObj.productMarketer

            # for PSE, this is the field "filler" for Market Model filler.
            projectObj.dummy = dummy
            projectObj.salesContact = salesContactId if salesContactId != 0 else projectObj.salesContact
            projectObj.vpaCustomer = vpaCustomerId if vpaCustomerId != 0 else projectObj.vpaCustomer
            projectObj.oem = oemId if oemId != 0 else projectObj.oem
            projectObj.tier1 = tierOneId if tierOneId != 0 else projectObj.tier1
            projectObj.ems = emsId if emsId != 0 else projectObj.ems
            projectObj.distributor = distributorId if distributorId != 0 else projectObj.distributor
            projectObj.priceType = priceTypeId if priceTypeId != 0 else projectObj.priceType
            projectObj.otherPriceComments = params["otherPriceComments"]
            projectObj.draft = False
            projectObj.projectDescription = projectDescription
            projectObj.projectName = projectName
            projectObj.comment = comment
            projectObj.dcChannel = dcChannelId if dcChannelId != 0 else projectObj.dcChannel
            projectObj.region = regionId if regionId != 0 else projectObj.region
            projectObj.secondRegion = secondRegionId if secondRegionId != 0 else projectObj.secondRegion
            projectObj.status = statusId if statusId != 0 else projectObj.status
            projectObj.familyPriceDetails = params["familyPriceDetails"]
            # projectObj.familyPriceApplicable =
            projectObj.estimatedSop = params["estimatedSop"]
            projectObj.spNumber = spNumber
            projectObj.productMarketer = productMarketerId if productMarketerId != 0 else projectObj.productMarketer
            projectObj.save()

    else:
        if errorTypesProjectEntryValidation.projectDoesNotExist not in errorList:
            # print("%%%%%%%%% updating values for project # ", projectId)
            outputProjectId = projectId

    return outputProjectId, errorList, conflictingProjects, attributeIds


"""
in order to create or modify a project in an automated manner.
this will validate all inputs and in case of conflicts return errors.
the non conflicting entries are returned for a bulk create process.
the conflicting entries are returned in an array.
Helper Querysets are objects with all valid applications, customers, sales names, etc... in order not to kill the DB / server with I/O operations. they are kept in memory and fetched only once during a batch job.
"""


def boUpCreatorValidator(params: dict, dummy: bool, helperQuerySets: dict, mode: int, creationDesired: bool) -> tuple[int, MutableSequence[errorTypesProjectEntryValidation], MutableSequence[int]]:

    outputProjectId, validationErrors, conflictingProjects, attributeIds = projectCreatorValidator(
        params=params, helperQuerySets=helperQuerySets, mode=mode, creationDesired=creationDesired)

    return outputProjectId, validationErrors, conflictingProjects, attributeIds


"""
main entry point for the bulk creation / update.
preassumption: the excel input was already checked for formalities (column naming, columns missing, characters, etc...)

mode:
0 = infineon bottom up (elke file) either for consistency check or for migration
1 = our application export
"""


def entryPointValidator(fileName: str, excelFilePath: str, mode: int, creationDesired: bool, helperQuerySets: Any):

    # freeze boUp, Tables, for all users.... tbd how to do this with a scheduler
    # prepare helper objects for one time DB I/O. otherwise the DB will be called too many times. this data is used to plausibilize user inputs in Excel and to match functional values.
    
    dtoArray = []
    
    if helperQuerySets == None: 
        helperQuerySets = {"productMarketers": marketerMetadata.objects.all()}
        helperQuerySets["applicationMain"] = ApplicationMain.objects.all()
        helperQuerySets["applicationDetail"] = ApplicationDetail.objects.all()
        helperQuerySets["mainCustomer"] = MainCustomers.objects.all()
        helperQuerySets["finalCustomer"] = FinalCustomers.objects.all()
        helperQuerySets["sales_name"] = SalesName.objects.all()
        helperQuerySets["distributor"] = Distributors.objects.all()
        helperQuerySets["ems"] = EMS.objects.all()
        helperQuerySets["tier1"] = Tier1.objects.all()
        helperQuerySets["oem"] = OEM.objects.all()
        helperQuerySets["vpaCustomer"] = VPACustomers.objects.all()
        helperQuerySets["products"] = Product.objects.all()

        # name related
        helperQuerySets["salesContact"] = SalesContacts.objects.all()
        helperQuerySets["status"] = ProjectStatus.objects.all()
        helperQuerySets["region"] = Regions.objects.all()
        helperQuerySets["secondRegion"] = SecondRegion.objects.all()
        helperQuerySets["projects"] = Project.objects.all()
        helperQuerySets["products"] = Product.objects.all()
        helperQuerySets["applicationLine"] = ApplicationLine.objects.all()

    productMarketers = helperQuerySets["productMarketers"]
    excelFilePath = "." + excelFilePath
    df = None
    print("filename", fileName, "ss", fileName[-3:])

    if fileName[-3:] == "csv":
        df = pd.read_csv(excelFilePath, encoding='ISO-8859-1', delimiter=";")
    else:
        df = pd.read_excel(excelFilePath)
    df = df.fillna('')
    projectErrorsArray = []

    """
    mode:
    0 = infineon bottom up (elke file) either for consistency check 
    1 = our application export
    2 = migration, Elke File, PL58
    3 = migration, PL90
    4 = migration 
    """

    if (mode == 0):

        """
        first of all, check no duplicated MC+EC+MA+AD+SN for uniqueness at application level (team level migration)
        for each row in the excel file, load the DTO (represented by a fixed dict).
        The DTO will be processed by boUpCreatorValidator.
        The expected input is the flat BoUp file as used in January 2023 by BPS team.
        """

        cols = ['Application Main', 'Application Detail',
                'MainCustomer', 'EndCustomer', 'Sales Name']
        df['indexBak'] = df.index
        df2 = df[df.duplicated(subset=cols, keep=False)]
        duplicatedRows = list(df2.index.values)
        #df2['DuplicateGroup'] = df2.groupby(duplicatedRows).ngroup()

        df2 = df2.sort_values(cols)
        df2['group'] = 'g' + (df2.groupby(cols).ngroup() + 1).astype(str)
        #df2['duplicate_count'] = df2.groupby(cols)['origin'].transform('size')

        # used to check uniqueness within the uploaded file itself

        print("duplicates %%%")
        print(duplicatedRows)
        print("%%%%%%%%%")
        print(df2)
        uniqueCombinations = []
        conflictingRowsFile = []

        df2.to_csv("./duplicates.csv", sep=";")

        df = df.rename(columns={"Application Main": "ApplicationMain",
                       "Application Detail": "ApplicationDetail", "Sales Name": "SalesName"})

        for index, row in df.iterrows():
            #print(index, "dummy?", row["Filler"], "main customer", row)

            # To Do: match the excel marketer name to a DB marketer name
            marketerFirstName = "unknown"  # marketerString.split("_")[0]
            marketerLastName = "unknown"  # marketerString.split("_")[1]

            # projectId = row["ID_APP_id"]

            # To Do: match the sales contact from Excel with a DB sales contact name
            salesContact = "unknown"


            """
            check that all application main, details are filled with data
            check that all main and end customers are filled with data
            check that sales name is filled with data
            """
            applicationMain = row["ApplicationMain"]
            applicationDetail = row["ApplicationDetail"]
            applicationLine = row["AL"]
            mainCustomer = row["MainCustomer"]
            endCustomer = row["EndCustomer"]
            salesName = row["SalesName"]
            rfp = row["RFP"]

            """
            tuple = (applicationMain, applicationDetail,
                     mainCustomer, endCustomer, salesName)

            if tuple not in uniqueCombinations:
                uniqueCombinations.append(tuple)
            """

            testParams = {
                "name": row["Project description"],
                "productMarketerFirstName": marketerFirstName,
                "productMarketerLastName": marketerLastName,
                "applicationMain": applicationMain,
                "applicationDetail": applicationDetail,
                "applicationLine": applicationLine,
                "mainCustomer": mainCustomer,
                "finalCustomer": endCustomer,
                "sales_name": salesName,
                "rfp": rfp,
                "distributor": row["Disti"],
                "ems": "",
                "tier1": row["Tier-1"],
                "oem": row["OEM"],
                "vpaCustomer": None,
                "salesContact": salesContact,
                "estimatedSop": row["SOP"],
                "priceCurrency": row["Currency"],
                "dummy": True if row["Filler"] == 1 else False,
                "region": row["Region"],
                "spNumber": row["SP Number"],
                "secondRegion": "",
                "draft": False,
                "comment": ["Comments"],
                "familyPriceDetails": ["Family Price"],
                "otherPriceComments": ["Price Source"],
                "dcChannel": row["DC_Channel"],
                "projectId": None,
                "projectId": None,
                "projectDescription": None,
                "familyPriceApplicable": (True if len(str(row["Family Price"])) > 0 else False),
                "status": ["Probability"],
                "priceValidUntil": None,
                "projectDescription": "",
                "spNumber": ""

            }

            # iterate over each DTO calling boUpCreatorValidator
            outputProjectId, validationErrors, conflictingProjectsDb, attributeIds, attributeIds = boUpCreatorValidator(params=testParams, dummy=(True if row["Filler"] == 1 else False),
                                                                                            helperQuerySets=helperQuerySets, mode=mode, creationDesired=creationDesired)

            conflictingRowsFile = []

            if index in duplicatedRows:
                validationErrors.append(
                    errorTypesProjectEntryValidation.projectCreationConflictFileLevel)

                # find the rows that have are conflicting - pandassql is extremelly slow, avoid
                """
                query = " SELECT * FROM df WHERE \
                        ApplicationMain = '" + str(applicationMain) + "' and ApplicationDetail = '" + str(applicationDetail) + "' and MainCustomer = '" + str(mainCustomer) + "' and EndCustomer = '" + str(endCustomer) + "' and SalesName = '" + str(salesName) + "';"

                queryJson_result = ps.sqldf(query, locals())
                print("queryJson_result")
                print(queryJson_result)
                """
                groupRow = df2.loc[df2['indexBak'] == index]
                group = groupRow.iloc[0]['group']  # groupRow["group"].values
                #print(index, "group", group, "type", type(group))
                # print(groupRow)

                allGroupRow = df2.loc[df2["group"] == group]
                conflictingRowsFile = allGroupRow['indexBak'].tolist()

                #print(index, "allGroupRow")
                # print(allGroupRow)
                #print(index, "conflicting rows", conflictingRowsFile)

            projectErrors = {"projectId": outputProjectId, "importRowNr": index, "originalFile": fileName, "idAppOriginal": row["ID_APP"],
                             "errors": validationErrors, "conflictingProjectsDb": conflictingProjectsDb, "conflictingRowsFile": conflictingRowsFile}
            projectErrorsArray.append(projectErrors)

            if mode == 2:
                # now map row volumes, prices, years into the DTO
                volumesArray = [row["vol2020"], row["vol2021"], row["vol2022"], row["vol2023"], row["vol2024"], row["vol2025"], row["vol2026"], row["vol2027"], row["vol2028"], row["vol2029"], row["vol2030"], row["vol2031"], row["vol2032"], row["vol2033"], row["vol2034"], row["vol2035"], row["vol2036"], row["vol2037"], row["vol2038"], row["vol2039"], row["vol2040"], row["vol2041"], row["vol2042"], row["vol2043"], row["vol2044"]]
                pricesArray = [row["price2020"], row["price2021"], row["price2022"], row["price2023"], row["price2024"], row["price2025"], row["price2026"], row["price2027"], row["price2028"], row["price2029"], row["price2030"], row["price2031"], row["price2032"], row["price2033"], row["price2034"], row["price2035"], row["price2036"], row["price2037"], row["price2038"], row["price2039"], row["price2040"], row["price2041"], row["price2042"], row["price2043"], row["price2044"]]
                print("prices array",pricesArray)
                yearsArray = [
                    2020,
                    2021,
                    2022,
                    2023,
                    2024,
                    2025,
                    2026,
                    2027,
                    2028,
                    2029,
                    2030,
                    2031,
                    2032,
                    2033,
                2034,
                    2035,
                    2036,
                    2037,
                    2038,
                    2039,
                    2040,
                    2041,
                    2042,
                    2043,
                    2044
                ]

                testParams["years"] = yearsArray
                testParams["volumes"] = volumesArray
                testParams["prices"] = pricesArray

                print("%%%%% input volumes", volumesArray)

            # if mode is 2, set draft to false and add to dtoArray
            if mode == 2:
                testParams["draft"] = False
                dtoArray.append(testParams)

    elif mode == 1:

        """
        mode 1 is our excel template for import / export
        for each row in the excel file, load the DTO (represented by a fixed dict)
        fetch the project id (immutable value in excel)
        """

        for index, row in df.iterrows():
            #print(index, "main customer", row["mainCustomer_id"])

            #marketerString = row["productMarketer_id"]
            marketerFirstName = "irrelevant" #marketerString.split("_")[0]
            marketerLastName = "irrelevant" #marketerString.split("_")[1]
            projectId = row["ID_APP_id"]

            # trim project name to max length...

            testParams = {"name": row["projectName"][:149],
                          "productMarketerFirstName": marketerFirstName,
                          "productMarketerLastName": marketerLastName,
                          "applicationMain": str(row["applicationMain_id"]).strip(),
                          "applicationDetail": str(row["applicationDetail_id"]).strip(),
                          "applicationLine": str(row["applicationLine"]).strip(),
                          "mainCustomer": str(row["mainCustomer_id"]).strip(),
                          "finalCustomer": str(row["endCustomer_id"]).strip(),
                          "sales_name": str(row["salesName_id"]).strip(),
                          "distributor": str(row["distributor_id"]).strip(),
                          "ems": str(row["ems_id"]).strip(),
                          "tier1": str(row["tier1_id"]).strip(),
                          "oem": str(row["oem_id"]).strip(),
                          "vpaCustomer": str(row["vpaCustomer_id"]).strip(),
                          "salesContact": str(row["salesContact"]).strip(),
                          "familyPriceApplicable": row["familyPriceApplicable"],
                          "familyPriceDetails": row["familyPriceDetails"],
                          "estimatedSop": row["sop"],
                          "status": row["statusProbability"],
                          "region": str(row["region"]).strip(),
                          "secondRegion": str(row["secondRegion"]).strip(),
                          "draft": False,
                          "dummy": row["dummy"],
                          "priceValidUntil": "unknown",
                          "projectId": projectId,
                          "id": projectId,
                          "rfp": str(row["rfp_id"]).strip(),
                          "projectDescription": "",
                          "spNumber": "",
                          "comment": ["Comments"],
                          #                          "dcChannel": row["DC_Channel"],

                          }

            print("%%%%% DTO key facts", testParams)

            # iterate over each DTO calling boUpCreatorValidator
            outputProjectId, validationErrors, conflictingProjects, attributeIds = boUpCreatorValidator(params=testParams, dummy=row["dummy"],
                                                                                                        helperQuerySets=helperQuerySets, mode=mode, creationDesired=True)
            # now map row volumes, prices, years into the DTO
            volumesArray = [row["vol2020"], row["vol2021"], row["vol2022"], row["vol2023"], row["vol2024"], row["vol2025"], row["vol2026"], row["vol2027"], row["vol2028"], row["vol2029"], row["vol2030"], row["vol2031"],
                            row["vol2032"], row["vol2033"], row["vol2034"], row["vol2035"], row["vol2036"], row["vol2037"], row["vol2038"], row["vol2039"], row["vol2040"], row["vol2041"], row["vol2042"], row["vol2043"], row["vol2044"]]
            pricesArray = [row["price2020"], row["price2021"], row["price2022"], row["price2023"], row["price2024"], row["price2025"], row["price2026"], row["price2027"], row["price2028"], row["price2029"], row["price2030"], row["price2031"],
                           row["price2032"], row["price2033"], row["price2034"], row["price2035"], row["price2036"], row["price2037"], row["price2038"], row["price2039"], row["price2040"], row["price2041"], row["price2042"], row["price2043"], row["price2044"]]

            yearsArray = [
                2020,
                2021,
                2022,
                2023,
                2024,
                2025,
                2026,
                2027,
                2028,
                2029,
                2030,
                2031,
                2032,
                2033,
                2034,
                2035,
                2036,
                2037,
                2038,
                2039,
                2040,
                2041,
                2042,
                2043,
                2044
            ]

            testParams["years"] = yearsArray
            testParams["volumes"] = volumesArray
            testParams["prices"] = pricesArray

            projectErrors = {"projectId": projectId,
                             "errors": validationErrors,
                             "conflictingProjectsDb": "",
                             "conflictingRowsFile": "",
                             "importRowNr": index,
                             "originalFile": fileName,
                             }
            projectErrorsArray.append(projectErrors)
            dtoArray.append(testParams)

    elif mode == 2:

        """
        This is Elke File for PL58.
        This has no sales names, so we will have to default to the first matching RFP.
        **
        rename fields 
        **
        check no duplicated MC+EC+MA+AD+SN for uniqueness at application level (team level migration)
        -> in Case of Elke Report, this will be a warning in the report file.
        **
        for each row in the excel file, load the DTO (represented by a fixed dict).
        The DTO will be processed by boUpCreatorValidator.
        The expected input is the flat BoUp file as used in January 2023 by BPS team.
        """
        print("df ####")
        print(df)
        df = df.rename(columns={"Application Main": "ApplicationMain",
                       "Application Detail": "ApplicationDetail", "RFP_str": "RFP"})

        cols = ['ApplicationMain', 'ApplicationDetail',
                'MainCustomer', 'EndCustomer', 'RFP']
        df['indexBak'] = df.index
        df2 = df[df.duplicated(subset=cols, keep=False)]
        duplicatedRows = list(df2.index.values)
        #df2['DuplicateGroup'] = df2.groupby(duplicatedRows).ngroup()

        df2 = df2.sort_values(cols)
        df2['group'] = 'g' + (df2.groupby(cols).ngroup() + 1).astype(str)
        #df2['duplicate_count'] = df2.groupby(cols)['origin'].transform('size')

        # used to check uniqueness within the uploaded file itself

        print("duplicates %%%")
        print(duplicatedRows)
        print("%%%%%%%%%")
        print(df2)
        uniqueCombinations = []
        conflictingRowsFile = []

        df2.to_csv("./duplicateReportsElkeFile.csv", sep=";")

        for index, row in df.iterrows():
            """
            check if row a Mamo Filler
            """

            if row["MainCustomer"] != "MAMO FILLER":

                #print(index, "dummy?", row["Filler"], "main customer", row)
                # To Do: match the excel marketer name to a DB marketer name
                marketerFirstName = "unknown"  # marketerString.split("_")[0]
                marketerLastName = "unknown"  # marketerString.split("_")[1]

                # projectId = row["ID_APP_id"]
                # To Do: match the sales contact from Excel with a DB sales contact name
                salesContact = "unknown"

                """
                check that all application main, details are filled with data
                check that all main and end customers are filled with data
                check that sales name is filled with data
                """
                applicationMain = row["ApplicationMain"]
                applicationDetail = row["ApplicationDetail"]
                applicationLine = row["AL"]
                mainCustomer = row["MainCustomer"]
                endCustomer = row["EndCustomer"]
                #salesName = row["SalesName"]
                rfp = row["RFP"]

                randomNumber = index #random.randrange(0, 99999)
                # true stands for no mamo filler
                syntheticProjectNameInput = "MIG-True" + str(applicationLine).replace(" ", "_") + "-" + str(row["PM"]).replace(" ", "_") + "-" + str(applicationMain).replace(" ", "_") + "-" + str(applicationDetail).replace(" ", "_") + "-" + str(mainCustomer).replace(" ", "_") + "-" + str(endCustomer).replace(" ", "_") + "-" + str(rfp).replace(" ", "_") + "_" + str(row["SOP"]).replace("", "noSop") + "_" + str(row["country"]).replace(" ", "_") + "_" + str(randomNumber)

                """
                sha 256
                """
                syntheticProjectName = hashlib.sha256(syntheticProjectNameInput.encode('utf-8')).hexdigest()

                testParams = {
                    "processingIndex": index,
                    "name": row["Project"],
                    "productMarketerFirstName": row["PM"], # workaround for initial loads
                    "productMarketerLastName": row["PM"],
                    "applicationMain": applicationMain,
                    "applicationDetail": applicationDetail,
                    "applicationLine": applicationLine,
                    "mainCustomer": mainCustomer,
                    "finalCustomer": endCustomer,
                    "sales_name": None,
                    "rfp": rfp,
                    "distributor": row["Disti"],
                    "ems": None,
                    "tier1": None,
                    "oem": row["OEM"],
                    "vpaCustomer": None,
                    "salesContact": None,
                    "estimatedSop": row["SOP"],
                    "priceCurrency": row["Currency"],
                    "dummy": True if row["MainCustomer"] == "MAMO FILLER" else False,
                    "region": row["country"],
                    "spNumber": 0,
                    "secondRegion": "",
                    "draft": False,
                    # the column "Project" in Elke File looks like a comment
                    "comment": row["Project"][:149],
                    "familyPriceDetails": "",
                    "otherPriceComments": row["Price_Source"],
                    "dcChannel": "",
                    "projectId": None,
                    "projectDescription": None,
                    "familyPriceApplicable": None,
                    "status": row["Status:Probability"],
                    "priceValidUntil": None,
                    "projectDescription": "",
                    "spNumber": "",
                    "projectName": syntheticProjectName,
                    "creatable": None
                }

                #print("%%%%% DTO", testParams)
                # iterate over each DTO calling boUpCreatorValidator
                outputProjectId, validationErrors, conflictingProjectsDb, attributeIds = boUpCreatorValidator(params=testParams, dummy=(True if row["MainCustomer"] == "MAMO FILLER" else False),
                                                                                                              helperQuerySets=helperQuerySets, mode=mode, creationDesired=creationDesired)

                conflictingRowsFile = []

                if index in duplicatedRows:
                    validationErrors.append(
                        errorTypesProjectEntryValidation.projectCreationConflictFileLevel)

                    # find the rows that have are conflicting - pandassql is extremelly slow, avoid
                    """
                    query = " SELECT * FROM df WHERE \
                            ApplicationMain = '" + str(applicationMain) + "' and ApplicationDetail = '" + str(applicationDetail) + "' and MainCustomer = '" + str(mainCustomer) + "' and EndCustomer = '" + str(endCustomer) + "' and SalesName = '" + str(salesName) + "';"

                    queryJson_result = ps.sqldf(query, locals())
                    print("queryJson_result")
                    print(queryJson_result)
                    """
                    groupRow = df2.loc[df2['indexBak'] == index]
                    # groupRow["group"].values
                    group = groupRow.iloc[0]['group']
                    #print(index, "group", group, "type", type(group))
                    # print(groupRow)

                    allGroupRow = df2.loc[df2["group"] == group]
                    conflictingRowsFile = allGroupRow['indexBak'].tolist()

                    #print(index, "allGroupRow")
                    # print(allGroupRow)
                    #print(index, "conflicting rows", conflictingRowsFile)

                projectErrors = {"projectId": outputProjectId, "importRowNr": index, "originalFile": fileName, "idAppOriginal": row["ID"],
                                 "errors": validationErrors, "conflictingProjectsDb": conflictingProjectsDb, "conflictingRowsFile": conflictingRowsFile}
                projectErrorsArray.append(projectErrors)

                if mode == 2:
                    # now map row volumes, prices, years into the DTO
                    # Elke File format
                    volumesArray = [row["CY20_pcs"], row["CY21_pcs"], row["CY22_pcs"], row["CY23_pcs"], row["CY24_pcs"], row["CY25_pcs"], row["CY26_pcs"], row["CY27_pcs"], row["CY28_pcs"], row["CY29_pcs"],
                                    row["CY30_pcs"], row["CY31_pcs"], row["CY32_pcs"], row["CY33_pcs"], row["CY34_pcs"], row["CY35_pcs"], row["CY36_pcs"], row["CY37_pcs"], row["CY38_pcs"], row["CY39_pcs"], row["CY40_pcs"]]
                    pricesArray = [row["CY20_price"], row["CY21_price"], row["CY22_price"], row["CY23_price"], row["CY24_price"], row["CY25_price"], row["CY26_price"], row["CY27_price"], row["CY28_price"], row["CY29_price"],
                                   row["CY30_price"], row["CY31_price"], row["CY32_price"], row["CY33_price"], row["CY34_price"], row["CY35_price"], row["CY36_price"], row["CY37_price"], row["CY38_price"], row["CY39_price"], row["CY40_price"]]
                    # remove exotic characters
                    index = 0
                    for volume in volumesArray:
                        try:
                            int(volume)
                        # if str(volume).isdigit() == False:
                        except:
                            print("could not ", volume, type(volume))
                            volumesArray[index] = 0
                        index = index + 1

                    indexB = 0
                    for price in pricesArray:
                        try:
                            float(price)
                        except:
                            pricesArray[indexB] = 0.0
                        indexB = indexB + 1
                    print("volumesArray output", volumesArray)

                    yearsArray = [
                        2020,
                        2021,
                        2022,
                        2023,
                        2024,
                        2025,
                        2026,
                        2027,
                        2028,
                        2029,
                        2030,
                        2031,
                        2032,
                        2033,
                    2034,
                        2035,
                        2036,
                        2037,
                        2038,
                        2039,
                        2040,
                    ]

                    testParams["years"] = yearsArray
                    testParams["volumes"] = volumesArray
                    testParams["prices"] = pricesArray
                    testParams["attributeIds"] = attributeIds

                    fatalErrors = [errorTypesProjectEntryValidation.salesNameDoesNotExist, errorTypesProjectEntryValidation.mainCustomerDoesNotExist, errorTypesProjectEntryValidation.finalCustomerDoesNotExist,
                    errorTypesProjectEntryValidation.projectCreationConflict, errorTypesProjectEntryValidation.regionIncorrect, errorTypesProjectEntryValidation.rfpDoesNotExist, errorTypesProjectEntryValidation.customersNotMatching,
                    errorTypesProjectEntryValidation.mainApplicationDoesNotExist, errorTypesProjectEntryValidation.detailApplicationDoesNotExist, errorTypesProjectEntryValidation.applicationLineDoesNotExist,
                    errorTypesProjectEntryValidation.statusDidNotExist, errorTypesProjectEntryValidation.regionDidNotExist, errorTypesProjectEntryValidation.willNotCreateProject,
                     ]
                    
                    print("volumesArray 2%%%???", volumesArray)
                    if any(item in fatalErrors for item in validationErrors) == False:
                        testParams["creatable"] = True
                    else:
                        testParams["creatable"] = False

                    print(index, "index, creatable?",
                          testParams["creatable"], syntheticProjectName)
                    print(validationErrors)

                # if mode is 2, set draft to false and add to dtoArray
                if mode == 2:
                    testParams["draft"] = False
                    dtoArray.append(testParams)
            else:

                projectErrors = {"projectId": row["ID"], "importRowNr": index, "originalFile": fileName, "idAppOriginal": row["ID"],
                "errors": [], "conflictingProjectsDb": [], "conflictingRowsFile": []}
                projectErrorsArray.append(projectErrors)
                print(index, "skipping due to MAMO FILLER")

    """
    if mode is 2 (Elke File import), we will now check each dto row and prepare bulk create of projects so that the rest of the algorithm can work properly
    For now this is meant for creation only.
    In projectCreatorValidator we checked for uniqueness. If uniqueness is not given, we will skip this all together,
    there is no way to test if we are updating. The synthetic project name is an unique key created with a relatively random number (row number in import file),
    so it's not possible to get a functional match with already existing objects.
    """
    if (mode == 2) & (creationDesired == True):
        print("creating DB entries ELKE file")

        newProjectsBulkArray = []
        createdIndices = []

        for dto in dtoArray:
            """
            prepare bulk create
            """
            if dto["creatable"] == True:

                attributeIds = dto["attributeIds"]

                """
                attributeIds = {
                        "salesNameId " : 0,
                        "finalCustomerId " : 0,
                        "mainCustomerId " : 0,
                        "applicationMainId " : 0,
                        "applicationDetailId " : 0,
                        "distributorId " : 0,
                        "vpaCustomerId " : 0,
                        "emsId " : 0,
                        "tierOneId " : 0,
                        "oemId " : 0,
                        "productMarketerId " : 0,
                        "statusId " : 0,
                        "regionId " : 0,
                        "secondRegionId " : 0,
                        "dcChannelId " : 0,
                        "priceTypeId " : 0,
                        "salesContactId " : 0,
                        "outputProjectId " : 0,
                        "applicationLineId " : 0,
                    }
                """
                projectObject = Project(
                    sales_name_id=attributeIds["salesNameId"],
                    applicationMain_id=attributeIds["applicationMainId"],
                    applicationDetail_id=attributeIds["applicationDetailId"],
                    applicationLine_id=attributeIds["applicationLineId"],
                    mainCustomer_id=attributeIds["mainCustomerId"],
                    finalCustomer_id=attributeIds["finalCustomerId"],
                    syntheticProjectName=dto["projectName"],
                    productMarketer_id=attributeIds["productMarketerId"],
                    draft=False,
                    dummy=dto["dummy"],
                    user_id=attributeIds["userId"],
                    projectName = dto["comment"],
                    region_id =  attributeIds["regionId"],
                    status_id = attributeIds["statusId"], 
                    salesNameDefaulted = attributeIds["salesNameDefaulted"]
                )

                newProjectsBulkArray.append(projectObject)
                createdIndices.append(dto["processingIndex"])

            else:
                pass

        newly_created_projects = Project.objects.bulk_create(
            newProjectsBulkArray, batch_size=1000
        )
        """
        now assign the project ids to each dto for further processing (preparation for longFormatProcessing)
        problem is, bulk create does not return ids or Pks (it's liek that...)
        so we need to retrieve all objects again
        """
        print("finished creating DB entries ELKE file")
        print("created indices", createdIndices)

        allProjects = Project.objects.all()

        for dto in dtoArray:
            if dto["processingIndex"] in createdIndices:

                # get the index, and retrieve
                relevantIndex = createdIndices.index(dto["processingIndex"])
                #print("will process", newly_created_projects[relevantIndex])
                fullProjectObject = allProjects.get(syntheticProjectName = newly_created_projects[relevantIndex].syntheticProjectName)
                #print("retrieved", fullProjectObject)
                dto["projectId"] = fullProjectObject.id
                dto["id"] = fullProjectObject.id
                #print("dto proc index", dto["processingIndex"], dto["projectId"], dto["id"])

        print("finished reasigning ids")
        print("newly created projects length", newly_created_projects)

    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%5")
    print("---> import finished!!!, DTO Count", len(dtoArray))
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%5")

    # unfreeze DB for all other users
    outputDf = df
    # now iterate through the input Df and add columns with all errors...

    """
    this will create the error report when testing files for quality
    """
    if True:

        outputDf["To Be Corrected"] = ""
        outputDf["outputId"] = ""
        outputDf["errors"] = ""
        outputDf["conflictingProjectsDbLevel"] = ""
        outputDf["conflictingProjectsFileLevel"] = ""

        for index, row in outputDf.iterrows():
            # skip mamo fillers
            if (mode == 2):
                # moved one indent since Mode 1 has no field MainCustomer (it has MainCustomerId)
                if (df.loc[index, "MainCustomer"] == "MAMO FILLER"):
                    pass

            errorDict = projectErrorsArray[index]
            errorString = ""
            conflictProjectsInDb = ""
            conflictProjectsInFile = ""

            for error in errorDict["errors"]:
                errorString = errorString + error.__str__() + " "
                df.loc[index, "To Be Corrected"] = True

            for project in errorDict["conflictingProjectsDb"]:
                conflictProjectsInDb = conflictProjectsInDb + \
                    str(project) + ". "

            for project in errorDict["conflictingRowsFile"]:
                conflictProjectsInFile = conflictProjectsInFile + \
                    str(project) + ". "

            df.loc[index, "outputId"] = errorDict["projectId"]
            df.loc[index, "errors"] = errorString
            df.loc[index, "conflictingProjectsDbLevel"] = conflictProjectsInDb
            df.loc[index, "conflictingProjectsFileLevel"] = conflictProjectsInFile

    return projectErrorsArray, outputDf, dtoArray


"""
this will update all projects entered currently into BoUp table 
eg. to be used when VHKs change, currencies / fx rates change
* for each row in BoUp
"""

def bulkUpdaterBoUpTable(vhkUpdate: bool, runDate: any, mode: int, projectDtoArray: any):
    """
    helper Objects: 
    0: Project.select_related("sales_name__rfp", "region")
    1: VhkCy.select_related("currency__currency")
    2: ProjectVolumePrices.objects.select_related(
            "project",
        )

    3: currencyObj = Currencies.objects.get(currency=currencyPrices)
    4: fxObject = ExchangeRates.objects.get(currency=currencyObj.pk, valid=True)
    5: ProjectVolumeMonth.objects.select_related().filter(
                project=project
            )
    6: MissingOrders.objects.filter(project=projectId)
    7: allFinalCustomers = FinalCustomers.objects.all()
    8: allMainCustomers = MainCustomers.objects.all()
    """

    allBoupEntries = BoUp.objects.all()
    allProjects = Project.objects.select_related("sales_name__rfp", "region", "applicationLine").all()
    costs = VhkCy.objects.select_related().all()
    currencies = CurrenciesArchive.objects.all()
    #fxRates = ExchangeRates.objects.all() #get(currency=currencyObj.pk, valid=True)
    fxRates = Currency.objects.all() 
    projectVolumePrices = ProjectVolumePrices.objects.select_related().all()
    projectVolumeMonth = ProjectVolumeMonth.objects.select_related().all()
    missingOrders = MissingOrders.objects.all()
    allFinalCustomers = FinalCustomers.objects.all()
    allMainCustomers = MainCustomers.objects.all()
    #allProducts = Product.objects.all()
    helperObjects = [allProjects, costs, projectVolumePrices, currencies, fxRates, projectVolumeMonth, missingOrders, allFinalCustomers, allMainCustomers]

    boupObjectsToBeUpdated = []
    boupObjectsToBeCreated = []

    """
    if mode is 2 we will bulk create new objects in BoUp table
    we need to prepare a BoUp object with the key params
    """

    if mode == 2:
        for dto in projectDtoArray:

            if dto["creatable"] == True:

                params = {
                            "finalRevenue": [],
                            "finalVolume": [],
                            "finalPrice": 0,
                            "finalGrossMargin": 0,
                            "finalGrossMarginPct": 0,
                            "final_revenue_month": 0,
                            "final_grossMargin_month": 0,
                            "final_grossMarginPct_month": 0,
                            "finalVhk": 0,
                            "final_revenue_FY": 0,
                            "final_grossProfit_FY": 0,
                            "final_grossProfitPct_FY": 0,
                            "final_volumes_FY": 0,
                            "vhkCy": 0,
                            "finalTotalCost": 0,
                            "asp": 0,
                            "weightedGrossMargin": 0,
                            "weightedGrossMarginPct": 0,
                            "weightedRevenue": 0,
                            "weightedVolume": 0,
                            }

                attributeIds = dto["attributeIds"]
                project = allProjects.get(syntheticProjectName=dto["projectName"])
                print("processing bulk create boup", project.id, "synt", dto["projectName"])
                probability = probability = float(project.status.status) / 100.0

                # workaround to fix issues with early projects
                applicationLineText = "N/A"
                try:
                    if project.applicationLine.applicationLineShortName != None:
                        applicationLineText = project.applicationLine.applicationLineShortName
                except:
                    pass

                boupObjectInput = BoUp(
                    applicationDetail = project.applicationDetail,
                    applicationMain = project.applicationMain,
                    mainCustomer=project.mainCustomer,
                    endCustomer=project.finalCustomer,
                    salesName=project.sales_name,
                    syntheticProjectName = project.syntheticProjectName, 
                    ID_APP = project,
                    productMarketer = project.productMarketer,
                    hfg = project.sales_name.rfp.hfg,
                    ppos = project.sales_name.rfp.ppos,
                    spNumber = project.spNumber,
                    familyPriceApplicable = project.familyPriceApplicable,
                    familyPriceDetails = project.familyPriceDetails,
                    comment = project.comment,
                    applicationLine = applicationLineText,
                    Reviewed = project.projectReviewed,
                    reviewDate = project.reviewDate,
                    region = project.region.region,
                    secondRegion = (project.secondRegion.region if project.secondRegion else None),
                    dcChannel = (
                        project.dcChannel.dcChannelDescription if project.dcChannel else ""
                    ),
                    priceType = (
                        project.priceType.priceTypeDisplay if project.priceType else ""
                    ),
                    endCustomerHelper = project.finalCustomer.finalCustomerName,
                    mainCustomerHelper = project.mainCustomer.customerName,
                    projectName = project.projectName,
                    distributor = project.distributor,
                    tier1 = project.tier1,
                    ems = project.ems,
                    vpaCustomer = project.vpaCustomer,
                    salesContact = project.salesContact,
                    statusProbability = project.status.statusDisplay,
                    probability = probability, 
                    sop = project.estimatedSop,
                    availablePGS = project.sales_name.rfp.availablePGS,
                    modifiedBy_id = 1,
                    modifiedDate = project.modifiedDate,
                    creationDate = project.creationDate,
                    package = project.sales_name.rfp.packageHelper,
                    series = project.sales_name.rfp.seriesHelper,
                    rfp = project.sales_name.rfp,
                    dummy = project.dummy,
                    basicType = project.sales_name.rfp.basicType,
                    priceSource = project.otherPriceComments,
                    gen = project.sales_name.rfp.familyHelper,
                    genDetail = project.sales_name.rfp.familyDetailHelper,
                    seriesLong = "N/A",
                    rfpHlp = project.sales_name.rfp.rfp,
                    mcHlp = project.mainCustomer.customerName,
                    ecHlp = project.finalCustomer.finalCustomerName,
                    #fxRate = self.fxRate # where does this come from in bulk create?
                    currency = "EUR",
                    contractualCurrency = project.contractualCurrency
                )

                persistor = bottomUpPersistor(params)
                success, outputValues, message, boUpObject = persistor.persist(
                    projectId=boupObjectInput.ID_APP_id, request=None, bulk=True, boUpObjectInput=boupObjectInput, probability=probability, helperObjects=helperObjects, vhkUpdate = True, runDate = runDate
                )

                boupObjectsToBeCreated.append(boUpObject)

    else:
        for boupLine in allBoupEntries:
            params = {
            "finalRevenue": [],
            "finalVolume": [],
            "finalPrice": 0,
            "finalGrossMargin": 0,
            "finalGrossMarginPct": 0,
            "final_revenue_month": 0,
            "final_grossMargin_month": 0,
            "final_grossMarginPct_month": 0,
            "finalVhk": 0,
            "final_revenue_FY": 0,
            "final_grossProfit_FY": 0,
            "final_grossProfitPct_FY": 0,
            "final_volumes_FY": 0,
            "vhkCy": 0,
            "finalTotalCost": 0,
            "asp": 0,
            "weightedGrossMargin": 0,
            "weightedGrossMarginPct": 0,
            "weightedRevenue": 0,
            "weightedVolume": 0,
            }

            probability = float(boupLine.probability)
            #print("current probability", probability)
            persistor = bottomUpPersistor(params)
            success, outputValues, message, boUpObject = persistor.persist(
                projectId=boupLine.ID_APP_id, request=None, bulk=True, boUpObjectInput=boupLine, probability=probability, helperObjects=helperObjects, vhkUpdate = vhkUpdate, runDate = runDate
            )
            
            if boUpObject == None:
                return False
            boupObjectsToBeUpdated.append(boUpObject)
    
    if mode == 2:
        BoUp.objects.bulk_create(
        boupObjectsToBeCreated, batch_size=1000)
    
    BoUp.objects.bulk_update(
        boupObjectsToBeUpdated, batch_size=1000, fields=[
        "gmLifeTime",
        "revEurLifeTime",
        "volLifeTime",
        "volWeightedLifeTime",
        "vol2020",
        "vol2021",
        "vol2022",
        "vol2023",
        "vol2024",
        "vol2025",
        "vol2026",
        "vol2027",
        "vol2028",
        "vol2029",
        "vol2030",
        "vol2031",
        "vol2032",
        "vol2033",
        "vol2034", 
        "vol2035",  
        "vol2036",  
        "vol2037",  
        "vol2038",  
        "vol2039", 
        "vol2040",  
        "vol2041",  
        "vol2042",  
        "vol2043",
        "vol2044",
        "price2020",
        "price2021",
        "price2022",
        "price2023",
        "price2024",
        "price2025",
        "price2026",
        "price2027",
        "price2028",
        "price2029",
        "price2030",
        "price2031",
        "price2032",
        "price2033",
        "price2034",
        "price2035",
        "price2036",
        "price2037",
        "price2038",
        "price2039",
        "price2040",
        "price2041",
        "price2042",
        "price2043",
        "price2044",
        "vhk2020",
        "vhk2021",
        "vhk2022",
        "vhk2023",
        "vhk2024",
        "vhk2025",
        "vhk2026",
        "vhk2027",
        "vhk2028",
        "vhk2029",
        "vhk2030",
        "vhk2031",
        "vhk2032",
        "vhk2033",
        "vhk2034",
        "vhk2035",
        "vhk2036",
        "vhk2037",
        "vhk2038",
        "vhk2039",
        "vhk2040",
        "vhk2041",
        "vhk2042",
        "vhk2043",
        "vhk2044",
        "gm2020",
        "gm2021",
        "gm2022",
        "gm2023",
        "gm2024",
        "gm2025",
        "gm2026",
        "gm2027",
        "gm2028",
        "gm2029",
        "gm2030",
        "gm2031",
        "gm2032",
        "gm2033",
        "gm2034",
        "gm2035",
        "gm2036",
        "gm2037",
        "gm2038",
        "gm2039",
        "gm2040",
        "gm2041",
        "gm2042",
        "gm2043",
        "gm2044",
        "wVol2020",
        "wVol2021",
        "wVol2022",
        "wVol2023",
        "wVol2024",
        "wVol2025",
        "wVol2026",
        "wVol2027",
        "wVol2028",
        "wVol2029",
        "wVol2030",
        "wVol2031",
        "wVol2032",
        "wVol2033",
        "wVol2034",
        "wVol2035",
        "wVol2036",
        "wVol2037",
        "wVol2038",
        "wVol2039",
        "wVol2040",
        "wVol2041",
        "wVol2042",
        "wVol2043",
        "wVol2044",
        "wRev2020",
        "wRev2021",
        "wRev2022",
        "wRev2023",
        "wRev2024",
        "wRev2025",
        "wRev2026",
        "wRev2027",
        "wRev2028",
        "wRev2029",
        "wRev2030",
        "wRev2031",
        "wRev2032",
        "wRev2033",
        "wRev2034",
        "wRev2035",
        "wRev2036",
        "wRev2037",
        "wRev2038",
        "wRev2039",
        "wRev2040",
        "wRev2041",
        "wRev2042",
        "wRev2043",
        "wRev2044",
        "wGrossMargin2020",
        "wGrossMargin2021",
        "wGrossMargin2022",
        "wGrossMargin2023",
        "wGrossMargin2024",
        "wGrossMargin2025",
        "wGrossMargin2026",
        "wGrossMargin2027",
        "wGrossMargin2028",
        "wGrossMargin2029",
        "wGrossMargin2030",
        "wGrossMargin2031",
        "wGrossMargin2032",
        "wGrossMargin2033",
        "wGrossMargin2034",
        "wGrossMargin2035",
        "wGrossMargin2036",
        "wGrossMargin2037",
        "wGrossMargin2038",
        "wGrossMargin2039",
        "wGrossMargin2040",
        "wGrossMargin2041",
        "wGrossMargin2042",
        "wGrossMargin2043",
        "wGrossMargin2044",
        "asp2020",
        "asp2021",
        "asp2022",
        "asp2023",
        "asp2024",
        "asp2025",
        "asp2026",
        "asp2027",
        "asp2028",
        "asp2029",
        "asp2030",
        "asp2031",
        "asp2032",
        "asp2033",
        "asp2034",
        "asp2035",
        "asp2036",
        "asp2037",
        "asp2038",
        "asp2039",
        "asp2040",
        "asp2041",
        "asp2042",
        "asp2043",
        "asp2044",
        "fy_vol2020",
        "fy_vol2021",
        "fy_vol2022",
        "fy_vol2023",
        "fy_vol2024",
        "fy_vol2025",
        "fy_vol2026",
        "fy_vol2027",
        "fy_vol2028",
        "fy_vol2029",
        "fy_vol2030",
        "fy_vol2031",
        "fy_vol2032",
        "fy_vol2033",
        "fy_vol2034",
        "fy_vol2035",
        "fy_vol2036",
        "fy_vol2037",
        "fy_vol2038",
        "fy_vol2039",
        "fy_vol2040",
        "fy_vol2041",
        "fy_vol2042",
        "fy_vol2043",
        "fy_vol2044",
        "fy_gm2020",
        "fy_gm2021",
        "fy_gm2022",
        "fy_gm2023",
        "fy_gm2024",
        "fy_gm2025",
        "fy_gm2026",
        "fy_gm2027",
        "fy_gm2028",
        "fy_gm2029",
        "fy_gm2030",
        "fy_gm2031",
        "fy_gm2032",
        "fy_gm2033",
        "fy_gm2034",
        "fy_gm2035",
        "fy_gm2036",
        "fy_gm2037",
        "fy_gm2038",
        "fy_gm2039",
        "fy_gm2040",
        "fy_gm2041",
        "fy_gm2042",
        "fy_gm2043",
        "fy_gm2044",
        "fy_wVol2020",
        "fy_wVol2021",
        "fy_wVol2022",
        "fy_wVol2023",
        "fy_wVol2024",
        "fy_wVol2025",
        "fy_wVol2026",
        "fy_wVol2027",
        "fy_wVol2028",
        "fy_wVol2029",
        "fy_wVol2030",
        "fy_wVol2031",
        "fy_wVol2032",
        "fy_wVol2033",
        "fy_wVol2034",
        "fy_wVol2035",
        "fy_wVol2036",
        "fy_wVol2037",
        "fy_wVol2038",
        "fy_wVol2039",
        "fy_wVol2040",
        "fy_wVol2041",
        "fy_wVol2042",
        "fy_wVol2043",
        "fy_wVol2044",
        "fy_wRev2020",
        "fy_wRev2021",
        "fy_wRev2022",
        "fy_wRev2023",
        "fy_wRev2024",
        "fy_wRev2025",
        "fy_wRev2026",
        "fy_wRev2027",
        "fy_wRev2028",
        "fy_wRev2029",
        "fy_wRev2030",
        "fy_wRev2031",
        "fy_wRev2032",
        "fy_wRev2033",
        "fy_wRev2034",
        "fy_wRev2035",
        "fy_wRev2036",
        "fy_wRev2037",
        "fy_wRev2038",
        "fy_wRev2039",
        "fy_wRev2040",
        "fy_wRev2041",
        "fy_wRev2042",
        "fy_wRev2043",
        "fy_wRev2044"
        ])
    print("finished updating BoUp as bulk")
    return True


class ProjectBulkCreator:
    projectsToBeCreated = []
    projectsToBeUpdated = []

    """
    Takes the BoUp exported Excel template and converts into long format prices, quantities.
    input array of DTOs. 
    updateOnly == False -> will create new entries, used for migration
    updateOnly == True -> will only update existing keys, used for Excel import / export workflow
    does: prepare and perform update and creation entries into projectVolumePrices / projectVolumeMonth and Log tables
    """
    def longFormatProcessing(self, projectDtoArray, user, updateOnly, helperQuerySets, mode):

        projectVolumePricesAllObjects = helperQuerySets["projectVolumePrices"]
        projectVolumeMonthAllObjects = helperQuerySets["projectVolumeMonth"]
        allProjectObjects = helperQuerySets["projects"]
        
        if mode == 2:
            print("mode 2 selecting all project objects")
            allProjectObjects = Project.objects.select_related().all()

        projectVolumePricesBulkUpdateArray = []
        projectVolumePricesBulkCreateArray = []
        projectVolumePricesMonthBulkUpdateArray = []
        projectVolumePricesMonthBulkCreateArray = []
        projectVolumePricesLogBulkUpdateArray = []
        projectVolumePricesLogBulkCreateArray = []

        for projectDto in projectDtoArray:
            print("input project dto")
            print(projectDto)
            # process the data submitted in the form...
            # following data will be extracted after running clean method defined under VolumeForm in forms.py file
            # field_value = form.cleaned_data.get("field_name")
            project = allProjectObjects.get(id=projectDto["id"])
            volumes = projectDto["volumes"]  # form.cleaned_data.get("volume")
            years = projectDto["years"]  # form.cleaned_data.get("years")
            prices = projectDto["prices"]       
            print("projectDto[prices",prices )

            # first disable all the existing volume entries for this project.
            currentVolumes = projectVolumePricesAllObjects.filter(project=project)
            currentMonthVolumes = projectVolumeMonthAllObjects.filter(project=project)

            for object in currentMonthVolumes:
                object.quantity = 0
            for object in currentVolumes:
                object.quantity = 0
                object.price = 0

            #currentVolumes.update(quantity=0)
            #currentVolumes.update(price=0)
            #currentMonthVolumes.update(quantity=0)
            runDate = datetime.datetime.now(tz=timezone.utc)

            # my custom code (Saadat)
            # this will generate dictionary with year as key and volume as value of user entered values
            # e.g {2020: 1020, 2021: 1203}
            years_with_volume = dict(zip(years, volumes))
            years_with_prices = dict(zip(years, prices))

            # getting already existing project and calendaryear
            existing_values_list = list(
                projectVolumePricesAllObjects.values_list(
                    "project__id", "calenderYear"
                ).order_by("id")
            )
            existing_qs = list(projectVolumePricesAllObjects.all().order_by("id"))
            existing_dict = dict(zip(existing_values_list, existing_qs))
            # existing_dict {(3, 2025): <ProjectVolumePrices: ID: 21 - QTY: 0 - YR: 2025> ... left side: year and project ID; full object

            # makeing list of user entered years to compare with above list. for each user entered year, the project ID is added.
            entered_values = [(project.id, year) for year in years]
            # entered_values [(3, 2025), (3, 2026), (3, 2027), (3, 2028), (3, 2029)]

            # this list will store queryset that already exist
            # and we can bulk_update on this queryset
            duplicate = []

            # this list store the values that doesnt exist already
            # so we can run bulk_create with these
            newYears = []
            # seperating new and old queryset
            # this will check if entered_values entry (e.g. (3, 2025)) is in the key of existing_dict. if it is, it will be appended to dict.
            for value in entered_values:
                if value in existing_dict:
                    existing_dict_value = existing_dict.get(value)
                    duplicate.append(existing_dict_value)
                else:
                    # appending year because we already have value of year.
                    newYears.append(value[1])

            # assigning new values to existing queryset. years with volume is the user input.
            for obj in duplicate:
                currentQuantity = obj.quantity
                obj.quantity = years_with_volume.get(obj.calenderYear)
                obj.price = years_with_prices.get(obj.calenderYear)
                obj.valid = True
                obj.user = user
                #print(obj.calenderYear, "updating", obj.price, obj.quantity)

            projectVolumePricesBulkUpdateArray.extend(duplicate)
            print("years_with_prices", years_with_prices)
            # creating new instances
            instance_objs = [
                ProjectVolumePrices(
                    project=project,
                    calenderYear=year,
                    quantity=years_with_volume.get(year),
                    price=years_with_prices.get(year),
                    valid=True,
                    user=user,
                )
                for year in newYears
            ]

            projectVolumePricesBulkCreateArray.extend(instance_objs)

            """
            the next block will prepare the storage of Logs.
            Logs are only created.
            """

            # rewrite of log objects
            for obj in projectVolumePricesBulkCreateArray:
                #print("obj", obj)
                newLogObject = ProjectVolumePricesLog(project=project,
                    calenderYear=obj.calenderYear,
                    runTimestamp=runDate)

                newLogObject.quantity = obj.quantity
                newLogObject.price = obj.price
                newLogObject.user = user
                newLogObject.modreason = "bulkUpdate"
                projectVolumePricesLogBulkCreateArray.append(newLogObject)

            for obj in projectVolumePricesBulkUpdateArray:

                newLogObject = ProjectVolumePricesLog(project=project,
                    calenderYear=obj.calenderYear,
                    runTimestamp=runDate,
                )
                newLogObject.quantity = obj.quantity
                newLogObject.quantity = obj.quantity
                newLogObject.user = user
                newLogObject.modreason = "bulkUpdate"
                projectVolumePricesLogBulkCreateArray.append(newLogObject)

            """
            The next block of code will create the monthly volume entries.
            This one is the largest "killer" of database calls.
            The iteration is based on user entered years. For each year, 12 months are created.
            The linSmoother function generates the monthly volume based on the yearly volume (linear interpolation).
            The ProjectVolumeMonth objects are created with a) projectId, calenderYear, month.
            Then, the monthVolume is assigned.

            Here, the algo is slightly modified wrt project creation.
            The second argument of linSmoother is EoP, so we will have to compute it based on the last year with volumes.

            One problem encountered during UAT are trailing zeroes in volumes during interpolation. so some conversions are required in order to keep the structure working.
            """

            from .helperFunctions import cleanYearsVolumes
            yearsForVolumeInterpolation, volumesForInterpolation = cleanYearsVolumes(years, volumes)

            year = 0
            monthVolume = []
            if (len(yearsForVolumeInterpolation) > 1) & (len(volumesForInterpolation) > 1):          
                monthVolume = linSmoother(yearsForVolumeInterpolation[0], yearsForVolumeInterpolation[-1], volumesForInterpolation)
            else:
                monthVolume = linSmoother(years[0], years[-1], volumes)

            """
            now make monthVolume match the expected length (years * 12)
            check how big are the gaps at beginning and end... and then close the gaps with chunks of 12 months with 0-volumes
            """

            if len(yearsForVolumeInterpolation) > 0:
                if len(yearsForVolumeInterpolation) != len(years):
                    placeHolder = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    firstYearInterp = yearsForVolumeInterpolation[0]
                    lastYearInterp = yearsForVolumeInterpolation[-1] 

                    placeHolderBegin = []
                    placeHolderEnd = []

                    deltaBegin = firstYearInterp - years[0]
                    deltaEnd = years[-1] - lastYearInterp

                    if deltaBegin > 1:
                        for index in range(0, (deltaBegin-1), 1):
                            placeHolderBegin = placeHolderBegin + placeHolder
                    elif (deltaBegin == 1):
                        placeHolderBegin = placeHolder
                    else:
                        pass

                    if deltaEnd > 1:
                        for index in range(0, (deltaEnd-1), 1):
                            placeHolderEnd = placeHolderEnd + placeHolder
                    elif (deltaEnd == 1):
                        placeHolderEnd = placeHolder
                    else:
                        pass

                    monthVolume = placeHolderBegin + monthVolume + placeHolderEnd


            months = [month for month in range(1, 13)]

            # my custom code (Saadat)
            # this will generate dictionary with year as key and {month : volume} as value of user entered values
            # e.g {2020: {1:1302, 2:1304, 3:1430, ..., 12:1620}, 2021: {1:1203, ..., 12:1104}}
            years_with_months_volume = {}
            #print("monthVolume", monthVolume)

            monthVolumeBis = monthVolume
            monthVolumeBis = [0 if a_ > 0 else a_ for a_ in monthVolumeBis]

            reversedVolumes = list(reversed(volumes))
            print(len(reversedVolumes), "reversed vol", reversedVolumes)
            try:
                lastNonZeroVolumeIndex = len(
                    reversedVolumes) - next(i for i, val in enumerate(reversedVolumes, 1) if val > 0)  # 2
                eopAlt = 0
                if lastNonZeroVolumeIndex != None:
                    eopAlt = years[lastNonZeroVolumeIndex]
            except:
                pass

            # the second case, an empty array, can only happen during migration. the system rejects empty or zero volumes.
            if monthVolume != []:
                for count, year in enumerate(years):
                    # if larger than EoP, set to 0 to avoid having "1000 pieces"
                    if (year > eopAlt) & (eopAlt != 0):
                        years_with_months_volume[year] = {
                            month: volume
                            for month, volume in zip(
                                months,
                                monthVolumeBis[count * 12 : (count + 1) * 12],
                            )
                        }
                    else:
                    #print("count", count, year)
                        years_with_months_volume[year] = {
                            month: volume
                            for month, volume in zip(
                                months,
                                monthVolume[count * 12 : (count + 1) * 12],
                            )
                        }
            else:
                monthVolume = []

                for index in range(0, (25*12), 1):
                    monthVolume.append(0)
                # this will create zero entries
                for count, year in enumerate(years):
                    if (year > eopAlt) & (eopAlt != 0):
                        years_with_months_volume[year] = {
                            month: volume
                            for month, volume in zip(
                                months,
                                monthVolumeBis[count * 12 : (count + 1) * 12],
                            )
                        }
                    else:
                        years_with_months_volume[year] = {
                            month: volume
                            for month, volume in zip(
                                months,
                                monthVolume[count * 12 : (count + 1) * 12],
                            )
                        }
            """
            if monthVolume != []:
                for count, year in enumerate(years):
                    years_with_months_volume[year] = {
                        month: volume
                        for month, volume in zip(
                            months,
                            monthVolumeBis[count * 12 : (count + 1) * 12],
                        )
                    }
                    
            else:
                monthVolume = []

                for index in range(0, (25*12), 1):
                    monthVolume.append(0)
                # this will create zero entries
                for count, year in enumerate(years):
                    years_with_months_volume[year] = {
                        month: volume
                        for month, volume in zip(
                            months,
                            monthVolume[count * 12 : (count + 1) * 12],
                        )
                    }

            print("---> OUTPUT years_with_months_volume", years_with_months_volume)
            """
            # getting already existing project, calendaryear and month
            # e.g (1, 2020, 1)
            existing_values_list = list(
                projectVolumeMonthAllObjects.values_list(
                    "project__id", "calenderYear", "month"
                ).order_by("id")
            )
            existing_qs = list(projectVolumeMonthAllObjects.all().order_by("id"))
            # merging vlaues_list and queryset in dict form
            # e.g {(1, 2020, 1): <QuerysetObject xxxxx >}
            existing_dict = dict(zip(existing_values_list, existing_qs))
            # makeing list of user entered years to compare with above list. for each user entered year, the project ID is added.

            entered_values_month = []

            for year in years_with_months_volume:
                for month in months:
                    entered_values_month.append((project.id, year, month))

            print("OUTPUT years_with_months_volume", years_with_months_volume)

            # this list will store queryset that already exist
            # and we can bulk_update on this queryset
            duplicate = []

            # this list store the values that doesnt exist already
            # so we can run bulk_create with these
            new = []

            # seperating new and old queryset

            for value in entered_values_month:
                # (3, 2028, 12)
                if value in list(existing_dict.keys()):
                    existing_dict_value = existing_dict.get(value)
                    duplicate.append(existing_dict_value)
                else:
                    # value contains combination of project id, year and month
                    # that aren't available in database
                    new.append(value)
            """
            new format:
                new (408, 2040, 4)
            years_with_months_volume format:
            {2020: {1: 1036.6666666666667, 2: 1183.3333333333333, 3: 1330.0, 4: 1476.6666666666665, 5: 1623.3333333333335, 6: 1770.0, 7: 1916.6666666666667, 8: 2063.333333333333, 9: 2210.0, 10: 2356.666666666667, 11: 2503.333333333333, 12: 2650.0}, 2021: {1: 2796.6666666666665, 2: 2943.3333333333335, 3: 3090.0, 4: 3236.6666666666665, 5: 3383.3333333333335, 6: 3530.0, 7: 3676.6666666666665, 8: 3823.3333333333335, 9: 3970.0, 10: 4116.666666666666, 11: 4263.333333333334, 12: 4410.0}, 2022: {1: 4269.44444

            print("output new vols mont", new)
            for vol in new:
                print("-----> new", vol, "corr", years_with_months_volume)
            """
            # assigning new values to existing queryset
            for obj in duplicate:
                currentQuantity = obj.quantity
                months_with_quantity = years_with_months_volume.get(
                    obj.calenderYear
                )  # {1:1200, 2:1243, 3:2343}
                quantity = months_with_quantity.get(obj.month)
                obj.quantity = quantity
                obj.valid = True
                obj.user = user

            projectVolumePricesMonthBulkUpdateArray.extend(duplicate)

            # creating new instances
            # (projectID, year, month)
            instance_objs = [
                ProjectVolumeMonth(
                    project=project,
                    calenderYear=obj[1],
                    quantity=years_with_months_volume.get(obj[1]).get(obj[2]),
                    valid=True,
                    user=user,
                    month=obj[2]
                )
                for obj in new
            ]

            projectVolumePricesMonthBulkCreateArray.extend(instance_objs)

        """
        ############
        now bulk create and update ProjectVolumePrices, ProjectVolumeMonth and logs
        updateOnly == False -> will create new entries, used for migration
        updateOnly == True -> will only update existing keys, used for Excel import / export workflow
        """

        # bulk update values that we added new values above
        ProjectVolumePrices.objects.bulk_update(
            projectVolumePricesBulkUpdateArray, ["quantity", "price", "user"]
        )

        if updateOnly == False:
            # queryset of newly created volumes
            newly_created_volumes = ProjectVolumePrices.objects.bulk_create(
                projectVolumePricesBulkCreateArray
            )

        # bulk update values that we added new values above
        ProjectVolumeMonth.objects.bulk_update(
            projectVolumePricesMonthBulkUpdateArray, ["quantity", "user"]
        )

        if updateOnly == False:
            newly_created_monthly_volumes = ProjectVolumeMonth.objects.bulk_create(
                projectVolumePricesMonthBulkCreateArray
            )

        # project volume prices Log update
        ProjectVolumePricesLog.objects.bulk_update(
            projectVolumePricesLogBulkUpdateArray, [
                "quantity", "price", "valid", "user"]
        )
        
        """
        # commented out since logs must be always created, we modify no logs
        if updateOnly == False:
            new_project_volume_prices_log_obj = ProjectVolumePricesLog.objects.bulk_create(
                projectVolumePricesLogBulkCreateArray
            )
        """

    """
    entry point
    requires: the excel filename, the file path, run mode: 0 / 1 / 2 (0: consistency validation, 1: import of our excel template, 2: migration)
    will do:
    validate entries
    convert wide into long format and evtl. create the entries in DB
    persist into BoUp table

    """

    def bulkCreatorEntryPoint(self, fileName: str, excelFilePath: str, mode: int, request: Any):
        """
        // helper querysets for running DB hits only a single time in all bulk lifecycle
        """
        helperQuerySets = {"productMarketers": marketerMetadata.objects.all()}
        helperQuerySets["applicationMain"] = ApplicationMain.objects.all()
        helperQuerySets["applicationDetail"] = ApplicationDetail.objects.all()
        helperQuerySets["mainCustomer"] = MainCustomers.objects.all()
        helperQuerySets["finalCustomer"] = FinalCustomers.objects.all()
        helperQuerySets["sales_name"] = SalesName.objects.all()
        helperQuerySets["distributor"] = Distributors.objects.all()
        helperQuerySets["ems"] = EMS.objects.all()
        helperQuerySets["tier1"] = Tier1.objects.all()
        helperQuerySets["oem"] = OEM.objects.all()
        helperQuerySets["vpaCustomer"] = VPACustomers.objects.all()
        # name related
        helperQuerySets["salesContact"] = SalesContacts.objects.all()
        helperQuerySets["status"] = ProjectStatus.objects.all()
        helperQuerySets["region"] = Regions.objects.all()
        helperQuerySets["secondRegion"] = SecondRegion.objects.all()
        helperQuerySets["projects"] = Project.objects.all()
        helperQuerySets["products"] = Product.objects.all()

        helperQuerySets["projectVolumePrices"] = ProjectVolumePrices.objects.select_related(
        ).all()
        helperQuerySets["projectVolumeMonth"] = ProjectVolumeMonth.objects.select_related(
        ).all()
        helperQuerySets["applicationLine"] = ApplicationLine.objects.all()

        """
        run the validation on mode 1 (excel workflow)
        """
        projectErrorsArray = None
        outputDf = None
        projectDtoArray = None        

        if mode == 1:
            projectErrorsArray, outputDf, projectDtoArray = entryPointValidator(fileName = fileName, excelFilePath = excelFilePath, mode = mode, creationDesired = False, helperQuerySets=helperQuerySets)

        elif mode == 2:
            projectErrorsArray, outputDf, projectDtoArray = entryPointValidator(fileName = fileName, excelFilePath = excelFilePath, mode = mode, creationDesired = True, helperQuerySets=helperQuerySets)

        # def entryPointValidator(fileName: str, excelFilePath: str, mode: int, creationDesired: bool, helperQuerysets: Any):

        """
        check the validation results and persist into ProjectVolumePrices, etc... tables
        third positional argument: updateOnly
        Do only if no errors!
        """

        print("%%%%%%%%%%%%%% projectErrorsArray", len(projectErrorsArray))
        #print(projectErrorsArray)
        
        if mode == 1:
            if len(projectErrorsArray) == 0:
                self.longFormatProcessing(projectDtoArray, request.user, True, helperQuerySets, mode)
        elif mode == 2:
            # create a subset of project dto array, where creatable == True
            creatableProjectDtoArray = [d for d in projectDtoArray if d['creatable'] in [True]]
            # only update set to false
            self.longFormatProcessing(creatableProjectDtoArray, request.user, False, helperQuerySets, mode)

        else:
            print("returning false")
            return False, outputDf
        """
        bulk update BoUp table
        """

        print("(((((((((((((((((( project dto array")
        print(projectDtoArray)
        bulkSuccess = bulkUpdaterBoUpTable(vhkUpdate = False, runDate = None, mode=mode, projectDtoArray=projectDtoArray)

        return bulkSuccess, outputDf


def bulkErrorUpdateEntrypoint(request):

    allBoupEntries = BoUp.objects.all()
    allProjects = Project.objects.select_related("sales_name__rfp", "region", "applicationLine").all()
    costs = VhkCy.objects.select_related().all()
    currencies = CurrenciesArchive.objects.all()
    fxRates = Currency.objects.all()  #ExchangeRates.objects.all() #get(currency=currencyObj.pk, valid=True)
    currencies = Currencies.objects.all()
    # get(currency=currencyObj.pk, valid=True)
    fxRates = ExchangeRates.objects.all()
    projectVolumePrices = ProjectVolumePrices.objects.select_related().all()
    projectVolumeMonth = ProjectVolumeMonth.objects.select_related().all()
    missingOrders = MissingOrders.objects.all()
    allFinalCustomers = FinalCustomers.objects.all()
    allMainCustomers = MainCustomers.objects.all()
    missingSalesPlan = MissingSalesPlan.objects.all()

    #allProducts = Product.objects.all()
    helperObjects = [allProjects, costs, projectVolumePrices, currencies, fxRates,
                     projectVolumeMonth, missingOrders, allFinalCustomers, allMainCustomers, missingSalesPlan]

    # clean up error table, we will only bulk create errors
    allErrorObjects = ProjectError.objects.all.delete()
    errorsBulkCreateArray = []

    for project in allProjects:
        statusProbability = 1.0

        try:
            statusProbability = float(project.status.status) / 100.0
        except:
            pass

        (
            revenue,
            volumes,
            prices,
            grossMargin,
            grossMarginPct,
            revenue_month,
            grossMargin_month,
            grossMarginPct_month,
            vhk,
            revenue_FY,
            grossProfit_FY,
            grossProfitPct_FY,
            volumes_FY,
            VhkCy,
            totalCost,
            sumRevenue,
            sumGrossMargin,
            sumCost,
            years,
            errors,
            weightedGrossMargin,
            weightedGrossMarginPct,
            weightedRevenue,
            asp,
            weightedVolume,
            sumVolume,
            sumWeightedVolume,
            sumWeightedRevenue,
            averageAsp,
            sumWeightedGrossMargin,
            projectCurrency,
            fxRate
        ) = getProjectOverview(project.id, request.user, statusProbability, helperObjects)

        errorString = ",".join([str(error.value) for error in errors])
        item = ProjectError(project=project, error_ids=errorString)
        errorsBulkCreateArray.append(item)

    newProjectErrors = ProjectError.objects.bulk_create(
        errorsBulkCreateArray, batch_size=1000
    )
