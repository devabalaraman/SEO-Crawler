from rest_framework import serializers
from .models import Domain, Page, Insight

class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = "__all__"

class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = "__all__"

class InsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insight
        fields = "__all__"
