from django.urls import path

from apps.referrals.constants import ReferralNames, ReferralUrls
from apps.referrals.views import (
    ReferralRootView,
    ReferralStatsView,
    ReferralTreeView,
)

urlpatterns = [
    path(ReferralUrls.TREE,  ReferralTreeView.as_view(),  name=ReferralNames.TREE),
    path(ReferralUrls.ROOT,  ReferralRootView.as_view(),  name=ReferralNames.ROOT),
    path(ReferralUrls.STATS, ReferralStatsView.as_view(), name=ReferralNames.STATS),
]
