from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.deletion import CASCADE, PROTECT
from django.utils.timezone import now

User = get_user_model()


class SnapshotTags(models.Model):
    tagName = models.CharField(max_length=30, blank=True, null=True)
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, blank=True, null=True)


class SnapshotMetaData(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, blank=True, null=True)
    date = models.DateTimeField(
        default=now, editable=False, blank=True, null=True)
    snapshotName = models.CharField(max_length=40, blank=True, null=True)
    tag = models.ForeignKey(
        SnapshotTags, on_delete=models.PROTECT, blank=True, null=True
    )
    fileName = models.CharField(max_length=40, blank=True, null=True)
    metadataFileName = models.CharField(max_length=40, blank=True, null=True)
    snapshotComments = models.CharField(max_length=50, blank=True, null=True)
