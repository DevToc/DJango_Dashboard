from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from productMarketing.excelFormInputValidator import (
    checkExcelFormInput,
    TypeOfParameter,
    checkExcelFormMonthInput,
)
from django.utils.safestring import mark_safe

# from betterforms.multiform import MultiForm, MultiModelForm
from django.urls import reverse
from enum import Enum
from typing import Any, Iterable, MutableSequence, TypeVar
from .bulkProcessing import testProjecTiming
from utils.helpers import tooltip
from .models import (
    Project,
    ProductFamily,
    DummyCustomerExceptionProductFamilies
)
from django.contrib import messages




class ReportForm(forms.Form):
    placeholder = forms.IntegerField(
        label="placeholder", initial=0, required=False)


# operand: abstraction for volumes or prices


class errorTypesAutomaticDistribution(Enum):
    other = 0
    eopSmallerEopError = 1
    sopLargerPeakError = 2
    peakLargerEopError = 3
    peakVolError = 4
    initialVolError = 5
    totalVolumeError = 6

    def __str__(self):
        # python < v3.10 does not support switch statements...

        if self.value == 0:
            return "Miscelaneous error found."
        elif self.value == 1:
            return "End of Production is before Start of Production. "
        elif self.value == 2:
            return "Start of Production is after Peak Year. "
        elif self.value == 3:
            return "Peak Year is after End of Production. "
        elif self.value == 4:
            return "Peak volume error. "
        elif self.value == 5:
            return "Initial volume error. "
        elif self.value == 6:
            return "Lifetime volume error. It's either 0 or unplausible, it should be at least 500 pieces."


def checkConditionsAutomaticVolume(
    sop: int, eop: int, peakYear: int, totalVolume: int
) -> MutableSequence[errorTypesAutomaticDistribution]:
    errorMutableSequence: MutableSequence[errorTypesAutomaticDistribution] = []

    # only peak, sop, total volume
    if int(sop) > int(peakYear):
        print("unplausible dates! 2")
        # sopLargerPeakError = True
        errorMutableSequence.append(
            errorTypesAutomaticDistribution.sopLargerPeakError)

    if int(totalVolume) < 500:
        totalVolumeError = True
        print("unplausible total volume")
        errorMutableSequence.append(
            errorTypesAutomaticDistribution.totalVolumeError)

    if sop >= eop:
        print("unplausible dates! 1")
        eopSmallerEopError = True
        errorMutableSequence.append(
            errorTypesAutomaticDistribution.eopSmallerEopError)

    if sop > peakYear:
        print("unplausible dates! 2")
        sopLargerPeakError = True
        errorMutableSequence.append(
            errorTypesAutomaticDistribution.sopLargerPeakError)

    if peakYear > eop:
        peakLargerEopError = True
        print("unplausible dates! 3")
        errorMutableSequence.append(
            errorTypesAutomaticDistribution.peakLargerEopError)
    """
    if peakVolume == 0:
        peakVolError = True
        print("unplausible volumes! 1")
        errorMutableSequence.append(
            errorTypesAutomaticDistribution.peakLargerEopError)

    """

    """


    if initialVolume == 0:
        initialVolError = True
        print("unplausible volumes! 2")

    if (totalVolume < initialVolume) | (totalVolume < peakVolume):
        totalVolumeError = True
        print("unplausible total volume")

    """

    return errorMutableSequence


class ProjectCreateForm(forms.ModelForm):

    trueFalseOptions = (
        (True, 'Yes'),
        (False, 'No')
    )
    # todo: uncomment , commented for migration / circular import
    product_families = list(
        ProductFamily.objects.values_list("family_name", "family_name"))
    product_families.insert(0, ("", "---------"))
    product_family = forms.CharField(
        widget=forms.Select(choices=product_families), required=False
    )

    estimatedSop = forms.IntegerField(
        max_value=2050, min_value=2020, initial=2020, label="Start of Production"
    )
    # sales filrters

    product_package = forms.CharField(widget=forms.Select(), required=False)
    product_series = forms.CharField(widget=forms.Select(), required=False)
    product = forms.CharField(widget=forms.Select(), required=False)
    #mainCustomer = forms.CharField(widget=forms.Select(), required=True)
    #finalCustomer = forms.CharField(widget=forms.Select(), required=True)

    # sales_name = forms.CharField(widget=forms.Select(), required=False)
    editMode = False
    dummy = forms.BooleanField(widget=forms.Select(
        choices=trueFalseOptions), required=False, initial=False)

    class Meta:
        model = Project
        fields = (
            # first tab fields
            "projectName",
            "productMarketer",
            "region",
            "secondRegion",
            "estimatedSop",
            "status",
            "salesContact",
            "comment",
            "applicationLine",
            # 2nd tab fields
            "mainCustomer",
            "finalCustomer",
            "distributor",
            "ems",
            "tier1",
            "oem",
            "vpaCustomer",
            "product_series",
            "product_package",
            "sales_name",
            "applicationMain",
            "applicationDetail",
            "dummy",
        )

        labels = {
            # "field_name": tooltip("Label", "Tooltip description"),
            "sales_name": tooltip("Sales Name", "Enter a sales name. This is field is mandatory. For the BlueBook and other reports, the reporting is done automatically at RFP level."),
            "vpaCustomer": "VPA Customer",
            "estimatedSop": "Start of Production",
            "secondRegion": tooltip("Second Region", "This is the supporting region."),
            "finalCustomer": tooltip("End Customer", "Ship To customer, as used in SnOp Tool. If you are working with distribution business, you can select IMS/Disti."),
            "mainCustomer": tooltip("Main Customer", "Bill To customer."),
            "product_series": tooltip("Series", "For PL90: this will be the family detail. This field is used only to filter the RFP or Sales Names choices."),
            "product_package": tooltip("Package", "This field is used only to filter the RFP or Sales Names choices."),
            "product": tooltip("Product (RFP)", "This field is used only to filter the Sales Names choices."),
            "dummy": tooltip("Project Filler?", "Is this project a dummy? E.g. Market Model Filler."),
            "tier1": tooltip("Tier One", "Optional field used for supply chain analytics. Select a Tier One Customer if available."),
            "oem": tooltip("OEM", "Optional field used for supply chain analytics. Select an OEM Customer if available."),
            "vpaCustomer": tooltip("VPA Customer", "Optional field used for supply chain analytics. Select a VPA Customer if available."),
            "ems": tooltip("EMS", "Engineering Manufacturing Services company (e.g. Zollner). Optional field used for supply chain analytics. Select an EMS Customer if available."),
            "distributor": tooltip("Distributor", "Optional field used for supply chain analytics. Select a Distributor if available."),
            "productMarketer": tooltip("Product Marketer", "The marketer responsible for this project, does not need to be you."),
            "applicationMain": tooltip("Application Main", "The main application."),
            "applicationDetail": tooltip("Application Detail", "The detail application."),
            "salesContact": tooltip("Sales Contact", "Sales colleague responsible for this project."),
            "status": tooltip("Project Status", "The project weighting factor according to Infineon's policy. Please select according to the business type (direct sales vs. distribution)."),
        }

    def __init__(self, *args, **kwargs):
        print("initializing project form, kwargs", kwargs)

        # in order to override unique contraint check for edit mode. pop before calling super in order to avoid crash.
        try:
            self.editMode = kwargs.pop("editMode", False)  # kwargs["editMode"]
            print(
                "edit mode found when initializing project create form", self.editMode
            )
        except:
            print("no edit mode found in project create form", self.editMode)

        try:
            self.request = kwargs.pop("request")
            print("--> popped request")
        except:
            pass

        super(ProjectCreateForm, self).__init__(*args, **kwargs)
        # so if we are creating a new project show only valid customers.
        # else we will show all customers. otherwise the front end will not show outdated customers in the dropdown.
        if self.editMode == True:
            self.fields["mainCustomer"].queryset = self.fields[
                "mainCustomer"
            ].queryset.order_by("customerName")
            self.fields["finalCustomer"].queryset = self.fields[
                "finalCustomer"
            ].queryset.order_by("finalCustomerName")
        else:
            self.fields["mainCustomer"].queryset = self.fields[
                "mainCustomer"
            ].queryset.filter(valid=True).order_by("customerName")
            self.fields["finalCustomer"].queryset = self.fields[
                "finalCustomer"
            ].queryset.filter(valid=True).order_by("finalCustomerName")

        self.fields["vpaCustomer"].queryset = self.fields[
            "vpaCustomer"
        ].queryset.order_by("customerName")
        self.fields["distributor"].queryset = self.fields[
            "distributor"
        ].queryset.order_by("distributorName")
        self.fields["tier1"].queryset = self.fields["tier1"].queryset.order_by(
            "tierOneName"
        )
        self.fields["ems"].queryset = self.fields["ems"].queryset.order_by(
            "emsName")

    def clean(self):
        cleaned_data = super().clean()
        mainApplicationObj = cleaned_data.get("applicationMain")
        applicationDetailObj = cleaned_data.get("applicationDetail")
        salesNameObj = cleaned_data.get("sales_name")
        mainCustomerObj = cleaned_data.get("mainCustomer")
        finalCustomerObj = cleaned_data.get("finalCustomer")
        print("finalCustomerObj", finalCustomerObj)
        dummy = bool(cleaned_data.get("dummy"))

        user = self.request.user
        print("AA using user", user, "edit mode",
              self.request.session["editMode"], "dummy", dummy, type(dummy))
        dummyCustomerError = False
        inputProjectId = 0

        if self.request.session["editMode"]:
            self.editMode = True
            inputProjectId = self.request.session["project_id"]

        print(
            "%%% data inputs",
            mainApplicationObj,
            applicationDetailObj,
            salesNameObj,
            mainCustomerObj,
            finalCustomerObj,
            "self edit mode",
            self.editMode,
        )

        # check if unique constraint
        # if editing a project, test if the existing project is the edited project.
        print("testing if project exists")

        try:
            query = Project.objects.get(
                applicationMain__appMainDescription=mainApplicationObj,
                applicationDetail__appDetailDescription=applicationDetailObj,
                sales_name__name=salesNameObj,
                mainCustomer__customerName=mainCustomerObj,
                finalCustomer__finalCustomerName=finalCustomerObj,
                productMarketer__user=user,
                dummy=dummy
            )

            if (self.editMode == False) | ((self.editMode == True) & (query.id != inputProjectId)):
                redirectUrl = reverse(
                    "edit_project_draft_entry", kwargs={"projectId": query.id}
                )
                print("---> project exists!", query,
                      "redirect URL", redirectUrl)

                raise ValidationError(
                    mark_safe(
                        (
                            'You already created a project with these key parameters. Please edit it under <a href="{0}">this link</a>.'
                        ).format(redirectUrl)
                    )
                )
            else:
                print("you are editing the current project, accepting")

        except Project.DoesNotExist:
            print("project did not exist!!")
        except:
            print("something else happened, unique constraint violated!")

        sop = cleaned_data.get("estimatedSop")

        # test timing only for project creation. otherwise editing old projects will lead to errors.
        pastError, dummyTimingError = testProjecTiming(
            sop, cleaned_data.get("dummy"))

        if self.editMode == False:
            if pastError == True:
                raise ValidationError(
                    "Start of Production is too far away in the past! Please review your data."
                )

        if dummyTimingError == True:
            raise ValidationError(
                "Project is marked as dummy and SoP is too close in the future. Dummy projects should start at least in 3 years"
            )

        # check if customer is a dummy and selected product family is in the override table
        if ("dummy" in mainCustomerObj.customerName) | ("dummy" in finalCustomerObj.finalCustomerName):
            familyStr = salesNameObj.rfp.familyHelper
            exceptions = DummyCustomerExceptionProductFamilies.objects.filter(
                exceptedFamily=familyStr)

            if exceptions.count() == 0:
                raise ValidationError(
                    "You selected a dummy customer for an product which is not a TC4 or an Aureo. Please select non dummy customers or refer to your Sales Counterpart in order to update information in SnOp. Our binding customer list is provided by SnOp tool."
                )


class VolumeForm(forms.Form):
    # for excel copy paste value
    excelData = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={"class": "d-none"},
        ),
    )

    thisIsCustomersData = forms.IntegerField(initial=0, required=False)
    # automatic distribution fields
    startOfProduction = forms.DecimalField(label=tooltip(
        "SoP Year", "This field is taken over from the project key facts and is shown here only for information. In order to modify it, please edit the project's key facts."), required=False)
    volume = []
    years = []
    monthlyLevel = False

    def __init__(self, *args, **kwargs):

        super(VolumeForm, self).__init__(*args, **kwargs)
        self.fields["excelData"].label = ""
        self.fields["startOfProduction"].widget.attrs["readonly"] = True
        self.fields["startOfProduction"].widget.attrs["hidden"] = True
        self.volumes = []
        self.years = []

        try:
            self.fields["startOfProduction"].initial = kwargs["initial"][
                "startOfProduction"
            ]
        except:
            print("did not find initial values!")
    
        try:
            self.request = kwargs["initial"][
                "request"
            ]
        except:
            print("did not find request values!")
    """
    def selfTest(self):
        cleaned_data = super().clean()
        if self.monthlyLevel == False:
            excelData = cleaned_data.get("excelData")
            startOfProduction = cleaned_data.get("startOfProduction")
            print("cleaning form!!! with sop", startOfProduction)
            if excelData:

                # the front end already filters and keeps the two first rows, unless we are entering data on a monthly basis.
                # the form was filled with copy, paste excel field
                excelDataRowCount: int = len(excelData.split("\n"))
                print("$$$ count of excel data rows", excelDataRowCount)

                if excelDataRowCount != 2:

                    messages.warning(self.request, "You need to enter two rows if working on calendar year basis!")
                    return False
                    raise ValidationError(
                        "You need to enter two rows if working on calendar year basis!"
                    )

                # try:
                years, volume = excelData.split("\n")
                print("##### volume form split, years", years)
                print("##### volume form split, volumes", volume)

                yearsCheck, outputDataCheck, errorMutableSequence = checkExcelFormInput(
                    excelData=excelData,
                    dataType=TypeOfParameter.volumes,
                    sop=startOfProduction,
                )
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
                    messages.warning(self.request, errorString)
                    return False
                    #raise ValidationError(str(errorString))

                else:
                    print("statement A")
                    self.years = yearsCheck
                    self.volume = outputDataCheck
                    print("statement b", self.years, "volumes", self.volume)
                    cleaned_data["years"] = self.years
                    cleaned_data["volume"] = self.volume
                    cleaned_data["excelData"] = excelData

                    return True

            else:
                print(
                    "##### raising validation error! is this customer data?",
                    cleaned_data["thisIsCustomersData"],
                )
                # if this is a customer estimates form raise only a warning
                if cleaned_data["thisIsCustomersData"]:
                    # case nothing was entered return on error
                    messages.warning(self.request, mark_safe(
                            (
                                'Input required! If you do not want to enter data manually, please go to the <a href="{0}">Automatic Volume Distribution</a>.'
                            ).format(reverse("create_volume_automatic_view"))
                        ))
                    return False

                    raise ValidationError(
                        "Input required! You can also skip this step if you want."
                    )

                else:
                    messages.warning(self.request, "Input required! You can also skip this step if you want.")
                    return False

                    # case nothing was entered return on error
                    raise ValidationError(
                        mark_safe(
                            (
                                'Input required! If you do not want to enter data manually, please go to the <a href="{0}">Automatic Volume Distribution</a>.'
                            ).format(reverse("create_volume_automatic_view"))
                        )
                    )
    """

    def clean(self):
        print("%%%%% cleaning form, yearly level")
        cleaned_data = super().clean()

        if self.monthlyLevel == False:
            excelData = cleaned_data.get("excelData")
            startOfProduction = cleaned_data.get("startOfProduction")
            print("cleaning form!!! with sop", startOfProduction)
            if excelData:

                # the front end already filters and keeps the two first rows, unless we are entering data on a monthly basis.
                # the form was filled with copy, paste excel field
                excelDataRowCount: int = len(excelData.split("\n"))
                print("$$$ count of excel data rows", excelDataRowCount)

                if excelDataRowCount != 2:
                    raise forms.ValidationError(
                        "You need to enter two rows if working on calendar year basis!"
                    )

                # try:
                years, volume = excelData.split("\n")
                print("##### volume form split, years", years)
                print("##### volume form split, volumes", volume)

                yearsCheck, outputDataCheck, errorMutableSequence = checkExcelFormInput(
                    excelData=excelData,
                    dataType=TypeOfParameter.volumes,
                    sop=startOfProduction,
                )
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

                    raise forms.ValidationError(str(errorString))

                else:
                    print("statement A")
                    self.years = yearsCheck
                    self.volume = outputDataCheck
                    print("statement b", self.years, "volumes", self.volume)
                    cleaned_data["years"] = self.years
                    cleaned_data["volume"] = self.volume
                    cleaned_data["excelData"] = excelData

            else:
                print(
                    "##### raising validation error! is this customer data?",
                    cleaned_data["thisIsCustomersData"],
                )
                # if this is a customer estimates form raise only a warning
                if cleaned_data["thisIsCustomersData"]:
                    # case nothing was entered return on error
                    raise forms.ValidationError(
                        "Input required! You can also skip this step if you want."
                    )

                else:

                    # case nothing was entered return on error
                    raise forms.ValidationError(
                        mark_safe(
                            (
                                'Input required! If you do not want to enter data manually, please go to the <a href="{0}">Automatic Volume Distribution</a>.'
                            ).format(reverse("create_volume_automatic_view"))
                        )
                    )

        return cleaned_data


"""
class VolumeMonthForm(VolumeForm):
    monthlyLevel = True

    def clean(self):
        cleaned_data = super().clean()
        excelData = cleaned_data.get("excelData")
        startOfProduction = cleaned_data.get("startOfProduction")
        print("cleaning form monthly level!!! FFrancisco with sop", startOfProduction)
        if excelData:

            # the front end already filters and keeps the two first rows, unless we are entering data on a monthly basis.
            # the form was filled with copy, paste excel field
            excelDataRowCount: int = len(excelData.split("\n"))
            print("$$$ count of excel data rows volume month ", excelDataRowCount)

            if excelDataRowCount != 3:
                raise ValidationError(
                    "You need to enter three rows if working on a monthly input basis!"
                )

            # try:
            years, months, volume = excelData.split("\n")
            print("francisco 123")
            years, months, outputData, errorMutableSequence = checkExcelFormMonthInput(
                excelData=excelData,
                dataType=TypeOfParameter.volumes,
                sop=startOfProduction,
            )
            print("francisco 3456")

            print(
                "stepB, month based errorMutableSequence",
                errorMutableSequence,
                len(errorMutableSequence),
            )

            if len(errorMutableSequence) > 0:
                errorString = ""
                errorMutableSequence = list(
                    dict.fromkeys(errorMutableSequence))
                for error in errorMutableSequence:
                    errorString = errorString + error.__str__()

                raise ValidationError(str(errorString))

            else:
                cleaned_data["years"] = years
                cleaned_data["months"] = months
                cleaned_data["volume"] = volume
                cleaned_data["excelData"] = outputData
                print("cleaned data monthly output", years)

        else:
            print("##### raising validation error!")
            # case nothing was entered return on error
            raise ValidationError(
                mark_safe(
                    (
                        'Input required! If you do not want to enter data manually, please go to the <a href="{0}">Automatic Volume Distribution</a>.'
                    ).format(reverse("create_volume_automatic_view"))
                )
            )

        return cleaned_data

"""


class VolumeAutomaticForm(forms.Form):

    # automatic distribution fields
    startOfProduction = forms.DecimalField(label=tooltip(
        "SoP Year", "This field is taken over from the project key facts and is shown here only for information. In order to modify it, please edit the project's key facts."), required=False)
    endOfProduction = forms.DecimalField(
        label=tooltip("End of Project Year", "The End of Project year (inclusive, means last year with production volume)."), initial=2030, required=False)
    totalVolume = forms.DecimalField(
        label=tooltip("Lifetime Quantity", "The total quantity for this project."), initial=0, required=False
    )
    peakYear = forms.DecimalField(
        label=tooltip("Peak Year", "Used to fine tune the smoothed cuve."), initial=2025, required=False)

    def __init__(self, *args, **kwargs):
        super(VolumeAutomaticForm, self).__init__(*args, **kwargs)
        self.fields["startOfProduction"].widget.attrs["readonly"] = True
        self.fields["startOfProduction"].widget.attrs["hidden"] = False

        try:
            self.fields["startOfProduction"].initial = kwargs["initial"][
                "startOfProduction"
            ]
        except:
            print("did not find initial values!")

    def clean(self):
        cleaned_data = super().clean()
        startOfProduction = cleaned_data.get("startOfProduction")
        print("cleaning form!!!")

        # either form was filled with automatic volume distribution or nothing was entered
        eop = cleaned_data["endOfProduction"]
        totalVolume = cleaned_data["totalVolume"]
        peakYear = cleaned_data["peakYear"]
        sop = cleaned_data["startOfProduction"]

        NoneType = type(None)
        if (
            (type(eop) != NoneType)
            & (type(totalVolume) != NoneType)
            & (type(peakYear) != NoneType)
            & (type(sop) != NoneType)
        ):
            print("entered eop, totalVolume, peakYear, sop", eop, peakYear, sop)

            # validations...
            # plausi checks:
            # sop < eop,
            # sop <= peak year <= eop,
            # peak volume != 0
            # initial volume > 0

            errorMutableSequence = checkConditionsAutomaticVolume(
                sop, eop, peakYear, totalVolume
            )

            print("error mut seq", errorMutableSequence)
            if len(errorMutableSequence) > 0:

                errorString = ""
                errorMutableSequence = list(
                    dict.fromkeys(errorMutableSequence))
                for error in errorMutableSequence:
                    errorString = errorString + error.__str__()
                raise ValidationError(str(errorString))

            else:
                return cleaned_data

        else:
            print("%%%%%%%%%%%%% raising validation error, inputs are required!!!")
            # case nothing was entered return on error
            raise ValidationError("Inputs are required!")

        return cleaned_data


class VolumeMonthForm(forms.Form):
    # for excel copy paste value
    excelData = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={"class": "d-none"},
        ),
    )
    # automatic distribution fields
    startOfProductionYear = forms.DecimalField(
        label=tooltip(
            "SoP Year", "This field is taken over from the project key facts and is shown here only for information. In order to modify it, please edit the project's key facts."), required=False)
    startOfProductionMonth = forms.DecimalField(
        label="SoP Month", required=False)

    def __init__(self, *args, **kwargs):

        super(VolumeMonthForm, self).__init__(*args, **kwargs)
        self.fields["excelData"].label = ""
        self.fields["startOfProductionYear"].widget.attrs["readonly"] = True
        self.fields["startOfProductionYear"].widget.attrs["hidden"] = True
        self.fields["startOfProductionMonth"].widget.attrs["readonly"] = True
        self.fields["startOfProductionMonth"].widget.attrs["hidden"] = True

        try:
            self.fields["startOfProductionYear"].initial = kwargs["initial"][
                "startOfProductionYear"
            ]
            self.fields["startOfProductionMonth"].initial = kwargs["initial"][
                "startOfProductionMonth"
            ]
        except:
            print("did not find initial values!")

    def clean(self):
        cleaned_data = super().clean()
        excelData = cleaned_data.get("excelData")
        startOfProductionYear = cleaned_data.get("startOfProductionYear")
        startOfProductionMonth = cleaned_data.get("startOfProductionMonth")
        print(
            "cleaning form!!! with sop", startOfProductionYear, startOfProductionMonth
        )

        if excelData:

            # the front end already filters and keeps the two first rows, unless we are entering data on a monthly basis.
            # the form was filled with copy, paste excel field
            excelDataRowCount: int = len(excelData.split("\n"))
            print("$$$ count of excel data rows", excelDataRowCount)

            if excelDataRowCount != 3:
                raise forms.ValidationError(
                    "You need to enter three rows if working on calendar year basis!"
                )

            # try:
            years, months, volume = excelData.split("\n")

            (
                yearsCheck,
                monthsCheck,
                outputDataCheck,
                errorMutableSequence,
            ) = checkExcelFormMonthInput(
                excelData=excelData,
                dataType=TypeOfParameter.volumes,
                sopYear=startOfProductionYear,
            )
            print("stepB", errorMutableSequence, len(errorMutableSequence))

            print("##### volume form split, years", yearsCheck)
            print("##### volume form split, months", monthsCheck)
            print("##### volume form split, volumes", outputDataCheck)

            if len(errorMutableSequence) > 0:
                errorString = ""
                errorMutableSequence = list(
                    dict.fromkeys(errorMutableSequence))
                for error in errorMutableSequence:
                    errorString = errorString + error.__str__()

                print("$$$$$$$$$$$$$$$$$$$$$$ final error string:", errorString)

                raise forms.ValidationError(str(errorString))

            else:
                print("statement b")
                cleaned_data["years"] = yearsCheck
                cleaned_data["months"] = monthsCheck
                cleaned_data["volume"] = outputDataCheck
                cleaned_data["excelData"] = excelData

        else:
            print("##### raising validation error!")
            # case nothing was entered return on error
            raise forms.ValidationError(
                mark_safe(
                    (
                        'Input required! If you do not want to enter data manually, please go to the <a href="{0}">Automatic Volume Distribution</a>.'
                    ).format(reverse("create_volume_automatic_view"))
                )
            )

        return cleaned_data


class PricingForm(forms.Form):

    trueFalseOptions = (
        (False, 'No'),
        (True, 'Yes')
    )


    positiveNegativeOptions = (
        (False, 'Negative Decline'),
        (True, 'Positive Increase')
    )

    ALLOWABLE_TYPES_PRICE_STATUS = (
        ("estim", "Estimation"),
        ("quote", "Quotation"),
        ("contr", "Contract"),
    )

    ALLOWABLE_TYPES_PRICE_CHANGE = (
        ("0", "0,0%"),
        ("0.5", "0,5%"),
        ("1.0", "1,0%"),
        ("1.5", "1,5%"),
        ("2.0", "2,0%"),
        ("2.5", "2,5%"),
        ("3.0", "3,0%"),
        ("3.5", "3,5%"),
        ("4.0", "4,0%"),
        ("5.0", "5,0%"),
        ("6.0", "6,0%"),
        ("7.0", "7,0%"),
        ("8.0", "8,0%"),
        ("9.0", "9,0%"),
        ("10.0", "10,0%"),
    )

    currency = forms.ChoiceField(label=tooltip(
        "Currency", "The currency you are using to enter prices. The prices will then be converted to EUR automatically within the system."), choices=(("USD", "USD"), ("EUR", "EURO")))
    price_commitment_until = forms.IntegerField(label=tooltip(
        "Price commitment until", "Until which year is the price commited by the customer."), min_value=2020, max_value=2050)
    startOfProduction = forms.DecimalField(label="SoP Year", required=False)
    priceType = forms.ChoiceField(
        label=tooltip(
            "Price Type", "Is the priced entered here contractually agreed, or is it based on a quotation or your best guess?."),
        choices=ALLOWABLE_TYPES_PRICE_STATUS
    )
    comment = forms.CharField(label=tooltip(
        "Comments", "Comments on the price finding and negotiation"), required=False)
    familyPriceComment = forms.CharField(
        label=tooltip("Family Price Comments", "Comments on the family price."), required=False)
    excelData = forms.CharField(
        label=tooltip("Pricing information",
                      "Enter here the price for each year. You can copy and paste from Excel if desired."),
        required=False,
        widget=forms.Textarea(
            attrs={"class": "d-none"},
        ),
    )

    #familyPrices = forms.BooleanField(label="Family price applicable?", required=False)

    familyPrices = forms.BooleanField(label="Family price applicable?", widget=forms.Select(
        choices=trueFalseOptions), required=False)

    useAutomaticPricing = forms.BooleanField(label=tooltip(
        "Use Automatic Price generation?", "This will delete the pricing above and interpolate between the initial price based on the yearly increase or decrease you select. The price interpolation will end in the last year where you entered positive quantities."), widget=forms.Select(
        choices=trueFalseOptions), required=False)

    declineIncrease = forms.BooleanField(label=tooltip(
        "Change Type", "Yearly price increase or decrease?"), widget=forms.Select(
        choices=positiveNegativeOptions), required=False)

    initialPrice = forms.DecimalField(label=tooltip(
        "Initial Unit Price", "The initial price that's going to be used. Do not use thousands separators."), min_value=0, max_value=1000, required=False)

    priceChange = forms.ChoiceField(
        label=tooltip(
            "Yearly Price Change", "The yearly percentual change of price."),
        choices=ALLOWABLE_TYPES_PRICE_CHANGE,
        required=False
    )


    def __init__(self, *args, **kwargs):
        super(PricingForm, self).__init__(*args, **kwargs)
        self.fields["excelData"].label = ""
        self.fields["startOfProduction"].widget.attrs["readonly"] = True
        self.fields["startOfProduction"].widget.attrs["hidden"] = True

        try:
            self.fields["startOfProduction"].initial = kwargs["initial"][
                "startOfProduction"
            ]
        except:
            print("did not find initial values!")

    def clean(self):
        cleaned_data = super().clean()
        excelData = cleaned_data.get("excelData")
        startOfProduction = cleaned_data.get("startOfProduction")
        print("A cleaning pricing form", excelData)
        useAutomaticPricing = cleaned_data.get("useAutomaticPricing")

        if (excelData != None) & (useAutomaticPricing == False):
            print("len excel data", len(excelData))

            # the front end already filters and keeps the two first rows, unless we are entering data on a monthly basis.
            # the form was filled with copy, paste excel field
            excelDataRowCount: int = len(excelData.split("\n"))

            if excelDataRowCount != 2:
                raise ValidationError(
                    "You need to enter two rows if working on calendar year basis!"
                )

            # try:
            years, prices = excelData.split("\n")
            print("%%%%%%%%% prices input", prices)
            yearsCheck, outputDataCheck, errorMutableSequence = checkExcelFormInput(
                excelData=excelData,
                dataType=TypeOfParameter.prices,
                sop=startOfProduction,
            )
            print("stepB", errorMutableSequence, len(errorMutableSequence))

            if len(errorMutableSequence) > 0:
                errorString = ""
                print("1234")
                errorMutableSequence = list(
                    dict.fromkeys(errorMutableSequence))
                for error in errorMutableSequence:
                    errorString = errorString + error.__str__()
                print("... price going to raise validation error")
                raise ValidationError(str(errorString))

            else:
                print("statement b")
                cleaned_data["years"] = years
                cleaned_data["prices"] = prices
                cleaned_data["excelData"] = excelData

        else:

            if useAutomaticPricing == True:

                return cleaned_data
            
            else:

                print("##### no excelData  no automatic -> raising validation error!")
                # case nothing was entered return on error
                raise ValidationError("Inputs required!")

        if excelData:
            # the form was filled with copy, paste excel field
            try:
                years, prices = excelData.split("\n")

                yearsCheck, outputDataCheck, errorMutableSequence = checkExcelFormInput(
                    excelData=excelData,
                    dataType=TypeOfParameter.prices,
                    sop=startOfProduction,
                )

                if len(errorMutableSequence) > 0:
                    errorString = ""

                    for error in errorMutableSequence:
                        errorString.append(error.__str__())

                    print("$$$$$$$$$$$$$$$$$$$$$$ final error string:", errorString)
                    raise ValidationError(errorString)

                else:

                    cleaned_data["years"] = yearsCheck
                    cleaned_data["prices"] = outputDataCheck
                    cleaned_data["excelData"] = excelData

            except:
                raise ValidationError(
                    "Enter Year in first row and Volume in second row"
                )

        return cleaned_data
