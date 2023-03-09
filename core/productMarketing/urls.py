# Francisco Falise, copyright 01/10/2022
from analytics.analyticDashboard import *
from analytics.managerialDashboard import *
#from analytics.reqCar import *
from analytics.req80 import *
from analytics.req79 import *
from analytics.req78 import *
from analytics.req77 import *
from analytics.req76 import *
from analytics.req75 import *
from analytics.req74 import *
from analytics.req73 import *
from django.urls import path
#from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import boupEntry, volumeEntry, priceSelection, priceEnterExcel
from .views import priceConfirmation, boupEntryOverview, salesNamesImportJob
from .views import vhklImportJob, DragonImportJob, fullImports
from .views import DragonImportJob, projectEdit, projectManagement
from .views import boupExportFile, dropdownApplicationDetail
from .views import dropdownProductSeries, dropdownPackage, dropdownProductSalesName, distributionConfigurator

from .loginDashboard import *

urlpatterns = [
    path('productMarketing/boupEntry', boupEntry, name='boupEntry'),
    path('productMarketing/boupEntry1/<int:projectId>',
         volumeEntry, name='volumeEntry'),
    path('productMarketing/boupEntry2/<int:projectId>',
         priceSelection, name='priceSelection'),
    path('productMarketing/boupEntry2a/<int:projectId>',
         priceEnterExcel, name='priceEnterExcel'),
    path('productMarketing/boupEntry3/<int:projectId>/<int:mode>',
         priceConfirmation, name='priceConfirmation'),
    path('productMarketing/boupEntry4/<int:projectId>',
         boupEntryOverview, name='boupEntryOverviewB'),
    ### import jobs
    path('productMarketing/salesNamesImportJob', salesNamesImportJob.as_view()),
    path('productMarketing/vhklImportJob', vhklImportJob.as_view()),
    path('productMarketing/DragonImportJob', DragonImportJob.as_view()),
    path('productMarketing/imports', fullImports, name='imports'),
    #### import views
    path('productMarketing/importExport',
         DragonImportJob.as_view(), name='import_export'),

    # edit a project
    path('productMarketing/projectEdit/<int:case>/<int:projectId>',
         projectEdit, name='projectEdit'),
    path('productMarketing/projectManagement/<int:case>',
         projectManagement, name='projectManagement'),

    # get KPI for Dashboard
    path('productMarketing/KPIDashboard1',
         KPIDashboard1.as_view(), name='KPI1'),
    path('productMarketing/KPIDashboard2',
         KPIDashboard2.as_view(), name='KPI2'),
    path('productMarketing/KPIDashboard3',
         KPIDashboard3.as_view(), name='KPI3'),
    path('productMarketing/KPIDashboard4',
         KPIDashboard4.as_view(), name='KPI4'),
    path('productMarketing/KPIDashboard5',
         KPIDashboard5.as_view(), name='KPI5'),
    path('productMarketing/KPIDashboard6',
         KPIDashboard6.as_view(), name='KPI6'),
    path('productMarketing/KPIDashboard7',
         KPIDashboard7.as_view(), name='KPI7'),
    path('productMarketing/KPIDashboard8',
         KPIDashboard8.as_view(), name='KPI8'),
    path('productMarketing/KPIDashboardCar',
         AnalyticDashboardCar.as_view(), name='KPIcar'),
    path('productMarketing/ManagerDashboard',
         ManagerialDashboardCar.as_view(), name='KPIcar'),


    path('productMarketing/loginDashboard',
         loginDashboard.as_view(), name='LoginD'),

    # just for testing, can be deleted
    path('productMarketing/boupExportFile',
         boupExportFile, name='boupExportFile'),
]

htmxurlpatterns = [
    path('productMarketing/dropdownApplicationDetail',
         dropdownApplicationDetail, name='dropdownApplicationDetail'),
    path('productMarketing/dropdownProductSeries',
         dropdownProductSeries, name='dropdownProductSeries'),
    path('productMarketing/dropdownPackage/<str:family>',
         dropdownPackage, name='dropdownProductSalesName'),
    path('productMarketing/dropdownProductSalesName/<str:family>/<str:series>',
         dropdownProductSalesName, name='dropdownProductSalesName'),
    path('productMarketing/distributionConfigurator/<int:projectId>',
         distributionConfigurator, name='distributionConfigurator'),
]

urlpatterns += htmxurlpatterns
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
