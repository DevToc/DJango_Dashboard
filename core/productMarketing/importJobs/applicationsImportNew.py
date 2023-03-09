"""
import application main, application detail, applicationLines, and SBUs

class ApplicationMain(models.Model):
    appMainDescription = models.CharField(max_length=40, blank=True, null=True)

class ApplicationDetail(models.Model):
    appDetailDescription = models.CharField(max_length=40, blank=True, null=True)
    appMain = models.ForeignKey(
        ApplicationMain, on_delete=models.PROTECT, blank=True, null=True
    )

class StrategicBusinessUnits(models.Model):
    businessUnitName = models.CharField(max_length=40, blank=True, null=True)
    appMain = models.ForeignKey(
        ApplicationMain, on_delete=models.PROTECT, blank=True, null=True
    )
"""
from core.project.models import ApplicationDetail, ApplicationLine, ApplicationMain, StrategicBusinessUnits
import pandas as pd

def runApplicationsImport():
    df1 = pd.read_csv(
        "./persistentLayer/importJobs/applicationsFinal.csv", sep=";", decimal=",")
    length = len(df1.index)
    index = 0
    print("### appMainDetailSbu input")
    print(df1)
    print("####")

    allApplicationsMain = ApplicationMain.objects.all()
    allApplicationsDetail = ApplicationDetail.objects.all()
    allSbus = StrategicBusinessUnits.objects.all()
    allApplicationLines = ApplicationLine.objects.all()

    for i in range(0, length, 1):
        sbuInput = df1.loc[i, "SBU"]
        sbu, created = StrategicBusinessUnits.objects.get_or_create(
            businessUnitName = sbuInput
        )

        applicationLineInput = df1.loc[i, "AL"]
        applicationLine, created = ApplicationLine.objects.get_or_create(
            applicationLineShortName = applicationLineInput
        )


    for i in range(0, length, 1):
        appMainInput = df1.loc[i, "Application Main"]
        appDetailInput = df1.loc[i, "Application Detail"]
        sbuInput = df1.loc[i, "SBU"]
        applicationLineInput = df1.loc[i, "AL"]

        sbu, created = StrategicBusinessUnits.objects.get_or_create(
            businessUnitName = sbuInput
        )

        applicationLine = ApplicationLine.objects.get(
            applicationLineShortName = applicationLineInput
        )

        appMain, created = ApplicationMain.objects.get_or_create(
            appMainDescription=appMainInput, appLine = applicationLine)

        appDetail, created = ApplicationDetail.objects.get_or_create(
            appDetailDescription = appDetailInput,
            appMain = appMain
        )

        appMain.sbu = sbu
        #appDetail.applicationLine = applicationLine

        appDetail.save()
        appMain.save()
        print(i, "%%% processed", appMain, appDetail, sbu, applicationLine)