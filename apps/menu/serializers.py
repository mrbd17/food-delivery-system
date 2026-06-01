from rest_framework import serializers

from .models import MenuItem


class GetMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = "__all__"
