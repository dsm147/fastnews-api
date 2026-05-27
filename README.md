# AI掘金头条新闻系统 (Toutiao News)

基于 FastAPI + Vue 3 构建的现代化新闻系统，支持用户注册登录、新闻浏览、收藏和历史记录等功能。

## 技术栈

### 后端
- **框架**: FastAPI (异步)
- **数据库**: MySQL + SQLAlchemy (异步 ORM)
- **缓存**: Redis
- **认证**: Token 令牌机制
- **密码加密**: passlib + bcrypt

### 前端
- **框架**: Vue 3 + Vite
- **UI 组件**: Vant
- **状态管理**: Pinia
- **路由**: Vue Router

## 项目结构

```
├── 01-接口规范文档/           # API 接口文档
├── 02-数据库sql文件/           # 数据库初始化脚本
├── toutiao_backend/           # 后端 API 服务
│   ├── main.py               # 应用入口
│   ├── crud/                 # 数据访问层 (CRUD)
│   ├── models/               # SQLAlchemy 数据模型
│   ├── routers/              # API 路由
│   ├── schemas/              # Pydantic 数据验证
│   ├── utils/                # 工具函数 (认证/安全/异常/响应)
│   ├── config/               # 配置文件 (DB/Redis)
│   └── cache/                # Redis 缓存层
├── frontened/                # Vue 3 前端
└── requirements.txt          # Python 依赖
```

## 功能模块

- **用户管理**: 注册、登录、信息获取与更新、密码修改
- **新闻管理**: 分类浏览、新闻列表（分页/筛选）、详情查看、浏览统计
- **收藏管理**: 添加/取消收藏、收藏列表、收藏状态检查
- **浏览历史**: 添加记录、历史列表、单条删除、清空
- **缓存系统**: Redis 缓存新闻详情/列表/分类数据

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

编辑 `toutiao_backend/config/db_conf.py` 和 `toutiao_backend/config/cache_conf.py`，配置数据库和 Redis 连接信息。

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

### 访问

- API 文档: http://localhost:8000/docs
- 前端页面: http://localhost:5173

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/user/register` | POST | 用户注册 |
| `/api/user/login` | POST | 用户登录 |
| `/api/user/info` | GET | 获取用户信息 |
| `/api/news/categories` | GET | 获取新闻分类 |
| `/api/news/list` | GET | 获取新闻列表 |
| `/api/news/detail` | GET | 获取新闻详情 |
| `/api/favorite/add` | POST | 添加收藏 |
| `/api/favorite/list` | GET | 获取收藏列表 |
| `/api/history/list` | GET | 获取浏览历史 |

完整接口文档请查看 `01-接口规范文档/`。
