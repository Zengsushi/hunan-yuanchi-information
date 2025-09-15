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

from .software_models import SoftwareAsset, SoftwareLicenseUpdateRecord, SoftwareVersionUpdateRecord, SoftwareDeployment
from .models import Supplier
from .serializers_software import (
    SoftwareAssetSerializer,
    SoftwareAssetListSerializer,
    SoftwareAssetCreateSerializer,
    SoftwareAssetUpdateSerializer,
    SoftwareLicenseUpdateRecordSerializer,
    SoftwareVersionUpdateRecordSerializer,
    SoftwareDeploymentSerializer,
    SoftwareAssetImportSerializer
)
from .filters import SoftwareAssetFilter


class SoftwareAssetViewSet(viewsets.ModelViewSet):
    """软件资产视图集"""

    queryset = SoftwareAsset.objects.select_related('supplier').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SoftwareAssetFilter
    search_fields = ['software_name', 'version', 'vendor', 'license_key', 'asset_owner']
    ordering_fields = ['software_name', 'version', 'vendor', 'purchase_date', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """根据操作类型返回不同的序列化器"""
        if self.action == 'list':
            return SoftwareAssetListSerializer
        elif self.action == 'create':
            return SoftwareAssetCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return SoftwareAssetUpdateSerializer
        return SoftwareAssetSerializer

    def get_queryset(self):
        """根据软件状态过滤查询集"""
        queryset = super().get_queryset()
        software_status = self.request.query_params.get('software_status')
        if software_status:
            queryset = queryset.filter(software_status=software_status)
        return queryset

    @action(detail=False, methods=['get'])
    def active(self, request):
        """获取激活状态软件列表"""
        queryset = self.get_queryset().filter(software_status='active')
        queryset = self.filter_queryset(queryset)
        print(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def expired(self, request):
        """获取过期软件列表"""
        queryset = self.get_queryset().filter(software_status='expired')
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def license_history(self, request, pk=None):
        """获取软件许可证更新历史"""
        software_asset = self.get_object()
        records = SoftwareLicenseUpdateRecord.objects.filter(software_asset=software_asset).order_by('-update_time')
        serializer = SoftwareLicenseUpdateRecordSerializer(records, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def version_history(self, request, pk=None):
        """获取软件版本更新历史"""
        software_asset = self.get_object()
        records = SoftwareVersionUpdateRecord.objects.filter(software_asset=software_asset).order_by('-update_time')
        serializer = SoftwareVersionUpdateRecordSerializer(records, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def deployments(self, request, pk=None):
        """获取软件部署信息"""
        software_asset = self.get_object()
        deployments = SoftwareDeployment.objects.filter(software_asset=software_asset).order_by('-deployment_date')
        serializer = SoftwareDeploymentSerializer(deployments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def import_assets(self, request):
        """导入软件资产"""
        file = request.FILES.get('file')
        if not file:
            return Response({'error': '请选择要导入的文件'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 读取文件
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file)
            else:
                return Response({'error': '不支持的文件格式，请使用CSV或Excel文件'}, status=status.HTTP_400_BAD_REQUEST)

            # 验证必需列
            required_columns = ['软件名称', '版本', '厂商', '软件类型', '许可证类型']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return Response({
                    'error': f'缺少必需的列: {", ".join(missing_columns)}'
                }, status=status.HTTP_400_BAD_REQUEST)

            # 处理数据
            success_count = 0
            error_list = []

            for index, row in df.iterrows():
                try:
                    # 准备数据
                    asset_data = {
                        'software_name': row['软件名称'],
                        'version': row['版本'],
                        'vendor': row['厂商'],
                        'software_type': row['软件类型'],
                        'license_type': row['许可证类型'],
                        'license_key': row.get('许可证密钥', ''),
                        'license_count': int(row.get('许可证数量', 1)),
                        'purchase_date': pd.to_datetime(row.get('采购日期')).date() if pd.notna(
                            row.get('采购日期')) else None,
                        'license_start_date': pd.to_datetime(row.get('许可证开始日期')).date() if pd.notna(
                            row.get('许可证开始日期')) else None,
                        'license_end_date': pd.to_datetime(row.get('许可证结束日期')).date() if pd.notna(
                            row.get('许可证结束日期')) else None,
                        'asset_owner': row.get('资产责任人', ''),
                        'project_source': row.get('项目来源', ''),
                        'software_status': row.get('软件状态', 'active'),
                        'description': row.get('描述', ''),
                    }

                    # 处理供应商
                    supplier_name = row.get('供应商')
                    if supplier_name:
                        supplier, created = Supplier.objects.get_or_create(
                            name=supplier_name,
                            defaults={'is_active': True}
                        )
                        asset_data['supplier'] = supplier.id

                    # 验证和创建
                    serializer = SoftwareAssetImportSerializer(data=asset_data)
                    if serializer.is_valid():
                        serializer.save()
                        success_count += 1
                    else:
                        error_list.append({
                            'row': index + 2,  # Excel行号从2开始
                            'errors': serializer.errors
                        })

                except Exception as e:
                    error_list.append({
                        'row': index + 2,
                        'errors': str(e)
                    })

            return Response({
                'success': True,
                'message': f'成功导入 {success_count} 条记录',
                'success_count': success_count,
                'error_count': len(error_list),
                'errors': error_list[:10]  # 只返回前10个错误
            })

        except Exception as e:
            return Response({
                'error': f'文件处理失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def export_assets(self, request):
        """导出软件资产"""
        # 获取查询参数
        software_status = request.query_params.get('software_status')
        format_type = request.query_params.get('format', 'csv')  # csv 或 excel

        # 构建查询集
        queryset = self.get_queryset()
        if software_status:
            queryset = queryset.filter(software_status=software_status)

        queryset = self.filter_queryset(queryset)

        # 准备导出数据
        export_data = []
        for asset in queryset:
            export_data.append({
                '软件名称': asset.software_name,
                '版本': asset.version,
                '厂商': asset.vendor,
                '软件类型': asset.get_software_type_display(),
                '许可证类型': asset.get_license_type_display(),
                '许可证密钥': asset.license_key or '',
                '许可证数量': asset.license_count,
                '已使用许可证': asset.used_license_count,
                '剩余许可证': asset.remaining_license_count,
                '供应商': asset.supplier.name if asset.supplier else '',
                '采购日期': asset.purchase_date.strftime('%Y-%m-%d') if asset.purchase_date else '',
                '许可证开始日期': asset.license_start_date.strftime('%Y-%m-%d') if asset.license_start_date else '',
                '许可证结束日期': asset.license_end_date.strftime('%Y-%m-%d') if asset.license_end_date else '',
                '许可证状态': asset.license_status_display,
                '资产责任人': asset.asset_owner or '',
                '项目来源': asset.project_source or '',
                '软件状态': asset.get_software_status_display(),
                '描述': asset.description or '',
                '创建时间': asset.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            })

        # 生成文件
        if format_type == 'excel':
            # Excel导出
            df = pd.DataFrame(export_data)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='软件资产')
            output.seek(0)

            response = HttpResponse(
                output.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response[
                'Content-Disposition'] = f'attachment; filename="software_assets_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
            return response

        else:
            # CSV导出
            response = HttpResponse(content_type='text/csv; charset=utf-8')
            response[
                'Content-Disposition'] = f'attachment; filename="software_assets_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
            response.write('\ufeff')  # BOM for Excel

            writer = csv.DictWriter(response, fieldnames=export_data[0].keys() if export_data else [])
            writer.writeheader()
            writer.writerows(export_data)

            return response

    @action(detail=False, methods=['get'])
    def download_template(self, request):
        """下载导入模板"""
        template_data = [
            {
                '软件名称': 'Microsoft Office',
                '版本': '2021',
                '厂商': 'Microsoft',
                '软件类型': 'office_software',
                '许可证类型': 'commercial',
                '许可证密钥': 'XXXXX-XXXXX-XXXXX-XXXXX-XXXXX',
                '许可证数量': 10,
                '供应商': '微软中国',
                '采购日期': '2023-01-15',
                '许可证开始日期': '2023-01-15',
                '许可证结束日期': '2026-01-15',
                '资产责任人': '张三',
                '项目来源': 'IT基础设施项目',
                '软件状态': 'active',
                '描述': '办公软件套件',
            }
        ]

        # 生成Excel模板
        df = pd.DataFrame(template_data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='软件资产模板')
        output.seek(0)

        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="software_assets_template.xlsx"'
        return response


class SoftwareLicenseUpdateRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """软件许可证更新记录视图集（只读）"""

    queryset = SoftwareLicenseUpdateRecord.objects.select_related('software_asset').all()
    serializer_class = SoftwareLicenseUpdateRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['software_asset', 'update_method']
    ordering_fields = ['update_time']
    ordering = ['-update_time']


class SoftwareVersionUpdateRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """软件版本更新记录视图集（只读）"""

    queryset = SoftwareVersionUpdateRecord.objects.select_related('software_asset').all()
    serializer_class = SoftwareVersionUpdateRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['software_asset']
    ordering_fields = ['update_time']
    ordering = ['-update_time']


class SoftwareDeploymentViewSet(viewsets.ModelViewSet):
    """软件部署视图集"""

    queryset = SoftwareDeployment.objects.select_related('software_asset').all()
    serializer_class = SoftwareDeploymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['target_system', 'deployed_by']
    filterset_fields = ['software_asset', 'deployment_status']
    ordering_fields = ['deployment_date']
    ordering = ['-deployment_date']
