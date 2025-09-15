from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.db.models import Q
import csv
import io
import pandas as pd
from datetime import datetime

from .models import HardwareAsset, Supplier, SpecificationUpdateRecord, WarrantyUpdateRecord
from .serializers_hardware import (
    HardwareAssetSerializer,
    HardwareAssetListSerializer,
    HardwareAssetCreateSerializer,
    HardwareAssetUpdateSerializer,
    SupplierSerializer,
    SupplierSimpleSerializer,
    SpecificationUpdateRecordSerializer,
    WarrantyUpdateRecordSerializer,
    HardwareAssetImportSerializer
)
from .filters import HardwareAssetFilter


class SupplierViewSet(viewsets.ModelViewSet):
    """供应商视图集"""
    
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'contact_person']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    filterset_fields = ['is_active']
    
    @action(detail=False, methods=['get'])
    def simple_list(self, request):
        """获取供应商简单列表（用于下拉选择）"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = SupplierSimpleSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def contacts(self, request, pk=None):
        """获取供应商联系人列表"""
        supplier = self.get_object()
        # 这里可以扩展为从供应商联系人表获取数据
        contacts = [{
            'id': supplier.id,
            'name': supplier.contact_person,
            'phone': supplier.phone,
            'email': supplier.email
        }] if supplier.contact_person else []
        return Response(contacts)


class HardwareAssetViewSet(viewsets.ModelViewSet):
    """硬件设施视图集"""
    
    queryset = HardwareAsset.objects.select_related('supplier').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = HardwareAssetFilter
    search_fields = ['asset_tag', 'model', 'manufacturer', 'serial_number', 'asset_owner']
    ordering_fields = ['asset_tag', 'model', 'manufacturer', 'purchase_date', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """根据动作选择序列化器"""
        if self.action == 'list':
            return HardwareAssetListSerializer
        elif self.action == 'create':
            return HardwareAssetCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return HardwareAssetUpdateSerializer
        return HardwareAssetSerializer
    
    def get_queryset(self):
        """获取查询集"""
        queryset = super().get_queryset()
        return queryset
    
    @action(detail=False, methods=['get'])
    def in_use(self, request):
        """获取在用资产列表"""
        queryset = self.get_queryset().filter(asset_status='in_use')
        queryset = self.filter_queryset(queryset)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def scrapped(self, request):
        """获取报废资产列表"""
        queryset = self.get_queryset().filter(asset_status='scrapped')
        queryset = self.filter_queryset(queryset)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def spec_history(self, request, pk=None):
        """获取规格参数更新历史"""
        hardware_asset = self.get_object()
        records = hardware_asset.spec_updates.all()
        serializer = SpecificationUpdateRecordSerializer(records, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def warranty_history(self, request, pk=None):
        """获取保修更新历史"""
        hardware_asset = self.get_object()
        records = hardware_asset.warranty_updates.all()
        serializer = WarrantyUpdateRecordSerializer(records, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def import_assets(self, request):
        """批量导入硬件设施"""
        file = request.FILES.get('file')
        if not file:
            return Response({'error': '请上传文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not file.name.endswith(('.csv', '.xlsx', '.xls')):
            return Response({'error': '文件格式不支持，请上传CSV或Excel文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 读取文件
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            # 验证必需列
            required_columns = [
                'asset_tag', 'model', 'asset_owner', 'purchase_date',
                'manufacturer', 'serial_number', 'warranty_type',
                'warranty_start_date', 'warranty_end_date'
            ]
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return Response({
                    'error': f'缺少必需列: {", ".join(missing_columns)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 批量创建
            success_count = 0
            error_list = []
            
            for index, row in df.iterrows():
                try:
                    # 准备数据
                    data = {
                        'asset_tag': row['asset_tag'],
                        'model': row['model'],
                        'asset_owner': row['asset_owner'],
                        'purchase_date': pd.to_datetime(row['purchase_date']).date(),
                        'manufacturer': row['manufacturer'],
                        'serial_number': row['serial_number'],
                        'warranty_type': row['warranty_type'],
                        'warranty_start_date': pd.to_datetime(row['warranty_start_date']).date(),
                        'warranty_end_date': pd.to_datetime(row['warranty_end_date']).date(),
                    }
                    
                    # 可选字段
                    optional_fields = [
                        'supplier_name', 'supplier_contact', 'project_source',
                        'asset_status', 'room', 'cabinet', 'u_position', 'dimensions'
                    ]
                    
                    for field in optional_fields:
                        if field in df.columns and pd.notna(row[field]):
                            data[field] = row[field]
                    
                    # 验证和创建
                    serializer = HardwareAssetImportSerializer(data=data)
                    if serializer.is_valid():
                        serializer.save()
                        success_count += 1
                    else:
                        error_list.append({
                            'row': index + 2,  # Excel行号从2开始
                            'asset_tag': row['asset_tag'],
                            'errors': serializer.errors
                        })
                
                except Exception as e:
                    error_list.append({
                        'row': index + 2,
                        'asset_tag': row.get('asset_tag', '未知'),
                        'errors': str(e)
                    })
            
            return Response({
                'success_count': success_count,
                'error_count': len(error_list),
                'errors': error_list
            })
        
        except Exception as e:
            return Response({'error': f'文件处理失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def export_assets(self, request):
        """导出硬件设施"""
        # 获取查询参数
        asset_status = request.query_params.get('asset_status')
        format_type = request.query_params.get('format', 'csv')  # csv 或 excel
        
        # 构建查询集
        queryset = self.get_queryset()
        if asset_status:
            queryset = queryset.filter(asset_status=asset_status)
        
        queryset = self.filter_queryset(queryset)
        
        # 准备导出数据
        export_data = []
        for asset in queryset:
            export_data.append({
                '资产标签': asset.asset_tag,
                '型号': asset.model,
                '资产责任人': asset.asset_owner,
                '供应商': asset.supplier.name if asset.supplier else '',
                '供应商联系人': asset.supplier_contact or '',
                '采购日期': asset.purchase_date.strftime('%Y-%m-%d'),
                '项目来源': asset.project_source or '',
                '资产状态': asset.get_asset_status_display(),
                '制造商': asset.manufacturer,
                '序列号': asset.serial_number,
                '机房': asset.room or '',
                '机柜': asset.cabinet or '',
                'U位': asset.u_position or '',
                '产品尺寸': asset.dimensions or '',
                '保修类型': asset.get_warranty_type_display(),
                '保修开始日期': asset.warranty_start_date.strftime('%Y-%m-%d'),
                '保修结束日期': asset.warranty_end_date.strftime('%Y-%m-%d'),
                '保修状态': asset.warranty_status_display,
                '监控状态': '是' if asset.monitoring_status else '否',
                '位置': asset.location,
                '创建时间': asset.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            })
        
        # 生成文件
        if format_type == 'excel':
            # Excel导出
            df = pd.DataFrame(export_data)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='硬件设施')
            output.seek(0)
            
            response = HttpResponse(
                output.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="hardware_assets_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
            return response
        
        else:
            # CSV导出
            response = HttpResponse(content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="hardware_assets_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
            response.write('\ufeff')  # BOM for Excel
            
            writer = csv.DictWriter(response, fieldnames=export_data[0].keys() if export_data else [])
            writer.writeheader()
            writer.writerows(export_data)
            
            return response
    
    @action(detail=False, methods=['get'])
    def download_template(self, request):
        """下载导入模板"""
        template_data = {
            'asset_tag': '示例资产标签',
            'model': '示例型号',
            'asset_owner': '示例责任人',
            'supplier_name': '示例供应商',
            'supplier_contact': '示例联系人',
            'purchase_date': '2024-01-01',
            'project_source': '示例项目',
            'asset_status': 'in_use',
            'manufacturer': '示例制造商',
            'serial_number': '示例序列号',
            'room': '示例机房',
            'cabinet': '示例机柜',
            'u_position': '1-2',
            'dimensions': '1U',
            'warranty_type': 'original',
            'warranty_start_date': '2024-01-01',
            'warranty_end_date': '2027-01-01'
        }
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="hardware_asset_import_template.csv"'
        response.write('\ufeff')  # BOM for Excel
        
        writer = csv.DictWriter(response, fieldnames=template_data.keys())
        writer.writeheader()
        writer.writerow(template_data)
        
        return response


class SpecificationUpdateRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """规格参数更新记录视图集（只读）"""
    
    queryset = SpecificationUpdateRecord.objects.select_related('hardware_asset').all()
    serializer_class = SpecificationUpdateRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['hardware_asset', 'update_method']
    ordering_fields = ['update_time']
    ordering = ['-update_time']


class WarrantyUpdateRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """保修更新记录视图集（只读）"""
    
    queryset = WarrantyUpdateRecord.objects.select_related('hardware_asset').all()
    serializer_class = WarrantyUpdateRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['hardware_asset']
    ordering_fields = ['update_time']
    ordering = ['-update_time']