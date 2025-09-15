# 运维资产管理系统

## 项目介绍

运维资产管理系统是一个基于 Django + Vue.js 的现代化运维管理平台，提供资产管理、IP地址管理、用户管理、业务监控等功能。系统采用前后端分离架构，支持WebSocket实时通信，集成Zabbix监控系统。

### 主要功能

- **资产管理**: 服务器、网络设备等IT资产的全生命周期管理
- **IP地址管理**: IP地址分配、扫描、监控和冲突检测
- **用户管理**: 用户认证、权限控制、会话管理
- **业务监控**: 实时监控数据展示、告警管理
- **组织架构**: 部门和人员组织结构管理
- **系统管理**: 菜单管理、系统配置等

## 技术架构

### 后端技术栈
- **框架**: Django 4.2.7 + Django REST Framework
- **数据库**: SQLite (可扩展为 PostgreSQL/MySQL)
- **异步支持**: Django Channels + WebSocket
- **服务器**: Uvicorn ASGI Server
- **监控集成**: Zabbix API
- **认证**: Token + Session 双重认证

### 前端技术栈
- **框架**: Vue 3.2.13
- **UI组件**: Ant Design Vue 4.2.6
- **路由**: Vue Router 4.5.1
- **HTTP客户端**: Axios
- **构建工具**: Vue CLI

## 环境要求

- Python 3.8+
- Node.js 14+
- npm 或 yarn

## 安装部署

### 1. 克隆项目
```bash
git clone <repository-url>
cd ops_assets_backend
```

### 2. 后端环境配置

#### 创建虚拟环境
```bash
python -m venv myvenv
# Windows
myvenv\Scripts\activate
# Linux/Mac
source myvenv/bin/activate
```

#### 安装依赖
```bash
pip install -r requirements.txt
```

#### 数据库迁移
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 创建超级用户
```bash
python manage.py createsuperuser
```

### 3. 前端环境配置

```bash
cd frontend
npm install
```

## 启动系统

### 方式一：分别启动前后端

#### 启动后端服务
```bash
# 方法1: 使用自定义启动脚本（推荐）
python start_asgi_server.py

# 方法2: 使用Django管理命令
python manage.py runserver 8000

# 方法3: 直接使用Uvicorn
uvicorn ops_assets_backend.asgi:application --host 127.0.0.1 --port 8000 --reload
```

#### 启动前端服务
```bash
cd frontend
npm run serve
```

### 方式二：使用批处理脚本（Windows）
```bash
# 如果有提供批处理脚本
run_git_push.bat
```

## 访问地址

- **前端应用**: http://localhost:8080
- **后端API**: http://localhost:8000/api/
- **Django管理后台**: http://localhost:8000/admin/
- **WebSocket**: ws://localhost:8000/ws/

## 项目结构

```
ops_assets_backend/
├── assets/                 # 资产管理模块
├── users/                  # 用户管理模块
├── ip_management/          # IP地址管理模块
├── business/               # 业务管理模块
├── organization/           # 组织架构模块
├── admin_management/       # 管理后台模块
├── menu_management/        # 菜单管理模块
├── frontend/               # Vue前端项目
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   ├── components/    # 通用组件
│   │   ├── api/          # API接口
│   │   └── router/       # 路由配置
│   └── package.json
├── ops_assets_backend/     # Django项目配置
├── logs/                   # 日志文件
├── requirements.txt        # Python依赖
├── manage.py              # Django管理脚本
└── start_asgi_server.py   # 自定义启动脚本
```

## 开发说明

### API接口

系统提供完整的RESTful API接口，主要包括：

- `/api/assets/` - 资产管理相关接口
- `/api/users/` - 用户管理相关接口
- `/api/ip-management/` - IP地址管理相关接口
- `/api/business/` - 业务管理相关接口
- `/api/organization/` - 组织架构相关接口

### 数据库配置

默认使用SQLite数据库，生产环境建议使用PostgreSQL或MySQL。修改 `ops_assets_backend/settings.py` 中的 `DATABASES` 配置：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ops_assets',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### WebSocket功能

系统支持WebSocket实时通信，用于：
- 实时监控数据推送
- 系统状态更新
- 用户在线状态管理

### 日志配置

系统日志存储在 `logs/` 目录下：
- `django.log` - 应用日志
- `error.log` - 错误日志

## 注意事项

1. **端口配置**: 确保8000端口（后端）和8080端口（前端）未被占用
2. **CORS配置**: 开发环境已配置CORS，生产环境需要调整允许的域名
3. **静态文件**: 生产环境需要配置静态文件服务
4. **安全配置**: 生产环境需要修改SECRET_KEY和DEBUG设置
5. **监控集成**: 如需使用Zabbix监控功能，需要配置Zabbix服务器连接

## 常见问题

### Q: 启动时提示端口被占用
A: 检查8000和8080端口是否被其他程序占用，或修改配置文件中的端口设置

### Q: 前端无法连接后端API
A: 检查后端服务是否正常启动，确认CORS配置是否正确

### Q: 数据库迁移失败
A: 确保数据库文件权限正确，或删除migrations文件重新生成

## 技术支持

如遇到问题，请检查：
1. Python和Node.js版本是否符合要求
2. 依赖包是否正确安装
3. 数据库连接是否正常
4. 日志文件中的错误信息

## 参与贡献

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情
