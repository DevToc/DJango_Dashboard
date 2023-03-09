from .models import *
from productMarketingDwh.models import *
from project.models import *

# if you want to add 15% you need to give for the param procent 0.15, if you want to decrese by 5% you need to give -0.05


def incDecProject(procent, endCustomer_id):

    involvedProjects = Project.objects.filter(finalCustomer_id=endCustomer_id)
    invProjectId = []
    for proj in involvedProjects:
        invProjectId.append(proj.id)

    ProjectVolumePricesEntries = ProjectVolumePrices.objects.filter(
        project_id__in=invProjectId)

    for entries in ProjectVolumePricesEntries:
        entries.price = float(entries.price) * (1+procent)
        entries.save()
