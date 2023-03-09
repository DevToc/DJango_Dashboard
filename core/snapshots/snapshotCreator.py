import pandas as pd
from productMarketingDwh.models import BoUp
from project.helperFunctions import getBoUpKeyMetrics
from datetime import datetime
from .models import SnapshotMetaData, SnapshotTags

def snapshotCreator(request, snapshotName, snapshotComments, tag):
    # here logic for saving
    # helper df due to django values logic for foreign keys
    print("request", request)
    print(request.POST.get('snapshotName'))

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
    print(years)
    print(weightedVolumes)
    print(weightedRevenues)
    print(asp)
    print(volumes)
    print(grossMargin)
    # make df and parse into csv
    # dictionary of lists 
    dict = {'years': years, 'weightedVolumes': weightedVolumes,
            'weightedGrossMargin': weightedGrossMargin, 'weightedRevenues': weightedRevenues, 'asp': asp, 'volumes': volumes, 'grossMargin': grossMargin}
    df2 = pd.DataFrame(dict)

    snapshotNameInput = None
    snapshotCommentsInput = None
    user = None
    tagInput = None 

    print("tag", tag)
    # persist data
    if tag != None:
        snapshotNameInput = request.POST.get('snapshotName')
        snapshotCommentsInput = request.POST.get('snapshotCommentsInput')
        user = request.user
        tagInput = request.POST.get('tagInput')
    else:
        snapshotNameInput = snapshotName
        snapshotCommentsInput = snapshotComments 
        user = request.user
        tagInput = tag

    print("snapshotNameInput", snapshotNameInput, "snapshotCommentsInput", snapshotCommentsInput)

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

    #print("using paths", snapshotFilePath)
    result.to_csv(snapshotFilePath, sep=";", decimal=",", header=True)
    df2.to_csv(metadataFilePath, sep=";", decimal=",", header=True)


    # print("snapshot full file name counts",
    #      snapshotFullFileName, "metadata", metadataFullFileName)

    # print("snapshot full file name counts", len(
    #    snapshotFullFileName), len(metadataFullFileName))
    snapshotObject, created = SnapshotMetaData.objects.get_or_create(
        user=user, snapshotName=snapshotNameInput)

    tagObj = None
    if tag != None: 
        tagObj = SnapshotTags.objects.get(id=tagInput)
        snapshotObject.tag = tagObj

    snapshotObject.fileName = snapshotFullFileName
    snapshotObject.user = user
    snapshotObject.snapshotComments = snapshotCommentsInput
    snapshotObject.metadataFileName = metadataFullFileName
    snapshotObject.save()