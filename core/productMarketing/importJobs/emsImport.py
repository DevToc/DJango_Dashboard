import pandas as pd
from .mainCustomer import *
from .vhkl import *
from .salesNames import *
from ..models import *


# ems
def runEmsImport():
    #df1 = pd.read_csv("./persistentLayer/importJobs/emsList.csv", sep=";", decimal=",")
    df1 = pd.read_csv(
        "./persistentLayer/importJobs/customerList.csv", sep=";", decimal=",")

    length = len(df1.index)
    index = 0
    print("### input")
    print(df1)
    print("####")
    for i in range(0, length, 1):

        emsInput = df1.loc[i, "emsName"]
        ems = EMS.objects.filter(emsName=emsInput)

        print("inputs", emsInput, "products", ems)
        if ems.count() > 0:
            print("found more than 0 rps!")

            if ems.count() == 1:

                emsObj, created = EMS.objects.get_or_create(emsName=emsInput)
                if created == True:
                    print(index, "created", emsObj)
                else:
                    print(index, "retrieved", emsObj)

            else:
                # tbd
                print("found more than one matching customer!!!")
                # either warning, automated email and then manual import or call support

        else:
            print("ems did not exist! creating")
            emsObj, created = EMS.objects.get_or_create(emsName=emsInput)
            if created == True:
                print(index, "created", emsObj)
            else:
                print(index, "retrieved", emsObj)

    return True
