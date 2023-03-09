from config import celery_app

from .models import Uploading
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.urls import reverse_lazy, reverse
from core.project.models import (
    Product,
    SalesName,
    ProductFamily,
    ProductPackage,
    ProductSeries,
)
from .forms import ImportForm
from enum import Enum
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.db.models import F
from django.utils import timezone
from datetime import datetime
from rest_framework import status
from django.db import connection
from django.core.files.storage import FileSystemStorage
from productMarketing.BoUpExport import protectCellsInExcel, excelExport
from core.project.models import marketerMetadata
from django.http import FileResponse
from django.contrib import messages
from core.project.bulkProcessing import entryPointValidator
import pandas as pd
import mimetypes
from django.contrib.auth.decorators import login_required
from productMarketing.importJobs.vrfcImport import importVrfcOohCsv
from productMarketing.importJobs.productImport import adolfRun
from productMarketing.importJobs.Dragon import runDragonImport
from core.project.helperFunctions import (
    missingVhkReport,
    vrfcFileExportOoh,
    vrfcFileExportSfc,
    vrfcFileExportSfc,
    productMasterDataFile,
    boupDeltasToOrdersReport,
    ordersWithNoProjectReport,
    projectsWithNoOrderReport,
)


@celery_app.task()
def upload_file(request):
    print("File UPload Begin ... \n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    try:
        success_url = reverse_lazy("import_export_main")
        responseDict = {"url": success_url, "outputFile": ""}

        inputFile = request.FILES["file"]
        fs = FileSystemStorage()
        filename = fs.save(inputFile.name, inputFile)
        uploaded_file_url = fs.url(filename)
        print("--------> saved file to:", uploaded_file_url)

        """
        if data consistency check, perform
        """
        exportType = request.POST["fileType"]
        print("retrieved file successfully!!!", exportType, filename)
        marketer = marketerMetadata.objects.get(user=request.user)
        runDate = datetime.today().strftime("%Y-%m-%d")

        if exportType == "dataConsistencyPse":
            print("here consistency checks")

            validationErrors, outputDf, dtoArray = entryPointValidator(
                fileName=inputFile.name,
                excelFilePath=uploaded_file_url,
                mode=0,
                creationDesired=False,
                helperQuerySets=None,
            )

            fileName = (
                str(marketer.familyName) + "_" + str(runDate) + "_boupEvaluation.xlsx"
            )
            filePath = "./persistentLayer/temp/" + fileName
            excelFile = outputDf.to_excel(filePath)

            messages.success(request, "File was uploaded successfully!")
            print("done")

            """
            with open("./output.xlsx", "rb") as excel:
                data = excel.read()
                response = HttpResponse(
                    data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'attachment; filename=%s_Report.xlsx' % 'example.xls'
            """
            print("responseeeee")
            responseDict = {"url": success_url, "outputFile": fileName}
            print("responseeeee2", filePath)

            return JsonResponse(responseDict, status=200)

        elif exportType == "reportToElke":
            if (uploaded_file_url[-3:] != "csv") & (uploaded_file_url[-4:] != "xlsx"):
                errorMessage = "Upload failed! Migration Data upload only accepts CSV with ; as a separator or an XLSX file!"
                messages.error(request, errorMessage)
                context = {
                    "form": self.form_class(),
                    "successMessage": errorMessage,
                }
                return render(request, self.template_name, context)

            from project.bulkProcessing import ProjectBulkCreator

            bulkCreator = ProjectBulkCreator()
            fileName = inputFile.name
            uploadSuccess, outputDf = bulkCreator.bulkCreatorEntryPoint(
                fileName=fileName,
                excelFilePath=uploaded_file_url,
                mode=2,
                request=request,
            )

            if uploadSuccess == True:
                fileName = (
                    str(marketer.familyName)
                    + "_"
                    + str(runDate)
                    + "_boupEvaluation.xlsx"
                )
                filePath = "./persistentLayer/temp/" + fileName
                excelFile = outputDf.to_excel(filePath)
                messages.success(request, "File was uploaded successfully!")
                print("done")
                responseDict = {"url": success_url, "outputFile": fileName}
                print("responseeeee2", filePath)
                return JsonResponse(responseDict, status=200)

            else:
                fileName = (
                    str(marketer.familyName)
                    + "_"
                    + str(runDate)
                    + "_boupEvaluation.xlsx"
                )
                filePath = "./persistentLayer/temp/" + fileName
                excelFile = outputDf.to_excel(filePath)
                messages.error(
                    request,
                    "An error happened during upload! Please check the attached error report!",
                )
                print("done")
                responseDict = {"url": success_url, "outputFile": fileName}
                print("responseeeee2", filePath)
                return JsonResponse(responseDict, status=200)

        elif exportType == "migrationPse":
            if (uploaded_file_url[-3:] != "csv") & (uploaded_file_url[-4:] != "xlsx"):
                errorMessage = "Upload failed! Migration Data upload only accepts CSV with ; as a separator or an XLSX file!"
                messages.error(request, errorMessage)
                context = {
                    "form": self.form_class(),
                    "successMessage": errorMessage,
                }
                return render(request, self.template_name, context)

            from project.bulkProcessing import ProjectBulkCreator

            bulkCreator = ProjectBulkCreator()
            fileName = inputFile.name
            uploadSuccess, outputDf = bulkCreator.bulkCreatorEntryPoint(
                fileName=fileName,
                excelFilePath=uploaded_file_url,
                mode=2,
                request=request,
            )

            if uploadSuccess == True:
                fileName = (
                    str(marketer.familyName)
                    + "_"
                    + str(runDate)
                    + "_boupEvaluation.xlsx"
                )
                filePath = "./persistentLayer/temp/" + fileName
                excelFile = outputDf.to_excel(filePath)
                messages.success(request, "File was uploaded successfully!")
                print("done")
                responseDict = {"url": success_url, "outputFile": fileName}
                print("responseeeee2", filePath)
                return JsonResponse(responseDict, status=200)

            else:
                fileName = (
                    str(marketer.familyName)
                    + "_"
                    + str(runDate)
                    + "_boupEvaluation.xlsx"
                )
                filePath = "./persistentLayer/temp/" + fileName
                excelFile = outputDf.to_excel(filePath)
                messages.error(
                    request,
                    "An error happened during upload! Please check the attached error report!",
                )
                print("done")
                responseDict = {"url": success_url, "outputFile": fileName}
                print("responseeeee2", filePath)
                return JsonResponse(responseDict, status=200)

        elif exportType == "dragon":
            if (uploaded_file_url[-3:] != "csv") & (uploaded_file_url[-4:] != "xlsx"):
                errorMessage = "Upload failed! VRFC upload only accepts CSV with ; as a separator or a XLSX file!"
                messages.error(request, errorMessage)
                context = {
                    "form": self.form_class(),
                    "successMessage": errorMessage,
                }
                return render(request, self.template_name, context)

            success, outputDf = runDragonImport(True, uploaded_file_url)
            successMessage = "Upload successfull! Dragon data was updated!"
            messages.success(request, successMessage)

            fileName = (
                str(marketer.familyName) + "_" + str(runDate) + "_dragonEvaluation.csv"
            )
            filePath = "./persistentLayer/temp/" + fileName
            # excelFile = outputDf.to_excel(filePath)
            excelFile = outputDf.to_csv(filePath, sep=";", decimal=",", header=True)
            messages.success(request, "File was uploaded successfully!")
            print("done")
            responseDict = {"url": success_url, "outputFile": fileName}
            print("dragon import finished", filePath)
            return JsonResponse(responseDict, status=200)

        elif exportType == "vrfc":

            if (uploaded_file_url[-3:] != "csv") & (uploaded_file_url[-4:] != "xlsx"):

                errorMessage = "Upload failed! VRFC upload only accepts CSV with ; as a separator or a XLSX file!"
                messages.error(request, errorMessage)
                context = {
                    "form": self.form_class(),
                    "successMessage": errorMessage,
                }
                return render(request, self.template_name, context)

            # run the vrfc import job
            outputDf = importVrfcOohCsv(fileUpload=True, uploadPath=uploaded_file_url)
            successMessage = "Upload successfull! VRFC data was updated!"
            messages.success(request, successMessage)
            context = {"form": self.form_class(), "successMessage": successMessage}

            outputFile = (
                str(marketer.familyName)
                + "_"
                + str(runDate)
                + "_vrfcImportEvaluation.xlsx"
            )
            filePath = "./persistentLayer/temp/" + outputFile
            return JsonResponse(responseDict, status=200)

            excelFile = outputDf.to_excel(filePath)

            responseDict = {"url": success_url, "outputFile": outputFile}
            print("&&&&&&&&&&&&&& VRFC processing successfull")
            return JsonResponse(responseDict, status=200)

        elif exportType == "pmdf":

            if (uploaded_file_url[-3:] != "csv") & (uploaded_file_url[-4:] != "xlsx"):

                errorMessage = "Upload failed! Product Master Data upload only accepts CSV with ; as a separator or a XLSX file!"
                messages.error(request, errorMessage)
                context = {
                    "form": self.form_class(),
                    "successMessage": errorMessage,
                }
                return render(request, self.template_name, context)
            print("starting adolf run")
            # run the adolf run import job
            uploadSuccess = adolfRun(fileUpload=True, uploadPath=uploaded_file_url)
            successMessage = "Upload successfull! Product Master Data was updated!"
            messages.success(request, successMessage)
            context = {"form": self.form_class(), "successMessage": successMessage}

            responseDict = {"url": success_url, "outputFile": ""}
            print("&&&&&&&&&&&&&& PMDF processing successfull")
            return JsonResponse(responseDict, status=200)

        elif exportType == "boupTemplate":
            if (uploaded_file_url[-3:] != "csv") & (uploaded_file_url[-4:] != "xlsx"):
                errorMessage = "Upload failed! Product Master Data upload only accepts CSV with ; as a separator or a XLSX file!"
                messages.error(request, errorMessage)
                context = {
                    "form": self.form_class(),
                    "successMessage": errorMessage,
                }
                return render(request, self.template_name, context)

            from project.bulkProcessing import ProjectBulkCreator

            bulkCreator = ProjectBulkCreator()
            fileName = inputFile.name
            print(
                "using args 1",
                fileName,
                "type",
                type(fileName),
                "len",
                len(fileName),
            )

            uploadSuccess, outputDf = bulkCreator.bulkCreatorEntryPoint(
                fileName=fileName,
                excelFilePath=uploaded_file_url,
                mode=1,
                request=request,
            )

            if uploadSuccess == True:
                fileName = (
                    str(marketer.familyName)
                    + "_"
                    + str(runDate)
                    + "_boupEvaluation.xlsx"
                )
                filePath = "./persistentLayer/temp/" + fileName
                excelFile = outputDf.to_excel(filePath)
                messages.success(request, "File was uploaded successfully!")
                print("done")
                responseDict = {"url": success_url, "outputFile": fileName}
                print("responseeeee2", filePath)
                return JsonResponse(responseDict, status=200)

            else:
                fileName = (
                    str(marketer.familyName)
                    + "_"
                    + str(runDate)
                    + "_boupEvaluation.xlsx"
                )
                filePath = "./persistentLayer/temp/" + fileName
                excelFile = outputDf.to_excel(filePath)
                messages.error(
                    request,
                    "An error happened during upload! Please check the attached error report!",
                )
                print("done")
                responseDict = {"url": success_url, "outputFile": fileName}
                print("responseeeee2", filePath)
                return JsonResponse(responseDict, status=200)

        else:
            pass

    except:

        # try:
        # print("request post", request.POST)
        exportType = request.POST["fileTypeExport"]
        print("file is empty / trying with download", exportType)

        if exportType == "notSelected":
            messages.error(request, "Please select an option!")
            context = {"form": self.form_class(request.POST, request.FILES)}
            return render(request, self.template_name, context)
        else:
            # prepare the file accordingly
            excelFile = None
            marketer = marketerMetadata.objects.get(user=request.user)

            if exportType == "boupTemplateAllProjects":
                excelFile = protectCellsInExcel("all", None, marketer.id)
            elif exportType == "boupTemplateMyTeamProjects":
                excelFile = protectCellsInExcel("myTeam", None, marketer.id)
            elif exportType == "missingVhkReports":
                excelFile = missingVhkReport(marketer)
            elif exportType == "vrfcOoh":
                excelFile = vrfcFileExportOoh(marketer)
            elif exportType == "vrfcSfc":
                excelFile = vrfcFileExportSfc(marketer)
            elif exportType == "pmdf":
                excelFile = productMasterDataFile(marketer)
            elif exportType == "vrfcOohDeltas":
                excelFile, dataFrame = boupDeltasToOrdersReport(marketer)
            elif exportType == "ordersWithNoProjectReport":
                excelFile, dataFrame = ordersWithNoProjectReport(marketer)
            elif exportType == "projectsWithNoOrdersReport":
                excelFile, dataFrame = projectsWithNoOrderReport(marketer)
            else:
                excelFile = protectCellsInExcel("myProjects", None, marketer.id)
            print("preparing file for download")

            response = FileResponse(open(excelFile, "rb"))
            return response
