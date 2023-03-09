from django.urls import path
from . import views

urlpatterns = [
    path('productMarketing/businessInsights',
         views.businessInsights, name='analytics'),
    path('productMarketing/dataSources/pmd',
         views.productMasterData, name='productMasterData'),
    path('productMarketing/dataSources/vrfc', views.vrfc, name='vrfc'),
    path('productMarketing/dataSources/dragon', views.dragon, name='dragon'),
    path('productMarketing/dataSources/pmdFullList',
         views.pmdFullList, name='productFullList'),
    path('productMarketing/dataSources/pmdFullListSalesNames',
         views.pmdFullListSalesNames, name='pmdFullListSalesNames'),

]
