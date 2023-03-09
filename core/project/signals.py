from django.db.models.signals import post_save

from django.dispatch import receiver
from .models import Project, ProjectError
from .helperFunctions import getProjectOverview
from currencies.models import Currency
from productMarketing.models import CurrenciesArchive, ExchangeRatesArchive
from datetime import datetime
from django.utils import timezone

@receiver(post_save, sender=Project)
def project_errors_signal(sender, instance, created, **kwargs):

    # e.g errors = "1,2,4,6,11"
    # instance argument is the instance of specific project.
    errorString = ""

    try:
        probability = float(instance.status.status) / 100.0
    except:
        probability = 0

    (
        revenue,
        volumes,
        prices,
        grossMargin,
        grossMarginPct,
        revenue_month,
        grossMargin_month,
        grossMarginPct_month,
        vhk,
        revenue_FY,
        grossProfit_FY,
        grossProfitPct_FY,
        volumes_FY,
        VhkCy,
        totalCost,
        sumRevenue,
        sumGrossMargin,
        sumCost,
        years,
        errors,
        weightedGrossMargin,
        weightedGrossMarginPct,
        weightedRevenue,
        asp,
        weightedVolume,
        sumVolume,
        sumWeightedVolume,
        sumWeightedRevenue,
        averageAsp,
        sumWeightedGrossMargin,
        projectCurrency,
        fxRate,
    ) = getProjectOverview(instance.id, None, probability, None)

    errorString = ",".join([str(error.value) for error in errors])

    if created:
        ProjectError.objects.create(project=instance, error_ids=errorString)
    else:
        try:
            instance.projecterror.error_ids = errorString
            instance.projecterror.save()
        except:
            ProjectError.objects.create(project=instance, error_ids=errorString)


"""
this signal is used to keep track of currency changes across the DB
"""
@receiver(post_save, sender=Currency)
def exchange_rate_change_signal(sender, instance, created, **kwargs):

    if created:
        # creation of a currency
        print("%%%% signal currency was created")
        currencyArchiveObject, created = CurrenciesArchive.objects.get_or_create(currency = instance.code)
        # check if thre is an existing exchange rate

        currentFxObjects = ExchangeRatesArchive.objects.filter(currency=currencyArchiveObject, valid=True)
        if currentFxObjects.count() == 1:
            currentFxObj = currentFxObjects.first()
            currentFxObj.valid = False
            currentFxObj.validTo = datetime.now(tz=timezone.utc)
            currentFxObj.save()        
        else:
            # create the entry
            currentFxObj, created = ExchangeRatesArchive.objects.get_or_create(currency=currencyArchiveObject, valid=True)
            currentFxObj.rate = instance.factor
            currentFxObj.save()

    else:
        # modification of a currency
        print("%%%% signal currency was modified", instance.is_default, instance.is_active, instance.factor, instance.symbol)
        currencyArchiveObject, created = CurrenciesArchive.objects.get_or_create(currency = instance.code)
        # check if thre is an existing exchange rate

        currentFxObjects = ExchangeRatesArchive.objects.filter(currency=currencyArchiveObject, valid=True)
        if currentFxObjects.count() == 1:
            # turn off the old entry
            currentFxObj = currentFxObjects.first()
            currentFxObj.valid = False
            currentFxObj.validTo = datetime.now(tz=timezone.utc)
            currentFxObj.save()
            # create the new entry
            currentFxObj, created = ExchangeRatesArchive.objects.get_or_create(currency=currencyArchiveObject, valid=True)
            currentFxObj.rate = instance.factor
            currentFxObj.save()
        else:
            # create the entry
            currentFxObj, created = ExchangeRatesArchive.objects.get_or_create(currency=currencyArchiveObject, valid=True)
            currentFxObj.rate = instance.factor
            currentFxObj.save()

    # each  modifcation of exchange rates should lead to an update in BoUp table (req. xxx)
    from project.bulkProcessing import bulkUpdaterBoUpTable
    runDate = datetime.now(tz=timezone.utc)
    # bulk update BoUp table with new VHKs
    bulkUpdaterBoUpTable(vhkUpdate = False, runDate = runDate, mode= 0, projectDtoArray=None)
