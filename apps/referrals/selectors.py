from typing import Any, Dict, Optional
from apps.authentication.models import User
from apps.referrals.models import ReferralNode


def get_referral_node(user_id: str) -> Optional[ReferralNode]:
    try:
        return ReferralNode.objects.select_related("user", "parent", "left_child", "right_child").get(user_id=user_id)
    except ReferralNode.DoesNotExist:
        return None


def build_tree_dict(node: Optional[ReferralNode]) -> Optional[Dict[str, Any]]:
    if node is None:
        return None

    return {
        "id": str(node.id),
        "user_id": str(node.user.id),
        "email": node.user.email,
        "referral_code": node.user.referral_code,
        "left_child": build_tree_dict(node.left_child),
        "right_child": build_tree_dict(node.right_child),
    }


def find_tree_root(node: ReferralNode) -> ReferralNode:
    current = node
    while current.parent is not None:
        current = current.parent
    return current


def count_subtree_nodes(node: Optional[ReferralNode]) -> int:
    if node is None:
        return 0
    return 1 + count_subtree_nodes(node.left_child) + count_subtree_nodes(node.right_child)


def get_referral_stats(node: ReferralNode) -> Dict[str, Any]:
    left_count = count_subtree_nodes(node.left_child)
    right_count = count_subtree_nodes(node.right_child)

    return {
        "user_id": str(node.user.id),
        "email": node.user.email,
        "left_count": left_count,
        "right_count": right_count,
        "total_team_count": left_count + right_count,
    }
