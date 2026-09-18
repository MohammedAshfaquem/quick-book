class ReferralNodeFields:
    USER        = "user"
    PARENT      = "parent"
    LEFT_CHILD  = "left_child"
    RIGHT_CHILD = "right_child"

    # Related names for reverse relations
    RELATION_REFERRAL_NODE = "referral_node"
    RELATION_CHILDREN      = "children"
    RELATION_LEFT_PARENT   = "left_parent"
    RELATION_RIGHT_PARENT  = "right_parent"



class ReferralUrls:
    TREE  = "<user_id>/tree/"   # GET /api/v1/referrals/<user_id>/tree/
    ROOT  = "<user_id>/root/"   # GET /api/v1/referrals/<user_id>/root/
    STATS = "<user_id>/stats/"  # GET /api/v1/referrals/<user_id>/stats/


class ReferralNames:
    TREE  = "referral-tree"
    ROOT  = "referral-root"
    STATS = "referral-stats"

