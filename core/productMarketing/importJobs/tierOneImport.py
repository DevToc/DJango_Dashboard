import pandas as pd
from .mainCustomer import *
from .vhkl import *
from .salesNames import *
from ..models import *

# tierOnes


def runTierOneImport():
    df1 = pd.read_csv(
        # "./persistentLayer/importJobs/tierOneList.csv", sep=";", decimal=","
        "./persistentLayer/importJobs/customerList.csv", sep=";", decimal=","

    )
    length = len(df1.index)
    index = 0
    for i in range(0, length, 1):

        tierOneInput = df1.loc[i, "tierOneName"]
        tierOne = Tier1.objects.filter(tierOneName=tierOneInput)

        print("inputs", tierOneInput, "tierOne", tierOne)
        if tierOne.count() > 0:
            print("found more than 0 tierOnes!")

            # what with sales name daisy chain wafer?

            if tierOne.count() == 1:

                tierOneObj, created = Tier1.objects.get_or_create(
                    tierOneName=tierOneInput
                )
                if created == True:
                    print(index, "created t1", tierOneObj)
                else:
                    print(index, "retrieved t1", tierOneObj)

            else:
                # tbd
                print("found more than one matching tier one!!!")
                # either warning, automated email and then manual import or call support

        else:
            print("tierOne did not exist! creating")
            tierOneObj, created = Tier1.objects.get_or_create(
                tierOneName=tierOneInput)
            if created == True:
                print(index, "created t1", tierOneObj)
            else:
                print(index, "retrieved t1", tierOneObj)

    return True
