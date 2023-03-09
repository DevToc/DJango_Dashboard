from django.http import JsonResponse, HttpResponseRedirect
from datetime import date, timedelta
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404, redirect
from .serializers import *
from django.contrib.auth.decorators import login_required
import pandas as pd
import csv
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.core import serializers
from django.urls import reverse_lazy
from core.project.helperFunctions import *
from productMarketingDwh.models import BoUp
from datetime import datetime
from django.contrib.auth.decorators import login_required
import mimetypes
from .models import SnapshotMetaData, SnapshotTags
from .forms import CreateSnapshotForm
from django.contrib import messages


@login_required(login_url="/login/")
def snapshotDownload(request, snapshotId):

    snapshotObj = SnapshotMetaData.objects.get(id=snapshotId)
    fileName = snapshotObj.metadataFileName
    fullFilePath = "./persistentLayer/snapshotStorage/" + fileName  # + ".csv"

    # fill these variables with real values
    # fileName = filename
    filePath = fullFilePath  # "./persistentLayer/temp/" + fileName
    fl_path = filePath  # ''
    fl = open(fl_path, 'rb')
    mime_type, _ = mimetypes.guess_type(fl_path)
    response = HttpResponse(fl, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filePath
    return response


@login_required(login_url="/login/")
def snapshotDownloadFull(request, snapshotId):

    snapshotObj = SnapshotMetaData.objects.get(id=snapshotId)
    fileName = snapshotObj.fileName
    fullFilePath = "./persistentLayer/snapshotStorage/" + fileName
    filePath = fullFilePath
    fl_path = filePath  # ''
    fl = open(fl_path, 'rb')
    mime_type, _ = mimetypes.guess_type(fl_path)
    response = HttpResponse(fl, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filePath
    return response


# endpoint for loading the snapshots in the front end after the html was rendered
class getSnapshotList(generics.ListCreateAPIView):
    print("getting snapshots list")
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    ###
    serializer_class = SnapshotSerializer
    queryset = SnapshotMetaData.objects.all()
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    print("getting snapshot list", queryset)


class getSnapshotList2(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def get(self, request):
        print("getting snapshots list2")

        outputArray = []
        ###
        queryset = SnapshotMetaData.objects.filter(user=request.user)

        for snapshot in queryset:
            tempDict = dict()
            tempDict['date'] = snapshot.date
            tempDict['tag'] = snapshot.tag.tagName
            tempDict['fileName'] = snapshot.fileName
            tempDict['metadataFileName'] = snapshot.metadataFileName
            tempDict['metadataFileName'] = snapshot.snapshotComments

            outputArray.append(tempDict)
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print("getting snapshot list", outputArray)
        return JsonResponse({"data": outputArray}, safe=True)


"""
* download CSV of selected snapshot
* delete a snapshot
"""


class snapshot(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def post(self, request):
        # snapshotForm = CreateSnapshotForm(request.POST)
        # if snapshotForm.is_valid():

        # download DB

        df = pd.DataFrame(list(BoUp.objects.all().values()))
        print("%%%%%%%%%%%%%% current boup objects")
        print(df)
        print("%%% ---> END")

        filePathBase = "./persistentLayer/snapshots/"

        metadataFileName = "./persistentLayer/snapshots/asd.csv"

        snapshotNameInput = request.POST.get('snapshotNameInput')
        snapshotCommentsInput = request.POST.get('snapshotCommentsInput')

        # check if already exists
        snapshotObject, created = SnapshotMetaData.objects.filter(
            user=user, snapshotName=snapshotNameInput)

        if snapshotObject.count() > 0:
            print("return on error, snapshot name already exists")

        tagInput = request.POST.get('tagInput')
        user = request.user

        tagObj = SnapshotTags.objects.get(id=tagInput)

        snapshotObject, created = SnapshotMetaData.objects.get_or_create(
            user=user, snapshotName=snapshotNameInput, tag=tagObj, fileName=fileName, snapshotComments=snapshotCommentsInput)

        url = '/ifx/productMarketing/view_snapshot/' + str(snapshotObject.id)
        return HttpResponseRedirect(url)

    # for downloading the requested snapshot as a CSV

    def get(self, request, snapshotId):
        print("################ getting", snapshotId)

        try:
            # here logic to retrieve a snapshot from persistent storage
            snapshotObj = SnapshotMetaData.objects.get(id=snapshotId)
            fileName = snapshotObj.fileName
            fullFilePath = "./persistentLayer/snapshotStorage/" + fileName  # + ".csv"
            # to do: how to avoid loading into pandas??
            df1 = pd.read_csv(fullFilePath, sep=';', decimal=",")

            response = HttpResponse(
                content_type='text/csv',
                headers={
                    'Content-Disposition': 'attachment; filename="testsnapshot.csv"'},
            )

            # with other applicable parameters
            df1.to_csv(path_or_buf=response)
            return response

        #     df_boup = pd.DataFrame(list(BoUp.objects.filter(id = boup_id).values()))

        except:
            print("failed to fetch snapshot CSV")
            return HttpResponse(status=401)

    # for deleting the requested snapshot

    def delete(self, request, format=None):
        snapshotId = request.query_params.get('snapshotId', None)

        # here logic to delete a snapshot
        # SnapshotMetaData.objects.filter(id=snapshotId).delete()

        return HttpResponse(status=200)


"""
* open one snapshot  (open a new view showing the deepdive of the selected snapshot using an URL)
"""

# screen for snapshot list, render the html. snapshot data is retrieved from


@login_required(login_url="/login/")
def viewSnapshotList(request):
    print("###### view snapshots")
    data = "asd123"
    return render(request, "snapshots/list.html", {'data': data, })

# screen for deleting a selected snapshot, tbd if with data tables.


@login_required(login_url="/login/")
def snapshotDelete(request, snapshotId):
    print("###### snapshotDelete")

    SnapshotMetaData.objects.filter(id=snapshotId).delete()
    return HttpResponse(status=200)

# retrieve a snapshot from persistent storage and display key metrics.


@login_required(login_url="/login/")
def snapshotDeepdive(request, snapshotId):
    print("###### snapshotDeepdive")
    baseline1 = snapshotId

    snapshotObj = SnapshotMetaData.objects.get(id=snapshotId)
    fileName = snapshotObj.metadataFileName
    fullFilePath = "./persistentLayer/snapshotStorage/" + fileName  # + ".csv"
    # to do: how to avoid loading into pandas??
    df1 = pd.read_csv(fullFilePath, sep=';', decimal=",")

    years = df1['years'].tolist()
    revenueValuesBaseline1 = df1['weightedRevenues'].tolist()
    profitValuesBaseline1 = df1['weightedGrossMargin'].tolist()

    snapshot1revenue = sum(revenueValuesBaseline1)
    snapshot1grossMargin = sum(profitValuesBaseline1)

    print("using baseline data profit", profitValuesBaseline1)

    if not baseline1:
        print("baseline1 missing from session! redirecting")
        return render(request, "snapshots/snapshotList.html")

    context = {"years": years,
               "revenueValuesBaseline1": revenueValuesBaseline1,
               "profitValuesBaseline1": profitValuesBaseline1,
               "tab": "keyfacts",
               "snapshotObj": snapshotObj,
               "snapshot1revenue": snapshot1revenue,
               "snapshot1grossMargin": snapshot1grossMargin
               }
    return render(request, "snapshots/snapshotDeepdive.html", context)

# returns all tags available for snapshots


@login_required(login_url="/login/")
def snapshotTagList(request):
    allSnapshotTags = SnapshotTags.objects.all()
    # data = serializers.serialize("json", allSnapshotTags) -> strange nested format
    outputArray = []

    for tag in allSnapshotTags:
        tempDict = dict()
        tempDict['tagName'] = tag.tagName
        tempDict['user_id'] = tag.user_id
        tempDict['id'] = tag.pk
        outputArray.append(tempDict)

    return JsonResponse(outputArray, safe=False)

# creates a snapshot tag


@login_required(login_url="/login/")
def createSnapshotTag(request):
    if request.method == 'POST':
        tagNameInput = request.POST.get('tagName')
        user = request.user
        SnapshotTags.objects.get_or_create(user=user, tagName=tagNameInput)
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=500)


"""@login_required(login_url="/login/")
def newSnapshot(request):

    if request.method == 'POST':
    return render(request, "snapshots/newSnapshot.html")

# view mit drop downs
"""


class newSnapshot(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    template_name = "snapshots/newSnapshot.html"
    form_class = CreateSnapshotForm
    success_url = reverse_lazy("snapshotList")

    def post(self, request, *args, **kwargs):
        print("req method post new snapshot", request.user)

        form = self.form_class(request.user, request.POST, request=request)
        print("-----> create form for validation")
        if form.is_valid():
            print("new snapshot form is valid",
                  request.POST.get('snapshotName'))
            # here logic for saving
            # helper df due to django values logic for foreign keys

            from .snapshotCreator import snapshotCreator

            snapshotCreator(request, None, None, request.POST.get('tagInput'))

            """

            helperDf = pd.DataFrame(
                list(BoUp.objects.all().values('productMarketer__name',
                                               'productMarketer__familyName',
                                               'productMarketer__country',
                                               'applicationMain__appMainDescription',
                                               'applicationDetail__appDetailDescription',
                                               'rfp__rfp',
                                               'rfp__hfg',
                                               'rfp__ppos',
                                               'rfp__package__package',
                                               'rfp__basicType',
                                               'rfp__availablePGS',
                                               'rfp__dummy',
                                               'rfp__familyHelper',
                                               'rfp__packageHelper',
                                               'salesName__name',
                                               'salesName__dummy',
                                               'mainCustomer__customerName',
                                               'endCustomer__finalCustomerName',
                                               'distributor__distributorName',
                                               'tier1__tierOneName',
                                               'vpaCustomer__customerName',
                                               'oem__oemName',
                                               'ems__emsName')))

            print("$$$$$$$$$ helper df")
            print(helperDf)
            df = pd.DataFrame(list(BoUp.objects.all().values()))
            df = df.fillna(0)

            result = pd.concat([helperDf, df], axis=1)

            print("%%%%%%%%%%%%%% current boup objects")
            print(result)
            print("%%% ---> END")

            # for each year get the boup metrics
            years, weightedVolumes, weightedGrossMargin, weightedRevenues, asp, volumes, grossMargin = getBoUpKeyMetrics(
                df)

            print(len(years), len(weightedVolumes), len(
                weightedGrossMargin), len(weightedRevenues), len(asp), "other", len(volumes), len(grossMargin))
            # make df and parse into csv
            # dictionary of lists 
            dict = {'years': years, 'weightedVolumes': weightedVolumes,
                    'weightedGrossMargin': weightedGrossMargin, 'weightedRevenues': weightedRevenues, 'asp': asp, 'volumes': volumes, 'grossMargin': grossMargin}
            df2 = pd.DataFrame(dict)

            # persist data
            snapshotNameInput = request.POST.get('snapshotName')
            snapshotCommentsInput = request.POST.get('snapshotCommentsInput')
            user = request.user
            dateToday = datetime.today().strftime('%Y%m%d')
            userIdStr = str(user.id)
            filePathBase = "./persistentLayer/snapshotStorage/"

            # replace spaces
            snapshotNameInput = snapshotNameInput.replace(' ', '_')

            snapshotFullFileName = dateToday + "_" + userIdStr + \
                snapshotNameInput + "_snapshot.csv"
            metadataFullFileName = dateToday + "_" + userIdStr + \
                snapshotNameInput + "_metadata.csv"

            metadataFilePath = filePathBase + metadataFullFileName
            snapshotFilePath = filePathBase + snapshotFullFileName

            # print("using paths", snapshotFilePath)
            result.to_csv(snapshotFilePath, sep=";", decimal=",", header=True)
            df2.to_csv(metadataFilePath, sep=";", decimal=",", header=True)

            tagInput = request.POST.get('tagInput')
            tagObj = SnapshotTags.objects.get(id=tagInput)
            # print("snapshot full file name counts",
            #      snapshotFullFileName, "metadata", metadataFullFileName)

            # print("snapshot full file name counts", len(
            #    snapshotFullFileName), len(metadataFullFileName))
            snapshotObject, created = SnapshotMetaData.objects.get_or_create(
                user=user, snapshotName=snapshotNameInput)
            snapshotObject.tag = tagObj
            snapshotObject.fileName = snapshotFullFileName
            snapshotObject.user = request.user
            snapshotObject.snapshotComments = snapshotCommentsInput
            snapshotObject.metadataFileName = metadataFullFileName
            snapshotObject.save()
            """

            return redirect(self.success_url)
        else:
            context = {"form": self.form_class(request.user, request.POST)}
            return render(request, self.template_name, context)

    def get(self, request):

        context = {"form": self.form_class(request.user)}
        return render(request, self.template_name, context)


@login_required(login_url="/login/")
def snapshotCompare(request):
    if request.method == 'POST':

        # try:
        baseline1 = request.POST.get('baseline1')
        baseline2 = request.POST.get('baseline2')
        # request.session["baseline1"] = baseline1
        # request.session["baseline2"] = baseline2

        snapshotObj = SnapshotMetaData.objects.get(id=baseline1)
        fileName = snapshotObj.metadataFileName
        fullFilePath = "./persistentLayer/snapshotStorage/" + fileName  # + ".csv"
        # to do: how to avoid loading into pandas??
        df1 = pd.read_csv(fullFilePath, sep=';', decimal=",")
        years = df1['years'].tolist()
        revenueValuesBaseline1 = df1['weightedRevenues'].tolist()
        profitValuesBaseline1 = df1['weightedGrossMargin'].tolist()

        snapshot1revenue = int(round(sum(revenueValuesBaseline1), 0))
        snapshot1grossMargin = int(round(sum(profitValuesBaseline1), 0))

        snapshotObj2 = SnapshotMetaData.objects.get(id=baseline2)
        fileName2 = snapshotObj2.metadataFileName
        fullFilePath2 = "./persistentLayer/snapshotStorage/" + fileName2  # + ".csv"
        # to do: how to avoid loading into pandas??
        df2 = pd.read_csv(fullFilePath2, sep=';', decimal=",")

        revenueValuesBaseline2 = df2['weightedRevenues'].tolist()
        profitValuesBaseline2 = df2['weightedGrossMargin'].tolist()

        snapshot2revenue = int(round(sum(revenueValuesBaseline2), 0))
        snapshot2grossMargin = int(round(sum(profitValuesBaseline2), 0))

        try:
            pctDeltaRev = round(((snapshot2revenue - snapshot1revenue) /
                                 snapshot2revenue), 2)
        except:
            pctDeltaRev = "N/A"

        try:
            pctDeltaGm = round((
                (snapshot2grossMargin - snapshot1grossMargin) / snapshot2grossMargin), 2)
        except:
            pctDeltaGm = "N/A"

        deltaWrev = pctDeltaRev
        deltaGm = pctDeltaGm

        print("deltaWrev", deltaWrev, "snapshot2revenue", snapshot2revenue,
              "snapshot1revenue", snapshot1revenue, "snapshot2revenue", snapshot2revenue)

        if not baseline1:
            print("baseline1 missing from session! redirecting")
            return render(request, "snapshots/snapshotCompare.html")

        if not baseline2:
            print("baseline2 missing from session! redirecting")
            return render(request, "snapshots/snapshotCompare.html")

        context = {"years": years, "revenueValuesBaseline1": revenueValuesBaseline1, "revenueValuesBaseline2": revenueValuesBaseline2,
                   "profitValuesBaseline1": profitValuesBaseline1, "profitValuesBaseline2": profitValuesBaseline2, "tab": "inspect", "snapshot1": snapshotObj, "snapshot2": snapshotObj2,
                   "snapshot1revenue": snapshot1revenue, "snapshot1grossMargin": snapshot1grossMargin,  "snapshot2revenue": snapshot2revenue, "snapshot2grossMargin": snapshot2grossMargin, "deltaWrev": deltaWrev,
                   "deltaGm": deltaGm}
        # success_url = reverse_lazy("snapshotCompareDeepDive")
        # return HttpResponseRedirect(success_url)
        return render(request, "snapshots/snapshotCompare.html", context)
        """
        except:
            print("failed to compare")
            compareError = [
                "Fatal error while retrieving baseline snapshots. Files could not be retrieved."]
            context = {"compareError": compareError}
            errorMessage = "Fatal error while retrieving baseline snapshots. Files could not be retrieved."
            messages.error(request, errorMessage)

            return render(request, "snapshots/snapshotCompare.html", context)
        """

    return render(request, "snapshots/snapshotCompare.html")


@ login_required(login_url="/login/")
def snapshotCompareDeepDive(request):

    years = []
    revenueValuesBaseline1 = []
    revenueValuesBaseline2 = []
    profitValuesBaseline1 = []
    profitValuesBaseline2 = []

    # here to logic to populate arrays with relevant data
    baseline1 = request.session["baseline1"]
    baseline2 = request.session["baseline2"]
    redirect_url = reverse_lazy("snapshotCompare")

    if not baseline1:
        print("baseline1 missing from session! redirecting")
        return HttpResponseRedirect(redirect_url)

    if not baseline2:
        print("baseline2 missing from session! redirecting")
        return HttpResponseRedirect(redirect_url)

    context = {"years": years, "revenueValuesBaseline1": revenueValuesBaseline1, "revenueValuesBaseline2": revenueValuesBaseline2,
               "profitValuesBaseline1": profitValuesBaseline1, "profitValuesBaseline2": profitValuesBaseline2}

    return render(request, "snapshots/snapshotCompareDeepDive.html", context)


@ login_required(login_url="/login/")
def snapshotUserList(request):
    User = get_user_model()
    users = User.objects.all()
    print("snapshot user list", users)

    outputArray = []

    for user in users:
        tempDict = dict()
        tempDict['username'] = user.username
        tempDict['firstName'] = user.first_name
        tempDict['lastName'] = user.last_name
        tempDict['id'] = user.pk
        outputArray.append(tempDict)

    return JsonResponse(outputArray, safe=False)
