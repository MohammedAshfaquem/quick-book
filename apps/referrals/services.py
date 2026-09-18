from collections import deque
from django.db import transaction

from apps.authentication.models import User
from apps.core.constants import CommonFields
from apps.referrals.constants import ReferralNodeFields
from apps.referrals.models import ReferralNode


def place_user_in_referral_tree(new_user: User, referrer_user: User) -> ReferralNode:
    """
    Places new_user under referrer_user's binary subtree using BFS (Breadth-First Search).

    BFS Algorithm Explanation:
    1. Start a level-order queue initialized with the referrer's node.
    2. Pop the front node from the queue.
    3. Check if its left_child is empty -> if empty, place the new node as left_child!
    4. Otherwise, check if its right_child is empty -> if empty, place the new node as right_child!
    5. If both left and right are occupied, enqueue left_child then right_child and repeat step 2.

    This guarantees a complete binary tree filled level-by-level, left-to-right.
    """
    with transaction.atomic():
        # Get or create referral node for referring user
        referrer_node, _ = ReferralNode.objects.get_or_create(user=referrer_user)

        # Get or create node for new user
        new_node, _ = ReferralNode.objects.get_or_create(user=new_user)

        # If new node already has a parent, return as is
        if new_node.parent is not None:
            return new_node

        # Level-order queue starting at referrer_node
        queue = deque([referrer_node])

        while queue:
            current = queue.popleft()

            # 1. Check Left Child
            if current.left_child is None:
                current.left_child = new_node
                current.save(update_fields=[ReferralNodeFields.LEFT_CHILD, CommonFields.UPDATED_AT])
                new_node.parent = current
                new_node.save(update_fields=[ReferralNodeFields.PARENT, CommonFields.UPDATED_AT])
                return new_node

            # 2. Check Right Child
            if current.right_child is None:
                current.right_child = new_node
                current.save(update_fields=[ReferralNodeFields.RIGHT_CHILD, CommonFields.UPDATED_AT])
                new_node.parent = current
                new_node.save(update_fields=[ReferralNodeFields.PARENT, CommonFields.UPDATED_AT])
                return new_node

            # 3. Both full -> add children to queue for next level
            queue.append(current.left_child)
            queue.append(current.right_child)

    return new_node
