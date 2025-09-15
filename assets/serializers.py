from rest_framework import serializers
from .models import Asset, AssetCategory, AssetStatus, Server, NetworkDevice, Supplier


class AssetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetCategory
        fields = '__all__'


class AssetStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetStatus
        fields = '__all__'


class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = '__all__'


class NetworkDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkDevice
        fields = '__all__'


class AssetSerializer(serializers.ModelSerializer):
    category = AssetCategorySerializer(read_only=True)
    status = AssetStatusSerializer(read_only=True)
    server = ServerSerializer(read_only=True)
    network_device = NetworkDeviceSerializer(read_only=True)

    class Meta:
        model = Asset
        fields = '__all__'


class AssetCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = '__all__'


class ServerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = '__all__'


class NetworkDeviceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkDevice
        fields = '__all__'


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'
