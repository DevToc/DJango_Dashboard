from .models import Project
from productMarketingDwh.models import BoUp
from .helperFunctions import getProjectOverview, HighLevelProjectProblems
import time
from datetime import datetime


class bottomUpPersistor:

    finalRevenue = []
    finalVolume = []
    finalPrice = []
    finalGrossMargin = []
    finalGrossMarginPct = []
    final_revenue_month = []
    final_grossMargin_month = []
    final_grossMarginPct_month = []
    finalVhk = []
    final_revenue_FY = []
    final_grossProfit_FY = []
    final_grossProfitPct_FY = []
    final_volumes_FY = []
    vhkCy = []
    finalTotalCost = []
    asp = []
    weightedGrossMargin = []
    weightedGrossMarginPct = []
    weightedRevenue = []
    weightedVolume = []
    message = ""
    fxRate = 1.0

    def __init__(self, params):
        self.finalRevenue = params["finalRevenue"]
        self.finalVolume = params["finalVolume"]
        self.finalPrice = params["finalPrice"]
        self.finalGrossMargin = params["finalGrossMargin"]
        self.finalGrossMarginPct = params["finalGrossMarginPct"]
        self.final_revenue_month = params["final_revenue_month"]
        self.final_grossMargin_month = params["final_grossMargin_month"]
        self.final_grossMarginPct_month = params["final_grossMarginPct_month"]
        self.finalVhk = params["finalVhk"]
        self.final_revenue_FY = params["final_revenue_FY"]
        self.final_grossProfit_FY = params["final_grossProfit_FY"]
        self.final_grossProfitPct_FY = params["final_grossProfitPct_FY"]
        self.final_volumes_FY = params["final_volumes_FY"]
        self.vhkCy = params["vhkCy"]
        self.finalTotalCost = params["finalTotalCost"]
        self.asp = params["asp"]
        self.weightedGrossMargin = params["weightedGrossMargin"]
        self.weightedGrossMarginPct = params["weightedGrossMarginPct"]
        self.weightedRevenue = params["weightedRevenue"]
        self.weightedVolume = params["weightedVolume"]

    def persist(
        self,
        projectId,
        request,
        bulk,
        boUpObjectInput,
        probability,
        helperObjects,
        vhkUpdate,
        runDate,
    ):
        print(
            "persisting project", projectId, "boupobjinpu", boUpObjectInput, probability
        )
        project = Project.objects.get(id=projectId)
        errors = []

        user = None
        if request != None:
            user = request.user

        try:
            if bulk == False:
                probability = float(project.status.status) / 100.0
        except:
            errors.append(HighLevelProjectProblems.projectKeyFactsError)
            outputDictionary = {
                "revenue": [],
                "grossMargin": [],
                "years": [],
                "errors": errors,
                "sumRevenue": 0,
                "sumGrossMargin": 0,
                "sumCost": 0,
                "sumVolume": 0,
                "sumWeightedVolume": 0,
                "sumWeightedRevenue": 0,
                "averageAsp": 0,
                "sumWeightedGrossMargin": 0,
            }

            print("####### returning A")

            # case probability was not set yet
            message = "You are missing mandatory project key facts, as in this case the project probability (weighting). Please fill out before continuing."
            return False, outputDictionary, message

        if (len(self.finalVolume) == 0) and (bulk == False):

            (
                revenue,
                volumes,
                prices,
                grossMargin,
                grossMarginPct,
                revenue_month,
                grossMargin_month,
                grossMarginPct_month,
                vhk,
                revenue_FY,
                grossProfit_FY,
                grossProfitPct_FY,
                volumes_FY,
                VhkCy,
                totalCost,
                sumRevenue,
                sumGrossMargin,
                sumCost,
                years,
                errors,
                weightedGrossMargin,
                weightedGrossMarginPct,
                weightedRevenue,
                asp,
                weightedVolume,
                sumVolume,
                sumWeightedVolume,
                sumWeightedRevenue,
                averageAsp,
                sumWeightedGrossMargin,
                projectCurrency,
                fxRate,
            ) = getProjectOverview(projectId, user, probability, None)
            # transfer
            self.finalRevenue = revenue
            self.finalVolume = volumes
            self.finalPrice = prices
            self.finalGrossMargin = grossMargin
            self.finalGrossMarginPct = grossMarginPct
            self.final_revenue_month = revenue_month
            self.final_grossMargin_month = grossMargin_month
            self.final_grossMarginPct_month = grossMarginPct_month
            self.finalVhk = vhk
            self.final_revenue_FY = revenue_FY
            self.final_grossProfit_FY = grossProfit_FY
            self.final_grossProfitPct_FY = grossProfitPct_FY
            self.final_volumes_FY = volumes_FY
            self.vhkCy = VhkCy
            self.finalTotalCost = totalCost
            self.weightedGrossMargin = weightedGrossMargin
            self.weightedGrossMarginPct = weightedGrossMarginPct
            self.weightedRevenue = weightedRevenue
            self.asp = asp
            self.weightedVolume = weightedVolume
            self.fxRate = fxRate

        elif (len(self.finalVolume) == 0) and (bulk == True):
            print("input probability", probability)
            (
                revenue,
                volumes,
                prices,
                grossMargin,
                grossMarginPct,
                revenue_month,
                grossMargin_month,
                grossMarginPct_month,
                vhk,
                revenue_FY,
                grossProfit_FY,
                grossProfitPct_FY,
                volumes_FY,
                VhkCy,
                totalCost,
                sumRevenue,
                sumGrossMargin,
                sumCost,
                years,
                errors,
                weightedGrossMargin,
                weightedGrossMarginPct,
                weightedRevenue,
                asp,
                weightedVolume,
                sumVolume,
                sumWeightedVolume,
                sumWeightedRevenue,
                averageAsp,
                sumWeightedGrossMargin,
                projectCurrency,
                fxRate,
            ) = getProjectOverview(projectId, user, probability, helperObjects)
            # transfer
            self.finalRevenue = revenue
            self.finalVolume = volumes
            self.finalPrice = prices
            self.finalGrossMargin = grossMargin
            self.finalGrossMarginPct = grossMarginPct
            self.final_revenue_month = revenue_month
            self.final_grossMargin_month = grossMargin_month
            self.final_grossMarginPct_month = grossMarginPct_month
            self.finalVhk = vhk
            self.final_revenue_FY = revenue_FY
            self.final_grossProfit_FY = grossProfit_FY
            self.final_grossProfitPct_FY = grossProfitPct_FY
            self.final_volumes_FY = volumes_FY
            self.vhkCy = VhkCy
            self.finalTotalCost = totalCost
            self.weightedGrossMargin = weightedGrossMargin
            self.weightedGrossMarginPct = weightedGrossMarginPct
            self.weightedRevenue = weightedRevenue
            self.asp = asp
            self.weightedVolume = weightedVolume
            self.fxRate = fxRate
        if (len(self.finalVolume) == 0) | (len(self.finalPrice) == 0):

            errors.append(
                HighLevelProjectProblems.pricesAndVolumesMissingCompletely)

            outputDictionary = {
                "revenue": revenue,
                "grossMargin": grossMargin,
                "years": years,
                "errors": errors,
                "sumRevenue": sumRevenue,
                "sumGrossMargin": sumGrossMargin,
                "sumCost": sumCost,
                "sumVolume": sumVolume,
                "sumWeightedVolume": sumWeightedVolume,
                "sumWeightedRevenue": sumWeightedRevenue,
                "averageAsp": averageAsp,
                "sumWeightedGrossMargin": sumWeightedGrossMargin,
            }

            message = "An error ocurred while submitting the bottom up. You are either missing volume or price information or both. Until you complete the missing data, the project cannot be submitted."
            return False, outputDictionary, message, None

        """
        # clear project id from session

        try:
            del request.session["project_id"]
        except KeyError:
            pass
        """

        project.draft = False
        revenue = self.finalRevenue
        volumes = self.finalVolume
        prices = self.finalPrice
        grossMargin = self.finalGrossMargin
        grossMarginPct = self.finalGrossMarginPct
        revenue_month = self.final_revenue_month
        grossMargin_month = self.final_grossMargin_month
        grossMarginPct_month = self.final_grossMarginPct_month
        vhk = self.finalVhk
        revenue_FY = self.final_revenue_FY
        grossProfit_FY = self.final_grossProfit_FY
        grossProfitPct_FY = self.final_grossProfitPct_FY
        volumes_FY = self.final_volumes_FY
        VhkCy = self.vhkCy

        # create entry in BoUp TABLE
        start_time = time.time()
        if bulk == False:
            if not project.oem:
                oem = ""
            else:
                oem = project.oem  # oem = project.oem.oemName

        BoUpObject = None
        created = None
        # based on unique key
        if bulk == False:
            BoUpObject, created = BoUp.objects.get_or_create(
                applicationMain=project.applicationMain,
                applicationDetail=project.applicationDetail,
                mainCustomer=project.mainCustomer,
                endCustomer=project.finalCustomer,
                salesName=project.sales_name,
                syntheticProjectName=project.syntheticProjectName
            )
        else:
            BoUpObject = boUpObjectInput

        # except:
        #   print("... going to raise validation error")
        #    return False

        try:
            if bulk == False:
                BoUpObject.ID_APP = project
                BoUpObject.productMarketer = project.productMarketer
                BoUpObject.hfg = project.sales_name.rfp.hfg
                BoUpObject.ppos = project.sales_name.rfp.ppos
                BoUpObject.spNumber = project.spNumber
                BoUpObject.familyPriceApplicable = project.familyPriceApplicable
                BoUpObject.familyPriceDetails = project.familyPriceDetails
                #BoUpObject.priceType = project.priceType
                BoUpObject.comment = project.comment
                BoUpObject.applicationLine = (
                    project.applicationLine.applicationLineShortName if project.applicationLine else "N/A"
                )
                BoUpObject.Reviewed = project.projectReviewed
                BoUpObject.reviewDate = project.reviewDate
                # change all these to FK?
                BoUpObject.region = project.region.region
                BoUpObject.secondRegion = project.region.region
                BoUpObject.dcChannel = (
                    project.dcChannel.dcChannelDescription if project.dcChannel else ""
                )
                BoUpObject.priceType = (
                    project.priceType.priceTypeDisplay if project.priceType else ""
                )
                BoUpObject.plHfg = project.product.plHfg
                BoUpObject.endCustomerHelper = project.finalCustomer.finalCustomerName
                BoUpObject.mainCustomerHelper = project.mainCustomer.customerName
                BoUpObject.projectName = project.projectName
                BoUpObject.distributor = project.distributor
                BoUpObject.tier1 = project.tier1
                BoUpObject.ems = project.ems
                BoUpObject.vpaCustomer = project.vpaCustomer
                BoUpObject.salesContact = project.salesContact
                BoUpObject.statusProbability = project.status.statusDisplay
                BoUpObject.probability = probability
                BoUpObject.sop = project.estimatedSop
                BoUpObject.availablePGS = project.sales_name.rfp.availablePGS
                # project.user,#modifiedBy = project.user.username,
                BoUpObject.modifiedBy = request.user
                BoUpObject.modifiedDate = project.modifiedDate
                BoUpObject.creationDate = project.creationDate
                BoUpObject.package = project.sales_name.rfp.packageHelper
                BoUpObject.series = project.sales_name.rfp.seriesHelper
                BoUpObject.rfp = project.sales_name.rfp
                BoUpObject.dummy = project.dummy
                BoUpObject.basicType = project.sales_name.rfp.basicType
                BoUpObject.priceSource = project.otherPriceComments
                BoUpObject.gen = project.sales_name.rfp.familyHelper
                BoUpObject.genDetail = project.sales_name.rfp.familyDetailHelper
                BoUpObject.seriesLong = "N/A"
                BoUpObject.rfpHlp = project.sales_name.rfp.rfp
                BoUpObject.mcHlp = project.mainCustomer.customerName
                BoUpObject.ecHlp = project.finalCustomer.finalCustomerName
                BoUpObject.fxRate = self.fxRate
                BoUpObject.syntheticProjectName = project.syntheticProjectName
                BoUpObject.contractualCurrency = project.contractualCurrency
                BoUpObject.currency = "EUR"

                if vhkUpdate == True:
                    BoUpObject.vhkDate = runDate
                BoUpObject.save()
        except:

            errors.append(HighLevelProjectProblems.otherProjectIntegrityError)
            outputDictionary = {
                "revenue": revenue,
                "grossMargin": grossMargin,
                "years": years,
                "errors": errors,
                "sumRevenue": sumRevenue,
                "sumGrossMargin": sumGrossMargin,
                "sumCost": sumCost,
                "sumVolume": sumVolume,
                "sumWeightedVolume": sumWeightedVolume,
                "sumWeightedRevenue": sumWeightedRevenue,
                "averageAsp": averageAsp,
                "sumWeightedGrossMargin": sumWeightedGrossMargin,
            }

            print("... going to raise second validation error")
            message = "An unique constraint was violated! This can happen when there already is a project in the Bottom Up table with the same combination of Main and End Customers, Main and Detail applications and sales name."
            return False, outputDictionary, message, None

        """
        bis oem
        """

        try:
            BoUpObject.oem = oem
        except:
            print("could not set oem!")

        BoUpObject.gmLifeTime = sum(grossMargin)
        BoUpObject.revEurLifeTime = sum(revenue)
        BoUpObject.volLifeTime = sum(volumes)
        BoUpObject.volWeightedLifeTime = sum(volumes) * probability

        BoUpObject.vol2020 = volumes[0]
        BoUpObject.vol2021 = volumes[1]
        BoUpObject.vol2022 = volumes[2]
        BoUpObject.vol2023 = volumes[3]
        BoUpObject.vol2024 = volumes[4]
        BoUpObject.vol2025 = volumes[5]
        BoUpObject.vol2026 = volumes[6]
        BoUpObject.vol2027 = volumes[7]
        BoUpObject.vol2028 = volumes[8]
        BoUpObject.vol2029 = volumes[9]
        BoUpObject.vol2030 = volumes[10]
        BoUpObject.vol2031 = volumes[11]
        BoUpObject.vol2032 = volumes[12]
        BoUpObject.vol2033 = volumes[13]
        BoUpObject.vol2034 = volumes[14]
        BoUpObject.vol2035 = volumes[15]
        BoUpObject.vol2036 = volumes[16]
        BoUpObject.vol2037 = volumes[17]
        BoUpObject.vol2038 = volumes[18]
        BoUpObject.vol2039 = volumes[19]
        BoUpObject.vol2040 = volumes[20]
        BoUpObject.vol2041 = volumes[21]
        BoUpObject.vol2042 = volumes[22]
        BoUpObject.vol2043 = volumes[23]
        BoUpObject.vol2044 = 0.0

        # original code linked all volCustomer to first entry in volumes
        BoUpObject.volCustomer2020 = volumes[0]
        BoUpObject.volCustomer2021 = volumes[0]
        BoUpObject.volCustomer2022 = volumes[0]
        BoUpObject.volCustomer2023 = volumes[0]
        BoUpObject.volCustomer2024 = volumes[0]
        BoUpObject.volCustomer2025 = volumes[0]
        BoUpObject.volCustomer2026 = volumes[0]
        BoUpObject.volCustomer2027 = volumes[0]
        BoUpObject.volCustomer2028 = volumes[0]
        BoUpObject.volCustomer2029 = volumes[0]
        BoUpObject.volCustomer2030 = volumes[0]
        BoUpObject.volCustomer2031 = volumes[0]
        BoUpObject.volCustomer2032 = volumes[0]
        BoUpObject.volCustomer2033 = volumes[0]
        BoUpObject.volCustomer2034 = volumes[0]
        BoUpObject.volCustomer2035 = volumes[0]
        BoUpObject.volCustomer2036 = volumes[0]
        BoUpObject.volCustomer2037 = volumes[0]
        BoUpObject.volCustomer2038 = volumes[0]
        BoUpObject.volCustomer2039 = volumes[0]
        BoUpObject.volCustomer2040 = volumes[0]
        BoUpObject.volCustomer2041 = volumes[0]
        BoUpObject.volCustomer2042 = volumes[0]
        BoUpObject.volCustomer2043 = volumes[0]
        BoUpObject.volCustomer2044 = volumes[0]

        BoUpObject.price2020 = prices[0]
        BoUpObject.price2021 = prices[1]
        BoUpObject.price2022 = prices[2]
        BoUpObject.price2023 = prices[3]
        BoUpObject.price2024 = prices[4]
        BoUpObject.price2025 = prices[5]
        BoUpObject.price2026 = prices[6]
        BoUpObject.price2027 = prices[7]
        BoUpObject.price2028 = prices[8]
        BoUpObject.price2029 = prices[9]
        BoUpObject.price2030 = prices[10]
        BoUpObject.price2031 = prices[11]
        BoUpObject.price2032 = prices[12]
        BoUpObject.price2033 = prices[13]
        BoUpObject.price2034 = prices[14]
        BoUpObject.price2035 = prices[15]
        BoUpObject.price2036 = prices[16]
        BoUpObject.price2037 = prices[17]
        BoUpObject.price2038 = prices[18]
        BoUpObject.price2039 = prices[19]
        BoUpObject.price2040 = prices[20]
        BoUpObject.price2041 = prices[21]
        BoUpObject.price2042 = prices[22]
        BoUpObject.price2043 = prices[23]
        BoUpObject.price2044 = 0.0

        BoUpObject.vhk2020 = vhk[0]
        BoUpObject.vhk2021 = vhk[1]
        BoUpObject.vhk2022 = vhk[2]
        BoUpObject.vhk2023 = vhk[3]
        BoUpObject.vhk2024 = vhk[4]
        BoUpObject.vhk2025 = vhk[5]
        BoUpObject.vhk2026 = vhk[6]
        BoUpObject.vhk2027 = vhk[7]
        BoUpObject.vhk2028 = vhk[8]
        BoUpObject.vhk2029 = vhk[9]
        BoUpObject.vhk2030 = vhk[10]
        BoUpObject.vhk2031 = vhk[11]
        BoUpObject.vhk2032 = vhk[12]
        BoUpObject.vhk2033 = vhk[13]
        BoUpObject.vhk2034 = vhk[14]
        BoUpObject.vhk2035 = vhk[15]
        BoUpObject.vhk2036 = vhk[16]
        BoUpObject.vhk2037 = vhk[17]
        BoUpObject.vhk2038 = vhk[18]
        BoUpObject.vhk2039 = vhk[19]
        BoUpObject.vhk2040 = vhk[20]
        BoUpObject.vhk2041 = vhk[21]
        BoUpObject.vhk2042 = vhk[22]
        BoUpObject.vhk2043 = vhk[23]
        BoUpObject.vhk2044 = 0.0

        BoUpObject.gm2020 = grossMargin[0]
        BoUpObject.gm2021 = grossMargin[1]
        BoUpObject.gm2022 = grossMargin[2]
        BoUpObject.gm2023 = grossMargin[3]
        BoUpObject.gm2024 = grossMargin[4]
        BoUpObject.gm2025 = grossMargin[5]
        BoUpObject.gm2026 = grossMargin[6]
        BoUpObject.gm2027 = grossMargin[7]
        BoUpObject.gm2028 = grossMargin[8]
        BoUpObject.gm2029 = grossMargin[9]
        BoUpObject.gm2030 = grossMargin[10]
        BoUpObject.gm2031 = grossMargin[11]
        BoUpObject.gm2032 = grossMargin[12]
        BoUpObject.gm2033 = grossMargin[13]
        BoUpObject.gm2034 = grossMargin[14]
        BoUpObject.gm2035 = grossMargin[15]
        BoUpObject.gm2036 = grossMargin[16]
        BoUpObject.gm2037 = grossMargin[17]
        BoUpObject.gm2038 = grossMargin[18]
        BoUpObject.gm2039 = grossMargin[19]
        BoUpObject.gm2040 = grossMargin[20]
        BoUpObject.gm2041 = grossMargin[21]
        BoUpObject.gm2042 = grossMargin[22]
        BoUpObject.gm2043 = grossMargin[23]
        BoUpObject.gm2044 = 0.0

        BoUpObject.wVol2020 = float(weightedVolume[0])
        BoUpObject.wVol2021 = float(weightedVolume[1])
        BoUpObject.wVol2022 = float(weightedVolume[2])
        BoUpObject.wVol2023 = float(weightedVolume[3])
        BoUpObject.wVol2024 = float(weightedVolume[4])
        BoUpObject.wVol2025 = float(weightedVolume[5])
        BoUpObject.wVol2026 = float(weightedVolume[6])
        BoUpObject.wVol2027 = float(weightedVolume[7])
        BoUpObject.wVol2028 = float(weightedVolume[8])
        BoUpObject.wVol2029 = float(weightedVolume[9])
        BoUpObject.wVol2030 = float(weightedVolume[10])
        BoUpObject.wVol2031 = float(weightedVolume[11])
        BoUpObject.wVol2032 = float(weightedVolume[12])
        BoUpObject.wVol2033 = float(weightedVolume[13])
        BoUpObject.wVol2034 = float(weightedVolume[14])
        BoUpObject.wVol2035 = float(weightedVolume[15])
        BoUpObject.wVol2036 = float(weightedVolume[16])
        BoUpObject.wVol2037 = float(weightedVolume[17])
        BoUpObject.wVol2038 = float(weightedVolume[18])
        BoUpObject.wVol2039 = float(weightedVolume[19])
        BoUpObject.wVol2040 = float(weightedVolume[20])
        BoUpObject.wVol2041 = float(weightedVolume[21])
        BoUpObject.wVol2042 = float(weightedVolume[22])
        BoUpObject.wVol2043 = float(weightedVolume[23])
        BoUpObject.wVol2044 = 0.0

        BoUpObject.wRev2020 = weightedRevenue[0]
        BoUpObject.wRev2021 = weightedRevenue[1]
        BoUpObject.wRev2022 = weightedRevenue[2]
        BoUpObject.wRev2023 = weightedRevenue[3]
        BoUpObject.wRev2024 = weightedRevenue[4]
        BoUpObject.wRev2025 = weightedRevenue[5]
        BoUpObject.wRev2026 = weightedRevenue[6]
        BoUpObject.wRev2027 = weightedRevenue[7]
        BoUpObject.wRev2028 = weightedRevenue[8]
        BoUpObject.wRev2029 = weightedRevenue[9]
        BoUpObject.wRev2030 = weightedRevenue[10]
        BoUpObject.wRev2031 = weightedRevenue[11]
        BoUpObject.wRev2032 = weightedRevenue[12]
        BoUpObject.wRev2033 = weightedRevenue[13]
        BoUpObject.wRev2034 = weightedRevenue[14]
        BoUpObject.wRev2035 = weightedRevenue[15]
        BoUpObject.wRev2036 = weightedRevenue[16]
        BoUpObject.wRev2037 = weightedRevenue[17]
        BoUpObject.wRev2038 = weightedRevenue[18]
        BoUpObject.wRev2039 = weightedRevenue[19]
        BoUpObject.wRev2040 = weightedRevenue[20]
        BoUpObject.wRev2041 = weightedRevenue[21]
        BoUpObject.wRev2042 = weightedRevenue[22]
        BoUpObject.wRev2043 = weightedRevenue[23]
        BoUpObject.wRev2044 = 0.0

        # now ASP and weighted gross margin:   asp = weighted revenue / weighted volume. weighted gross margin = weighted revenue - weighted volume * cost per unit (aka VHK)
        BoUpObject.wGrossMargin2020 = weightedGrossMargin[0]
        BoUpObject.wGrossMargin2021 = weightedGrossMargin[1]
        BoUpObject.wGrossMargin2022 = weightedGrossMargin[2]
        BoUpObject.wGrossMargin2023 = weightedGrossMargin[3]
        BoUpObject.wGrossMargin2024 = weightedGrossMargin[4]
        BoUpObject.wGrossMargin2025 = weightedGrossMargin[5]
        BoUpObject.wGrossMargin2026 = weightedGrossMargin[6]
        BoUpObject.wGrossMargin2027 = weightedGrossMargin[7]
        BoUpObject.wGrossMargin2028 = weightedGrossMargin[8]
        BoUpObject.wGrossMargin2029 = weightedGrossMargin[9]
        BoUpObject.wGrossMargin2030 = weightedGrossMargin[10]
        BoUpObject.wGrossMargin2031 = weightedGrossMargin[11]
        BoUpObject.wGrossMargin2032 = weightedGrossMargin[12]
        BoUpObject.wGrossMargin2033 = weightedGrossMargin[13]
        BoUpObject.wGrossMargin2034 = weightedGrossMargin[14]
        BoUpObject.wGrossMargin2035 = weightedGrossMargin[15]
        BoUpObject.wGrossMargin2036 = weightedGrossMargin[16]
        BoUpObject.wGrossMargin2037 = weightedGrossMargin[17]
        BoUpObject.wGrossMargin2038 = weightedGrossMargin[18]
        BoUpObject.wGrossMargin2039 = weightedGrossMargin[19]
        BoUpObject.wGrossMargin2040 = weightedGrossMargin[20]
        BoUpObject.wGrossMargin2041 = weightedGrossMargin[21]
        BoUpObject.wGrossMargin2042 = weightedGrossMargin[22]
        BoUpObject.wGrossMargin2043 = weightedGrossMargin[23]
        BoUpObject.wGrossMargin2044 = 0.0

        BoUpObject.asp2020 = asp[0]
        BoUpObject.asp2021 = asp[1]
        BoUpObject.asp2022 = asp[2]
        BoUpObject.asp2023 = asp[3]
        BoUpObject.asp2024 = asp[4]
        BoUpObject.asp2025 = asp[5]
        BoUpObject.asp2026 = asp[6]
        BoUpObject.asp2027 = asp[7]
        BoUpObject.asp2028 = asp[8]
        BoUpObject.asp2029 = asp[9]
        BoUpObject.asp2030 = asp[10]
        BoUpObject.asp2031 = asp[11]
        BoUpObject.asp2032 = asp[12]
        BoUpObject.asp2033 = asp[13]
        BoUpObject.asp2034 = asp[14]
        BoUpObject.asp2035 = asp[15]
        BoUpObject.asp2036 = asp[16]
        BoUpObject.asp2037 = asp[17]
        BoUpObject.asp2038 = asp[18]
        BoUpObject.asp2039 = asp[19]
        BoUpObject.asp2040 = asp[20]
        BoUpObject.asp2041 = asp[21]
        BoUpObject.asp2042 = asp[22]
        BoUpObject.asp2043 = asp[23]
        BoUpObject.asp2044 = 0.0

        #########

        BoUpObject.fy_vol2020 = volumes_FY[0]
        BoUpObject.fy_vol2021 = volumes_FY[1]
        BoUpObject.fy_vol2022 = volumes_FY[2]
        BoUpObject.fy_vol2023 = volumes_FY[3]
        BoUpObject.fy_vol2024 = volumes_FY[4]
        BoUpObject.fy_vol2025 = volumes_FY[5]
        BoUpObject.fy_vol2026 = volumes_FY[6]
        BoUpObject.fy_vol2027 = volumes_FY[7]
        BoUpObject.fy_vol2028 = volumes_FY[8]
        BoUpObject.fy_vol2029 = volumes_FY[9]
        BoUpObject.fy_vol2030 = volumes_FY[10]
        BoUpObject.fy_vol2031 = volumes_FY[11]
        BoUpObject.fy_vol2032 = volumes_FY[12]
        BoUpObject.fy_vol2033 = volumes_FY[13]
        BoUpObject.fy_vol2034 = volumes_FY[14]
        BoUpObject.fy_vol2035 = volumes_FY[15]
        BoUpObject.fy_vol2036 = volumes_FY[16]
        BoUpObject.fy_vol2037 = volumes_FY[17]
        BoUpObject.fy_vol2038 = volumes_FY[18]
        BoUpObject.fy_vol2039 = volumes_FY[19]
        BoUpObject.fy_vol2040 = volumes_FY[20]
        BoUpObject.fy_vol2041 = volumes_FY[21]
        BoUpObject.fy_vol2042 = volumes_FY[22]
        BoUpObject.fy_vol2043 = volumes_FY[23]
        BoUpObject.fy_vol2044 = 0.0

        BoUpObject.fy_gm2020 = grossProfit_FY[0]
        BoUpObject.fy_gm2021 = grossProfit_FY[1]
        BoUpObject.fy_gm2022 = grossProfit_FY[2]
        BoUpObject.fy_gm2023 = grossProfit_FY[3]
        BoUpObject.fy_gm2024 = grossProfit_FY[4]
        BoUpObject.fy_gm2025 = grossProfit_FY[5]
        BoUpObject.fy_gm2026 = grossProfit_FY[6]
        BoUpObject.fy_gm2027 = grossProfit_FY[7]
        BoUpObject.fy_gm2028 = grossProfit_FY[8]
        BoUpObject.fy_gm2029 = grossProfit_FY[9]
        BoUpObject.fy_gm2030 = grossProfit_FY[10]
        BoUpObject.fy_gm2031 = grossProfit_FY[11]
        BoUpObject.fy_gm2032 = grossProfit_FY[12]
        BoUpObject.fy_gm2033 = grossProfit_FY[13]
        BoUpObject.fy_gm2034 = grossProfit_FY[14]
        BoUpObject.fy_gm2035 = grossProfit_FY[15]
        BoUpObject.fy_gm2036 = grossProfit_FY[16]
        BoUpObject.fy_gm2037 = grossProfit_FY[17]
        BoUpObject.fy_gm2038 = grossProfit_FY[18]
        BoUpObject.fy_gm2039 = grossProfit_FY[19]
        BoUpObject.fy_gm2040 = grossProfit_FY[20]
        BoUpObject.fy_gm2041 = grossProfit_FY[21]
        BoUpObject.fy_gm2042 = grossProfit_FY[22]
        BoUpObject.fy_gm2043 = grossProfit_FY[23]
        BoUpObject.fy_gm2044 = 0.0
        BoUpObject.fy_wVol2020 = float(volumes_FY[0]) * probability
        BoUpObject.fy_wVol2021 = float(volumes_FY[1]) * probability
        BoUpObject.fy_wVol2022 = float(volumes_FY[2]) * probability
        BoUpObject.fy_wVol2023 = float(volumes_FY[3]) * probability
        BoUpObject.fy_wVol2024 = float(volumes_FY[4]) * probability
        BoUpObject.fy_wVol2025 = float(volumes_FY[5]) * probability
        BoUpObject.fy_wVol2026 = float(volumes_FY[6]) * probability
        BoUpObject.fy_wVol2027 = float(volumes_FY[7]) * probability
        BoUpObject.fy_wVol2028 = float(volumes_FY[8]) * probability
        BoUpObject.fy_wVol2029 = float(volumes_FY[9]) * probability
        BoUpObject.fy_wVol2030 = float(volumes_FY[10]) * probability
        BoUpObject.fy_wVol2031 = float(volumes_FY[11]) * probability
        BoUpObject.fy_wVol2032 = float(volumes_FY[12]) * probability
        BoUpObject.fy_wVol2033 = float(volumes_FY[13]) * probability
        BoUpObject.fy_wVol2034 = float(volumes_FY[14]) * probability
        BoUpObject.fy_wVol2035 = float(volumes_FY[15]) * probability
        BoUpObject.fy_wVol2036 = float(volumes_FY[16]) * probability
        BoUpObject.fy_wVol2037 = float(volumes_FY[17]) * probability
        BoUpObject.fy_wVol2038 = float(volumes_FY[18]) * probability
        BoUpObject.fy_wVol2039 = float(volumes_FY[19]) * probability
        BoUpObject.fy_wVol2040 = float(volumes_FY[20]) * probability
        BoUpObject.fy_wVol2041 = float(volumes_FY[21]) * probability
        BoUpObject.fy_wVol2042 = float(volumes_FY[22]) * probability
        BoUpObject.fy_wVol2043 = float(volumes_FY[23]) * probability
        BoUpObject.fy_wVol2044 = 0.0

        BoUpObject.fy_wRev2020 = revenue_FY[0] * probability
        BoUpObject.fy_wRev2021 = revenue_FY[1] * probability
        BoUpObject.fy_wRev2022 = revenue_FY[2] * probability
        BoUpObject.fy_wRev2023 = revenue_FY[3] * probability
        BoUpObject.fy_wRev2024 = revenue_FY[4] * probability
        BoUpObject.fy_wRev2025 = revenue_FY[5] * probability
        BoUpObject.fy_wRev2026 = revenue_FY[6] * probability
        BoUpObject.fy_wRev2027 = revenue_FY[7] * probability
        BoUpObject.fy_wRev2028 = revenue_FY[8] * probability
        BoUpObject.fy_wRev2029 = revenue_FY[9] * probability
        BoUpObject.fy_wRev2030 = revenue_FY[10] * probability
        BoUpObject.fy_wRev2031 = revenue_FY[11] * probability
        BoUpObject.fy_wRev2032 = revenue_FY[12] * probability
        BoUpObject.fy_wRev2033 = revenue_FY[13] * probability
        BoUpObject.fy_wRev2034 = revenue_FY[14] * probability
        BoUpObject.fy_wRev2035 = revenue_FY[15] * probability
        BoUpObject.fy_wRev2036 = revenue_FY[16] * probability
        BoUpObject.fy_wRev2037 = revenue_FY[17] * probability
        BoUpObject.fy_wRev2038 = revenue_FY[18] * probability
        BoUpObject.fy_wRev2039 = revenue_FY[19] * probability
        BoUpObject.fy_wRev2040 = revenue_FY[20] * probability
        BoUpObject.fy_wRev2041 = revenue_FY[21] * probability
        BoUpObject.fy_wRev2042 = revenue_FY[22] * probability
        BoUpObject.fy_wRev2043 = revenue_FY[23] * probability
        BoUpObject.fy_wRev2044 = 0.0

        if bulk == False:
            BoUpObject.save()

        outputDictionary = {
            "revenue": revenue,
            "grossMargin": grossMargin,
            "years": years,
            "errors": errors,
            "sumRevenue": sumRevenue,
            "sumGrossMargin": sumGrossMargin,
            "sumCost": sumCost,
            "sumVolume": sumVolume,
            "sumWeightedVolume": sumWeightedVolume,
            "sumWeightedRevenue": sumWeightedRevenue,
            "averageAsp": averageAsp,
            "sumWeightedGrossMargin": sumWeightedGrossMargin,
        }

        message = "Project was submitted to the Bottom Up table and is now active."

        if bulk == True:
            return True, outputDictionary, message, BoUpObject
        else:
            return True, outputDictionary, message, None
