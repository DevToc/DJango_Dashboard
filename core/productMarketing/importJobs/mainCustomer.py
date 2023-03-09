# Francisco Falise, copyright 01/10/2022
# for each row get the rfp of the salesname, lookup in the Product.rfp table. if exist, set as foreign key and save salesname.
# if no rfp exist, create the rfp. then generate the respective entry

import pandas as pd
from ..models import *


def runMainCustomerImport():
    df1 = pd.read_csv(
        "./persistentLayer/importJobs/customerList.csv", sep=";", decimal=","
    )
    length = len(df1.index)
    index = 0
    print("### input main customers")
    print(df1)
    print("####")
    for i in range(0, length, 1):

        mainCustomerInput = df1.loc[i, "customerName"]
        mainCustomer = MainCustomers.objects.filter(customerName=mainCustomerInput)

        print("inputs", mainCustomerInput, "products", mainCustomer)
        if mainCustomer.count() > 0:
            print("found more than 0 mainCustomer!")

            ## what with sales name daisy chain wafer?

            if mainCustomer.count() == 1:

                customerObj, created = MainCustomers.objects.get_or_create(
                    customerName=mainCustomerInput
                )
                if created == True:
                    print(index, "created", customerObj)
                else:
                    print(index, "retrieved", customerObj)

            else:
                # tbd
                print("found more than one matching mainCustomer!!!")
                ## either warning, automated email and then manual import or call support

        else:
            print("mainCustomer did not exist! creating")
            customerObj, created = MainCustomers.objects.get_or_create(
                customerName=mainCustomerInput
            )
            if created == True:
                print(index, "created", customerObj)
            else:
                print(index, "retrieved", customerObj)

    #### hard coded "multiple" customer
    multipleCustomers = "Multiple"
    mainCustomer = MainCustomers.objects.filter(customerName=multipleCustomers)
    print("inputs", mainCustomerInput, "products", mainCustomer)

    if mainCustomer.count() > 0:
        print("found more than 0 mainCustomer!")

        ## what with sales name daisy chain wafer?

        if mainCustomer.count() == 1:

            customerObj, created = MainCustomers.objects.get_or_create(
                customerName=multipleCustomers
            )
            if created == True:
                print(index, "created multipleCustomers", customerObj)
            else:
                print(index, "retrieved multipleCustomers", customerObj)

        else:
            # tbd
            print("found more than one matching customer for multipleCustomers!!!")
            ## either warning, automated email and then manual import or call support

    else:
        print("customer did not exist! creating")
        customerObj, created = MainCustomers.objects.get_or_create(
            customerName=multipleCustomers
        )
        if created == True:
            print(index, "created multipleCustomers", customerObj)
        else:
            print(index, "retrieved multipleCustomers", customerObj)

    return True


def runFinalCustomerImport():
    df1 = pd.read_csv(
        "./persistentLayer/importJobs/customerList.csv", sep=";", decimal=","
    )
    length = len(df1.index)
    index = 0
    print("### input")
    print(df1)
    print("####")
    for i in range(0, length, 1):

        mainCustomerInput = df1.loc[i, "customerName"]
        mainCustomer = FinalCustomers.objects.filter(
            finalCustomerName=mainCustomerInput
        )

        print("inputs", mainCustomerInput, "products", mainCustomer)
        if mainCustomer.count() > 0:
            print("found more than 0 main customer for final cust!")

            ## what with sales name daisy chain wafer?

            if mainCustomer.count() == 1:

                customerObj, created = FinalCustomers.objects.get_or_create(
                    finalCustomerName=mainCustomerInput
                )
                if created == True:
                    print(index, "created final cust", customerObj)
                else:
                    print(index, "retrieved final cust", customerObj)

            else:
                # tbd
                print("found more than one matching customer!!!")
                ## either warning, automated email and then manual import or call support

        else:
            print("customer did not exist! creating")
            customerObj, created = FinalCustomers.objects.get_or_create(
                finalCustomerName=mainCustomerInput
            )
            if created == True:
                print(index, "created final cust", customerObj)
            else:
                print(index, "retrieved final cust", customerObj)

    #### hard coded "multiple" customer
    multipleCustomers = "Multiple"
    mainCustomer = FinalCustomers.objects.filter(finalCustomerName=multipleCustomers)
    print("inputs", mainCustomerInput, "products", mainCustomer)

    if mainCustomer.count() > 0:
        print("found more than 0 maincusts for final custs!")

        ## what with sales name daisy chain wafer?

        if mainCustomer.count() == 1:

            customerObj, created = FinalCustomers.objects.get_or_create(
                finalCustomerName=multipleCustomers
            )
            if created == True:
                print(index, "created multipleCustomers for final cust", customerObj)
            else:
                print(index, "retrieved multipleCustomers for final cust", customerObj)

        else:
            # tbd
            print("found more than one matching customer for multipleCustomers!!!")
            ## either warning, automated email and then manual import or call support

    else:
        print("customer did not exist! creating")
        customerObj, created = FinalCustomers.objects.get_or_create(
            finalCustomerName=multipleCustomers
        )
        if created == True:
            print(index, "created multipleCustomers", customerObj)
        else:
            print(index, "retrieved multipleCustomers", customerObj)

    return True


def runFinalCustomerImportWorkaround():
    # FinalCustomers.objects.all().delete()
    FinalCustomersObjs = FinalCustomers.objects.all()
    avnet = MainCustomers.objects.get(customerName="AVNET")

    for customer in FinalCustomersObjs:
        customer.mainCust = avnet
        customer.save()

    return True
