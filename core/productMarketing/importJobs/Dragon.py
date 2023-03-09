"""
Infineon Technologies AG
The Goal is to import the entries from the Dragon.xlsx into the Dragon table while checking if the entry already exists.
Go through each row to get the End Costumer, Main Costumer.
Look up in the respective tables if exaclty one entry exists.
If more entries exists throw an error message. If no entry exist create the entry.
"""
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
from productMarketing.models import (
    Dragon,
    FinalCustomers,
    MainCustomers,
    SalesOpportunities,
    ErrorTypesSalesOpportunities,
    SalesOpportunitiesConflicts,
    SalesName,
    Project,
    ProjectsToSalesOpportunitiesConflicts,
)
from core.project.models import Project, ProjectError, ToDoItems

# from ..models import *
from enum import Enum

class OpportunityChanges(Enum):
    descriptionChanged = 0
    statusChanged = 1
    sopMonth = 2
    eopMonth = 3
    lifetimeRevenue = 4
    lifetimeQuantity = 5

    def __str__(self) -> str:
        if self.value == 0:
            return "Opportunity description changed."
        elif self.value == 1:
            return "Opportunity status changed."
        elif self.value == 2:
            return "Opportunity SoP month changed."
        elif self.value == 3:
            return "Opportunity EoP month changed."
        elif self.value == 4:
            return "Opportunity lifetime revenue changed."
        elif self.value == 5:
            return "Opportunity lifetime quantity changed."

## operand: abstraction for volumes or prices
class ErrorTypesSalesOpportunitesValidation(Enum):
    # for dragon to sales opportunity
    salesNameMissing = 0
    endCustomerMissing = 1
    mainCustomerMissing = 2

    # for sales opportunity to project and viceversa
    projectNotFound = 3
    salesOpportunityNotFound = 4
    salesNameNotFound = 5  # if typo on import
    multipleMatchingSalesOpportunities = 6

    def __str__(self) -> str:
        # python < v3.10 does not support switch statements...

        if self.value == 0:
            return "salesNameMissing"
        elif self.value == 1:
            return "endCustomerMissing"
        elif self.value == 2:
            return "mainCustomerMissing"
        elif self.value == 3:
            return "projectNotFound"
        elif self.value == 4:
            return "salesOpportunityNotFound"
        elif self.value == 5:
            return "salesNameNotFound"
        elif self.value == 6:
            return "multipleMatchingSalesOpportunities"

## to dos: type annotations
def runDragonImport(fileUpload:bool, uploadPath:str):
    now = datetime.now()
    date = now.strftime("%Y%m%d")

    """
    Create the possible error types
    * sales name missing / end customer missing / final customer missing
    """

    errorTypesSalesOpportunities: MutableSequence[
        ErrorTypesSalesOpportunitesValidation
    ] = [
        ErrorTypesSalesOpportunitesValidation.salesNameMissing,
        ErrorTypesSalesOpportunitesValidation.endCustomerMissing,
        ErrorTypesSalesOpportunitesValidation.mainCustomerMissing,
        ErrorTypesSalesOpportunitesValidation.projectNotFound,
        ErrorTypesSalesOpportunitesValidation.multipleMatchingSalesOpportunities,
        ErrorTypesSalesOpportunitesValidation.salesNameNotFound,
        ErrorTypesSalesOpportunitesValidation.salesOpportunityNotFound,
    ]

    for errorType in errorTypesSalesOpportunities:
        errorObj, created = ErrorTypesSalesOpportunities.objects.get_or_create(
            errorType=errorType.value,
        )

        errorObj.errorDescription = errorType.__str__()
        errorObj.save()

    """
    Bring the data in the wanted form.
    """

    df = None
    if fileUpload == False:
        df = pd.read_excel("./persistentLayer/importJobs/Dragon.xlsx", decimal=".")
    else:
        uploadPath = "./" + uploadPath
        df = pd.read_excel(uploadPath, decimal=".")

    length = len(df.index)
    print("### input")
    print(df)
    print("####")

    """
    Go through each row to check if an entry exists already exists or if we need to create it.
    For that lookup in the currencies and product table, if the referenced object exists there.
    If we have more than one entry referenced, then we need to throw an error.
    """

    dragonOpportunitiesThatChanged = []
    dragonOpportunitiesIdsThatChanged = []

    for i in range(0, length, 1):

        TRANSACTION_NUMBER_IMPORT = df.loc[i, "TRANSACTION NUMBER"]
        OPPORTUNITY_DESCRIPTION_IMPORT = df.loc[i, "1_OPPORTUNITY_DESCRIPTION"]
        CUSTOMER_CLASSIFICATION_IMPORT = df.loc[i, "CUSTOMER_CLASSIFICATION"]
        END_CUSTOMER_IMPORT = df.loc[i, "4_END_CUSTOMER"]
        DC_CHANNEL_IMPORT = df.loc[i, "DC_CHANNEL"]
        MARKET_APP_IMPORT = df.loc[i, "MARKET_APP"]
        FOCUS_PROJECT_FLAG_IMPORT = df.loc[i, "FOCUS_PROJECT_FLAG"]
        OPPORTUNITY_CHANNEL_IMPORT = df.loc[i, "OPPORTUNITY_CHANNEL"]
        DC_REGION_NAME_IMPORT = df.loc[i, "DC_REGION - NAME"]
        SOCKET_COMMENT_IMPORT = df.loc[i, "SOCKET_COMMENT"]
        ITEM_NUMBER_IMPORT = df.loc[i, "ITEM_NUMBER"]
        PL_IMPORT = df.loc[i, "2_PL"]
        HFG_IMPORT = df.loc[i, "3_HFG"]
        RFP_SP_NAME_IMPORT = df.loc[i, "RFP_SP_NAME"]
        CY_PART_FAMILY_IMPORT = df.loc[i, "CY PART FAMILY"]
        CY_PART_NAME_IMPORT = df.loc[i, "CY PART NAME"]
        MAIN_CUSTOMER_IMPORT = df.loc[i, "2_MAIN_CUSTOMER"]
        DC_CUSTOMER_IMPORT = df.loc[i, "3_DC_CUSTOMER"]
        PRODUCT_DESCRIPTION_IMPORT = df.loc[i, "3_PRODUCT_DESCRIPTION"]
        COMMENT_SALES_I_IMPORT = df.loc[i, "COMMENT_SALES_I"]
        SOCKET_COMPETITOR_IMPORT = df.loc[i, "SOCKET_COMPETITOR"]
        CREATION_DAY_IMPORT = df.loc[i, "CREATION - DAY"]
        PRODUCT_STATUS_AGGREGATED_IMPORT = df.loc[i, "PRODUCT_STATUS_AGGREGATED"]
        PRODUCT_STATUS_IMPORT = df.loc[i, "1_PRODUCT_STATUS"]
        SOCKET_STATUS_IMPORT = df.loc[i, "SOCKET_STATUS"]
        DESIGN_WIN_CLAIM_STATUS_IMPORT = df.loc[i, "DESIGN_WIN_CLAIM_STATUS_"]
        OPPORTUNITY_REASON_IMPORT = df.loc[i, "OPPORTUNITY_REASON"]
        DESIGN_LOSS_DAY_IMPORT = df.loc[i, "DESIGN_LOSS - DAY"]
        LOST_REASON_DESCRIPTION_IMPORT = df.loc[i, "LOST_REASON_DESCRIPTION"]
        SALES_FLAG_IMPORT = df.loc[i, "SALES_FLAG"]
        IFX_RESPONSIBLE_IMPORT = df.loc[i, "4_IFX_RESPONSIBLE"]
        DESIGN_WIN_EXP_MONTH_IMPORT = df.loc[i, "8_DESIGN_WIN_EXP - MONTH"]
        RAMP_UP__MONTH_IMPORT = df.loc[i, "9 RAMP_UP -  MONTH"]
        RAMP_DOWN__MONTH_IMPORT = df.loc[i, "9_RAMP_DOWN -  MONTH"]
        TRAFFIC_LIGHT_IMPORT = df.loc[i, "TRAFFIC_LIGHT"]
        TRAFFIC_LIGHT_COMMENT_IMPORT = df.loc[i, "TRAFFIC_LIGHT_COMMENT"]
        APPROVER_1_IMPORT = df.loc[i, "APPROVER 1"]
        APPROVER_2_IMPORT = df.loc[i, "APPROVER 2"]
        DW_APPR_FIN_YEAR_IMPORT = df.loc[i, "DW_APPR - FIN_YEAR"]
        DW_APPR_FIN_QUARTER_IMPORT = df.loc[i, "DW_APPR - FIN_QUARTER"]
        DW_APPR_FIN_MONTH_IMPORT = df.loc[i, "DW_APPR - FIN_MONTH"]
        DW_APPR_FIN_DAY_IMPORT = df.loc[i, "DW_APPR - FIN DAY"]
        BUSINESS_WIN_MONTH_IMPORT = df.loc[i, "BUSINESS_WIN-MONTH"]
        MAIN_CUSTOMER_NUMBER_IMPORT = df.loc[i, "MAIN_CUSTOMER - NUMBER"]
        DW_POT_UW_USD_IMPORT = df.loc[i, "DW_POT_UW_USD"]
        if np.isnan(df.loc[i, "DW_ACHIEVE_USD"]):
            DW_ACHIEVE_USD_IMPORT = 1.0
        else:
            DW_ACHIEVE_USD_IMPORT = df.loc[i, "DW_ACHIEVE_USD"]

        PLANNED_REV_UW_USD_IMPORT = df.loc[i, "PLANNED_REV_UW_USD"]
        LIFETIME_REV_USD_IMPORT = df.loc[i, "LIFETIME_REV_USD"]
        IFX_PRODUCT_QUANTITY_IMPORT = df.loc[i, "IFX_PRODUCT_QUANTITY"]
        Item_Internal_Device_IMPORT = df.loc[i, "Item: Internal Device"]
        Product_IMPORT = df.loc[i, "Product"]

        print(DW_ACHIEVE_USD_IMPORT, np.isnan(df.loc[i, "DW_ACHIEVE_USD"]))

        endCustomer = END_CUSTOMER_IMPORT  # FinalCustomers.objects.filter(finalCustomerName=END_CUSTOMER_IMPORT)
        mainCustomer = MAIN_CUSTOMER_IMPORT  #  MainCustomers.objects.filter(customerName = MAIN_CUSTOMER_IMPORT)
        # print("EndCostumer", EndCostumers, "MainCostumer", MainCostumers)

        """
        if EndCostumers.count() > 0:
            EndCostumer = EndCostumers[0]
        else:
            EndCostumer = FinalCustomers.objects.get(id = 0)
        if MainCostumers.count() > 0:
            MainCostumer = MainCostumers[0]
        else:
            MainCostumer = MainCustomers.objects.get(id = 0)
        """

        DragonObj, created = Dragon.objects.get_or_create(
            END_CUSTOMER=endCustomer,
            MAIN_CUSTOMER=mainCustomer,
            RFP_SP_NAME=RFP_SP_NAME_IMPORT,
            TRANSACTION_NUMBER= TRANSACTION_NUMBER_IMPORT ## this is sales name
        )

        print("RFP_SP_NAME_IMPORT", RFP_SP_NAME_IMPORT)

        if created == True:
            print(i, "created", DragonObj)
        else:
            print(i, "retrieved", DragonObj)

            changeItem = thisdict = {
            "dragonObjId": DragonObj.id,
            "changes": []
            }

            changes = False

            # req: 99 - check if changes of key data... propagate alerts across the system
            if DragonObj.OPPORTUNITY_DESCRIPTION != OPPORTUNITY_DESCRIPTION_IMPORT:
                changeItem["changes"].append(OpportunityChanges.descriptionChanged)
                changes = True

            if DragonObj.PRODUCT_STATUS_AGGREGATED != PRODUCT_STATUS_AGGREGATED_IMPORT:
                changeItem["changes"].append(OpportunityChanges.statusChanged)
                changes = True

            if DragonObj.RAMP_UP_MONTH != RAMP_UP__MONTH_IMPORT:
                changeItem["changes"].append(OpportunityChanges.sopMonth)
                changes = True

            if DragonObj.RAMP_DOWN_MONTH != RAMP_DOWN__MONTH_IMPORT:
                changeItem["changes"].append(OpportunityChanges.eopMonth)
                changes = True

            if DragonObj.LIFETIME_REV_USD != LIFETIME_REV_USD_IMPORT:
                changeItem["changes"].append(OpportunityChanges.lifetimeRevenue)
                changes = True

            if DragonObj.IFX_PRODUCT_QUANTITY != IFX_PRODUCT_QUANTITY_IMPORT:
                changeItem["changes"].append(OpportunityChanges.lifetimeQuantity)
                changes = True

            if changes == True:
                dragonOpportunitiesThatChanged.append(changeItem)
                dragonOpportunitiesIdsThatChanged.append(DragonObj.id)
                print("change detected!")

        #DragonObj.TRANSACTION_NUMBER = TRANSACTION_NUMBER_IMPORT
        DragonObj.OPPORTUNITY_DESCRIPTION = OPPORTUNITY_DESCRIPTION_IMPORT
        DragonObj.MARKET_APP = MARKET_APP_IMPORT
        DragonObj.PRODUCT_STATUS_AGGREGATED = PRODUCT_STATUS_AGGREGATED_IMPORT
        DragonObj.RAMP_UP_MONTH = RAMP_UP__MONTH_IMPORT
        DragonObj.RAMP_DOWN_MONTH = RAMP_DOWN__MONTH_IMPORT
        DragonObj.LIFETIME_REV_USD = LIFETIME_REV_USD_IMPORT
        DragonObj.IFX_PRODUCT_QUANTITY = IFX_PRODUCT_QUANTITY_IMPORT

        DragonObj.save()

        """
        DC_REGION_NAME = DC_REGION_NAME_IMPORT, ### region 1
        MARKET_APP = MARKET_APP_IMPORT, ### application detail
        OPPORTUNITY_DESCRIPTION = OPPORTUNITY_DESCRIPTION_IMPORT,


        TRANSACTION_NUMBER = TRANSACTION_NUMBER_IMPORT,
        CUSTOMER_CLASSIFICATION = CUSTOMER_CLASSIFICATION_IMPORT,
        END_CUSTOMER = endCustomer,
        DC_CHANNEL = DC_CHANNEL_IMPORT,
        FOCUS_PROJECT_FLAG = FOCUS_PROJECT_FLAG_IMPORT,
        OPPORTUNITY_CHANNEL = OPPORTUNITY_CHANNEL_IMPORT,
        SOCKET_COMMENT = SOCKET_COMMENT_IMPORT,
        ITEM_NUMBER = ITEM_NUMBER_IMPORT,
        PL = PL_IMPORT,
        HFG = HFG_IMPORT ,
        RFP_SP_NAME = RFP_SP_NAME_IMPORT ,
        CY_PART_FAMILY = CY_PART_FAMILY_IMPORT ,
        CY_PART_NAME = CY_PART_NAME_IMPORT ,
        MAIN_CUSTOMER = endCustomer ,
        DC_CUSTOMER = DC_CUSTOMER_IMPORT ,
        PRODUCT_DESCRIPTION = PRODUCT_DESCRIPTION_IMPORT ,
        COMMENT_SALES_I = COMMENT_SALES_I_IMPORT ,
        SOCKET_COMPETITOR = SOCKET_COMPETITOR_IMPORT ,
        CREATION_DAY = CREATION_DAY_IMPORT ,
        PRODUCT_STATUS = PRODUCT_STATUS_IMPORT ,
        SOCKET_STATUS = SOCKET_STATUS_IMPORT ,
        DESIGN_WIN_CLAIM_STATUS = DESIGN_WIN_CLAIM_STATUS_IMPORT ,
        OPPORTUNITY_REASON = OPPORTUNITY_REASON_IMPORT ,
        DESIGN_LOSS_DAY = DESIGN_LOSS_DAY_IMPORT ,
        LOST_REASON_DESCRIPTION = LOST_REASON_DESCRIPTION_IMPORT ,
        SALES_FLAG = SALES_FLAG_IMPORT ,
        IFX_RESPONSIBLE = IFX_RESPONSIBLE_IMPORT ,
        DESIGN_WIN_EXP_MONTH = DESIGN_WIN_EXP_MONTH_IMPORT ,

        TRAFFIC_LIGHT = TRAFFIC_LIGHT_IMPORT ,
        TRAFFIC_LIGHT_COMMENT = TRAFFIC_LIGHT_COMMENT_IMPORT ,
        APPROVER_1 = APPROVER_1_IMPORT ,
        APPROVER_2 = APPROVER_2_IMPORT ,
        DW_APPR_FIN_YEAR = DW_APPR_FIN_YEAR_IMPORT ,
        DW_APPR_FIN_QUARTER = DW_APPR_FIN_QUARTER_IMPORT ,
        DW_APPR_FIN_MONTH = DW_APPR_FIN_MONTH_IMPORT ,
        DW_APPR_FIN_DAY = DW_APPR_FIN_DAY_IMPORT ,
        BUSINESS_WIN_MONTH = BUSINESS_WIN_MONTH_IMPORT ,
        MAIN_CUSTOMER_NUMBER = MAIN_CUSTOMER_NUMBER_IMPORT ,
        DW_POT_UW_USD = DW_POT_UW_USD_IMPORT ,
        DW_ACHIEVE_USD = DW_ACHIEVE_USD_IMPORT ,
        PLANNED_REV_UW_USD = PLANNED_REV_UW_USD_IMPORT ,
        Item_Internal_Device = Item_Internal_Device_IMPORT ,
        Product = Product_IMPORT
        )

    """

    """
    #### section A
    run sales opportunities batch import
    * functional key is product + main + end customer.
    * if key already available, update the dragon transaction id and mark as updated
    * if key not available, create a new sales opportunity
    * if integrity errors on dragon side, create entries in the conflict table regarding dragon

    #### section B
    run sales opportunities match to projects
    * if match of functional key, assign
    * if orphan from sales opportunity side, create a project draft and insert into ErrorTypesSalesOpportunities
    * if orphan from project side, create a warning / mark as not available in dragon

    """

    ################ section A
    """
    truncate the errors table first
    tbd if some kind of versioning here. evtl dump to a csv the errors table before truncating as some kind of log.
    """
    dragonObjects = Dragon.objects.all()
    allErrorObj = ErrorTypesSalesOpportunities.objects.all()

    ### truncate the  SalesOpportunitiesConflicts table (tbd if use a batch job identifier instead...)

    if len(dragonObjects) > 0:
        for dragonObject in dragonObjects:
            finalCustomerName = dragonObject.END_CUSTOMER
            mainCustomerName = dragonObject.MAIN_CUSTOMER
            salesNameInput = dragonObject.RFP_SP_NAME
            mainCustomer = None
            finalCustomer = None
            salesName = None
            errorTypes: MutableSequence[ErrorTypesSalesOpportunitesValidation] = []

            try:
                finalCustomer = FinalCustomers.objects.get(
                    finalCustomerName=finalCustomerName
                )
            except:
                print("could not get an endcustomer", dragonObject)
                errorTypes.append(
                    ErrorTypesSalesOpportunitesValidation.endCustomerMissing
                )

            try:
                mainCustomer = MainCustomers.objects.get(
                    customerName=mainCustomerName
                )
            except:
                print("could not get a main customer", dragonObject)
                errorTypes.append(
                    ErrorTypesSalesOpportunitesValidation.mainCustomerMissing
                )

            try:
                salesName = SalesName.objects.get(name=salesNameInput, dummy=False, valid=True)
                print("got salesname", salesNameInput)
            except:
                print("could not get a matching sales name", dragonObject, salesNameInput)
                errorTypes.append(
                    ErrorTypesSalesOpportunitesValidation.salesNameMissing
                )

            """"
            if on error, sales opportunity not be created, but an entry of the conflicts table.
            the import will update existing entries of sales opportunites.
            """
            print("&&& trying to match project to sales opp", salesName, mainCustomer, finalCustomer)
            print("%%% inputs", mainCustomerName, finalCustomerName, salesName)

            if (
                (mainCustomer != None)
                and (finalCustomer != None)
                and (salesName != None)
            ):

                """
                Req. 99: if the salesOpportunity metadata has been updated, the projects related to the sales opportunity should get a warning
                """
                salesOpportunity, created = SalesOpportunities.objects.get_or_create(
                    mainCustomer=mainCustomer,
                    endCustomer=finalCustomer,
                    salesName=salesName,
                )
                salesOpportunity.dragonOpportunity = dragonObject
                salesOpportunity.save()                    

            else:
                for error in errorTypes:

                    errorObj = allErrorObj.get(errorType=error.value)

                    print("--> ERROR: creating entry of  opportunity conflict", dragonObject, error.value, error)
                    SalesOpportunitiesConflicts.objects.get_or_create(
                        dragonOpportunity=dragonObject, errorType=errorObj
                    )

    df1 = pd.DataFrame(list(SalesOpportunitiesConflicts.objects.all().values()))
    filename1 = date + "_SalesOpportunitiesConflicts.csv"
    path1 = "./persistentLayer/logs/" + filename1
    #df1.to_csv(path1, mode="a", sep=";", decimal=",", header=False)
    df1.to_csv(path1, mode="a", sep=";", decimal=",", header=False)

    df1Bak = pd.DataFrame.from_records(
        SalesOpportunitiesConflicts.objects.all().values(
            "id",
            "dragonOpportunity",  # <-- get the name through the foreign key
            "dragonOpportunity__TRANSACTION_NUMBER",
            "dragonOpportunity__OPPORTUNITY_DESCRIPTION",
            "dragonOpportunity__MAIN_CUSTOMER",
            "dragonOpportunity__END_CUSTOMER",
            "dragonOpportunity__RFP_SP_NAME",
            "errorType__errorType",
            "errorType__errorDescription",
        )
    ).rename(
        columns={
            "id": "BoUp Tool ID",
            "dragonOpportunity": "BoUp Tool technical Dragon ID",
            "dragonOpportunity": "Dragon ID",
        }
    )
    # very important, reset the status
    SalesOpportunitiesConflicts.objects.all().delete()

    """
    now, for the existing sales opportunites, check if
    * project existing
    and for the existing projects, check if
    * sales opportunity exists
    """
    ############ section B
    salesOpportunities = SalesOpportunities.objects.all()
    projects = Project.objects.all()
    ### truncate the  ProjectsToSalesOpportunitiesConflicts table (tbd if use a batch job identifier instead...)

    ProjectsToSalesOpportunitiesConflicts.objects.all().delete()
    dragonRelatedToDoItems = ToDoItems.objects.filter(source="dragon")
    dragonRelatedToDoItemsBulkCreateArray = []
    dragonRelatedToDoItemsBulkUpdateArray = []

    for salesOpportunity in salesOpportunities:
        errorTypes: MutableSequence[ErrorTypesSalesOpportunitesValidation] = []
        mainCustomer = salesOpportunity.mainCustomer
        endCustomer = salesOpportunity.finalCustomer
        salesName = salesOpportunity.salesName

        projects = Project.objects.filter(
            mainCustomer=mainCustomer, finalCustomer=endCustomer, sales_name=salesName
        )

        if projects.count() == 0:
            errorTypes.append(ErrorTypesSalesOpportunitesValidation.projectNotFound)

        ### depending on the crosschecks we implement, this could scale up to any kind of conflicts we think about
        errorObj = allErrorObj.get(errorType=errorType.value)

        # if there are no projects matching this sales opportunity, this will not be run
        for project in projects:
            for errorType in errorTypes:
                ProjectsToSalesOpportunitiesConflicts.objects.get_or_create(
                    project=project, errorType=errorObj
                )
            
            #print("$$$$ salesOpportunity", salesOpportunity.dragonOpportunity, "drgop", dragonOpportunitiesIdsThatChanged)
            # if the respective dragon opportunity has been modified, add a to do item for the marketer
            if salesOpportunity.dragonOpportunity in dragonOpportunitiesIdsThatChanged:
                changeItem = dragonOpportunitiesThatChanged.get(dragonObjId=salesOpportunity.dragonOpportunity.id)
                changes = changeItem["changes"]
                changeString = ""
                for change in changes:
                    changeString = changeString + str(change.value) + ","

                newToDoItem = ToDoItems(project=project,source="dragon",dragonCodes= changeString, description="Dragon Opportunity changed.")
                dragonRelatedToDoItemsBulkCreateArray.append(newToDoItem)
                print("---> creating to do item")

    newly_created_todoItems = ToDoItems.objects.bulk_create(
        dragonRelatedToDoItemsBulkCreateArray, batch_size=1000
    )

    for project in projects:
        errorTypes: MutableSequence[ErrorTypesSalesOpportunitesValidation] = []
        mainCustomer = project.mainCustomer
        endCustomer = project.finalCustomer
        salesName = project.sales_name

        matchingSalesOpportunities = SalesOpportunities.objects.filter(
            mainCustomer=mainCustomer, finalCustomer=endCustomer, salesName=salesName
        )

        salesOpportunity = None
        if matchingSalesOpportunities.count() > 1:
            errorTypes.append(
                ErrorTypesSalesOpportunitesValidation.multipleMatchingSalesOpportunities
            )
        elif matchingSalesOpportunities.count() == 0:
            errorTypes.append(
                ErrorTypesSalesOpportunitesValidation.salesOpportunityNotFound
            )
        else:
            salesOpportunity = matchingSalesOpportunities.first()

        ### depending on the crosschecks we implement, this could scale up to any kind of conflicts we think about
        for errorType in errorTypes:
            errorObj = allErrorObj.get(errorType=errorType.value)
            ProjectsToSalesOpportunitiesConflicts.objects.get_or_create(
                project=project, errorType=errorObj
            )

    df = pd.DataFrame(
        list(ProjectsToSalesOpportunitiesConflicts.objects.all().values())
    )

    filename2 = date + "_ProjectsToSalesOpportunitiesConflicts.csv"
    path2 = "./persistentLayer/logs/" + filename2

    df.to_csv(path2, mode="a", sep=";", decimal=",", header=False)

    """
    now bulk update Project level errors if no sales opportunity found
    """
    allProjectErrors = ProjectError.objects.all()
    projectErrorsUpdate = []
    projectErrorsCreate = []

    allProjectErrorsProjectIds = allProjectErrors.values_list(
                    "project", flat=True
                ).order_by("project")

    allProjectsToSalesOpportunitiesConflicts = ProjectsToSalesOpportunitiesConflicts.objects.all()

    for project in projects:
        print("%% checking", project)
        projectLevelErrors = ""

        thisProjectsErrors = allProjectsToSalesOpportunitiesConflicts.filter(project=project)

        if thisProjectsErrors.count() > 0:
            for object in thisProjectsErrors:
                if object.errorType.errorType == 4:
                    projectLevelErrors = projectLevelErrors + ",26"
                elif object.errorType.errorType == 6:
                    projectLevelErrors = projectLevelErrors + ",27"

        if len(projectLevelErrors) > 0:
            # if project has no error, create a new error entry. else retrieve and modify accordingly.
            if project.id not in allProjectErrorsProjectIds:
                # remove leading comma first
                projectLevelErrors = projectLevelErrors[1:]
                item = ProjectError(project_id = project, error_ids=projectLevelErrors)
                projectErrorsCreate.append(item)
            else:
                print("editing project errors")
                currentProjectErrorObject = allProjectErrors.get(project=project.id)

                # check if a project 26 or 27 is stored here. if yes, check if remove 
                if "26" in currentProjectErrorObject.error_ids:
                    REPLACEMENTS = [
                    (",26,", ","),
                    (",26", ""),
                    ("26,", ""),
                    ]
                    for old, new in REPLACEMENTS:
                        currentProjectErrorObject.error_ids = currentProjectErrorObject.error_ids.replace(old, new)

                if "27" in currentProjectErrorObject.error_ids:
                    REPLACEMENTS = [
                    (",27,", ","),
                    (",27", ""),
                    ("27,", ""),
                    ]
                    for old, new in REPLACEMENTS:
                        currentProjectErrorObject.error_ids = currentProjectErrorObject.error_ids.replace(old, new)

                currentProjectErrorObject.error_ids = currentProjectErrorObject.error_ids + projectLevelErrors
                projectErrorsUpdate.append(currentProjectErrorObject)

    ProjectError.objects.bulk_update(
        projectErrorsUpdate, ["project", "error_ids"], batch_size=1000
    )

    newly_created_projectErrors = ProjectError.objects.bulk_create(
        projectErrorsCreate, batch_size=1000
    )

    return True, df1Bak
