from rest_framework import serializers


class ReferralTreeSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    user_id = serializers.UUIDField()
    email = serializers.EmailField()
    referral_code = serializers.CharField()
    left_child = serializers.DictField(allow_null=True)
    right_child = serializers.DictField(allow_null=True)


class ReferralRootSerializer(serializers.Serializer):
    root_user_id = serializers.UUIDField(source="user.id")
    root_email = serializers.EmailField(source="user.email")
    root_referral_code = serializers.CharField(source="user.referral_code")


class ReferralStatsSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    email = serializers.EmailField()
    left_count = serializers.IntegerField()
    right_count = serializers.IntegerField()
    total_team_count = serializers.IntegerField()
