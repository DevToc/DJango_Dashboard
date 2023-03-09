from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE, PROTECT
from django.utils.timezone import now

# from jsignature.fields import JSignatureField
from django.urls import reverse
from productMarketing.models import *

from django.db.models.query import QuerySet
from django_group_by import GroupByMixin


class VrfcSalesForecast(models.Model):
    rfp = models.ForeignKey(
        Product, on_delete=models.PROTECT, blank=True, null=False)
    mainCustomerVrfc = models.ForeignKey(
        MainCustomers, on_delete=models.PROTECT, blank=True, null=False
    )
    endCustomerVrfc = models.ForeignKey(
        FinalCustomers, on_delete=models.PROTECT, blank=True, null=False
    )
    year = models.CharField(max_length=5, blank=True, null=True)
    fiscalQuarter = models.SmallIntegerField(default=0, blank=True, null=True)
    fiscalYear = models.CharField(max_length=5, blank=True, null=True)
    quarter = models.SmallIntegerField(default=0, blank=True, null=True)
    quantity = models.IntegerField(default=0, blank=True, null=True)
    asp = models.DecimalField(blank=True, null=True,
                              max_digits=10, decimal_places=4)
    revenue = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )


class VrfcPmForecast(models.Model):
    rfp = models.ForeignKey(
        Product, on_delete=models.PROTECT, blank=True, null=False)
    mainCustomerVrfc = models.ForeignKey(
        MainCustomers, on_delete=models.PROTECT, blank=True, null=False
    )
    endCustomerVrfc = models.ForeignKey(
        FinalCustomers, on_delete=models.PROTECT, blank=True, null=False
    )
    fiscalYear = models.CharField(max_length=5, blank=True, null=True)
    quarter = models.SmallIntegerField(default=0, blank=True, null=True)
    quantity = models.IntegerField(default=0, blank=True, null=True)
    asp = models.DecimalField(blank=True, null=True,
                              max_digits=10, decimal_places=4)
    revenue = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )


class VRFCQuerySet(QuerySet, GroupByMixin):
    pass


class VrfcOrdersOnHand(models.Model):
    objects = VRFCQuerySet.as_manager()

    rfp = models.ForeignKey(
        Product, on_delete=models.PROTECT, blank=True, null=False)
    mainCustomerVrfc = models.ForeignKey(
        MainCustomers, on_delete=models.PROTECT, blank=True, null=False
    )
    endCustomerVrfc = models.ForeignKey(
        FinalCustomers, on_delete=models.PROTECT, blank=True, null=False
    )
    fiscalYear = models.CharField(max_length=5, blank=True, null=True)
    quarter = models.SmallIntegerField(default=0, blank=True, null=True)
    year = models.CharField(max_length=5, blank=True, null=True)
    fiscalQuarter = models.SmallIntegerField(default=0, blank=True, null=True)
    quantity = models.IntegerField(default=0, blank=True, null=True)
    asp = models.DecimalField(blank=True, null=True,
                              max_digits=16, decimal_places=5)
    revenue = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )


class ErrorTypesVrfcOohConflicts(models.Model):
    errorType = models.SmallIntegerField(blank=True, null=True)


#    evaluationDate = models.DateTimeField(default=now, editable=False)


class vrfcOohConflicts(models.Model):
    vrfcOohEntry = models.ForeignKey(
        VrfcOrdersOnHand, on_delete=PROTECT, null=True, blank=True
    )
    errorType = models.ForeignKey(
        ErrorTypesVrfcOohConflicts, on_delete=PROTECT, null=True, blank=True
    )
    evaluationDate = models.DateTimeField(default=now, editable=False)


class BoUpQuerySet(QuerySet, GroupByMixin):
    pass


class BoUp(models.Model):
    objects = BoUpQuerySet.as_manager()
    ALLOWABLE_TYPES_BL = (
        ("PSE", "PSE"),
        ("ACEE", "ACEE"),
        ("BDI", "BDI"),
        ("HSMM", "HSMM"),
    )

    ALLOWABLE_TYPES_PROJECT_STATUS = (
        ("100", "BW (100%)"),
        ("90", "DW (90%)"),
        ("60", "DI (60%)"),
        ("40", "DI (40%)"),
        ("10", "OP (10%)"),
        ("0", "LO (0%)"),
    )

    ALLOWABLE_TYPES_REGION = (
        ("EMEA", "EMEA"),
        ("AMERICAS", "AMERICAS"),
        ("AP", "AP"),
        ("JAPAN", "JAPAN"),
        ("GC", "GC"),
        ("MISC", "MISC"),
    )

    ALLOWABLE_TYPES_APPLICATION_MAIN = (
        ("BMS", "BMS"),
        ("INV", "INV"),
        ("PCC", "PCC"),
        ("EMS", "EMS"),
        ("TCU", "TCU"),
        ("FCC", "FCC"),
        ("Aux", "Aux"),
        ("PSE", "PSE"),
    )

    ALLOWABLE_TYPES_APPLICATION_LINE = (
        ("ATV.PSE", "ATV.PSE"),
        ("ATV.HSMM", "ATV.HSMM"),
        ("ATV.BDI", "ATV.BDI"),
        ("ATV.ACEE", "ATV.ACEE"),
    )

    ALLOWABLE_TYPES_DCCHANNEL = (
        ("direct", "Direct"),
        ("distribution", "Distribution"),
    )

    ALLOWABLE_TYPES_STATUS = (
        ("ATV.PSE", "ATV.PSE"),
        ("ATV.PSE.JP", "ATV.PSE.JP"),
    )

    ALLOWABLE_TYPES_PRICE_STATUS = (
        ("estim", "Estimation"),
        ("quote", "Quotation"),
        ("contr", "Contract"),
    )

    ALLOWABLE_TYPES_APPLICATION_DETAIL = (
        ("BMS", "BMS___"),
        ("BMS-12V", "BMS 12V"),
        ("BMS-48v", "BMS 48v"),
        ("BMS-HV", "BMS HV"),
        ("BMS-Other", "BMS - Other"),
        ("INV", "INV___"),
        ("INV-48v", "INV 48v"),
        ("INV-HV", "INV HV"),
        ("INV-Other", "INV - Other"),
        ("PCC", "PCC___"),
        ("DCDC-HV", "DCDC HV"),
        ("DCDC-LV", "DCDC LV"),
        ("OBC", "OBC"),
        ("OBC-Connectivity", "OBC Connectivity"),
        ("OBC+DCDC-integ.", "OBC+DCDC integ."),
        ("PCC-Other", "PCC - Other"),
        ("EMS", "EMS___"),
        ("EMS-Engine", "EMS Engine"),
        ("EMS-Small-Engine", "EMS Small Engine"),
        ("EMS-Trucks", "EMS Trucks"),
        ("EMS-Other", "EMS - Other"),
        ("TCU___", "TCU___"),
        ("TCU-ICE", "TCU ICE"),
        ("TCUxEV", "TCU xEV"),
        ("TxCase", "Tx Case"),
        ("TCU-Other", "TCU - Other"),
        ("FCEV", "FCEV___"),
        ("FCEV-sub-app", "FCEV sub-app"),
        ("FCEV-Other", "FCEV - Other"),
        ("Aux", "Aux___"),
        ("Aux-Fans-HV", "Aux -Fans HV"),
        ("Aux-Fans-LV", "Aux -Fans LV"),
        ("Aux-Pumps-HV", "Aux -Pumps HV"),
        ("Aux-Pumps-LV", "Aux -Pumps LV"),
        ("Aux-Other", "Aux - Other"),
        ("PSE", "PSE___"),
        ("eSound", "eSound"),
        ("DomainCont.", "Domain Cont."),
        ("PSE-Other", "PSE - Other"),
        ("Placeholder1", "Placeholder 1 out of 15"),
        ("Placeholder2", "Placeholder 2 out of 15"),
        ("Placeholder3", "Placeholder 3 out of 15"),
        ("Placeholder4", "Placeholder 4 out of 15"),
        ("Placeholder5", "Placeholder 5 out of 15"),
        ("Placeholder6", "Placeholder 6 out of 15"),
        ("Placeholder7", "Placeholder 7 out of 15"),
        ("Placeholder8", "Placeholder 8 out of 15"),
        ("Placeholder9", "Placeholder 9 out of 15"),
        ("Placeholder10", "Placeholder 10 out of 15"),
        ("Placeholder11", "Placeholder 11 out of 15"),
        ("Placeholder12", "Placeholder 12 out of 15"),
        ("Placeholder13", "Placeholder 13 out of 15"),
        ("Placeholder14", "Placeholder 14 out of 15"),
        ("Placeholder15", "Placeholder 15 out of 15"),
    )

    ALLOWABLE_TYPES_CURRENCIES = (
        ("EUR", "EUR"),
        ("USD", "USD"),
        ("JPY", "JPY"),
        ("MXN", "MXN"),
        ("CHF", "CHF"),
    )

    Reviewed = models.BooleanField(blank=True, null=True)
    reviewDate = models.DateField(blank=True, null=True)
    ID_APP = models.ForeignKey(
        Project, on_delete=models.CASCADE, blank=True, null=True)
    applicationLine = models.CharField(
        max_length=30, choices=ALLOWABLE_TYPES_APPLICATION_LINE, blank=True, null=True
    )

    vhkDate = models.DateTimeField(auto_now=True)
    productMarketer = models.ForeignKey(
        marketerMetadata, on_delete=models.PROTECT, blank=True, null=True
    )
    hfg = models.CharField(max_length=20, blank=True, null=True)
    ppos = models.CharField(max_length=30, blank=True, null=True)
    spNumber = models.IntegerField(blank=True, null=True)
    applicationMain = models.ForeignKey(
        ApplicationMain, on_delete=models.PROTECT)
    plHfg = models.CharField(max_length=30, blank=True, null=True)

    # there are dummy projects as placeholders
    dummy = models.BooleanField(blank=True, null=True, default=False)
    # valid should be used only to turn off, if not delete a project. the proper way to remove a project would be to set the status probability to 0.
    vaild = models.BooleanField(blank=True, null=True, default=True)
    syntheticProjectName = models.CharField(
        max_length=65, verbose_name="SyntheticProjectName", blank=True, null=True)

    # watchout !! chained field refers to the field here in this table! chained model field referst to the field name in table app detail (Foreing key!)
    applicationDetail = ChainedForeignKey(
        ApplicationDetail,
        chained_field="applicationMain",
        chained_model_field="appMain",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.CASCADE,
    )

    rfp = models.ForeignKey(
        Product, on_delete=models.CASCADE, blank=True, null=True)
    salesName = models.ForeignKey(
        SalesName, on_delete=models.PROTECT, blank=True, null=True
    )
    priceSource = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    familyPriceApplicable = models.BooleanField(
        default=False, blank=True, null=True)
    familyPriceDetails = models.CharField(max_length=50, blank=True, null=True)
    priceType = models.CharField(
        max_length=5, choices=ALLOWABLE_TYPES_PRICE_STATUS, blank=True, null=True
    )
    currency = models.CharField(
        max_length=3,
        choices=ALLOWABLE_TYPES_CURRENCIES,
        blank=True,
        null=True,
        default="EUR",
    )
    contractualCurrency = models.CharField(
        max_length=3,
        choices=ALLOWABLE_TYPES_CURRENCIES,
        blank=True,
        null=True,
        default="EUR",
    )

    fxRate = models.DecimalField(
        default=1.0, blank=True, null=True, max_digits=15, decimal_places=6
    )
    comment = models.CharField(max_length=300, blank=True, null=True)
    region = models.CharField(
        max_length=10, choices=ALLOWABLE_TYPES_REGION, default="EMEA"
    )
    secondRegion = models.CharField(
        max_length=10, default="EMEA", blank=True, null=True
    )

    dcChannel = models.CharField(max_length=12, blank=True, null=True)
    priceType = models.CharField(max_length=15, blank=True, null=True)

    projectName = models.CharField(max_length=150, default="")
    mainCustomer = models.ForeignKey(
        MainCustomers, on_delete=models.PROTECT, blank=False, null=False
    )
    endCustomer = models.ForeignKey(
        FinalCustomers, on_delete=models.PROTECT, blank=False, null=False
    )
    mainCustomerHelper = models.CharField(
        max_length=50, default="", blank=True, null=True
    )

    endCustomerHelper = models.CharField(
        max_length=50, default="", blank=True, null=True
    )

    distributor = models.ForeignKey(
        Distributors, on_delete=models.PROTECT, blank=True, null=True
    )  # before was charfield
    tier1 = models.ForeignKey(
        Tier1, on_delete=models.PROTECT, blank=True, null=True
    )  # before was charfield
    oem = models.ForeignKey(
        OEM, on_delete=models.PROTECT, blank=True, null=True)
    ems = models.ForeignKey(
        EMS, on_delete=models.PROTECT, blank=True, null=True
    )  # before was charfield

    vpaCustomer = models.ForeignKey(
        VPACustomers, on_delete=models.PROTECT, blank=True, null=True
    )
    """
    vpaCustomer = models.CharField(
        max_length=40, default="", blank=True, null=True)
    """
    dragonId = models.CharField(
        max_length=40, blank=True, null=True, default="fieldMissing"
    )
    salesContact = models.CharField(
        max_length=100, default="", blank=True, null=True)
    probability = models.CharField(
        max_length=15, choices=ALLOWABLE_TYPES_PROJECT_STATUS, default=0
    )
    statusProbability = models.CharField(max_length=40, default="fieldMissing")
    fxRate = models.DecimalField(decimal_places=5, max_digits=10, blank=True, null=True)
    sop = models.IntegerField(blank=True, null=True)
    availablePGS = models.CharField(max_length=40, blank=True, null=True)
    # productCheck = models.CharField  # entfaellt da DB benutzt wird
    modifiedBy = models.ForeignKey(
        User, on_delete=models.PROTECT, blank=True, null=True
    )
    modifiedDate = models.DateTimeField(
        default=now, editable=True, blank=True, null=True
    )
    creationDate = models.DateTimeField(
        default=now, editable=False, blank=True, null=True
    )
    timeBottomUp = models.CharField(
        max_length=40, default="fieldMissing", blank=True, null=True
    )
    basicType = models.CharField(max_length=40, default="fieldMissing")
    package = models.CharField(max_length=40, blank=True, null=True)
    series = models.CharField(max_length=40, blank=True, null=True)
    gen = models.CharField(max_length=40, default="fieldMissing")
    seriesLong = models.CharField(
        max_length=40, default="fieldMissing", blank=True, null=True
    )
    genDetail = models.CharField(
        max_length=40, default="fieldMissing", blank=True, null=True
    )
    gmLifeTime = models.DecimalField(
        default=1.0, blank=True, null=True, max_digits=28, decimal_places=12
    )
    revEurLifeTime = models.DecimalField(
        default=1.0, blank=True, null=True, max_digits=28, decimal_places=12
    )
    volLifeTime = models.DecimalField(
        default=1.0, blank=True, null=True, max_digits=28, decimal_places=12
    )
    volWeightedLifeTime = models.DecimalField(
        default=1.0, blank=True, null=True, max_digits=28, decimal_places=12
    )

    rfpHlp = models.CharField(max_length=40, blank=True, null=True)
    mcHlp = models.CharField(max_length=40, blank=True, null=True)
    ecHlp = models.CharField(max_length=40, blank=True, null=True)

    vol2020 = models.IntegerField(default=0, blank=True, null=True)
    vol2021 = models.IntegerField(default=0, blank=True, null=True)
    vol2022 = models.IntegerField(default=0, blank=True, null=True)
    vol2023 = models.IntegerField(default=0, blank=True, null=True)
    vol2024 = models.IntegerField(default=0, blank=True, null=True)
    vol2025 = models.IntegerField(default=0, blank=True, null=True)
    vol2026 = models.IntegerField(default=0, blank=True, null=True)
    vol2027 = models.IntegerField(default=0, blank=True, null=True)
    vol2028 = models.IntegerField(default=0, blank=True, null=True)
    vol2029 = models.IntegerField(default=0, blank=True, null=True)
    vol2030 = models.IntegerField(default=0, blank=True, null=True)
    vol2031 = models.IntegerField(default=0, blank=True, null=True)
    vol2032 = models.IntegerField(default=0, blank=True, null=True)
    vol2033 = models.IntegerField(default=0, blank=True, null=True)
    vol2034 = models.IntegerField(default=0, blank=True, null=True)
    vol2035 = models.IntegerField(default=0, blank=True, null=True)
    vol2036 = models.IntegerField(default=0, blank=True, null=True)
    vol2037 = models.IntegerField(default=0, blank=True, null=True)
    vol2038 = models.IntegerField(default=0, blank=True, null=True)
    vol2039 = models.IntegerField(default=0, blank=True, null=True)
    vol2040 = models.IntegerField(default=0, blank=True, null=True)
    vol2041 = models.IntegerField(default=0, blank=True, null=True)
    vol2042 = models.IntegerField(default=0, blank=True, null=True)
    vol2043 = models.IntegerField(default=0, blank=True, null=True)
    vol2044 = models.IntegerField(default=0, blank=True, null=True)
    vol2045 = models.IntegerField(default=0, blank=True, null=True)
    vol2046 = models.IntegerField(default=0, blank=True, null=True)
    vol2047 = models.IntegerField(default=0, blank=True, null=True)
    vol2048 = models.IntegerField(default=0, blank=True, null=True)
    vol2049 = models.IntegerField(default=0, blank=True, null=True)

    volCustomer2020 = models.IntegerField(default=0, blank=True, null=True)
    volCustomer2021 = models.IntegerField(default=0, blank=True, null=True)
    volCustomer2022 = models.IntegerField(default=0, blank=True, null=True)
    volCustomer2023 = models.IntegerField(default=0, blank=True, null=True)
    volCustomer2024 = models.IntegerField(default=0, blank=True, null=True)
    volCustomer2025 = models.IntegerField(default=0, blank=True, null=True)
    volCustomer2026 = models.IntegerField(default=0, blank=True, null=True)
    volCustomer2027 = models.IntegerField(default=0, blank=True, null=True)
    volCustomer2028 = models.IntegerField(default=0, blank=True, null=True)
    volCustomer2029 = models.IntegerField(default=0, blank=True, null=True)
    volCustomer2030 = models.IntegerField(default=0, blank=True, null=True)
    volCustomer2031 = models.IntegerField(default=0, blank=True, null=True)
    volCustomer2032 = models.IntegerField(default=0, blank=True, null=True)
    volCustomer2033 = models.IntegerField(default=0, blank=True, null=True)
    volCustomer2034 = models.IntegerField(default=0, blank=True, null=True)
    volCustomer2035 = models.IntegerField(default=0, blank=True, null=True)
    volCustomer2036 = models.IntegerField(default=0, blank=True, null=True)
    volCustomer2037 = models.IntegerField(default=0, blank=True, null=True)
    volCustomer2038 = models.IntegerField(default=0, blank=True, null=True)
    volCustomer2039 = models.IntegerField(default=0, blank=True, null=True)
    volCustomer2040 = models.IntegerField(default=0, blank=True, null=True)
    volCustomer2041 = models.IntegerField(default=0, blank=True, null=True)
    volCustomer2042 = models.IntegerField(default=0, blank=True, null=True)
    volCustomer2043 = models.IntegerField(default=0, blank=True, null=True)
    volCustomer2044 = models.IntegerField(default=0, blank=True, null=True)
    volCustomer2045 = models.IntegerField(default=0, blank=True, null=True)
    volCustomer2046 = models.IntegerField(default=0, blank=True, null=True)
    volCustomer2047 = models.IntegerField(default=0, blank=True, null=True)
    volCustomer2048 = models.IntegerField(default=0, blank=True, null=True)
    volCustomer2049 = models.IntegerField(default=0, blank=True, null=True)

    price2020 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    price2021 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    price2022 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    price2023 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    price2024 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    price2025 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    price2026 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    price2027 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    price2028 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    price2029 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    price2030 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    price2031 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    price2032 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    price2033 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    price2034 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    price2035 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    price2036 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    price2037 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    price2038 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    price2039 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    price2040 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    price2041 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    price2042 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    price2043 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    price2044 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )

    price2045 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    price2046 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    price2047 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    price2048 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    price2049 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )

    vhk2020 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    vhk2021 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    vhk2022 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    vhk2023 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    vhk2024 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    vhk2025 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    vhk2026 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    vhk2027 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    vhk2028 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    vhk2029 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    vhk2030 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    vhk2031 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    vhk2032 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    vhk2033 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    vhk2034 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    vhk2035 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    vhk2036 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    vhk2037 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    vhk2038 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    vhk2039 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    vhk2040 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    vhk2041 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    vhk2042 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    vhk2043 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    vhk2044 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    vhk2045 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    vhk2046 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    vhk2047 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    vhk2048 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    vhk2049 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )

    gm2020 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2)
    gm2021 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2)
    gm2022 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2)
    gm2023 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2)
    gm2024 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2)
    gm2025 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2)
    gm2026 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2)
    gm2027 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2)
    gm2028 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2)
    gm2029 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2)
    gm2030 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2)
    gm2031 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2)
    gm2032 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2)
    gm2033 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2)
    gm2034 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2)
    gm2035 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2)
    gm2036 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2)
    gm2037 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2)
    gm2038 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2)
    gm2039 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2)
    gm2040 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2)
    gm2041 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2)
    gm2042 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2)
    gm2043 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2)
    gm2044 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2)
    gm2045 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2)

    gm2046 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2)

    gm2047 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2)

    gm2048 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2)

    gm2049 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2)

    wVol2020 = models.IntegerField(default=0, blank=True, null=True)
    wVol2021 = models.IntegerField(default=0, blank=True, null=True)
    wVol2022 = models.IntegerField(default=0, blank=True, null=True)
    wVol2023 = models.IntegerField(default=0, blank=True, null=True)
    wVol2024 = models.IntegerField(default=0, blank=True, null=True)
    wVol2025 = models.IntegerField(default=0, blank=True, null=True)
    wVol2026 = models.IntegerField(default=0, blank=True, null=True)
    wVol2027 = models.IntegerField(default=0, blank=True, null=True)
    wVol2028 = models.IntegerField(default=0, blank=True, null=True)
    wVol2029 = models.IntegerField(default=0, blank=True, null=True)
    wVol2030 = models.IntegerField(default=0, blank=True, null=True)
    wVol2031 = models.IntegerField(default=0, blank=True, null=True)
    wVol2032 = models.IntegerField(default=0, blank=True, null=True)
    wVol2033 = models.IntegerField(default=0, blank=True, null=True)
    wVol2034 = models.IntegerField(default=0, blank=True, null=True)
    wVol2035 = models.IntegerField(default=0, blank=True, null=True)
    wVol2036 = models.IntegerField(default=0, blank=True, null=True)
    wVol2037 = models.IntegerField(default=0, blank=True, null=True)
    wVol2038 = models.IntegerField(default=0, blank=True, null=True)
    wVol2039 = models.IntegerField(default=0, blank=True, null=True)
    wVol2040 = models.IntegerField(default=0, blank=True, null=True)
    wVol2041 = models.IntegerField(default=0, blank=True, null=True)
    wVol2042 = models.IntegerField(default=0, blank=True, null=True)
    wVol2043 = models.IntegerField(default=0, blank=True, null=True)
    wVol2044 = models.IntegerField(default=0, blank=True, null=True)
    wVol2045 = models.IntegerField(default=0, blank=True, null=True)
    wVol2046 = models.IntegerField(default=0, blank=True, null=True)
    wVol2047 = models.IntegerField(default=0, blank=True, null=True)
    wVol2048 = models.IntegerField(default=0, blank=True, null=True)
    wVol2049 = models.IntegerField(default=0, blank=True, null=True)

    wRev2020 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wRev2021 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wRev2022 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wRev2023 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wRev2024 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wRev2025 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wRev2026 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wRev2027 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wRev2028 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wRev2029 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wRev2030 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wRev2031 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wRev2032 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wRev2033 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wRev2034 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wRev2035 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wRev2036 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wRev2037 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wRev2038 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wRev2039 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wRev2040 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wRev2041 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wRev2042 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wRev2043 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wRev2044 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wRev2045 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wRev2046 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wRev2047 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wRev2048 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wRev2049 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )

    wGrossMargin2020 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wGrossMargin2021 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wGrossMargin2022 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wGrossMargin2023 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wGrossMargin2024 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wGrossMargin2025 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wGrossMargin2026 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wGrossMargin2027 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wGrossMargin2028 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wGrossMargin2029 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wGrossMargin2030 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wGrossMargin2031 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wGrossMargin2032 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wGrossMargin2033 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wGrossMargin2034 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wGrossMargin2035 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wGrossMargin2036 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wGrossMargin2037 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wGrossMargin2038 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wGrossMargin2039 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wGrossMargin2040 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wGrossMargin2041 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wGrossMargin2042 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wGrossMargin2043 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wGrossMargin2044 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wGrossMargin2045 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wGrossMargin2046 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wGrossMargin2047 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wGrossMargin2048 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    wGrossMargin2049 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )

    asp2020 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    asp2021 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    asp2022 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    asp2023 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    asp2024 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    asp2025 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    asp2026 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    asp2027 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    asp2028 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    asp2029 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    asp2030 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    asp2031 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    asp2032 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    asp2033 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    asp2034 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    asp2035 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    asp2036 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    asp2037 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    asp2038 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    asp2039 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    asp2040 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    asp2041 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    asp2042 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    asp2043 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    asp2044 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )

    asp2045 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    asp2046 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    asp2047 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    asp2048 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    asp2049 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )

    fy_vol2020 = models.IntegerField(default=0, blank=True, null=True)
    fy_vol2021 = models.IntegerField(default=0, blank=True, null=True)
    fy_vol2022 = models.IntegerField(default=0, blank=True, null=True)
    fy_vol2023 = models.IntegerField(default=0, blank=True, null=True)
    fy_vol2024 = models.IntegerField(default=0, blank=True, null=True)
    fy_vol2025 = models.IntegerField(default=0, blank=True, null=True)
    fy_vol2026 = models.IntegerField(default=0, blank=True, null=True)
    fy_vol2027 = models.IntegerField(default=0, blank=True, null=True)
    fy_vol2028 = models.IntegerField(default=0, blank=True, null=True)
    fy_vol2029 = models.IntegerField(default=0, blank=True, null=True)
    fy_vol2030 = models.IntegerField(default=0, blank=True, null=True)
    fy_vol2031 = models.IntegerField(default=0, blank=True, null=True)
    fy_vol2032 = models.IntegerField(default=0, blank=True, null=True)
    fy_vol2033 = models.IntegerField(default=0, blank=True, null=True)
    fy_vol2034 = models.IntegerField(default=0, blank=True, null=True)
    fy_vol2035 = models.IntegerField(default=0, blank=True, null=True)
    fy_vol2036 = models.IntegerField(default=0, blank=True, null=True)
    fy_vol2037 = models.IntegerField(default=0, blank=True, null=True)
    fy_vol2038 = models.IntegerField(default=0, blank=True, null=True)
    fy_vol2039 = models.IntegerField(default=0, blank=True, null=True)
    fy_vol2040 = models.IntegerField(default=0, blank=True, null=True)
    fy_vol2041 = models.IntegerField(default=0, blank=True, null=True)
    fy_vol2042 = models.IntegerField(default=0, blank=True, null=True)
    fy_vol2043 = models.IntegerField(default=0, blank=True, null=True)
    fy_vol2044 = models.IntegerField(default=0, blank=True, null=True)
    fy_vol2045 = models.IntegerField(default=0, blank=True, null=True)
    fy_vol2046 = models.IntegerField(default=0, blank=True, null=True)
    fy_vol2047 = models.IntegerField(default=0, blank=True, null=True)
    fy_vol2048 = models.IntegerField(default=0, blank=True, null=True)
    fy_vol2049 = models.IntegerField(default=0, blank=True, null=True)

    fy_gm2020 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_gm2021 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_gm2022 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_gm2023 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_gm2024 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_gm2025 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_gm2026 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_gm2027 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_gm2028 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_gm2029 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_gm2030 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_gm2031 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_gm2032 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_gm2033 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_gm2034 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_gm2035 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_gm2036 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_gm2037 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_gm2038 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_gm2039 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_gm2040 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_gm2041 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_gm2042 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_gm2043 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_gm2044 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_gm2045 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_gm2046 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_gm2047 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_gm2048 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_gm2049 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )

    fy_wVol2020 = models.IntegerField(default=0, blank=True, null=True)
    fy_wVol2021 = models.IntegerField(default=0, blank=True, null=True)
    fy_wVol2022 = models.IntegerField(default=0, blank=True, null=True)
    fy_wVol2023 = models.IntegerField(default=0, blank=True, null=True)
    fy_wVol2024 = models.IntegerField(default=0, blank=True, null=True)
    fy_wVol2025 = models.IntegerField(default=0, blank=True, null=True)
    fy_wVol2026 = models.IntegerField(default=0, blank=True, null=True)
    fy_wVol2027 = models.IntegerField(default=0, blank=True, null=True)
    fy_wVol2028 = models.IntegerField(default=0, blank=True, null=True)
    fy_wVol2029 = models.IntegerField(default=0, blank=True, null=True)
    fy_wVol2030 = models.IntegerField(default=0, blank=True, null=True)
    fy_wVol2031 = models.IntegerField(default=0, blank=True, null=True)
    fy_wVol2032 = models.IntegerField(default=0, blank=True, null=True)
    fy_wVol2033 = models.IntegerField(default=0, blank=True, null=True)
    fy_wVol2034 = models.IntegerField(default=0, blank=True, null=True)
    fy_wVol2035 = models.IntegerField(default=0, blank=True, null=True)
    fy_wVol2036 = models.IntegerField(default=0, blank=True, null=True)
    fy_wVol2037 = models.IntegerField(default=0, blank=True, null=True)
    fy_wVol2038 = models.IntegerField(default=0, blank=True, null=True)
    fy_wVol2039 = models.IntegerField(default=0, blank=True, null=True)
    fy_wVol2040 = models.IntegerField(default=0, blank=True, null=True)
    fy_wVol2041 = models.IntegerField(default=0, blank=True, null=True)
    fy_wVol2042 = models.IntegerField(default=0, blank=True, null=True)
    fy_wVol2043 = models.IntegerField(default=0, blank=True, null=True)
    fy_wVol2044 = models.IntegerField(default=0, blank=True, null=True)
    fy_wVol2045 = models.IntegerField(default=0, blank=True, null=True)
    fy_wVol2046 = models.IntegerField(default=0, blank=True, null=True)
    fy_wVol2047 = models.IntegerField(default=0, blank=True, null=True)
    fy_wVol2048 = models.IntegerField(default=0, blank=True, null=True)
    fy_wVol2049 = models.IntegerField(default=0, blank=True, null=True)

    #     m_wRev2020 = models.DecimalField(
    fy_wRev2020 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_wRev2021 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_wRev2022 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_wRev2023 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_wRev2024 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_wRev2025 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_wRev2026 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_wRev2027 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_wRev2028 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_wRev2029 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_wRev2030 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_wRev2031 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_wRev2032 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_wRev2033 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_wRev2034 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_wRev2035 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_wRev2036 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_wRev2037 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_wRev2038 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_wRev2039 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_wRev2040 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_wRev2041 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_wRev2042 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_wRev2043 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_wRev2044 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_wRev2045 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_wRev2046 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_wRev2047 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_wRev2048 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )
    fy_wRev2049 = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=2
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=[
                    "mainCustomer",
                    "endCustomer",
                    "applicationDetail",
                    "applicationMain",
                    "salesName",
                    "syntheticProjectName"
                ],
                name="unique_together_project_boup",
            ),
        ]
