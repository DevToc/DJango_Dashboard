from turtle import position
import numpy as np
from scipy.stats import poisson
import pandas as pd
from scipy.interpolate import interp1d


def arraySum(arr):
    sum = 0
    for i in arr:
        sum = sum + i

    return(sum)


def interpolator(sop, eop, initialVolume, peakVolume, peakYear, distributionType, totalVolume):
    print("interpolating ----->!")

    # estimate total volume

    # poison
    if True:

        x = []

        if totalVolume != 0:
            # lam = peak year, relative
            relPeak = peakYear - sop
            print("rel peak", relPeak, "total volume", totalVolume)

            # lambda determines how far away is the production peak from the eop. the farther away, the larger the lambda value should be.
            # to do: iterate with lambdas until peak is reached at peak year...
            # to do: iterate until peak volume is respected
            lambdaValue = relPeak

            # do distribution for 10 years
            for i in range(0, (eop-sop + 1), 1):
                x.append(poisson.pmf(i, lambdaValue))
            print("count", len(x), "sum", arraySum(x))

            for i in range(0, eop-sop, 1):
                x[i] = x[i] * totalVolume

            print("---> final poisson distribution", x)

            return x


def checkConditions(sop, eop, initialVolume, peakVolume, peakYear, distributionType, totalVolume):

    eopSmallerEopError = False
    sopLargerPeakError = False
    peakLargerEopError = False
    peakVolError = False
    initialVolError = False
    totalVolumeError = False

    # only peak, sop, total volume
    if distributionType == "poisson":

        if int(sop) > int(peakYear):
            print("unplausible dates! 2")
            sopLargerPeakError = True

        if int(totalVolume) < 500:
            totalVolumeError = True
            print("unplausible total volume")

            """
            if sop >= eop:
                print("unplausible dates! 1")
                eopSmallerEopError = True

            if sop > peakYear:
                print("unplausible dates! 2")
                sopLargerPeakError = True

            if peakYear > eop:
                peakLargerEopError = True
                print("unplausible dates! 3")

            if peakVolume == 0:
                peakVolError = True
                print("unplausible volumes! 1")

            if initialVolume == 0:
                initialVolError = True
                print("unplausible volumes! 2")

            if (totalVolume < initialVolume) | (totalVolume < peakVolume):
                totalVolumeError = True
                print("unplausible total volume")
            """

    return eopSmallerEopError, sopLargerPeakError, peakLargerEopError, peakVolError, initialVolError, totalVolumeError


"""
Feb 2023: new monthly level interpolation for Poisson
"""
def interpolatorMonthly(sop, eop, totalVolume, peakYear):
    x = []
    
    if totalVolume != 0:
        # lam = peak year, relative
        relPeak = peakYear - sop
        print("%%% NEW interpolatorMonthly")
        print("rel peak", relPeak, "total volume", totalVolume)
        originalVolume = totalVolume

        # lambda determines how far away is the production peak from the eop. the farther away, the larger the lambda value should be.
        # to do: iterate with lambdas until peak is reached at peak year...
        # to do: iterate until peak volume is respected
        lambdaValue = relPeak * 12

        # do distribution for months years
        for i in range(0, ((eop-sop + 1)*12), 1):
            x.append(poisson.pmf(i, lambdaValue))

        print("count", len(x), "sum", arraySum(x))
        print("poisson x", x)

        # the distribution could have yielded a value of 0, so we need to adjust this

        for i in range(0, ((eop-sop + 1)*12), 1):
            calculatedVolume = x[i] * totalVolume
            x[i] = calculatedVolume

        # set a minimum of 1000 pieces or a percentage of the total volume
        boundary = 1000
        toBeSubtracted = 0
        for i in range(0, ((eop-sop + 1)*12), 1):
            xvalue = x[i]
            if xvalue < boundary:
                toBeSubtracted = toBeSubtracted + boundary
                x[i] = boundary
        print("to be subtracted", toBeSubtracted)

        if toBeSubtracted > 0:
            subtractionValue = toBeSubtracted / (len(x) - (toBeSubtracted % boundary))
            for i in range(0, ((eop-sop + 1)*12), 1):
                xvalue = x[i]
                if xvalue > boundary:
                    x[i] = xvalue - subtractionValue

        print("current sum x vs original volume", sum(x), originalVolume)

        if sum(x) != originalVolume:
            delta = sum(x) - originalVolume
            newSubtractionValue = delta / (len(x))
            for i in range(0, ((eop-sop + 1)*12), 1):
                x[i] = x[i] - newSubtractionValue


        print("---> final poisson distribution", x)
        print("%%% END interpolatorMonthly")

        return x


def yearToMonthPoissonSmoother(sop, eop, totalVolume, peakYear):

    print("poisson distribution for year to month ----->!")

    # estimate total volume

    # poison
    if True:
        x = []
        if totalVolume != 0:
            # lam = peak year, relative
            relPeakMonth = (peakYear - sop) * 12
            print("rel peak", relPeakMonth, "total volume", totalVolume)

            # lambda determines how far away is the production peak from the eop. the farther away, the larger the lambda value should be.
            # to do: iterate with lambdas until peak is reached at peak year...
            # to do: iterate until peak volume is respected
            lambdaValue = relPeakMonth
            monthInTotal = 12*(eop-sop)
            # do distribution for 10 years
            for i in range(0, monthInTotal, 1):
                x.append(poisson.pmf(i, lambdaValue))
            print("count", len(x), "sum", arraySum(x))

            for i in range(0, monthInTotal, 1):
                """
                Comment FF: Patric changed this line, but this lead to a massive destruction... rolled back to old version
                x[i] = x[i] * (totalVolume-monthInTotal*1000)+1000 #shifting the volumes up, so everything is at least 1000 but the total volume is still correct
                """
                x[i] = x[i] * totalVolume

            # at least 1...
            for i in range(0, len(x), 1):
                if x[i] < 1.0:
                    x [i] = 1.0


            #print("testing sum", arraySum(x))
            print("---> final poisson distribution", x)

            return x


'''
Input: StartOfProdcution, EndOfProduction (the start and end year), totalVolume= an array with the total volume for each year
Output: an array which has the volume for each month

Für alle Teilstrecken wird die Steigung (m) und t (y-Achse-Schnittpunkt) berechnet. 

'''


def calc_m_t(sop, eop, totalVolume):
    sop = int(sop)
    eop = int(eop)
    years = list(range(sop, eop+1))
    #print("using", sop, eop, "years", years, "total volume", totalVolume)
    years_adj = [x-sop for x in years]
    totalVolume_adj = [int(x)/12 for x in totalVolume]
    #print("totalVolume_adj", totalVolume_adj)

    totalVolume_adj = totalVolume_adj
    #print("years_adj", years_adj)

    waypointsx = []
    waypointsV = []
    waypointsV.append(totalVolume_adj[0])
    waypointsV.append(totalVolume_adj[1])
    waypointsx.append(0)
    waypointsx.append(1)
    m = []
    t = []
    for i in years_adj:  # [:-1]
        # first y=mx + t
        if i == 0:
            t.append(totalVolume_adj[0])
            m.append(totalVolume_adj[1] - t[0])
            waypointsV.append(m[0]*1.5+t[0])
            waypointsx.append(1.5)
        elif i == 1:
            continue
        else:
            #black line which can make high jumps, but is stetig 
            """
            Aussage Patric: black line ist die richtige. 
            Jahreslevel ist fast korrekt. Der kleine Fehler ist der Integrationsfehler (Riemann / Approximationsfehler) 
            """
            if True: 
                #print("i",i)
                #to make it go through the middle = the vol for year divided through 12 
                waypointsV.append(totalVolume_adj[i])
                waypointsx.append(i)

                m_val = (waypointsV[-1]-waypointsV[-2]) / \
                (waypointsx[-1]-waypointsx[-2])
                t_val = waypointsV[-1]-m_val * waypointsx[-1]
                print("black line m_val",m_val)
            
            
                t.append(t_val)
                m.append(m_val)

                waypointsV.append(m[i-1]*(i+0.5)+t[i-1])
                waypointsx.append(i+0.5)
            
                """
                comment FF: it was true until feb 11
                """
            if False: 
                """
                red line which is not stetig but looks better
                die Steigung der Teilstrecken wird in diesem Ansatz reduziert. 
                Dies kann zu Fehler auf Jahreslevel führen.
                """
                #if V[-1] is smaller or bigger than reduce to it  
                #print("i",i)
                #to make it go through the middle = the vol for year divided through 12 
                waypointsV.append(totalVolume_adj[i])
                waypointsx.append(i)

                m_val = (waypointsV[-1]-waypointsV[-2]) / \
                (waypointsx[-1]-waypointsx[-2])
                t_val = waypointsV[-1]-m_val * waypointsx[-1]
                #print("m_val",m_val)
            
            
                t.append(t_val)
                m.append(m_val)
                #if point not in condition adjust V
                if i != years_adj[-1]:
                    if totalVolume_adj[i] == totalVolume_adj[i+1]:
                        waypointsV.append(totalVolume_adj[i+1])
                    elif totalVolume_adj[i] < totalVolume_adj[i+1]:
                        if m[i-1]*(i+0.5)+t[i-1] > totalVolume_adj[i+1]:
                            waypointsV.append(totalVolume_adj[i+1])
                        else:
                            waypointsV.append(m[i-1]*(i+0.5)+t[i-1])  
                    elif totalVolume_adj[i] > totalVolume_adj[i+1]:
                        if m[i-1]*(i+0.5)+t[i-1] < totalVolume_adj[i+1]:
                            waypointsV.append(totalVolume_adj[i+1])
                        else:
                            waypointsV.append(m[i-1]*(i+0.5)+t[i-1])  
                            
                else:
                    waypointsV.append(m[i-1]*(i+0.5)+t[i-1])   
                waypointsx.append(i+0.5)
    boundries = waypointsx[::2]

    return m, t, boundries


"""
totalVolume ist ein Array
To Do: checken dass EOP und SOP passsen (0 Werte von Volumes entfernen...)
"""
def linSmoother(sop, eop, totalVolume):

    """
    steigung
    boundries = startpunkt X der Teilstrecken 
    """
    m, t, boundries = calc_m_t(sop, eop, totalVolume)
    resultvol = []
    print("boundries and m and t ",boundries, m, t)

    for i in range(1, len(boundries)*12+1):
        """
        x_val ist der einzelne monat (wo auf der x achse wird der monat beginnen)
        """

        x_val = i/12 - 0.5
        
        """
        wenn man vor dem ersten startpunkt ist, nimm mal 0
        special case, da es bei 0 begint
        """

        if x_val < boundries[0]:
            new_val = x_val*m[0]+t[0] 

            # wenn neeuer wert kleiner als 0 ist, dann auf 0 cappen
            if new_val < 0:
                resultvol.append(0)
            else:
                resultvol.append(new_val)

            """
            To Do: falls wert kleiner ist als 0, der negative wert müsste jetzt im gleichen Jahr an einem anderen Monat abgezogen werden,
            damit die gesamtsumme noch stimm. Und dann auch ein Check, damit dieser wert nicht unter 0 liegt. 
            """

        """
        letzter schritt benötigt auch eine besondere behandlung, da es auf 0 kommen muss
        es gibt kein Punkt... 
        """

        if x_val >= boundries[-1]:
            new_val = x_val*m[-1]+t[-1]
            if new_val < 0:
                resultvol.append(0)
            else:
                resultvol.append(new_val)

        """
        das ist für den mittleren path. 
        a) vom Mittelpunkt der Strecke (mitte vom Jahr) bis Ende des Jahres 
        b) und vom Anfang des Folgejahres bis Mitte vom Folgejahr
        """

        for idx, _ in enumerate(boundries):
            if idx == len(boundries)-1:
                continue
            if x_val < boundries[idx+1] and x_val >= boundries[idx]:
                new_val = x_val*m[idx]+t[idx]
                if new_val < 0:
                    resultvol.append(0)
                else:
                    resultvol.append(x_val*m[idx]+t[idx])

    """
    Comment FF: removed these lines since they were screweing stuff up, as in poison smoother.

    #to make sure there is at least 1000 per month we need to remove for each year 12000 (this are basically the 1000 which each month is going to have)
    #we determine how much procent it makes up of the total Volume, to know how much we taken away, to spread the amount which we taken away evenly,
    #we multiply each entry with the remaning procents (i.e. 10% taken away so multiply by 0.9)
    #after multiplying we give each month 1000 back of the taken amount, so in the end it has the same total amount and with have an adjusted slope
    totalVol = sum(totalVolume)
    #resultvol = []
    print("total vol", totalVol)

    if totalVol > 0:
        print(totalVol)
        procent = (totalVol - (eop-sop+1)*12000) / totalVol
        print(procent)
        resultvol = list(map(lambda x: x*procent + 1000, resultvol))
    else:
        resultvol = list(map(lambda x: x*1, resultvol))

    print("resultvol vol", resultvol)
    """

    return resultvol



def yearToMonthVolCalculator(sop, eop, volumeEntries):
    sop = int(sop)
    eop = int(eop)
    years = list(range(sop, eop+1))

    resultvol = []
    volumeAverage = [int(x)/12 for x in volumeEntries]
    decProcentList = [0.1,0.08,0.06,0.04,0.02,0,0,-0.02,-0.04,-0.06,-0.08,-0.1]
    incProcentList = [-0.1,-0.08,-0.06,-0.04,-0.02,0,0,0.02,0.04,0.06,0.08,0.1]
    lastProcentList = [0,0,0,0,0,0,0,0,0,0,0,0]
    for year in range(0,len(years)): 
        if year == len(years)-1:
            procentList = lastProcentList
        elif volumeAverage[year] > volumeAverage[year+1]:
            procentList = decProcentList
        elif volumeAverage[year] < volumeAverage[year+1]:
            procentList = incProcentList
        else:
            procentList = lastProcentList
        for month in range(0,12): 
            resultvol.append(volumeAverage[year]*(1+procentList[month]))


    '''
    print("first year", volumeEntries[0])  
    print(sum(resultvol[:12]))
    print("second year", volumeEntries[1])
    print(sum(resultvol[12:24]))
    print("third year",  volumeEntries[2])
    print(sum(resultvol[24:36]))
    print("third year",  volumeEntries[3])
    print(sum(resultvol[36:48]))
    '''
    return resultvol


