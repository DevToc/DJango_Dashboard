from django.urls import path
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import newSnapshot, snapshotDownload, snapshotDownloadFull, getSnapshotList, viewSnapshotList, snapshot, snapshotDeepdive, snapshotDelete, createSnapshotTag, snapshotCompare, snapshotCompareDeepDive, snapshotTagList, snapshotUserList

urlpatterns = [
    path('productMarketing/snapshots',
         getSnapshotList.as_view(), name='snapshotsAll'),
    path('productMarketing/snapshotList',
         viewSnapshotList, name='snapshotList'),
    path('productMarketing/snapshots/<int:snapshotId>',
         snapshot.as_view(), name='snapshot'),
    path('productMarketing/view_snapshot/<int:snapshotId>',
         snapshotDeepdive, name='snapshotDeepdive'),
    path('productMarketing/deleteSnapshot/<int:snapshotId>',
         snapshotDelete, name='snapshotDelete'),

    path('productMarketing/createSnapshotTag',
         createSnapshotTag, name='createSnapshotTag'),
    path('productMarketing/snapshotCompare',
         snapshotCompare, name='snapshotCompare'),
    path('productMarketing/snapshotCompareDeepDive',
         snapshotCompareDeepDive, name='snapshotCompareDeepDive'),
    # for filters
    path('productMarketing/snapshotTagList',
         snapshotTagList, name='snapshotTagList'),
    path('productMarketing/snapshotUserList',
         snapshotUserList, name='snapshotUserList'),
    path('productMarketing/newSnapshot',
         newSnapshot.as_view(), name='newSnapshot'),
    path('productMarketing/snapshot', snapshot.as_view()),
    # download only high level KPIs
    path('productMarketing/snapshotDownload/<int:snapshotId>',
         snapshotDownload, name='snapshotDownload'),
    # download full boup
    path('productMarketing/snapshotDownloadFull/<int:snapshotId>',
         snapshotDownloadFull, name='snapshotDownloadFull'),
]
