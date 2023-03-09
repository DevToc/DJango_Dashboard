from django.db import models


class Uploading(models.Model):
    filename = models.CharField(max_length=30)
    # path = models.CharField(max_length=30)
    docfile = models.FileField(upload_to="documents/%Y/%m/%d")
