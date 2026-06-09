# YWAgentPlatform - 统一运维管理平台

统一运维门户，类似阿里云控制台模式，提供统一入口管理多个运维子应用。

## 技术架构

| 层面 | 技术栈 |
|------|--------|
| 前端 | Vue 3 + TypeScript + Ant Design Vue 4 + Vite + Pinia |
| 后端 | Python 3.12 + FastAPI + SQLAlchemy 2.0 (async) + MySQL 8 |
| 缓存 | Redis 7 |
| 部署 | Docker Compose + Nginx |

## 核心功能

- **统一门户入口** - 所有运维应用统一访问入口
- **应用中心** - 卡片式展示，子应用通过 iframe 嵌入，Token 自动传递免登录
- **RBAC 权限** - 应用级 / 菜单级 / 按钮级精细权限控制
- **SSO 认证** - JWT 双Token（Access 30min + Refresh 7d）
- **操作审计** - 中间件自动记录所有写操作到审计日志表
- **用户管理** - 用户 CRUD、角色分配、状态启停
- **角色管理** - 角色 CRUD、权限树分配

## 权限模型

```
用户(User) ──M:N──▶ 角色(Role) ──M:N──▶ 权限(Permission)

权限类型 (三级):
  app:cmdb           → 应用级 (能否进入子应用)
  menu:system:user   → 菜单级 (侧边栏是否可见)
  btn:user:create    → 按钮级 (页面内操作按钮是否显示)

示例:
  用户A → CMDB管理员   → app:cmdb (能进CMDB，不能进工单)
  用户B → Agent管理员  → app:agent (能进Agent，不能进CMDB)
  用户C → 超级管理员   → 所有权限
```

前端通过 `v-permission="'btn:user:create'"` 指令控制按钮显隐。

## 接入的子应用

| 应用 | 编码 | 说明 | 技术栈 |
|------|------|------|--------|
| AgenticOps 智能运维 | cmdb | AI运维平台（资产管理、RAG知识库、NL2SQL） | FastAPI + Vue 3 |
| Agent 自动化平台 | agent | 多Agent运维自动化（工作流、SSH、告警） | Express + React 18 |
| Daily 数据工具 | daily | 游戏运营数据查询与导出 | Python Scripts |

子应用接入方式: Portal 通过 iframe 加载子应用 URL，附带 Token 参数实现免登录。

## 目录结构

```
YWAgentPlatform/
├── frontend/                    # 前端 (Vue 3 + Ant Design Vue 4)
│   ├── src/
│   │   ├── api/                 # API 请求封装
│   │   ├── directives/          # v-permission 按钮权限指令
│   │   ├── layouts/             # MainLayout (侧边栏+顶栏+内容区)
│   │   ├── router/              # 路由 + 导航守卫
│   │   ├── store/               # Pinia 状态 (user/app)
│   │   ├── utils/               # Token 工具
│   │   └── views/               # 页面
│   │       ├── login/           # 登录
│   │       ├── dashboard/       # 工作台
│   │       ├── app-center/      # 应用中心 (卡片)
│   │       ├── app-container/   # 子应用 iframe 容器
│   │       └── system/          # 用户/角色/权限/审计日志
│   ├── Dockerfile
│   └── package.json
├── backend/                     # 后端 (Python 3.12 + FastAPI)
│   ├── app/
│   │   ├── api/                 # 路由 (auth/users/roles/permissions/applications/audit)
│   │   ├── core/                # 配置、安全、数据库
│   │   ├── models/              # SQLAlchemy 模型
│   │   ├── schemas/             # Pydantic 数据校验
│   │   ├── middleware/          # 审计日志中间件
│   │   └── services/            # 初始化种子数据
│   ├── .env.example             # 环境变量模板
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
├── nginx/
│   └── default.conf             # Nginx 反向代理
├── docker/
│   └── mysql/
│       └── init.sql             # 数据库建表 + 种子数据
├── docker-compose.yml           # 应用部署 (Backend + Frontend + Nginx)
├── docker-compose.db.yml        # 数据库部署 (MySQL + Redis)
├── deploy.sh                    # 一键部署/更新脚本
├── .env.example                 # docker-compose 环境变量模板
├── .gitignore
├── 部署文档.md                   # 详细部署步骤
└── README.md
```

## API 概览

| 模块 | 路径前缀 | 说明 |
|------|----------|------|
| 认证 | `/api/v1/auth` | 登录、登出、刷新Token、获取用户信息 |
| 用户 | `/api/v1/users` | 用户 CRUD、分配角色 |
| 角色 | `/api/v1/roles` | 角色 CRUD、分配权限 |
| 权限 | `/api/v1/permissions` | 权限树 CRUD |
| 应用 | `/api/v1/applications` | 子应用注册管理、可见应用列表 |
| 审计 | `/api/v1/audit-logs` | 操作日志查询 (仅管理员) |
