import pandas as pd
from .mainCustomer import *
from .vhkl import *
from .salesNames import *
from ..models import *

# vpaCustomers


def runVpaCustomerImport():
    df1 = pd.read_csv(
        # "./persistentLayer/importJobs/vpaCustomerList.csv", sep=";", decimal=","
        "./persistentLayer/importJobs/customerList.csv", sep=";", decimal=","

    )
    length = len(df1.index)
    index = 0
    for i in range(0, length, 1):

        vpaCustomerInput = df1.loc[i, "vpaCustomerName"]
        vpaCustomer = VPACustomers.objects.filter(
            customerName=vpaCustomerInput)

        print("inputs", vpaCustomerInput, "vpaCustomer", vpaCustomer)
        if vpaCustomer.count() > 0:
            print("found more than 0 vpaCustomers!")

            # what with sales name daisy chain wafer?

            if vpaCustomer.count() == 1:

                vpaCustomerObj, created = VPACustomers.objects.get_or_create(
                    customerName=vpaCustomerInput
                )
                if created == True:
                    print(index, "created t1", vpaCustomerObj)
                else:
                    print(index, "retrieved t1", vpaCustomerObj)

            else:
                # tbd
                print("found more than one matching tier one!!!")
                # either warning, automated email and then manual import or call support

        else:
            print("vpaCustomer did not exist! creating")
            vpaCustomerObj, created = VPACustomers.objects.get_or_create(
                customerName=vpaCustomerInput)
            if created == True:
                print(index, "created t1", vpaCustomerObj)
            else:
                print(index, "retrieved t1", vpaCustomerObj)

    return True
