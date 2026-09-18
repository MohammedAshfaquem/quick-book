from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.errors import Errors
from apps.core.exceptions import QuickBookException
from apps.referrals.selectors import (
    build_tree_dict,
    find_tree_root,
    get_referral_node,
    get_referral_stats,
)
from apps.referrals.serializers import (
    ReferralRootSerializer,
    ReferralStatsSerializer,
)


class ReferralTreeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        """Return tree structure."""
        node = get_referral_node(str(user_id))

        if node is None:
            raise QuickBookException(Errors.Referral.USER_NOT_FOUND)

        tree_data = build_tree_dict(node)
        return Response(tree_data)


class ReferralRootView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReferralRootSerializer

    def get(self, request, user_id):
        """Return top root user info."""
        node = get_referral_node(str(user_id))

        if node is None:
            raise QuickBookException(Errors.Referral.USER_NOT_FOUND)

        root_node = find_tree_root(node)
        serializer = ReferralRootSerializer(root_node)
        return Response(serializer.data)


class ReferralStatsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReferralStatsSerializer

    def get(self, request, user_id):
        node = get_referral_node(str(user_id))

        if node is None:
            raise QuickBookException(Errors.Referral.USER_NOT_FOUND)

        stats_data = get_referral_stats(node)
        serializer = ReferralStatsSerializer(stats_data)
        return Response(serializer.data)
