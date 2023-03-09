import copy

""" Global static inputs: """ #tbd
familyPriceThreshold = 100

"""Generate debug data"""
import random

random.seed(0)

class Customer:
    def __init__(self, name, rfps):
        self.name = name #string
        self.rfps = rfps #list of strings

    def getCustomerRFPs(self):
        return(self.rfps)

class Rfp:
    def __init__(self, name, years, volumes, prices, vhk, familyPriceApplicable):
        self.name = name
        self.years = years #list of int
        self.volumes = volumes #list of int
        self.prices = prices #list of float
        self.vhk = vhk #list of float
        self.familyPriceApplicable = familyPriceApplicable #boolean

        self.currencyPrices = "EUR"
        self.currencyVhk = "EUR"
        self.fxPrices = 1
        self.fxVhk = 1
        self.priceValidUntil = 2024
        self.priceIncreasedBy = 1

    def getRfpInput(self):
        return (self.years, self.volumes, self.prices, self.vhk, self.currencyPrices, self.currencyVhk, self.fxPrices, self.fxVhk, self.priceValidUntil, self.familyPriceApplicable, self.priceIncreasedBy)

listOfRFPs = []
for i in range(3):
    years = [2022, 2023, 2024, 2025, 2026, 2027]
    volumes = [random.randint(0,10) for i in range(6)]
    prices = [random.randint(10,100) for i in range(6)]
    vhk = [random.randint(5,50) for i in range(6)]
    familyPriceApplicable = True
    rfpName = "rfp"+str(i)

    listOfRFPs.append(Rfp(rfpName, years, volumes, prices, vhk, familyPriceApplicable))

consideredCustomer = Customer("cust1",listOfRFPs)

"""Platzhalter für manuellen/dynamischen Input des Nutzers"""
### Dynamic inputs - hier dummy Daten zur veranschaulichung des Formats
#consideredCustomer = "cust2" #Platzhalter manueller Input
#consideredCustomer = Customer("cust1",listOfRFPs)
familyPrice_reductionRate = 0.98
consideredRFP = "RFP under consideration"
consideredBasePrices = [5.5, 5.8, 5.9]
consideredVhk = [2.5, 2.8, 2.9]
consideredVolumes = [6, 5, 7]
consideredFxPrices= 1.04  #it is understood as the excahnge rate from source into EUR
consideredFxVhk = 1.00
consideredPriceValidUntil = 2024 #int that defines the last year in which the price is valid
consideredDFamilyPriceApplicable = True #defines whether the rfp is subject to family prices if they apply (tbd: same rate for all prices?)
consideredPriceIncreasedBy = 1.04  #new price after expiration of old price, e.g. 4% more than before

relevantYears = [2023, 2024, 2025] #könnte über slider mit start und end gemacht und dann im backend so übersetzen, dass eine liste rauskommt
minPrices = [4, 5, 5, 4.8, 5, 5] #tbd: required annually?
maxPrices = [5.5, 6.5, 6.5, 6.3, 6.5, 6.5] #tbd: required annually?
annualPriceIncrease = 1.02 #slider
minMaxBound = True #defines whether plausability checks are conducted and price in-/decrease is bounded to min or mx prices

benchmarkPriceDeviations = [0.95, 1.05] #definiert über slider

expectedCapacityShortage = 0.99 #slider
expectedVolumeOutage = 1.00 #slider
inflationVHK = 1.085 #slider (oder vorgegebener Wert)
inflationQuotationCurrency = 1.109 #slider (oder vorgegebener Wert)

"""Platzhalter für systemseitigen Dateninput"""
# def getCustomerRFPs(customerName):
#     ###access the database and return all RFPs sold to this customer in a list
#     rfps = [rfp1, rfp2, rfp3, ...] #list of all relevant rfps of considered customer, list of variable length
#     return rfps

# def getRfpInput(rfp):
#     ###access data base and return all relevant information for the entered rfp
#     years = [2020, 2021, 2022, 2023, 2024, 2025]
#     volumes = [60000, 65000, 70000, 75000, 80000, 85000]
#     prices = [5.5, 5.8, 5.9, 6.0, 6.0, 6.0]
#     vhk = [2.5, 2.8, 2.9,3.0,3.0,3.0]
#     currencyPrices = "USD" #how to avoid spelling mistakes?
#     currencyVhk= "EUR"
#     fxPrices= 1.04  #it is understood as the excahnge rate from source into EUR
#     fxVhk = 1.00
#     priceValidUntil = 2024 #int that defines the last year in which the price is valid
#     familyPriceApplicable = True #defines whether the rfp is subject to family prices if they apply (tbd: same rate for all prices?)
#     priceIncreasedBy = 1.04  #new price after expiration of old price, e.g. 4% more than before
    
#     ###### weitere Infos von Francisco; keine Ahnung wie man daran kommt, kann aber in dem Format bleiben
#     # inflationApplicableTo: [AnalysisObjects]
#     # [AnalysisObjects.vhk, AnalysisObjects.prices]
#     # Also erwartet ist den Impact von Inflation auf VHK und ab Ablauf der Preisbindung auch auf die Preise.
#     # Falls Preise nicht dabei sind, dann wird angenommen, preise bleiben fix (und Inflation frisst die Marge auf)
#     # allocationApplicable: Bool
#     # ist chip shortage zu berücksichtigen
#     # allocationVolume
#     # max. lieferbare Volumen
#     return (years, volumes, prices, vhk, currencyPrices, currencyVhk, fxPrices, fxVhk, priceValidUntil, familyPriceApplicable, priceIncreasedBy)


def getRfpTurnOver_base(rfp, relevantYears):
    years = rfp.getRfpInput()[0]
    volume = rfp.getRfpInput()[1]
    prices = rfp.getRfpInput()[2]
    vhk = rfp.getRfpInput()[3]
    startYearIndex = years.index(relevantYears[0])
    endYearIndex = years.index(relevantYears[-1])
    annualSingleMargin = [x-y for x, y in zip(prices[startYearIndex:endYearIndex+1], vhk[startYearIndex:endYearIndex+1])]
    turnOver = [x*y for x, y in zip(annualSingleMargin, volume[startYearIndex:endYearIndex+1])]
    return(turnOver)

def getConsideredRfpTurnOver_adjustedPrices(consideredBasePrices, consideredPriceValidUntil, relevantYears, priceAdjustments):
    listOfAnnualTurnoversConsideredRfp = []
    for priceAdjustment in priceAdjustments:
        adjustedPrices = []
        for year in relevantYears:
            if year > consideredPriceValidUntil:
                adjustedPrices.append(consideredBasePrices[relevantYears.index(year)]*priceAdjustment)
            else:
                adjustedPrices.append(consideredBasePrices[relevantYears.index(year)])
        annualSingleMargin = [x-y for x, y in zip(adjustedPrices, consideredVhk)]
        annualTurnoverConsideredRFP = [x*y for x, y in zip(annualSingleMargin, consideredVolumes)]
        listOfAnnualTurnoversConsideredRfp.append(annualTurnoverConsideredRFP) 
    return(listOfAnnualTurnoversConsideredRfp)

def getRfpTurnOver_familyPrice(rfp, relevantYears, familyPrice_reductionRate, familyPrice_reductionYears):
    years = rfp.getRfpInput()[0]
    volume = rfp.getRfpInput()[1]
    prices = rfp.getRfpInput()[2]
    vhk = rfp.getRfpInput()[3]
    familyPriceApplicable = rfp.getRfpInput()[9]
    startYearIndex = years.index(relevantYears[0])
    endYearIndex = years.index(relevantYears[-1])
    #calculate familyPrices
    for i in familyPrice_reductionYears:
        relevantIndex = years.index(i)
        if familyPriceApplicable:
            prices[relevantIndex] = prices[relevantIndex]*familyPrice_reductionRate
    annualSingleMargin = [x-y for x, y in zip(prices[startYearIndex:endYearIndex+1], vhk[startYearIndex:endYearIndex+1])]
    turnOver = [x*y for x, y in zip(annualSingleMargin, volume[startYearIndex:endYearIndex+1])]
    return(turnOver)


##### Hier gehts los #####

"""Calculate all benchmark price deviations"""
benchmarkPriceDeviations.insert(1, 1)
if benchmarkPriceDeviations[1] -benchmarkPriceDeviations[0] > 0.03:
    benchmarkPriceDeviations.insert(1, (benchmarkPriceDeviations[1] -benchmarkPriceDeviations[0])/2 + benchmarkPriceDeviations[0]) 
if benchmarkPriceDeviations[-1] - benchmarkPriceDeviations[-2] > 0.03:
    benchmarkPriceDeviations.insert(-1, benchmarkPriceDeviations[-1]-(benchmarkPriceDeviations[-1] - benchmarkPriceDeviations[-2])/2)

"""Initialize variables"""
relevantRfps = consideredCustomer.getCustomerRFPs()
revenue = [0 for entry in relevantYears]
annualCustomerTurnover_base = [0 for entry in relevantYears] #current annual turnover without considered RFP

""" Calculate overall annual turnover without considered RFP to define delta to family prices threshold """
for rfp in relevantRfps:
    turnOver = getRfpTurnOver_base(rfp, relevantYears)
    for i in range(len(annualCustomerTurnover_base)):
        annualCustomerTurnover_base[i] += turnOver[i]
deltaFamilyPrice = [max(familyPriceThreshold-i, 0) for i in annualCustomerTurnover_base]

"""Calculate turnover with adjusted prices considering family prices"""
# annualSingleMargin_min = [x-y for x, y in zip(minPrices, consideredVhk)]
# annualTurnoverConsideredRFP_min = [x*y for x, y in zip(annualSingleMargin_min, consideredVolumes)]
annualTurnoverConsideredRFPAdjusted = getConsideredRfpTurnOver_adjustedPrices(consideredBasePrices, consideredPriceValidUntil, relevantYears, benchmarkPriceDeviations)
overallAnnualTurnoverAdjusted = copy.deepcopy(annualTurnoverConsideredRFPAdjusted)

for adjustedPriceTurnover in overallAnnualTurnoverAdjusted:
    overallAdjustedPriceTurnover = []
    familyPriceIndices = []
    familyPriceYears = []

    for i in range(len(deltaFamilyPrice)):
        if deltaFamilyPrice[i] <= adjustedPriceTurnover[i]:
            familyPriceIndices.append(i)
            familyPriceYears.append(relevantYears[i])

    for rfp in relevantRfps:
        turnover_family = getRfpTurnOver_familyPrice(rfp, relevantYears, familyPrice_reductionRate, familyPriceYears)

        for i in range(len(adjustedPriceTurnover)):
            adjustedPriceTurnover[i] += turnover_family[i]
            
print(overallAnnualTurnoverAdjusted)

# """Calculate annual customer turnover with RFP not considering family prices"""
# annualSingleMargin_base = [x-y for x, y in zip(consideredBasePrices, consideredVhk)]
# annualTurnoverConsideredRFP_base = [x*y for x, y in zip(annualSingleMargin_base, consideredVolumes)]

# annualCustomerTurnOver_base = [x+y for x,y in (annualCustomerTurnover_base, annualTurnoverConsideredRFP_base)] #benchmark; no family prices, incl current rfp

# """Calculate turnover with min prices considering family prices"""
# annualSingleMargin_min = [x-y for x, y in zip(minPrices, consideredVhk)]
# annualTurnoverConsideredRFP_min = [x*y for x, y in zip(annualSingleMargin_min, consideredVolumes)]

# familyPriceIndices = []

# for i in range(len(deltaFamilyPrice)):
#     if deltaFamilyPrice[i] <= annualTurnoverConsideredRFP_min[i]:
#         familyPriceIndices.append(i)

# for rfp in relevantRfps:
#     for j in range(len(relevantYears)):
#         if j in familyPriceIndices:
#             turnover_family = getRfpTurnOver_familyPrice(rfp)
#         else:
#             turnover_family = getRfpTurnOver_base(rfp)
#     for i in range(len(annualTurnoverConsideredRFP_min)):
#             annualTurnoverConsideredRFP_min[i] += turnover_family[i]

# """Calculate turnover with max prices considering family prices"""
# annualSingleMargin_max = [x-y for x, y in zip(maxPrices, consideredVhk)]
# annualTurnoverConsideredRFP_max = [x*y for x, y in zip(annualSingleMargin_max, consideredVolumes)]

# familyPriceIndices = []

# for i in range(len(deltaFamilyPrice)):
#     if deltaFamilyPrice[i] <= annualTurnoverConsideredRFP_max[i]:
#         familyPriceIndices.append(i)

# for rfp in relevantRfps:
#     for j in range(len(relevantYears)):
#         if j in familyPriceIndices:
#             turnover_family = getRfpTurnOver_familyPrice(rfp)
#         else:
#             turnover_family = getRfpTurnOver_base(rfp)
#     for i in range(len(annualTurnoverConsideredRFP_min)):
#             annualTurnoverConsideredRFP_max[i] += turnover_family[i]

#Output: 4 Kennzahlen pro Jahr: 1) jährlicher Umsatz des Kunden ohne consideredRFP, keine Berücksichtigung von FamilyPrices
                                #2) jährlicher Umsatz des Kunden mit consideredRFP, keine Berücksichtigung von FamilyPrices
                                #3) jährlicher Umsatz des Kunden mit consideredRFP zu minPreisen, Berücksichtigung von Family Prices
                                #4) jährlicher Umsatz des Kunden mit consideredRFP zu maxPreisen, Berücksichtigung von Family Prices