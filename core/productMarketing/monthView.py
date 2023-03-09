from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.urls import reverse_lazy, reverse
from .models import Project
from .forms import ProjectCreateForm, VolumeForm, PricingForm, VolumeAutomaticForm
from productMarketing.excelFormInputValidator import checkExcelFormInput, TypeOfParameter
from productMarketingDwh.models import *
from enum import Enum
from productMarketing.interpolator import *
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import F
from .models import Project, Product, SalesName, ProductPackage, ProductSeries


from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from productMarketing.excelFormInputValidator import checkExcelFormInput, TypeOfParameter
from django.utils.safestring import mark_safe
# from betterforms.multiform import MultiForm, MultiModelForm
from django.urls import reverse
from .models import Project, ProductFamily, ProductPackage, ProductSeries




import os
from enum import Enum
from typing import Any, Iterable, MutableSequence, TypeVar


'''
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
            return "Years are not consecutive or congruent. Check also if you did not mistake quantities for years. "
        elif self.value == 2:
            return "Volumes are not consecutive or congruent with the entered years. "
        elif self.value == 3:
            return "Prices are not consecutive or congruent with the entered years. "
        elif self.value == 4:
            return "Years and prices or volumes do not match. "
        elif self.value == 5:
            return "Years are empty. "
        elif self.value == 6:
            return "Prices are empty. "
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
       
        # abort if not possible to convert to int and set error flag
        try:
            intAttempt = int(input[i-1])
            
        except:
            areAllInt = False
            break
    return areAllInt


# checks if all floats
def checkIfFloats(input: MutableSequence[str]) -> bool:
    areAllFloats: bool = True

    for i in range(1, (len(input)), 1):
        try:
            floatAttempt = float(input[i])
        except:
            areAllFloats = False
            break
    return areAllFloats


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

    if len(pricesInput) > 0:
        # check that prices are floats.
        areAllFloat = checkIfFloats(input=pricesInput)

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







'''

'''
class CreateVolumeMonthExcelView(LoginRequiredMixin, View):
    print("$$$$$ running CreateVolumeMonthExcelView")
    template_name = "project/project_create_view/step2b_excel.html"
    form_class = VolumeMonthForm  
    success_url = reverse_lazy("create_pricing_view")

    def get(self, request, *args, **kwargs):

        # getting project instance that was created in first step
        project_id = request.session.get("project_id", None)
        if project_id:
            project = Project.objects.get(id=project_id)
            # getting estimated SOP from created project
            estimatedSop = project.estimatedSop
            # feeding that sop to startOfProduction field
            initial_dict = {"startOfProduction": estimatedSop} #month empty 
            context = {"form": self.form_class(initial=initial_dict)}
            print("rendering view with sop", estimatedSop)
            return render(request, self.template_name, context)
        else:
            return redirect(reverse("create_project_view"))

    def post(self, request, *args, **kwargs):
        project_id = request.session.get("project_id", None)
        project = Project.objects.get(id=project_id)
        estimatedSop = project.estimatedSop
        initial_dict = {"startOfProductionYear": estimatedSop}

        form = self.form_class(request.POST, initial=initial_dict)
        print("initialized form after post with project ID", project_id)
        if form.is_valid():
            # process the data submitted in the form...
            # following data will be extracted after running clean method defined under VolumeForm in forms.py file
            # field_value = form.cleaned_data.get("field_name")
            print("form is valid!")
            project = Project.objects.get(id=project_id)
            excelData = form.cleaned_data.get("excelData")
            excelData = excelData.strip()

            years, months, outputData, errorMutableSequence = checkExcelFormMonthInput( 
                excelData=excelData, dataType=TypeOfParameter.volumes, sopYear =project.estimatedSop)

            if len(errorMutableSequence) == 0:
                volumes = outputData
                years = list(set(years)).sort() #to make list unique
                print(len(years))
                volumesPost = []
                year = 0
                for i in range(0, (len(years))*12, 1):

                    if i != 0 and i % 12 == 0:
                        #print(int(years[year]), "----", int(volumes[i]))
                        year = year + 1
                    month = (i % 12)+1  # +1 so we dont have the 0th month
                    volumeObjectM, created = ProjectVolumeMonth.objects.get_or_create(
                        project=project, calenderYear=int(years[year]), month=month)
                    volumeObjectM.quantity = monthVolume[i]
                    volumeObjectM.save()
                    # volumesPost.append(f(int(years[0])+0.5+(i/12)))
                    print(i)
                    print(created, "---> volume month object,", volumeObjectM)

                # prepare the volume confirmation form
                firstYear = years[0]
                lastYear = years[len(years) - 1]
                deltaYears = int(firstYear) - 2020
                print("pre volumes array", volumesPost)
                print("last year", lastYear)
                if deltaYears > 0:
                    for i in range(0, deltaYears, 1):
                        volumesPost.insert(0, 0)

                deltaYearsEnd = 2045 - int(lastYear)
                print("deltaYearsEnd", deltaYearsEnd, deltaYearsEnd > 0)

                if (deltaYearsEnd > 0):
                    for i in range(0, deltaYearsEnd, 1):
                        volumesPost.append(0)
                        print("##")

            return redirect(self.success_url)
        else:

            context = {"form": form}
            return render(request, self.template_name, context)
'''



'''

class VolumeMonthForm(forms.Form):
    # for excel copy paste value
    excelData = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={"class": "d-none"},
        ),
    )
    # automatic distribution fields
    startOfProductionYear = forms.DecimalField(label="SoP Year", required=False)
    startOfProductionMonth = forms.DecimalField(label="SoP Month", required=False)

    def __init__(self, *args, **kwargs):

        super(VolumeMonthForm, self).__init__(*args, **kwargs)
        self.fields["excelData"].label = ""
        self.fields["startOfProductionYear"].widget.attrs["readonly"] = True
        self.fields["startOfProductionYear"].widget.attrs["hidden"] = True
        self.fields["startOfProductionMonth"].widget.attrs["readonly"] = True
        self.fields["startOfProductionMonth"].widget.attrs["hidden"] = True

        try:
            self.fields["startOfProductionYear"].initial = kwargs["initial"]["startOfProductionYear"]
            self.fields["startOfProductionMonth"].initial = kwargs["initial"]["startOfProductionMonth"]
        except:
            print("did not find initial values!")

    def clean(self):
        cleaned_data = super().clean()
        excelData = cleaned_data.get("excelData")
        startOfProductionYear = cleaned_data.get("startOfProductionYear")
        startOfProductionMonth = cleaned_data.get("startOfProductionMonth")
        print("cleaning form!!! with sop", startOfProductionYear, startOfProductionMonth)
        if excelData:

            # the front end already filters and keeps the two first rows, unless we are entering data on a monthly basis.
            # the form was filled with copy, paste excel field
            excelDataRowCount: int = len(excelData.split("\n"))
            print("$$$ count of excel data rows", excelDataRowCount)

            if excelDataRowCount != 3:
                raise ValidationError(
                    "You need to enter three rows if working on calendar year basis!"
                )

            # try:
            years, months, volume = excelData.split("\n")
            print("##### volume form split, years", years)
            print("##### volume form split, months", months)
            print("##### volume form split, volumes", volume)

            yearsCheck, monthsCheck, outputDataCheck, errorMutableSequence = checkExcelFormMonthInput(
                excelData=excelData, dataType=TypeOfParameter.volumes, sopYear=startOfProductionYear)
            print("stepB", errorMutableSequence, len(errorMutableSequence))

            if len(errorMutableSequence) > 0:
                errorString = ""
                print("1234")
                errorMutableSequence = list(
                    dict.fromkeys(errorMutableSequence))
                for error in errorMutableSequence:
                    errorString = errorString + error.__str__()

                print("$$$$$$$$$$$$$$$$$$$$$$ final error string:", errorString)
                print("12345")

                raise ValidationError(
                    str(errorString)
                )

            else:
                print("statement b")
                cleaned_data["years"] = years
                cleaned_data["months"] = months
                cleaned_data["volume"] = volume
                cleaned_data["excelData"] = excelData

        else:
            print("##### raising validation error!")
            # case nothing was entered return on error
            raise ValidationError(mark_safe(('Input required! If you do not want to enter data manually, please go to the <a href="{0}">Automatic Volume Distribution</a>.'
                                             ).format(reverse('create_volume_automatic_view'))))

        return cleaned_data

'''


'''
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
                        print("string is or contains a space! returning on error1")
                        yearsIsOnError = True

                    if string.isdigit() == False:
                        errorMutableSequence.append(
                            errorTypesExcelValidation.yearsBadCharacter
                        )
                        print("string is or contains a space! returning on error2")
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
            print("---> years and months is not on error step 1!")
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
                )

                for i in range(0, (len(yearsInput)), 1):
                    years.append(int(yearsInput[i]))
                for i in range(0, (len(monthsInput)), 1):
                    months.append(int(monthsInput[i]))

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


# checks if all values are consecutive, eg. 0 -> 1 -> 2 -> 3... if a gap, returns false
#months start with 1 and end with 12
def checkMonthsCongruency(years: MutableSequence[int], months: MutableSequence[int]) -> bool:
    areMonthsCongruent: bool = True
    areYearsCongruent: bool = True
    areYearsGoingUp: bool = True
    areMonthsGoingUp: bool = True
    yearCounter= 0
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
            #print(months[j])
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

    if len(yearsInput) > 0:
        # check that years are ints. if not return errorTypesExcelValidation.yearsBadCharacter
        areAllIntY = checkIfInt(input=yearsInput)
        areAllIntM = checkIfInt(input=monthsInput)

        if areAllIntY == False:
            errorsFound = True
            errorMutableSequence.append(
                errorTypesExcelValidation.yearsBadCharacter)
        else:
            # convert to int
            years: MutableSequence[int] = []
            for i in range(0, (len(yearsInput)), 1):
                years.append(int(yearsInput[i]))

        if areAllIntM == False:
            errorsFound = True
            errorMutableSequence.append(
                errorTypesExcelValidation.monthsBadCharacter)
        else:
            months: MutableSequence[int] = []
            for i in range(0, (len(monthsInput)), 1):
                months.append(int(monthsInput[i]))

        # check that the first year matches the start of production
        if years[0] != sop:
            errorsFound = True
            errorMutableSequence.append(
                    errorTypesExcelValidation.yearsDoNotMatchSop
                )

        # check that years and months are congruent (Gaps). if not return errorTypesExcelValidation.yearsNotCongruent
        areYearsCongurent, areMonthsCongurent = checkMonthsCongruency(years=years, months=months)

        if areYearsCongurent == False:
            errorsFound = True
            errorMutableSequence.append(
                    errorTypesExcelValidation.yearsNotCongruent)
        
        if areMonthsCongurent == False:
            errorsFound = True
            errorMutableSequence.append(
                    errorTypesExcelValidation.monthsNotCongruent)

    else:
        errorMutableSequence.append(errorTypesExcelValidation.yearsEmpty)
        errorsFound = True
    
    if len(months)== 0:
        errorMutableSequence.append(errorTypesExcelValidation.monthsEmpty)
        errorsFound = True 

    return errorsFound, errorMutableSequence
'''

'''  checkMonthsCongruency
#standard case returns True True like it should 
years=[2020,2020,2020,2020,2020,2020,2020,2020,2020,2020,2020,2020,2021,2021,2021,2021,2021,2021,2021,2021,2021,2021,2021,2021]
months=[1,2,3,4,5,6,7,8,9,10,11,12,1,2,3,4,5,6,7,8,9,10,11,12]

# first 2 months are the same, returns True False like it should
years=[2020,2020,2020,2020,2020,2020,2020,2020,2020,2020,2020,2020,2021,2021,2021,2021,2021,2021,2021,2021,2021,2021,2021,2021]
months=[1,1,3,4,5,6,7,8,9,10,11,12,1,2,3,4,5,6,7,8,9,10,11,12]

#first year to high returns False True like it should 
years=[2023,2020,2020,2020,2020,2020,2020,2020,2020,2020,2020,2020,2021,2021,2021,2021,2021,2021,2021,2021,2021,2021,2021,2021]
months=[1,2,3,4,5,6,7,8,9,10,11,12,1,2,3,4,5,6,7,8,9,10,11,12]

#only 11 2020, returns False True like it should 
years=[2020,2020,2020,2020,2020,2020,2020,2020,2020,2020,2020,2021,2021,2021,2021,2021,2021,2021,2021,2021,2021,2021,2021,2021]
months=[1,2,3,4,5,6,7,8,9,10,11,12,1,2,3,4,5,6,7,8,9,10,11,12]

#13 2020, returns False True like it should 
years=[2020,2020,2020,2020,2020,2020,2020,2020,2020,2020,2020,2020,2020,2021,2021,2021,2021,2021,2021,2021,2021,2021,2021,2021]
months=[1,2,3,4,5,6,7,8,9,10,11,12,1,2,3,4,5,6,7,8,9,10,11,12]

#skipped the 1 after 12 retruns True False like it should 
years=[2020,2020,2020,2020,2020,2020,2020,2020,2020,2020,2020,2020,2021,2021,2021,2021,2021,2021,2021,2021,2021,2021,2021,2021]
months=[1,2,3,4,5,6,7,8,9,10,11,12,2,3,4,5,6,7,8,9,10,11,12]

#first year bigger then second returns True True False True like it should
years=[2021,2020,2020,2020,2020,2020,2020,2020,2020,2020,2020,2020,2021,2021,2021,2021,2021,2021,2021,2021,2021,2021,2021,2021]
months=[1,2,3,4,5,6,7,8,9,10,11,12,2,3,4,5,6,7,8,9,10,11,12]

areYearsCongurent, areMonthsCongurent, areYearsGoingUp, areMonthsGoingUp = checkMonthsCongruency(years=years, months=months)

print(areYearsCongurent, areMonthsCongurent,areYearsGoingUp, areMonthsGoingUp)
'''

'''checkMonths
#standard case returns False [] 
excelString = "   2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2022  , 2022  , 2022  , 2022  , 2022  , 2022  , 2022  , 2022  , 2022  , 2022  , 2022  , 2022 \n 1  , 2  , 3  , 4  , 5  , 6  , 7  , 8  , 9  , 10  , 11  , 12  , 1  , 2  , 3  , 4  , 5  , 6  , 7  , 8  , 9  , 10  , 11  , 12  , 1  , 2  , 3  , 4  , 5  , 6  , 7  , 8  , 9  , 10  , 11  , 12 "

#giving not number in years returns True [<errorTypesExcelValidation.yearsBadCharacter: 7>]
excelString = "   do \n 1  , 2  , 3  , 4  , 5  , 6  , 7  , 8  , 9  , 10  , 11  , 12  , 1  , 2  , 3  , 4  , 5  , 6  , 7  , 8  , 9  , 10  , 11  , 12  , 1  , 2  , 3  , 4  , 5  , 6  , 7  , 8  , 9  , 10  , 11  , 12 "

#giving not number in months returns True [<errorTypesExcelValidation.monthsBadCharacter: 17>]
"   2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2022  , 2022  , 2022  , 2022  , 2022  , 2022  , 2022  , 2022  , 2022  , 2022  , 2022  , 2022 \n do, 2  , 3  , 4  , 5  , 6  , 7  , 8  , 9  , 10  , 11  , 12  , 1  , 2  , 3  , 4  , 5  , 6  , 7  , 8  , 9  , 10  , 11  , 12  , 1  , 2  , 3  , 4  , 5  , 6  , 7  , 8  , 9  , 10  , 11  , 12 "

#nothing in year returns True [<errorTypesExcelValidation.yearsEmpty: 5>]
excelString = "   \n 1  , 2  , 3  , 4  , 5  , 6  , 7  , 8  , 9  , 10  , 11  , 12  , 1  , 2  , 3  , 4  , 5  , 6  , 7  , 8  , 9  , 10  , 11  , 12  , 1  , 2  , 3  , 4  , 5  , 6  , 7  , 8  , 9  , 10  , 11  , 12 "

#nothing in months returns True [<errorTypesExcelValidation.monthsEmpty: 16>]
excelString = "  2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2022  , 2022  , 2022  , 2022  , 2022  , 2022  , 2022  , 2022  , 2022  , 2022  , 2022  , 2022 \n "

#sopyear 2021 returns True [<errorTypesExcelValidation.yearsDoNotMatchSop: 12>]
excelString = "   2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2022  , 2022  , 2022  , 2022  , 2022  , 2022  , 2022  , 2022  , 2022  , 2022  , 2022  , 2022 \n 1, 2  , 3  , 4  , 5  , 6  , 7  , 8  , 9  , 10  , 11  , 12  , 1  , 2  , 3  , 4  , 5  , 6  , 7  , 8  , 9  , 10  , 11  , 12  , 1  , 2  , 3  , 4  , 5  , 6  , 7  , 8  , 9  , 10  , 11  , 12 "

rows = excelString.split("\n")
yearsInput = rows[0].strip().split(",")  
monthsInput = rows[1].strip().split(",")
sopYear = 2020
checkError, checkErrors = checkMonths(yearsInput=yearsInput, monthsInput=monthsInput, sop=sopYear)
print(checkError, checkErrors)
'''


'''checkExcelFormMonthInput
#standard case returns like it should
excelString = "2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021 \n 1 , 2  , 3  , 4  , 5  , 6  , 7  , 8  , 9  , 10  , 11  , 12  , 1  , 2  , 3  , 4  , 5  , 6  , 7  , 8  , 9  , 10  , 11  , 12 \n 100  , 200  , 300  , 400  , 500  , 600  , 700  , 800  , 700  , 600  , 500  , 400  , 300  , 200  , 200  , 200  , 200  , 300  , 400  , 500  , 600  , 700  , 800  , 900 "

#changing a year into "a" returns errors [<errorTypesExcelValidation.yearsBadCharacter: 7>] years [] months [] volumes or prices []
excelString = "a  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021 \n 1 , 2  , 3  , 4  , 5  , 6  , 7  , 8  , 9  , 10  , 11  , 12  , 1  , 2  , 3  , 4  , 5  , 6  , 7  , 8  , 9  , 10  , 11  , 12 \n 100  , 200  , 300  , 400  , 500  , 600  , 700  , 800  , 700  , 600  , 500  , 400  , 300  , 200  , 200  , 200  , 200  , 300  , 400  , 500  , 600  , 700  , 800  , 900 "

#changing month into "a" returns errors [<errorTypesExcelValidation.monthsBadCharacter: 17>] years [] months [] volumes or prices []
excelString = "2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021 \n a , 2  , 3  , 4  , 5  , 6  , 7  , 8  , 9  , 10  , 11  , 12  , 1  , 2  , 3  , 4  , 5  , 6  , 7  , 8  , 9  , 10  , 11  , 12 \n 100  , 200  , 300  , 400  , 500  , 600  , 700  , 800  , 700  , 600  , 500  , 400  , 300  , 200  , 200  , 200  , 200  , 300  , 400  , 500  , 600  , 700  , 800  , 900 "

#changing a year into " " returns errors [<errorTypesExcelValidation.yearsBadCharacter: 7>] years [] months [] volumes or prices []
excelString = "  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021 \n 1 , 2  , 3  , 4  , 5  , 6  , 7  , 8  , 9  , 10  , 11  , 12  , 1  , 2  , 3  , 4  , 5  , 6  , 7  , 8  , 9  , 10  , 11  , 12 \n 100  , 200  , 300  , 400  , 500  , 600  , 700  , 800  , 700  , 600  , 500  , 400  , 300  , 200  , 200  , 200  , 200  , 300  , 400  , 500  , 600  , 700  , 800  , 900 "

#changing month into " " returns errors [<errorTypesExcelValidation.monthsBadCharacter: 17>] years [] months [] volumes or prices []
excelString = "2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021 \n  , 2  , 3  , 4  , 5  , 6  , 7  , 8  , 9  , 10  , 11  , 12  , 1  , 2  , 3  , 4  , 5  , 6  , 7  , 8  , 9  , 10  , 11  , 12 \n 100  , 200  , 300  , 400  , 500  , 600  , 700  , 800  , 700  , 600  , 500  , 400  , 300  , 200  , 200  , 200  , 200  , 300  , 400  , 500  , 600  , 700  , 800  , 900 "

#only giving 2 rows (year and months) returns: len rows is not 3! 0 Afound error: Input format does not match the required template. Check if you forgot to enter years, prices or volumes. 
excelString = "2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2020  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021  , 2021 \n  , 2  , 3  , 4  , 5  , 6  , 7  , 8  , 9  , 10  , 11  , 12  , 1  , 2  , 3  , 4  , 5  , 6  , 7  , 8  , 9  , 10  , 11  , 12 "


sopYear = 2020
yearsCheck, monthsCheck, outputDataCheck, errorMutableSequence = checkExcelFormMonthInput(excelData=excelString, dataType=TypeOfParameter.volumes, sopYear=sopYear)
'''