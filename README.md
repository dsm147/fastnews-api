# AI掘金头条新闻系统 (Toutiao News)

基于 FastAPI + Vue 3 构建的现代化新闻系统，支持用户注册登录、新闻浏览、收藏和历史记录等功能。

## 技术栈

### 后端
- **框架**: FastAPI (异步)
- **数据库**: MySQL + SQLAlchemy (异步 ORM)
- **缓存**: Redis
- **认证**: JWT (Access Token + Refresh Token)
- **密码加密**: passlib + bcrypt
- **配置管理**: Pydantic Settings (环境变量 / .env)
- **日志系统**: loguru 结构化日志
- **数据库迁移**: Alembic
- **测试**: pytest + httpx + pytest-asyncio
- **限流**: slowapi
- **监控**: Prometheus 指标

### 前端
- **框架**: Vue 3 + Vite
- **UI 组件**: Vant
- **状态管理**: Pinia
- **路由**: Vue Router

## 项目结构

```
├── 01-接口规范文档/           # API 接口文档
├── 02-数据库sql文件/           # 数据库初始化脚本
├── .github/workflows/         # GitHub Actions CI/CD
├── toutiao_backend/           # 后端 API 服务
│   ├── main.py               # 应用入口
│   ├── services/             # 业务逻辑层 (Service 层)
│   ├── crud/                 # 数据访问层 (CRUD)
│   ├── models/               # SQLAlchemy 数据模型
│   ├── routers/              # API 路由
│   ├── schemas/              # Pydantic 数据验证
│   ├── utils/                # 工具函数 (JWT/认证/安全/异常/响应)
│   ├── config/               # 配置文件 (DB/Redis/Settings/日志/限流)
│   ├── cache/                # Redis 缓存层（含缓存失效机制）
│   └── tests/                # 测试套件（46 项测试）
├── alembic/                  # 数据库迁移脚本
├── frontened/                # Vue 3 前端
├── Dockerfile                # Docker 容器化
├── docker-compose.yml        # Docker 多服务编排
└── requirements.txt          # Python 依赖
```

## 功能模块

- **用户管理**: 注册、登录、信息获取与更新、密码修改（含旧 Token 失效）
- **新闻管理**: 分类浏览、新闻列表（分页/筛选/关键字搜索）、详情查看、浏览量统计、相关新闻推荐
- **收藏管理**: 添加/取消收藏、收藏列表、状态检查、清空
- **浏览历史**: 添加记录（自动去重）、历史列表、单条删除、清空
- **JWT 认证**: Access Token（短期无状态）+ Refresh Token（DB 存储支持撤销）
- **限流保护**: slowapi 对登录/注册接口限流，防止暴力破解
- **分层架构**: Router → Service → CRUD → Model，关注点分离
- **缓存系统**: Redis 缓存新闻详情/列表/分类数据（带随机过期时间避免缓存雪崩，支持主动失效）
- **异常处理**: 统一异常响应格式，分级处理业务/数据库/系统异常（含完整日志记录）
- **全局配置**: Pydantic Settings 环境变量驱动，开发/生产环境分离
- **测试覆盖**: 46 项测试覆盖用户/新闻/收藏/历史/认证/安全/响应模块
- **健康检查**: `/health` 端点用于 Docker 和负载均衡探针

## 快速开始

### 环境要求

- Python 3.10+
- MySQL
- Redis

### 安装

```bash
# 安装后端依赖
pip install -r requirements.txt

# 初始化数据库
mysql -u root -p < 02-数据库sql文件/database.sql
```

### 配置

复制环境变量模板并修改：

```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库和 Redis 连接信息
```

### 启动

```bash
# 启动后端服务
cd toutiao_backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 启动前端 (新开终端)
cd frontened
npm install
npm run dev
```

### Docker 部署

```bash
docker-compose up --build
```

### 访问

- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health
- 前端页面: http://localhost:5173

## 数据库迁移

```bash
# 生成迁移脚本
alembic revision --autogenerate -m "描述变更"

# 应用迁移
alembic upgrade head

# 查看状态
alembic current

# 回滚
alembic downgrade -1
```

## 运行测试

```bash
# 运行所有测试
pytest toutiao_backend/tests/ -v

# 运行指定测试模块
pytest toutiao_backend/tests/test_security.py -v
```

## CI/CD

- GitHub Actions 自动运行测试（push/PR 到 main 分支）
- 测试环境自动启动 MySQL 和 Redis 服务

## API 接口

| 接口 | 方法 | 说明 | 认证 |
|------|------|------|------|
| `/health` | GET | 健康检查 | 否 |
| `/api/v1/user/register` | POST | 用户注册（限流 5次/分钟） | 否 |
| `/api/v1/user/login` | POST | 用户登录（限流 10次/分钟） | 否 |
| `/api/v1/user/info` | GET | 获取用户信息 | JWT |
| `/api/v1/user/update` | PUT | 更新用户信息 | JWT |
| `/api/v1/user/password` | PUT | 修改密码（旧 Token 失效） | JWT |
| `/api/v1/news/categories` | GET | 获取新闻分类 | 否 |
| `/api/v1/news/list` | GET | 获取新闻列表（支持关键字搜索） | 否 |
| `/api/v1/news/detail` | GET | 获取新闻详情（含相关新闻） | 否 |
| `/api/v1/favorite/check` | GET | 检查收藏状态 | JWT |
| `/api/v1/favorite/add` | POST | 添加收藏 | JWT |
| `/api/v1/favorite/remove` | DELETE | 取消收藏 | JWT |
| `/api/v1/favorite/list` | GET | 获取收藏列表 | JWT |
| `/api/v1/favorite/clear` | DELETE | 清空收藏 | JWT |
| `/api/v1/history/add` | POST | 添加浏览记录 | JWT |
| `/api/v1/history/list` | GET | 获取浏览历史 | JWT |
| `/api/v1/history/delete/{history_id}` | DELETE | 删除单条记录 | JWT |
| `/api/v1/history/clear` | DELETE | 清空历史 | JWT |

完整接口文档请查看 `01-接口规范文档/`。
