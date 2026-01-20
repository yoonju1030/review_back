from .models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

    def create(self, validated_data):
        try:
            user = User.objects.create_user(
                id=validated_data["id"], password=validated_data["password"]
            )
            return user
        except Exception as e:
            raise e

    def checkValid(self, validate_data):
        try:
            pass
        except Exception as e:
            raise e
