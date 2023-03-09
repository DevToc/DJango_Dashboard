from .models import *
from rest_framework import serializers


class SnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = SnapshotMetaData
        fields = '__all__'
