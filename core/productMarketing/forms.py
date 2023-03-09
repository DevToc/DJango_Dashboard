# from telnetlib import VT3270REGIME
# from django import forms
# from datetime import *
# import os
# import sys
# import importlib
# from .models import *
# #from bootstrap_datepicker_plus.widgets import DatePickerInput, TimePickerInput, DateTimePickerInput, MonthPickerInput, YearPickerInput
# #from .django_range_slider import fields
# import datetime
# from dynamic_forms import DynamicField, DynamicFormMixin

# class FileUpload(forms.ModelForm):

#     class Meta:
#         fields= ('file',)

# class EnterProjectForm(forms.ModelForm):

#     def __init__(self, *args, **kwargs):
#         super(EnterProjectForm, self).__init__(*args, **kwargs)
#         #self.fields['businessLine'].disabled = True
#         #self.fields['customerMain'].queryset = MainCustomers.objects.filter().order_by("customerName")
#         #self.fields['endCustomer'].queryset = FinalCustomers.objects.filter().order_by("finalCustomerName")
#         #self.fields['oem'].queryset = OEM.objects.filter().order_by("oemName")
#         #self.fields['distributors'].queryset = OEM.objects.filter().order_by("oemName")
#         #self.fields['ems'].queryset = OEM.objects.filter().order_by("oemName")
#         #self.fields['tierOne'].queryset = OEM.objects.filter().order_by("oemName")


#     estimatedSop = forms.IntegerField(max_value = 2050, min_value = 2020, initial = 2020)

#     class Meta:

#         model = Project
#         labels = {
#             "projectName": "projectName",
#             "applicationLine": "applicationLine",
#             "productMarketer": "productMarketer",
#             "spNumber": "spNumber",
#             #"product": "product",
#             #"applicationMain": "applicationMain",
#             #"applicationDetail": "applicationDetail",
#             "estimatedSop": "estimatedSop",
#             #"customerMain": "customerMain",
#             #"endCustomer": "endCustomer",
#             "comment": "comment",
#         }

#         fields = '__all__'
#         #### business line is selected implicetly by user attributes
#         exclude = ('user', 'applicationMain', 'applicationDetail', 'product', 'mainCustomer', 'endCustomer', 'oem',)

# """### here for chained dropdown
# class ApplicationMainForm(DynamicFormMixin, forms.Form):
#     counter = 0
#     def applicationDetailChoices(form):
#         if ApplicationMainForm.counter == 0:
#             ApplicationMainForm.counter = ApplicationMainForm.counter + 1
#             allObjects = ApplicationDetail.objects.all()
#             print("all objectsA!!", allObjects)
#             return allObjects #ApplicationDetail.objects.filter(appMain = 1)

#         applicationDetail = form['applicationMain'].value()
#         print("filtered values app detail", ApplicationDetail.objects.filter(appMain = applicationDetail))
#         return ApplicationDetail.objects.filter(appMain = applicationDetail)

#     def initialApplicationDetail(form):
#         if ApplicationMainForm.counter == 1:
#             ApplicationMainForm.counter = ApplicationMainForm.counter + 1
#             allObjects = ApplicationDetail.objects.all()
#             print("all objectsB!!", allObjects)
#             return allObjects #ApplicationDetail.objects.filter(appMain = 1).first()

#         applicationDetail = form['applicationMain'].value()
#         return ApplicationDetail.objects.filter(appMain = 1).first()


#     applicationMain = forms.ModelChoiceField(
#         queryset = ApplicationMain.objects.all(),
#         initial = ApplicationMain.objects.first(),
#     )

#     applicationDetail = DynamicField(
#         forms.ModelChoiceField,
#         queryset = applicationDetailChoices,
#         initial = initialApplicationDetail,
#     )

# """


# ## here for chained dropdown
# class ProductSelectionForm2(DynamicFormMixin, forms.Form):

#     counter = 0
#     def prodSeriesChoices(form):
#         if ProductSelectionForm2.counter == 0:
#             ProductSelectionForm2.counter = ProductSelectionForm2.counter + 1
#             allObjects = ProductSeries.objects.all()
#             print("all objects!!", allObjects)
#             return ProductFamily.objects.all()

#         productFamily = form['prodFam'].value()
#         print("filtered values app detail", ProductSeries.objects.filter(productFamily = productFamily))
#         return ProductSeries.objects.filter(productFamily = productFamily)

#     def initialProdSeries(form):
#         if ProductSelectionForm2.counter == 0:
#             ProductSelectionForm2.counter = ProductSelectionForm2.counter + 1
#             allObjects = ProductSeries.objects.all()
#             print("all objects!!", allObjects)
#             return ProductSeries.objects.all()

#         return ProductSeries.objects.first()

#     ###########

#     def productChoices(form):
#         productFamily = form['prodFam'].value()
#         productSeries = form['prodSeries'].value()

#         # get rfp
#         rfpA = Product.objects.filter(productfamily__productseries = productSeries).first()

#         print("#### input prod family ", productFamily, "input product series", productSeries,"rfp result:", rfpA, "sales name result", SalesName.objects.filter(rfp = rfpA))
#         # and with in sales name
#         salesNames = SalesName.objects.filter(rfp = rfpA)   #.all()

#         return salesNames

#     def initialProductChoices(form):
#         return SalesName.objects.all()

#     prodSeries = DynamicField(
#         forms.ModelChoiceField,
#         queryset = prodSeriesChoices,
#         initial = initialProdSeries,
#     )

#     prodSalesName = DynamicField(
#         forms.ModelChoiceField,
#         queryset = productChoices,
#         initial = initialProductChoices,
#     )

# # standalone = no model behind
# class EnterVolumeFormStandalone(forms.Form):
#     v20 = forms.IntegerField(label='2020', initial=0, required=False)
#     v21 = forms.IntegerField(label='2021', initial=0, required=False)
#     v22 = forms.IntegerField(label='2022', initial=0, required=False)
#     v23 = forms.IntegerField(label='2023', initial=0, required=False)
#     v24 = forms.IntegerField(label='2024', initial=0, required=False)
#     v25 = forms.IntegerField(label='2025', initial=0, required=False)
#     v26 = forms.IntegerField(label='2026', initial=0, required=False)
#     v27 = forms.IntegerField(label='2027', initial=0, required=False)
#     v28 = forms.IntegerField(label='2028', initial=0, required=False)
#     v29 = forms.IntegerField(label='2029', initial=0, required=False)
#     v30 = forms.IntegerField(label='2030', initial=0, required=False)
#     v31 = forms.IntegerField(label='2031', initial=0, required=False)
#     v32 = forms.IntegerField(label='2032', initial=0, required=False)
#     v33 = forms.IntegerField(label='2033', initial=0, required=False)
#     v34 = forms.IntegerField(label='2034', initial=0, required=False)
#     v35 = forms.IntegerField(label='2035', initial=0, required=False)
#     v36 = forms.IntegerField(label='2036', initial=0, required=False)
#     v37 = forms.IntegerField(label='2037', initial=0, required=False)
#     v38 = forms.IntegerField(label='2038', initial=0, required=False)
#     v39 = forms.IntegerField(label='2039', initial=0, required=False)
#     v40 = forms.IntegerField(label='2040', initial=0, required=False)
#     v41 = forms.IntegerField(label='2041', initial=0, required=False)
#     v42 = forms.IntegerField(label='2042', initial=0, required=False)
#     v43 = forms.IntegerField(label='2043', initial=0, required=False)
#     v44 = forms.IntegerField(label='2044', initial=0, required=False)
#     v45 = forms.IntegerField(label='2045', initial=0, required=False)
#     v46 = forms.IntegerField(label='2046', initial=0, required=False)
#     v47 = forms.IntegerField(label='2047', initial=0, required=False)
#     v48 = forms.IntegerField(label='2048', initial=0, required=False)
#     v49 = forms.IntegerField(label='2049', initial=0, required=False)
#     v50 = forms.IntegerField(label='2050', initial=0, required=False)

# # standalone, no model behind
# class SelectPriceSourceForm(forms.Form):
#     dataSource = forms.ChoiceField(
#         widget = forms.Select(
#             attrs={
#                 "class": "form-control",
#                 "autocomplete":"off"
#             }
#         ),
#     choices=[
#         ('excel', 'Excel copy & paste'),
#         ('manual', 'Manual Entry'),
#         ('pricesDB', 'Price Database'),
#         ('vpaDB', 'VPA Database'),
#         ])

# class ReportForm(forms.Form):
#     placeholder = forms.IntegerField(label='placeholder', initial=0, required=False)


# class PriceConfirmationForm(forms.Form):

#     currency = forms.ChoiceField(
#         widget = forms.Select(
#             attrs={
#                 "class": "form-control",
#                 "autocomplete":"off"
#             }
#         ),
#     choices=[
#         ('EUR', 'EUR'),
#         ('USD', 'USD'),
#         ('JPY', 'JPY'),
#         ('MXN', 'MXN'),
#         ('CHF', 'CHF'),
#         ])

#     v20 = forms.DecimalField(label='2020', initial=0, required=False)
#     v21 = forms.DecimalField(label='2021', initial=0, required=False)
#     v22 = forms.DecimalField(label='2022', initial=0, required=False)
#     v23 = forms.DecimalField(label='2023', initial=0, required=False)
#     v24 = forms.DecimalField(label='2024', initial=0, required=False)
#     v25 = forms.DecimalField(label='2025', initial=0, required=False)
#     v26 = forms.DecimalField(label='2026', initial=0, required=False)
#     v27 = forms.DecimalField(label='2027', initial=0, required=False)
#     v28 = forms.DecimalField(label='2028', initial=0, required=False)
#     v29 = forms.DecimalField(label='2029', initial=0, required=False)
#     v30 = forms.DecimalField(label='2030', initial=0, required=False)
#     v31 = forms.DecimalField(label='2031', initial=0, required=False)
#     v32 = forms.DecimalField(label='2032', initial=0, required=False)
#     v33 = forms.DecimalField(label='2033', initial=0, required=False)
#     v34 = forms.DecimalField(label='2034', initial=0, required=False)
#     v35 = forms.DecimalField(label='2035', initial=0, required=False)
#     v36 = forms.DecimalField(label='2036', initial=0, required=False)
#     v37 = forms.DecimalField(label='2037', initial=0, required=False)
#     v38 = forms.DecimalField(label='2038', initial=0, required=False)
#     v39 = forms.DecimalField(label='2039', initial=0, required=False)
#     v40 = forms.DecimalField(label='2040', initial=0, required=False)
#     v41 = forms.DecimalField(label='2041', initial=0, required=False)
#     v42 = forms.DecimalField(label='2042', initial=0, required=False)
#     v43 = forms.DecimalField(label='2043', initial=0, required=False)
#     v44 = forms.DecimalField(label='2044', initial=0, required=False)
#     v45 = forms.DecimalField(label='2045', initial=0, required=False)
#     v46 = forms.DecimalField(label='2046', initial=0, required=False)
#     v47 = forms.DecimalField(label='2047', initial=0, required=False)
#     v48 = forms.DecimalField(label='2048', initial=0, required=False)
#     v49 = forms.DecimalField(label='2049', initial=0, required=False)
#     v50 = forms.DecimalField(label='2050', initial=0, required=False)


# class EnterVolumeAutomaticForm(forms.Form):

#     startOfProduction = forms.DecimalField(label='SoP Year', required=False)
#     endOfProduction = forms.DecimalField(label='EoP Year', initial=2030, required=False)
#     initialVolume = forms.DecimalField(label='Initial Volume (optional)', initial=100000, required=False)
#     peakVolume = forms.DecimalField(label='Peak Volume', initial=100000, required=False)
#     totalVolume = forms.DecimalField(label='Peak Volume', initial=0, required=False)

#     peakYear = forms.DecimalField(label='Peak Year', initial=2025, required=False)
#     distributionType = forms.ChoiceField(
#         widget = forms.Select(
#             attrs={
#                 "class": "form-control",
#                 "autocomplete":"off"
#             }
#         ),
#     choices=[
#         ('poisson', 'Poisson'),
#         ('gamma', 'Gamma'),
#         ('chi', 'Chi-Squared'),
#         ('linearUP', 'Linear until peak'),
#         ('normal', 'Gaussian'),

#         ])

#     def __init__(self, *args, **kwargs):
#         project = kwargs['project']
#         del kwargs['project']
#         super().__init__(*args, **kwargs)
#         if project:
#             print("fetched sop",  Project.objects.get(pk=project).estimatedSop)
#             self.fields['startOfProduction'].initial = Project.objects.get(pk=project).estimatedSop

# """

# class EnterVolumeForm(forms.ModelForm):

#   class Meta:

#         model = Project
#         labels = {
#             "applicationLine": "applicationLine",
#             "productMarketer": "productMarketer",
#             "spNumber": "spNumber",
#             "product": "product",
#             "applicationMain": "applicationMain",
#             "applicationDetail": "applicationDetail",
#             "estimatedSop": "estimatedSop",
#         }

#         fields = '__all__'
#         #### business line is selected implicetly by user attributes
#         exclude = ('user','businessLine')
# """
