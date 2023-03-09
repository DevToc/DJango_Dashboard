from django.urls import path

from .views import (
    BulkProcessing,
    ProjectOverview,
    ProjectManagementAll,
    ProjectManagementCanceled,
    ProjectManagementCompleted,
    ProjectManagementDraft,
    ProjectManagementInProgress,
    ProjectManagementTopTenRevenue,
    ProjectManagementQualityChecks,
    CreateProjectView,
    EditProjectDraftEntry,
    EditProjectDraftView,
    EditProjectKeyFacts,
    CreateProjectEntryPoint,
    SelectVolumeEntryType,
    VolumeTypeSelectMonthYear,
    CreateVolumeAutomaticView,
    CreateVolumeExcelMonthView,
    CreateVolumeExcelView,
    CreateCustomerVolumeExcelView,
    ProjectDeepdive,
    ProjectDeepdiveHistory,
    ProjectDeepdiveHistoryAjax,
    CreatePricingView,
    series_list_json,
    package_list_json,
    sales_name_json,
    hfg_info_json,
    product_list_json,
    hfgData,
    pposData,
    basicTypeData,
    end_customers_list_json,
    checkInputPlausi,
    checkInputPlausiRfpLevel,
    saveAndSubmit,
    saveAsDraft,
    deleteProject,
    reviewProject
)

urlpatterns = [
    path(
        "bulkProcessing",
        BulkProcessing,
        name="bulkProcessing",
    ),
    ###
    path(
        "project-management/all",
        ProjectManagementAll.as_view(),
        name="project_management_all_view",
    ),
    path(
        "project-management/inprogress",
        ProjectManagementInProgress.as_view(),
        name="project_management_inprogress_view",
    ),
    path(
        "project-management/draft",
        ProjectManagementDraft.as_view(),
        name="project_management_draft_view",
    ),
    path(
        "project-management/completed",
        ProjectManagementCompleted.as_view(),
        name="project_management_completed_view",
    ),
    path(
        "project-management/canceled",
        ProjectManagementCanceled.as_view(),
        name="project_management_canceled_view",
    ),
    path(
        "project-management/quality-checks",
        ProjectManagementQualityChecks.as_view(),
        name="project_management_quality_checks_view",
    ),
    path(
        "project-management/toptenrevenue",
        ProjectManagementTopTenRevenue.as_view(),
        name="project_management_toptenrevenue",
    ),
    path(
        "create/",
        CreateProjectView.as_view(),
        name="create_project_view",
    ),
    path(
        "editDraft/",
        EditProjectDraftView.as_view(),
        name="edit_project_draft_view",
    ),
    path(
        "editDraft/<int:projectId>",
        EditProjectDraftEntry,
        name="edit_project_draft_entry",
    ),
    path(
        "editProjectKeyFacts/<int:projectId>",
        EditProjectKeyFacts,
        name="edit_project_key_facts",
    ),
    path(
        "creteProjectEntryPoint/",
        CreateProjectEntryPoint,
        name="create_project_view_reset",
    ),
    # select if automatic of manual volume creation
    path("volumeTypeSelect/", SelectVolumeEntryType, name="create_volume_view"),
    # select if input will happen on a monthly or yearly basis
    path(
        "volumeTypeSelectMonthYear/",
        VolumeTypeSelectMonthYear,
        name="create_volume_select_view",
    ),
    # automatic volume distribution
    path(
        "volumeAutomatic/",
        CreateVolumeAutomaticView.as_view(),
        name="create_volume_automatic_view",
    ),
    # excel copy and paste volume input
    path(
        "volumeExcel/",
        CreateVolumeExcelView.as_view(),
        name="create_volume_excel_view",
    ),
    path(
        "volumeExcelMonth/",
        CreateVolumeExcelMonthView.as_view(),
        name="create_volume_excel_month_view",
    ),
    path(
        "volumeCustomerExcel/",
        CreateCustomerVolumeExcelView.as_view(),
        name="create_volume_customer_excel_view",
    ),
    path(
        "projectOverview/",
        ProjectOverview.as_view(),
        name="project_overviewB",
    ),
    path(
        "projectDeepdive/<int:projectId>",
        ProjectDeepdive.as_view(),
        name="project_deepdive",
    ),
    path(
        "projectDeepdive/history/<int:pk>",
        ProjectDeepdiveHistory.as_view(),
        name="project_deepdive_history",
    ),
    path(
        "projectDeepdive/ajax-history/",
        ProjectDeepdiveHistoryAjax.as_view(),
        name="project_deepdive_history_ajax",
    ),
    path(
        "pricing/",
        CreatePricingView.as_view(),
        name="create_pricing_view",
    ),
    path("series-lists/", series_list_json, name="series_list_json"),
    path("package-lists/", package_list_json, name="package_list_json"),
    path("sales-names-lists/", sales_name_json, name="sales_name_list_json"),
    path("hfg_info_json/", hfg_info_json, name="hfg_info_json"),
    path("product_list_json/", product_list_json, name="product_list_json"),
    path("hfg_json/", hfgData, name="hfg_json"),
    path("ppos_json/", pposData, name="ppos_json"),
    path("basicType_json/", basicTypeData, name="basicType_json"),
    path(
        "end_customers_list_json/",
        end_customers_list_json,
        name="end_customers_list_json",
    ),
    path(
        "checkInputPlausi/<int:salesName>/<int:appMain>/<int:appDetail>/<int:mainCustomer>/<int:finalCustomer>",
        checkInputPlausi,
        name="check_input_plausi",
    ),
    path(
        "checkInputPlausiRfp/<int:salesName>/<int:appMain>/<int:appDetail>/<int:mainCustomer>/<int:finalCustomer>",
        checkInputPlausiRfpLevel,
        name="check_input_plausi_rfplevel",
    ),
    path(
        "boupSaveAndSubmit/<int:projectId>",
        saveAndSubmit,
        name="boupEntryOverview",
    ),
    path("boupSaveAsDraft/<int:projectId>", saveAsDraft, name="saveAsDraft"),
    path("deleteProject/<int:projectId>", deleteProject, name="delete_project"),
    path("reviewProject/<int:projectId>", reviewProject, name="review_project"),
]
