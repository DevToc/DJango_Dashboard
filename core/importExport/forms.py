# from project.models import Product, ProductFamily, ProductPackage, ProductSeries
from importExport.models import Uploading
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.safestring import mark_safe
from django.urls import reverse
from enum import Enum
from typing import Any, Iterable, MutableSequence, TypeVar
import datetime


class ImportForm(ModelForm):

    # inputFile = forms.FileField()

    """Form for the file upload"""

    class Meta:
        model = Uploading
        labels = {"inputFile": "Upload a file here"}
        fields = "__all__"
        # exclude = ('user',ß
