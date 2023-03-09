from django_filters import (
    FilterSet,
    ChoiceFilter,
    CharFilter,
    ModelMultipleChoiceFilter,
    ModelChoiceFilter,
)
from django import forms
from .models import (
    Project,
    marketerMetadata,
    ApplicationMain,
    ApplicationDetail,
    ProjectStatus,
    ProjectError,
)

from .helperFunctions import HighLevelProjectProblems


class ProjectFilter(FilterSet):
    # productMarketer = CharFilter(
    #     lookup_expr="icontains",
    #     label=False,
    #     widget=forms.TextInput(
    #         attrs={"class": "form-control bg-light", "placeholder": "Search ..."}
    #     ),
    # )
    # productMarketer = ModelMultipleChoiceFilter(queryset=marketerMetadata.objects.all())
    productMarketer = ModelMultipleChoiceFilter(queryset=marketerMetadata.objects.all())
    applicationMain = ModelMultipleChoiceFilter(queryset=ApplicationMain.objects.all())
    applicationDetail = ModelMultipleChoiceFilter(
        queryset=ApplicationDetail.objects.all()
    )
    status = ModelMultipleChoiceFilter(queryset=ProjectStatus.objects.all())

    def __init__(self, *args, **kwargs):
        super(ProjectFilter, self).__init__(*args, **kwargs)
        self.filters["productMarketer"].label = "Product Marketer"
        self.filters["applicationMain"].label = "Application Main"
        self.filters["applicationDetail"].label = "Application Detail"
        self.filters["status"].label = "Status"
        self.filters["estimatedSop"].label = "Estimated SOP"

    class Meta:
        model = Project
        fields = [
            "productMarketer",
            "applicationMain",
            "applicationDetail",
            "status",
            "estimatedSop",
        ]


class ProjectErrorFilter(FilterSet):
    original_list = ProjectError.objects.values_list("error_ids", flat=True)
    # Use list comprehension to split each string and add the integers to a new list
    new_list = [
        int(x) for sublist in [i.split(",") for i in original_list] for x in sublist
    ]
    # Remove duplicates
    new_list = list(set(new_list))
    # creating tuple of options
    errors_list = [(x, x) for x in new_list]

    error_ids = ChoiceFilter(
        lookup_expr="contains",
        field_name="projecterror__error_ids",
        choices=errors_list,
        label="Error Code",
    )
    productMarketer = forms.ModelChoiceField(queryset=marketerMetadata.objects.all())
    applicationMain = forms.ModelChoiceField(queryset=ApplicationMain.objects.all())
    applicationDetail = forms.ModelChoiceField(queryset=ApplicationDetail.objects.all())
    status = forms.ModelChoiceField(queryset=ProjectStatus.objects.all())

    def __init__(self, *args, **kwargs):
        super(ProjectErrorFilter, self).__init__(*args, **kwargs)
        self.filters["productMarketer"].label = "Product Marketer"
        self.filters["applicationMain"].label = "Application Main"
        self.filters["applicationDetail"].label = "Application Detail"
        self.filters["status"].label = "Status"
        self.filters["estimatedSop"].label = "Estimated SOP"
        self.filters["projectReviewed"].label = "Reviewed"

    class Meta:

        model = Project
        fields = [
            "productMarketer",
            "applicationMain",
            "applicationDetail",
            "status",
            "estimatedSop",
            "draft",
            "dummy",
            "projectReviewed",
        ]
