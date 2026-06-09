#!/bin/bash
# ============================================
# YWAgentPlatform 一键部署/更新脚本
# 用法:
#   ./deploy.sh          # 更新全部 (拉代码+重建所有服务)
#   ./deploy.sh backend  # 仅更新后端
#   ./deploy.sh frontend # 仅更新前端
#   ./deploy.sh db       # 仅启动/重启数据库
#   ./deploy.sh init     # 首次部署 (全量初始化)
# ============================================

set -e

PROJECT_DIR="/data_ca/YWAgentPlatform"
COMPOSE_FILE="docker-compose.yml"
DB_COMPOSE_FILE="docker-compose.db.yml"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

cd "$PROJECT_DIR" || { log_error "项目目录不存在: $PROJECT_DIR"; exit 1; }

# 检查 .env 文件是否存在
check_env() {
    if [ ! -f .env ]; then
        log_error "缺少 .env 文件! 请先创建:"
        echo "  cp .env.example .env"
        echo "  然后编辑 .env 填入 MYSQL_ROOT_PASSWORD"
        exit 1
    fi
    if [ ! -f backend/.env ]; then
        log_error "缺少 backend/.env 文件! 请先创建:"
        echo "  cp backend/.env.example backend/.env"
        echo "  然后编辑填入真实密码和 JWT 密钥"
        exit 1
    fi
}

# 拉取最新代码
pull_code() {
    log_info "拉取最新代码..."
    git pull origin $(git rev-parse --abbrev-ref HEAD)
    log_info "当前版本: $(git log --oneline -1)"
}

# 仅启动数据库
deploy_db() {
    check_env
    log_info "启动 MySQL + Redis..."
    docker compose -f "$DB_COMPOSE_FILE" up -d
    log_info "等待数据库就绪..."
    sleep 10
    docker compose -f "$DB_COMPOSE_FILE" ps
    log_info "数据库启动完成"
}

# 部署后端
deploy_backend() {
    check_env
    log_info "构建并部署后端..."
    docker compose -f "$COMPOSE_FILE" up -d --build backend
    log_info "后端部署完成"
}

# 部署前端
deploy_frontend() {
    check_env
    log_info "构建并部署前端..."
    docker compose -f "$COMPOSE_FILE" up -d --build frontend
    # 重启 nginx 以加载新前端
    docker compose -f "$COMPOSE_FILE" restart nginx
    log_info "前端部署完成"
}

# 部署全部应用 (不含数据库，数据库由 docker-compose.db.yml 单独管理)
deploy_all() {
    check_env
    log_info "构建并部署所有应用服务 (Backend + Frontend + Nginx)..."
    docker compose -f "$COMPOSE_FILE" up -d --build
    log_info "全部应用服务部署完成"
}

# 首次初始化
deploy_init() {
    log_info "========== 首次部署初始化 =========="

    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先执行:"
        echo "  curl -fsSL https://get.docker.com | sh"
        echo "  systemctl enable --now docker"
        exit 1
    fi

    # 检查 Docker Compose 插件
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose 插件未安装，请先执行:"
        echo "  apt-get install docker-compose-plugin  (Ubuntu/Debian)"
        echo "  yum install docker-compose-plugin      (CentOS/RHEL)"
        exit 1
    fi

    # 检查 .env 文件
    if [ ! -f .env ]; then
        log_warn "未找到 .env 文件，从模板创建..."
        cp .env.example .env
        log_error "请编辑 .env 文件填入真实的 MYSQL_ROOT_PASSWORD，然后重新运行 ./deploy.sh init"
        exit 1
    fi

    if [ ! -f backend/.env ]; then
        log_warn "未找到 backend/.env，从模板创建..."
        cp backend/.env.example backend/.env
        log_error "请编辑 backend/.env 填入真实密码和 JWT 密钥，然后重新运行 ./deploy.sh init"
        exit 1
    fi

    # 1. 先启动数据库
    log_info "启动 MySQL + Redis..."
    deploy_db

    log_info "等待 MySQL 初始化 (首次需要 30 秒)..."
    sleep 30

    # 2. 再启动应用
    deploy_all

    # 健康检查
    log_info "执行健康检查..."
    if curl -sf http://localhost/health > /dev/null 2>&1; then
        log_info "健康检查通过"
    else
        log_warn "健康检查未通过，可能还在启动中，请稍后手动检查"
    fi

    echo ""
    log_info "========== 部署完成 =========="
    echo ""
    echo "  访问地址: http://10.225.138.183"
    echo "  API 文档: http://10.225.138.183:8010/docs"
    echo "  默认账号: 见 init.sql 中的初始化用户"
    echo ""
    echo "  配置域名访问:"
    echo "    修改本地 hosts: 10.225.138.183 yw.ops.com"
    echo "    然后访问: http://yw.ops.com"
    echo ""
}

# 显示状态
show_status() {
    echo ""
    log_info "当前容器状态:"
    docker compose -f "$COMPOSE_FILE" ps
    echo ""
    log_info "当前代码版本: $(git log --oneline -1)"
    echo ""
}

# 主逻辑
case "${1:-all}" in
    init)
        deploy_init
        ;;
    db)
        deploy_db
        ;;
    backend|back|api)
        pull_code
        deploy_backend
        show_status
        ;;
    frontend|front|web)
        pull_code
        deploy_frontend
        show_status
        ;;
    all|"")
        pull_code
        deploy_all
        show_status
        ;;
    status|ps)
        show_status
        ;;
    logs)
        docker compose -f "$COMPOSE_FILE" logs -f --tail=100 ${2:-}
        ;;
    restart)
        docker compose -f "$COMPOSE_FILE" restart ${2:-}
        show_status
        ;;
    down)
        docker compose -f "$COMPOSE_FILE" down
        log_info "所有服务已停止"
        ;;
    *)
        echo "用法: $0 {init|all|backend|frontend|db|status|logs|restart|down}"
        echo ""
        echo "  init      首次部署 (启动数据库 + 构建应用)"
        echo "  all       更新全部 (默认: git pull + 重建应用服务)"
        echo "  backend   仅更新后端 (git pull + 重建后端)"
        echo "  frontend  仅更新前端 (git pull + 重建前端)"
        echo "  db        仅启动/重启数据库 (MySQL + Redis)"
        echo "  status    查看服务状态"
        echo "  logs      查看日志 (可跟服务名: $0 logs backend)"
        echo "  restart   重启服务 (可跟服务名: $0 restart nginx)"
        echo "  down      停止应用服务 (不影响数据库)"
        exit 1
        ;;
esac
