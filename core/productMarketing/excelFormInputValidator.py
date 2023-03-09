# from .views import TypeOfParameter, operatingSystem
import os
from enum import Enum
from typing import Any, Iterable, MutableSequence, TypeVar


def is_not_blank(s):
    return bool(s and not s.isspace())


class operatingSystem(Enum):
    macOs = 1
    windows = 2
    linux = 3


class TypeOfParameter(Enum):
    volumes = 1
    prices = 2


# operand: abstraction for volumes or prices
class errorTypesExcelValidation(Enum):
    none = 0
    yearsNotCongruent = 1
    volumesNotCongruent = 2
    pricesNotCongruent = 3
    yearsAndOperandsCountDoNotMatch = 4
    yearsEmpty = 5
    pricesEmpty = 6
    yearsBadCharacter = 7
    volumesBadCharacter = 8
    volumesEmpty = 9
    dataEmpty = 10
    pricesBadCharacter = 11
    yearsDoNotMatchSop = 12
    formatNotMatchingTemplate = 13
    monthsNotCongruent = 14
    monthsAndOperandsCountDoNotMatch = 15
    monthsEmpty = 16
    monthsBadCharacter = 17
    yearsNotGoingUp = 18
    monthsNotGoingUp = 19

    def __str__(self):
        # python < v3.10 does not support switch statements...

        if self.value == 0:
            return "No error found."
        elif self.value == 1:
            return "Years are not consecutive or congruent. Check also if you did not mistake quantities for years or entered prices instead of volumes. "
        elif self.value == 2:
            return "Volumes are not consecutive or congruent with the entered years. "
        elif self.value == 3:
            return "Prices are not consecutive or congruent with the entered years. "
        elif self.value == 4:
            return "Years and prices or volumes do not match. "
        elif self.value == 5:
            return "Years are empty. "
        elif self.value == 6:
            return "Prices are empty or equal zero. "
        elif self.value == 7:
            return "Years format or entered characters are incorrect. "
        elif self.value == 8:
            return "Volumes format or entered characters are incorrect. "
        elif self.value == 9:
            return "Volumes are completely empty. "
        elif self.value == 10:
            return "Input is completely empty. "
        elif self.value == 11:
            return "Prices format or entered characters are incorrect. Please avoid using thousands separators. You might also miss one or multiple prices. "
        elif self.value == 12:
            return "The entered years do not match the Start of Production. "
        elif self.value == 13:
            return "Input format does not match the required template. Check if you forgot to enter years, prices or volumes. "
        elif self.value == 14:
            return "Months are not consecutive or congruent. Check also if you did not mistake quantities for months. "
        elif self.value == 15:
            return "Months and prices or volumes do not match. "
        elif self.value == 16:
            return "Months are empty. "
        elif self.value == 17:
            return "Months format or entered characters are incorrect. "
        elif self.value == 18:
            return "Years are getting lower at some point. "
        elif self.value == 19:
            return "Months are getting lower at some point. "


T = TypeVar("T")

# checks if all values are convertible to ints, eg no strange characters


def checkIfInt(input: MutableSequence[str]) -> bool:
    areAllInt: bool = True
    for i in range(1, (len(input))+1, 1):
        if is_not_blank(input[i-1]) == True:

            # abort if not possible to convert to int and set error flag
            try:
                intAttempt = int(input[i-1])

            except:
                areAllInt = False
                break
        else:
            try:
                intAttempt = int(input[i-1])
            except:
                areAllInt = False
                break
    print("are all int?", areAllInt)
    return areAllInt


# checks if all floats
def checkIfFloats(input: MutableSequence[str]) -> bool:
    areAllFloats: bool = True
    for i in range(1, (len(input)), 1):
        if is_not_blank(input[i]) == True:
            try:
                floatAttempt = float(input[i])
            except:
                areAllFloats = False
                break
    return areAllFloats


# checks if all values are consecutive, eg. 2020 -> 2021 -> 2022 -> 2023... if a gap, returns false
def checkYearsCongruency(years: MutableSequence[int]) -> bool:
    areYearsCongruent: bool = True

    for i in range(1, (len(years)), 1):
        delta = years[i] - years[i - 1]
        #print("i", i, "delta", delta, "years", years[i], years[i - 1])
        if abs(delta) > 1:
            areYearsCongruent = False
            break
        elif delta == 0:
            areYearsCongruent = False
            break

    # check that years are realistic (e.g. not mistaken with volumes)

    for i in range(1, (len(years)), 1):
        if (years[i] > 2060) or (years[i] < 2010):
            areYearsCongruent = False
            break

    return areYearsCongruent


# entry point for checking years
def checkYears(yearsInput: MutableSequence[str], sop: int) -> tuple[bool, MutableSequence[errorTypesExcelValidation]]:

    errorMutableSequence: MutableSequence[errorTypesExcelValidation] = []
    errorsFound: bool = False
    areYearsCongurent: bool = True

    if len(yearsInput) > 0:
        # check that years are ints. if not return errorTypesExcelValidation.yearsBadCharacter
        areAllInt = checkIfInt(input=yearsInput)

        if areAllInt == False:
            errorsFound = True
            errorMutableSequence.append(
                errorTypesExcelValidation.yearsBadCharacter)
        else:
            # convert to int
            years: MutableSequence[int] = []
            for i in range(0, (len(yearsInput)), 1):
                years.append(int(yearsInput[i]))

            # check that the first year matches the start of production
            if years[0] != sop:
                errorsFound = True
                errorMutableSequence.append(
                    errorTypesExcelValidation.yearsDoNotMatchSop
                )

            # check that years are congruent (Gaps). if not return errorTypesExcelValidation.yearsNotCongruent
            areYearsCongurent = checkYearsCongruency(years=years)

            if areYearsCongurent == False:
                errorsFound = True
                errorMutableSequence.append(
                    errorTypesExcelValidation.yearsNotCongruent)
    else:
        errorMutableSequence.append(errorTypesExcelValidation.yearsEmpty)
        errorsFound = True

    return errorsFound, errorMutableSequence


def checkMonthsCongruency(years: MutableSequence[int], months: MutableSequence[int]) -> tuple[bool, bool, bool, bool]:
    areMonthsCongruent: bool = True
    areYearsCongruent: bool = True
    areYearsGoingUp: bool = True
    areMonthsGoingUp: bool = True
    yearCounter = 0
    for i in range(1, (len(years)), 1):
        deltaY = years[i] - years[i - 1]
        #print("i", i, "deltaY", deltaY, "years", years[i], years[i - 1])
        if abs(deltaY) > 1:
            areYearsCongruent = False
            break
        if deltaY == 0:
            yearCounter = yearCounter + 1
            #print("YearCounter:", yearCounter)
            if yearCounter == 12:
                areYearsCongruent = False
        elif deltaY == -1:
            areYearsGoingUp = False
            break
        else:
            if yearCounter < 11:
                #print("else case",yearCounter)
                areYearsCongruent = False
            yearCounter = 0
    for j in range(1, (len(months)), 1):
        if j % 12 == 0:
            # print(months[j])
            if months[j] != 1:
                #print("special case", months[j])
                areMonthsCongruent = False
                break
            continue
        deltaM = months[j] - months[j - 1]
        #print("j", j, "deltaM", deltaM, "months", months[j], months[j - 1])
        if abs(deltaM) > 1 or deltaM == 0:
            areMonthsCongruent = False
            break
        elif deltaM == -1:
            areMonthsGoingUp = False
            break

    # check that years and months are realistic (e.g. not mistaken with volumes), for months

    for i in range(1, (len(years)), 1):
        if (years[i] > 2060) or (years[i] < 2010):
            areYearsCongruent = False
            break

    for i in range(1, (len(months)), 1):
        if (months[i] > 12) or (years[i] < 1):
            areMonthsCongruent = False
            break

    return areYearsCongruent, areMonthsCongruent, areYearsGoingUp, areMonthsGoingUp


# entry point for checking years
def checkMonths(
    yearsInput: MutableSequence[str], monthsInput: MutableSequence[str], sop: int
) -> tuple[bool, MutableSequence[errorTypesExcelValidation]]:

    errorMutableSequence: MutableSequence[errorTypesExcelValidation] = []
    errorsFound: bool = False
    areYearsCongurent: bool = True
    areMonthsCongurent: bool = True
    print("running checkMonths", yearsInput)
    years: MutableSequence[int] = []

    if len(yearsInput) > 0:
        # check that years are ints. if not return errorTypesExcelValidation.yearsBadCharacter
        areAllIntY = checkIfInt(input=yearsInput)
        areAllIntM = checkIfInt(input=monthsInput)
        if areAllIntY == False:
            errorsFound = True
            errorMutableSequence.append(
                errorTypesExcelValidation.yearsBadCharacter)
            print("aAA")
        else:
            # convert to int
            for i in range(0, (len(yearsInput)), 1):
                if is_not_blank(yearsInput[i]) == True:
                    years.append(int(yearsInput[i]))

            print("BBB")

        if areAllIntM == False:
            errorsFound = True
            errorMutableSequence.append(
                errorTypesExcelValidation.monthsBadCharacter)
        else:
            months: MutableSequence[int] = []
            for i in range(0, (len(monthsInput)), 1):
                if is_not_blank(monthsInput[i]) == True:
                    months.append(int(monthsInput[i]))

        if errorsFound == False:
            # check that the first year matches the start of production
            if years[0] != sop:
                errorsFound = True
                errorMutableSequence.append(
                    errorTypesExcelValidation.yearsDoNotMatchSop
                )

            # check that years and months are congruent (Gaps). if not return errorTypesExcelValidation.yearsNotCongruent
            areYearsCongruent, areMonthsCongruent, areYearsGoingUp, areMonthsGoingUp = checkMonthsCongruency(
                years=years, months=months)

            if areYearsCongruent == False:
                errorsFound = True
                errorMutableSequence.append(
                    errorTypesExcelValidation.yearsNotCongruent)

            if areMonthsCongruent == False:
                errorsFound = True
                errorMutableSequence.append(
                    errorTypesExcelValidation.monthsNotCongruent)
            if areYearsGoingUp == False:
                errorsFound = True
                errorMutableSequence.append(
                    errorTypesExcelValidation.yearsNotGoingUp)

            if areMonthsGoingUp == False:
                errorsFound = True
                errorMutableSequence.append(
                    errorTypesExcelValidation.monthsNotGoingUp)
    else:
        errorMutableSequence.append(errorTypesExcelValidation.yearsEmpty)
        errorsFound = True

    if len(monthsInput) == 0:
        errorMutableSequence.append(errorTypesExcelValidation.monthsEmpty)
        errorsFound = True

    return errorsFound, errorMutableSequence


# check if prices are congruent (gaps) and number vs. years
def checkPricesCongruency(
    prices: MutableSequence[float], years: MutableSequence[int]
) -> tuple[bool, MutableSequence[errorTypesExcelValidation]]:
    errorMutableSequence: MutableSequence[errorTypesExcelValidation] = []
    errorsFound: bool = False
    arePricesCongurent: bool = True

    # check first no gaps exist

    # check against years
    if len(prices) != len(years):
        errorsFound = True
        errorMutableSequence.append(
            errorTypesExcelValidation.pricesNotCongruent)

    return errorsFound, errorMutableSequence


# entry point for checking prices
def checkPrices(
    pricesInput: MutableSequence[str], years: MutableSequence[int]
) -> tuple[bool, MutableSequence[errorTypesExcelValidation]]:

    errorMutableSequence: MutableSequence[errorTypesExcelValidation] = []
    errorsFound: bool = False
    arePricesCongurent: bool = True
    pricesFloat: MutableSequence[float] = []

    if len(pricesInput) > 0:
        print("len prices input", len(pricesInput))
        """
        # try to cast to floats
        try:
            for i in range(0, (len(pricesInput)), 1):
                print(i, "casting", pricesInput[i])
                pricesFloat.append(float(pricesInput[i]))
        except:
            print("fatal error, could not cast to float")
            errorsFound = True
            errorMutableSequence.append(
                errorTypesExcelValidation.pricesBadCharacter)
        """

        # check that prices are floats.
        areAllFloat = checkIfFloats(input=pricesInput)
        print("are all float??", areAllFloat, "prices input", pricesInput)
        if areAllFloat == False:
            errorsFound = True
            errorMutableSequence.append(
                errorTypesExcelValidation.pricesBadCharacter)
        else:
            # convert to floats
            prices: MutableSequence[float] = []
            for i in range(0, (len(pricesInput)), 1):
                prices.append(float(pricesInput[i]))
            # check that prices are congruent with years.
            arePricesNotCongurent, errors = checkPricesCongruency(
                prices=prices, years=years
            )

            if arePricesNotCongurent == True:
                errorMutableSequence.extend(errors)
                errorsFound = True

            # are all prices == zero?
            if(max(prices) > 0.0):
                print("at least one price is not zero!")
            else:
                errorsFound = True
                errorMutableSequence.append(
                    errorTypesExcelValidation.pricesEmpty)

    else:
        errorMutableSequence.append(errorTypesExcelValidation.pricesEmpty)
        errorsFound = True

    return errorsFound, errorMutableSequence


# checks if volumes are contiguous (no gaps) and if number matches length of years
def checkVolumesCongruency(
    volumes: MutableSequence[int], years: MutableSequence[int]
) -> tuple[bool, MutableSequence[errorTypesExcelValidation]]:
    errorMutableSequence: MutableSequence[errorTypesExcelValidation] = []
    errorsFound: bool = False
    areVolumesCongurent: bool = True

    """
    ### check first no gaps exist (0 volume), if not at beggining nor end
    for i in range (1, (len(volumes)), 1):
        if (volumes[i] == 0)
    """
    print("checking volumes congruency", len(volumes), len(years))
    # check against years
    if len(volumes) != len(years):
        errorsFound = True
        errorMutableSequence.append(
            errorTypesExcelValidation.volumesNotCongruent)
        print("volumes are not congruent with years!")

    return errorsFound, errorMutableSequence


# entry point for checking volumes
def checkVolumes(
    volumesInput: MutableSequence[str], years: MutableSequence[int]
) -> tuple[bool, MutableSequence[errorTypesExcelValidation]]:
    print("entry point volumes check, input", volumesInput)
    errorMutableSequence: MutableSequence[errorTypesExcelValidation] = []
    errorsFound: bool = False
    areVolumesCongurent: bool = True

    if len(volumesInput) > 0:
        # check that years are ints. if not return errorTypesExcelValidation.yearsBadCharacter
        areAllInt = checkIfInt(input=volumesInput)

        if areAllInt == False:
            errorsFound = True
            errorMutableSequence.append(
                errorTypesExcelValidation.volumesBadCharacter)
        else:
            # convert to ints
            volumes: MutableSequence[int] = []
            for i in range(0, (len(volumesInput)), 1):
                if is_not_blank(volumesInput[i]) == True:
                    volumes.append(int(volumesInput[i]))

            # check that years are congruent with volumes.
            areVolumesNotCongurent, errors = checkVolumesCongruency(
                volumes=volumes, years=years
            )
            print("outputs", areVolumesCongurent, errors)
            if areVolumesNotCongurent == True:
                errorMutableSequence.extend(errors)
                errorsFound = True

    else:
        errorMutableSequence.append(errorTypesExcelValidation.volumesEmpty)
        errorsFound = True

    print("found volumes errors?", errorsFound)
    return errorsFound, errorMutableSequence


# only for combinations of years and prices or years and volumes.
# returns an array of years (Ints) and an array of volumes (Ints) or prices (floats), as well as an error type
# tbd: handling of locale (decimal and thousands separator)
def checkExcelFormInput(
    excelData: str, dataType: TypeOfParameter, sop: int
) -> tuple[
    MutableSequence[int],
    MutableSequence[Any],
    MutableSequence[errorTypesExcelValidation],
]:
    errorMutableSequence: MutableSequence[errorTypesExcelValidation] = []
    outputData: MutableSequence[Any] = []
    years: MutableSequence[int] = []
    volumesOutput: MutableSequence[int] = []
    pricesOutput: MutableSequence[float] = []
    yearsIsOnError: bool = False
    volumesIsOnError: bool = False
    pricesIsOnError: bool = False

    print("excelData")
    print(excelData)
    print("len", len(excelData))
    print("checking with sop", sop)
    if (len(excelData) > 0) and (excelData.isspace() == False):

        print("excel data count", len(excelData))
        excelData = excelData.replace("\r", " ")

        print(excelData.split("\n"))
        rows = excelData.split("\n")

        # if less or more than 2 entries, then something went catastrophically wrong! (2 lines)
        if len(rows) != 2:
            errorMutableSequence.append(
                errorTypesExcelValidation.formatNotMatchingTemplate
            )
            print("len rows is not 2!")
            if len(errorMutableSequence) > 0:
                for i in range(0, (len(errorMutableSequence)), 1):
                    print(i, "Afound error:",
                          errorMutableSequence[i].__str__())

            return [], [], errorMutableSequence

        # makes arrays
        yearsInput = rows[0].strip().split(",")  # ("\t")

        if len(yearsInput) > 0:
            print("years input --->", yearsInput)
            for i in range(0, (len(yearsInput)), 1):
                yearsInput[i] = yearsInput[i].strip()

                # try to check if there is a random space character. if yes, return on error and request the user to copy and paste purely from excel, without manipulating data in between.
                for string in yearsInput[i]:
                    if string.isspace():
                        errorMutableSequence.append(
                            errorTypesExcelValidation.yearsBadCharacter
                        )
                        print("string is or contains a space! returning on error")
                        yearsIsOnError = True

                    if string.isdigit() == False:
                        errorMutableSequence.append(
                            errorTypesExcelValidation.yearsBadCharacter
                        )
                        print("string is or contains a space! returning on error")
                        yearsIsOnError = True

        # check years congruency, conversion to Int, match to SOP
        if yearsIsOnError == False:
            print("---> years is not on error step 1!")
            yearsIsOnError, yearsErrors = checkYears(
                yearsInput=yearsInput, sop=sop)

            if yearsIsOnError == False:
                print(
                    "---> years is not on error step 2!",
                    dataType,
                    "of type",
                    type(dataType),
                    "is volumes?",
                    dataType == TypeOfParameter.volumes,
                )

                for i in range(0, (len(yearsInput)), 1):
                    years.append(int(yearsInput[i]))

                # plausibility checks on prices
                if dataType == TypeOfParameter.prices:

                    pricesInput = rows[1].split(",")

                    if len(pricesInput) > 0:
                        for i in range(0, (len(pricesInput)), 1):

                            # [i] = years[i].strip()
                            pricesInput[i] = pricesInput[i].strip()
                            # tbd how to deal with locales for decimal / thousands separators
                            pricesInput[i] = str(
                                pricesInput[i]).replace(",", ".")

                        # try to check if there is a random space character. if yes, return on error and request the user to copy and paste purely from excel, without manipulating data in between.
                        for string in pricesInput:
                            print(
                                "i",
                                i,
                                "is space?",
                                string.isspace(),
                                "string:",
                                string,
                                "is digit?",
                                string.isdigit(),
                            )
                            if string.isspace():
                                errorMutableSequence.append(
                                    errorTypesExcelValidation.pricesBadCharacter
                                )
                                print(
                                    "string is or contains a space! returning on error"
                                )
                                pricesIsOnError = True

                            """                            
                            if string not in ["0", ]:
                                errorMutableSequence.append(errorTypesExcelValidation.pricesBadCharacter)
                                print("string is not a number but a special character!!")

                                pricesIsOnError = True
                            """

                        # check prices for congruency with years, characters
                        """
                        check with possible conflict of requirement 123:
                        'prices have to be entered before the SOP and EOP due to FY/CY calculations (missing three months in EOP - 1y).'
                        """

                        if pricesIsOnError == False:
                            pricesIsOnError, pricesErrors = checkPrices(
                                pricesInput=pricesInput, years=years
                            )
                            print("prices check step C", pricesIsOnError,
                                  "%%% errors", pricesErrors)
                            if pricesIsOnError == False:
                                for i in range(0, (len(pricesInput)), 1):
                                    pricesOutput.append(float(pricesInput[i]))
                                outputData = pricesOutput
                            else:
                                errorMutableSequence.extend(pricesErrors)
                    else:
                        errorMutableSequence.append(
                            errorTypesExcelValidation.pricesEmpty
                        )

                # plausibility checks on volumes
                elif dataType == TypeOfParameter.volumes:
                    volumesInput = rows[1].strip().split(",")
                    print("volumes input", volumesInput)
                    if len(volumesInput) > 0:

                        print("volumes input pre strip", volumesInput)
                        for i in range(0, (len(volumesInput)), 1):
                            volumesInput[i] = volumesInput[i].strip()

                        # try to check if there is a random space character. if yes, return on error and request the user to copy and paste purely from excel, without manipulating data in between.
                        for string in volumesInput:
                            if string.isspace():
                                errorMutableSequence.append(
                                    errorTypesExcelValidation.volumesBadCharacter
                                )
                                print(
                                    "string is or contains a space! returning on error"
                                )
                                volumesIsOnError = True
                            if string.isdigit() == False:
                                errorMutableSequence.append(
                                    errorTypesExcelValidation.volumesBadCharacter
                                )
                                volumesIsOnError = True

                        if volumesIsOnError == False:
                            # check volumes for congruency with years, characters, etc.
                            volumesIsOnError, volumesErrors = checkVolumes(
                                volumesInput=volumesInput, years=years
                            )

                            if volumesIsOnError == False:
                                for i in range(0, (len(volumesInput)), 1):
                                    volumesOutput.append(int(volumesInput[i]))

                                outputData = volumesOutput
                            else:
                                errorMutableSequence.extend(volumesErrors)

                    else:
                        errorMutableSequence.append(
                            errorTypesExcelValidation.volumesEmpty
                        )
            else:
                errorMutableSequence.extend(yearsErrors)
        else:
            # errorMutableSequence.extend(yearsErrors)
            print("statement not req")

    else:
        errorMutableSequence.append(errorTypesExcelValidation.dataEmpty)

    if len(errorMutableSequence) > 0:
        for i in range(0, (len(errorMutableSequence)), 1):
            print(
                i, "################# Bfound error:", errorMutableSequence[i].__str__(
                )
            )

    print("########### ---> FINAL OUTPUT")
    print("errors", errorMutableSequence)
    print("years", years)
    print("volumes or prices", outputData)
    return years, outputData, errorMutableSequence


def checkExcelFormMonthInput(
    excelData: str, dataType: TypeOfParameter, sopYear: int,
) -> tuple[
    MutableSequence[int],
    MutableSequence[int],
    MutableSequence[Any],
    MutableSequence[errorTypesExcelValidation],
]:
    errorMutableSequence: MutableSequence[errorTypesExcelValidation] = []
    outputData: MutableSequence[Any] = []
    years: MutableSequence[int] = []
    months: MutableSequence[int] = []
    volumesOutput: MutableSequence[int] = []
    pricesOutput: MutableSequence[float] = []
    yearsIsOnError: bool = False
    monthsIsOnError: bool = False
    volumesIsOnError: bool = False
    pricesIsOnError: bool = False

    print("excelData")
    print(excelData)
    print("len", len(excelData))
    print("checking with sop", sopYear)
    if (len(excelData) > 0) and (excelData.isspace() == False):

        print("excel data count", len(excelData))
        excelData = excelData.replace("\r", " ")

        print(excelData.split("\n"))
        rows = excelData.split("\n")

        # if less or more than 2 entries, then something went catastrophically wrong! (2 lines)
        if len(rows) != 3:
            errorMutableSequence.append(
                errorTypesExcelValidation.formatNotMatchingTemplate
            )
            print("len rows is not 3!")
            if len(errorMutableSequence) > 0:
                for i in range(0, (len(errorMutableSequence)), 1):
                    print(i, "Afound error:",
                          errorMutableSequence[i].__str__())

            return [], [], [], errorMutableSequence

        # makes arrays
        yearsInput = rows[0].strip().split(",")  # ("\t")
        if len(yearsInput) > 0:
            print("years input --->", yearsInput)
            for i in range(0, (len(yearsInput)), 1):
                yearsInput[i] = yearsInput[i].strip()

                # try to check if there is a random space character. if yes, return on error and request the user to copy and paste purely from excel, without manipulating data in between.
                for string in yearsInput[i]:
                    if string.isspace():
                        errorMutableSequence.append(
                            errorTypesExcelValidation.yearsBadCharacter
                        )
                        print(
                            "years input string is or contains a space! returning on error1")
                        yearsIsOnError = True

                    if string.isdigit() == False:
                        errorMutableSequence.append(
                            errorTypesExcelValidation.yearsBadCharacter
                        )
                        print(
                            "years input string is or contains a space! returning on error2")
                        yearsIsOnError = True

        monthsInput = rows[1].strip().split(",")
        if len(monthsInput) > 0:
            print("months input --->", monthsInput)
            for i in range(0, (len(monthsInput)), 1):
                monthsInput[i] = monthsInput[i].strip()
                for string in monthsInput[i]:
                    if string.isspace():
                        errorMutableSequence.append(
                            errorTypesExcelValidation.monthsBadCharacter
                        )
                        print("string is or contains a space! returning on error3")
                        monthsIsOnError = True

                    if string.isdigit() == False:
                        errorMutableSequence.append(
                            errorTypesExcelValidation.monthsBadCharacter
                        )
                        print("string is or contains a space! returning on error4")
                        monthsIsOnError = True

        # check years congruency, conversion to Int, match to SOP
        if yearsIsOnError == False and monthsIsOnError == False:
            print("---> years and months is not on error step 1!",
                  errorMutableSequence)
            checkError, checkErrors = checkMonths(
                yearsInput=yearsInput, monthsInput=monthsInput, sop=sopYear)

            if checkError == False:
                print(
                    "---> years is not on error step 2!",
                    dataType,
                    "of type",
                    type(dataType),
                    "is volumes?",
                    dataType == TypeOfParameter.volumes,
                    errorMutableSequence
                )

                for i in range(0, (len(yearsInput)), 1):
                    if is_not_blank(yearsInput[i]) == True:
                        years.append(int(yearsInput[i]))
                for i in range(0, (len(monthsInput)), 1):
                    if is_not_blank(monthsInput[i]) == True:
                        months.append(int(monthsInput[i]))

                # plausibility checks on prices
                if dataType == TypeOfParameter.prices:

                    pricesInput = rows[2].split(",")

                    if len(pricesInput) > 0:
                        for i in range(0, (len(pricesInput)), 1):

                            # [i] = years[i].strip()
                            pricesInput[i] = pricesInput[i].strip()
                            # tbd how to deal with locales for decimal / thousands separators
                            pricesInput[i] = str(
                                pricesInput[i]).replace(",", ".")

                        # try to check if there is a random space character. if yes, return on error and request the user to copy and paste purely from excel, without manipulating data in between.
                        for string in pricesInput:
                            print(
                                "i",
                                i,
                                "is space?",
                                string.isspace(),
                                "string:",
                                string,
                                "is digit?",
                                string.isdigit(),
                            )
                            if string.isspace():
                                errorMutableSequence.append(
                                    errorTypesExcelValidation.pricesBadCharacter
                                )
                                print(
                                    "string is or contains a space! returning on error"
                                )
                                pricesIsOnError = True

                            """                            
                            if string not in ["0", ]:
                                errorMutableSequence.append(errorTypesExcelValidation.pricesBadCharacter)
                                print("string is not a number but a special character!!")

                                pricesIsOnError = True
                            """

                        # check prices for congruency with years, characters
                        """
                        check with possible conflict of requirement 123:
                        'prices have to be entered before the SOP and EOP due to FY/CY calculations (missing three months in EOP - 1y).'
                        """

                        if pricesIsOnError == False:
                            pricesIsOnError, pricesErrors = checkPrices(
                                pricesInput=pricesInput, years=years
                            )

                            if pricesIsOnError == False:
                                for i in range(0, (len(pricesInput)), 1):
                                    pricesOutput.append(float(pricesInput[i]))
                                outputData = pricesOutput
                            else:
                                errorMutableSequence.extend(pricesErrors)
                    else:
                        errorMutableSequence.append(
                            errorTypesExcelValidation.pricesEmpty
                        )

                # plausibility checks on volumes
                elif dataType == TypeOfParameter.volumes:
                    volumesInput = rows[2].strip().split(",")
                    print("volumes input", volumesInput)
                    if len(volumesInput) > 0:

                        print("volumes input pre strip", volumesInput)
                        for i in range(0, (len(volumesInput)), 1):
                            if is_not_blank(volumesInput[i]):
                                volumesInput[i] = volumesInput[i].strip()

                        # try to check if there is a random space character. if yes, return on error and request the user to copy and paste purely from excel, without manipulating data in between.
                        for string in volumesInput:
                            if is_not_blank(volumesInput[i]):

                                if string.isspace():
                                    errorMutableSequence.append(
                                        errorTypesExcelValidation.volumesBadCharacter
                                    )
                                    print(
                                        "string is or contains a space! returning on error"
                                    )
                                    volumesIsOnError = True
                                if string.isdigit() == False:
                                    errorMutableSequence.append(
                                        errorTypesExcelValidation.volumesBadCharacter
                                    )
                                    volumesIsOnError = True

                        if volumesIsOnError == False:
                            # check volumes for congruency with years, characters, etc.
                            volumesIsOnError, volumesErrors = checkVolumes(
                                volumesInput=volumesInput, years=years
                            )

                            if volumesIsOnError == False:
                                for i in range(0, (len(volumesInput)), 1):
                                    if is_not_blank(volumesInput[i]):
                                        volumesOutput.append(
                                            int(volumesInput[i]))

                                outputData = volumesOutput
                            else:
                                errorMutableSequence.extend(volumesErrors)
                        else:
                            print("volumes is on error, AAA",
                                  errorMutableSequence)

                    else:
                        errorMutableSequence.append(
                            errorTypesExcelValidation.volumesEmpty
                        )
            else:
                errorMutableSequence.extend(checkErrors)
        else:
            # errorMutableSequence.extend(yearsErrors)
            print("statement not req")

    else:
        errorMutableSequence.append(errorTypesExcelValidation.dataEmpty)

    if len(errorMutableSequence) > 0:
        for i in range(0, (len(errorMutableSequence)), 1):
            print(
                i, "################# Bfound error:", errorMutableSequence[i].__str__(
                )
            )

    print("########### ---> FINAL OUTPUT")
    print("errors", errorMutableSequence)
    print("years", years)
    print("months", months)
    print("volumes or prices", outputData)
    return years, months, outputData, errorMutableSequence


# for testing with MyPy
# excelString = ""
# excelString = " "

# random string 1
# excelString = "aa  asss 1233"
# random string 2
# excelString = "dfghj%%%%%%%!!!!"
# random string 3
# excelString = "dfghj456789"
# random string 4
# excelString = "aaaaddddd"
# random string 5
# excelString = "111111111111111111111"
# random string 6
# excelString = "2000"
# random string 7
# excelString = "    2020	2021"
# one volume missing
# excelString = "2020	2021\n 2"
# tab character etnered manually in vscode
# excelString = "2020	2021\n 2\t 2"
# one space character entered manually in vscode after the first volume
# excelString = "2020	2021\n 2 2"


# only years
# excelString = "2020 2021 2022 2023"
# one year missing
# excelString = "    2020	2021	2023	2024	2025	2026\n 2	2	2	2	2	2"
# volumes correct
# excelString = "    2020	2021	2022	2023	2024	2025\n 2	2	2	2	2	2"

# volumes instead of years
# excelString = "    3	3000	2023	2024	2025	2026\n 2	2	2	2	2	2"

# prices, years not congruent
# excelString = "2020	2021	2023	2024	2025	2026\n2,20	2,2	10,2	100000,4	5555,3	99,9"

# prices, correct, using commas. in Excel formatted as number, european locale (comma for decimal sep)
# excelString = "2020	2021	2022	2023	2024	2025\n2,20	2,2	10,2	100000,4	5555,3	99,9"

# prices, deleted a price manually in VSCode, using commas. in Excel formatted as number, european locale (comma for decimal sep)
# excelString = "2020	2021	2022	2023	2024	2025\n2,20		10,2	100000,4	5555,3	99,9"

# missing two final prices (excel cell empty)
# excelString = "2020	2021	2022	2023	2024	2025\n2,20	2,20	10,20	100000,40		"

# missing one initial price -> leads to strange parsing with numbers being separated
# excelString = "2020	2021	2022	2023	2024	2025\n	2,20	10,20	100000,40	10,20	10,20"

# prices, correct, alternating commas and dots for decimals. in Excel formatted as number, european locale (comma for decimal sep)
# excelString = "2020	2021	2022	2023	2024	2025\n2.20	2,2	10,2	100000.4	5555,3	99,9"

# prices, correct, alternating commas and dots for decimals and added thousands separators.
# excelString = "2020	2021	2022	2023	2024	2025\n2.20	2,2	10,2	10.0000.4	5,555,3	99,9"

# missing one price in the middle
# excelString = "2020	2021	2022	2023	2024	2025\n9,99	2,20		100000,40	10,20	10,20"

# prices, correct, volumes with decimals. in Excel formatted as number, european locale (comma for decimal sep)
"""
excelString = "2020.0	2021,1	2022	2023	2024	2025\n2.20	2,2	10,2	100000.4	5555,3	99,9"
excelString = "2020	2021,1	2022	2023	2024	2025\n2.20	2,2	10,2	100000.4	5555,3	99,9"
excelString = "2020,1	20211	2022	2023	2024	2025\n2.20	2,2	10,2	100000.4	5555,3	99,9"
excelString = "2020,1	2021	2022	2023	2024	2025\n2.20	2,2	10,2	100000.4	5555,3	99,9"
"""

# bad selection
excelString = "										                      																						2020	2021	2022	2023	2024	2025	2026	2027	2028	2029	2030	0	5	10	15	20	20	19	18	13	6	0	"

# excelString = "2020	2021 2022	2023	2024	2025\n2.20	2,2	10,2	100000.4	5555,3	99,9"
# years, outputData, errorMutableSequence = checkExcelFormInput(excelData = excelString, dataType = TypeOfParameter.prices, sop = 2020)

# years, outputData, errorMutableSequence = checkExcelFormInput(excelData = excelData, dataType = TypeOfParameter.volumes, sop = project.estimatedSop)

"""
print("mypy result %%%")
print(years)
print(outputData)
print(errorMutableSequence, "count", len(errorMutableSequence))
"""
