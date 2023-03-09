import pandas as pd
from .mainCustomer import *
from .vhkl import *
from .salesNames import *
from ..models import *

# distributors


def runDistributorsImport():
    """
    df1 = pd.read_csv(
        "./persistentLayer/importJobs/distributorsList.csv", sep=";", decimal=","
    )"""

    df1 = pd.read_csv(
        "./persistentLayer/importJobs/customerList.csv", sep=";", decimal=",")
    length = len(df1.index)
    index = 0
    for i in range(0, length, 1):

        distributorInput = df1.loc[i, "distributorName"]
        distributor = Distributors.objects.filter(
            distributorName=distributorInput)

        print("inputs", distributorInput, "distributor", distributor)
        if distributor.count() > 0:
            print("found more than 0 distributors!")

            # what with sales name daisy chain wafer?

            if distributor.count() == 1:

                distributorObj, created = Distributors.objects.get_or_create(
                    distributorName=distributorInput
                )
                if created == True:
                    print(index, "created", distributorObj)
                else:
                    print(index, "retrieved", distributorObj)

            else:
                # tbd
                print("found more than one matching customer!!!")
                # either warning, automated email and then manual import or call support

        else:
            print("distributor did not exist! creating")
            distributorObj, created = Distributors.objects.get_or_create(
                distributorName=distributorInput
            )
            if created == True:
                print(index, "created", distributorObj)
            else:
                print(index, "retrieved", distributorObj)

    return True
