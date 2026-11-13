from rest_framework import serializers

from apps.accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    stores = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "roles", "stores", "created_at"]
        read_only_fields = ["id", "email", "created_at"]

    def get_roles(self, obj):
        roles = ["CUSTOMER"]
        if obj.is_staff:
            roles.append("ADMIN")
        if obj.store_memberships.filter(active=True).exists():
            roles.append("SELLER")
        return roles

    def get_stores(self, obj):
        memberships = obj.store_memberships.filter(active=True).select_related("store")
        return [
            {"id": membership.store_id, "name": membership.store.name, "role": membership.role}
            for membership in memberships
        ]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["email", "password"]

    def validate_email(self, value):
        return value.strip().lower()

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
