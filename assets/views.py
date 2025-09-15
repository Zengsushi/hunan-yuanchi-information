from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from django.db.models import Count
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Asset, AssetCategory, AssetStatus, Server, NetworkDevice,Supplier
from .serializers import (
    AssetSerializer, AssetCreateSerializer,
    AssetCategorySerializer,
    AssetStatusSerializer,
    ServerSerializer, ServerCreateSerializer,
    SupplierSerializer,
    NetworkDeviceSerializer, NetworkDeviceCreateSerializer
)


class AssetCategoryViewSet(viewsets.ModelViewSet):
    queryset = AssetCategory.objects.all()
    serializer_class = AssetCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class AssetStatusViewSet(viewsets.ModelViewSet):
    queryset = AssetStatus.objects.all()
    serializer_class = AssetStatusSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AssetCreateSerializer
        return AssetSerializer


class ServerViewSet(viewsets.ModelViewSet):
    queryset = Server.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ServerCreateSerializer
        return ServerSerializer


class NetworkDeviceViewSet(viewsets.ModelViewSet):
    queryset = NetworkDevice.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return NetworkDeviceCreateSerializer
        return NetworkDeviceSerializer

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    @action(detail=False, methods=['get'])
    def simple_list(self, request):
        queryset = Supplier.objects.all()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)
        serializer = SupplierSerializer(queryset, many=True)
        return Response(serializer.data)
        