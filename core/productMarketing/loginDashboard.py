

from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView

from core.project.helperFunctions import *


from core.project.models import *


'''

project.productMarketer.user = request.user

allProjects = Project.objects.all()

numberOfMyProject = allProjects.filter(productMarketer=request.user).count()

numberOfMyDrafts = allProjects.filter(draft=True).count()

allBoUpObjects = BoUp.objects.all()

myBoUpObjects = allBoUpObjects.filter(productMarketer=request.user).aggregate('revEurLifeTime')

ProjectError


'''


def loginDashboardJson1(marketerId):

    #marketerId = 1
    # top row: JSON (total project, total rev, total draft, total project with error)
    allMarketerProjects = Project.objects.filter(productMarketer_id=marketerId)
    projectCount = allMarketerProjects.count()
    DraftProjectsCount = allMarketerProjects.filter(draft=1).count()
    totalRevenue = BoUp.objects.filter(
        productMarketer=marketerId).aggregate(revSum=Sum('revEurLifeTime'))
    totalRevenue = int(round(totalRevenue['revSum'], 0))
    projectId = []
    for project in allMarketerProjects:
        projectId.append(project.id)

    pendingItemCount = ProjectError.objects.filter(
        project_id__in=projectId).count()

    print("returning sum all projects of marketer rev eur lifetime", totalRevenue)

    jsonTop = {'Total Projects': projectCount,
               'Revenue': totalRevenue, 'Draft Projects': DraftProjectsCount, 'Pending Items': pendingItemCount}

    return jsonTop


def loginDashboardJson2(marketerId):
    # middle right section: for all projects of marketer: project id=ID_APP_id, endcustomer= endCustomer_id, gm=gmLifeTime, rev=revEurLifeTime
    print("test", marketerId)
    allBoUpObjects = BoUp.objects.filter(productMarketer=marketerId)

    idList = []
    endCustomerList = []
    gmList = []
    revList = []
    endCustomerNameList = []
    for BoUpEntry in allBoUpObjects:
        idList.append(BoUpEntry.ID_APP_id)
        endCustomerList.append(BoUpEntry.endCustomer_id)
        gmList.append(BoUpEntry.gmLifeTime)
        revList.append(BoUpEntry.revEurLifeTime)
        endCustomerNameList.append(BoUpEntry.endCustomerHelper)

    jsonMiddleRight = {'Project Id': idList, 'endCustomer': endCustomerList,
                       'endCustomerNames': endCustomerNameList, 'gm': gmList, 'rev': revList}

    return jsonMiddleRight


def loginDashboardJson3(marketerId):
    allBoUpObjects = BoUp.objects.filter(productMarketer=marketerId)

    # bottom section: rev sum über alle Projecte auf Jahres Level
    totalRev = []

    totalRev.append(allBoUpObjects.aggregate(revSum=Sum('wRev2020'))['revSum'])
    totalRev.append(allBoUpObjects.aggregate(revSum=Sum('wRev2021'))['revSum'])
    totalRev.append(allBoUpObjects.aggregate(revSum=Sum('wRev2022'))['revSum'])
    totalRev.append(allBoUpObjects.aggregate(revSum=Sum('wRev2023'))['revSum'])
    totalRev.append(allBoUpObjects.aggregate(revSum=Sum('wRev2024'))['revSum'])
    totalRev.append(allBoUpObjects.aggregate(revSum=Sum('wRev2025'))['revSum'])
    totalRev.append(allBoUpObjects.aggregate(revSum=Sum('wRev2026'))['revSum'])
    totalRev.append(allBoUpObjects.aggregate(revSum=Sum('wRev2027'))['revSum'])
    totalRev.append(allBoUpObjects.aggregate(revSum=Sum('wRev2028'))['revSum'])
    totalRev.append(allBoUpObjects.aggregate(revSum=Sum('wRev2029'))['revSum'])
    totalRev.append(allBoUpObjects.aggregate(revSum=Sum('wRev2030'))['revSum'])
    totalRev.append(allBoUpObjects.aggregate(revSum=Sum('wRev2031'))['revSum'])
    totalRev.append(allBoUpObjects.aggregate(revSum=Sum('wRev2032'))['revSum'])
    totalRev.append(allBoUpObjects.aggregate(revSum=Sum('wRev2033'))['revSum'])
    totalRev.append(allBoUpObjects.aggregate(revSum=Sum('wRev2034'))['revSum'])
    totalRev.append(allBoUpObjects.aggregate(revSum=Sum('wRev2035'))['revSum'])
    totalRev.append(allBoUpObjects.aggregate(revSum=Sum('wRev2036'))['revSum'])
    totalRev.append(allBoUpObjects.aggregate(revSum=Sum('wRev2037'))['revSum'])
    totalRev.append(allBoUpObjects.aggregate(revSum=Sum('wRev2038'))['revSum'])
    totalRev.append(allBoUpObjects.aggregate(revSum=Sum('wRev2039'))['revSum'])
    totalRev.append(allBoUpObjects.aggregate(revSum=Sum('wRev2040'))['revSum'])
    totalRev.append(allBoUpObjects.aggregate(revSum=Sum('wRev2041'))['revSum'])
    totalRev.append(allBoUpObjects.aggregate(revSum=Sum('wRev2042'))['revSum'])
    totalRev.append(allBoUpObjects.aggregate(revSum=Sum('wRev2043'))['revSum'])
    totalRev.append(allBoUpObjects.aggregate(revSum=Sum('wRev2044'))['revSum'])

    years = [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030, 2031,
             2032, 2033, 2034, 2035, 2036, 2037, 2038, 2039, 2040, 2041, 2042, 2043, 2044]

    jsonBottom = {'Total Revenue': totalRev, 'Years': years}

    return jsonBottom


class loginDashboard(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def get(self, request):
        print("getting login Dashboard")

        ###
        #marketerId = request.user
        marketerId = 1
        json1 = loginDashboardJson1(marketerId)
        json2 = loginDashboardJson2(marketerId)
        json3 = loginDashboardJson3(marketerId)
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print(json1, json2, json3)
        return JsonResponse({"jsonTop": json1, "jsonMiddleRight": json2, "jsonBottom": json3}, safe=True)
