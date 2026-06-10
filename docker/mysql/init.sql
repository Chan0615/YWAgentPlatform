-- YW.Ops Portal 数据库初始化
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
SET time_zone = '+08:00';

CREATE DATABASE IF NOT EXISTS yw_agent_portal CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE yw_agent_portal;

-- 用户表
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `nickname` VARCHAR(100) DEFAULT '',
    `email` VARCHAR(100) DEFAULT '',
    `phone` VARCHAR(20) DEFAULT '',
    `avatar` VARCHAR(500) DEFAULT '',
    `status` TINYINT DEFAULT 1 COMMENT '1:启用 0:禁用',
    `last_login_at` DATETIME DEFAULT NULL,
    `last_login_ip` VARCHAR(50) DEFAULT '',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 角色表
CREATE TABLE IF NOT EXISTS `roles` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(50) NOT NULL,
    `code` VARCHAR(50) NOT NULL UNIQUE,
    `description` VARCHAR(200) DEFAULT '',
    `status` TINYINT DEFAULT 1,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 权限表 (树形结构)
CREATE TABLE IF NOT EXISTS `permissions` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `parent_id` INT DEFAULT 0 COMMENT '父级ID, 0为顶级',
    `name` VARCHAR(100) NOT NULL,
    `code` VARCHAR(100) NOT NULL UNIQUE COMMENT '权限编码 如 app:agenticops, menu:user, btn:user:create',
    `type` ENUM('app', 'menu', 'button') NOT NULL COMMENT '权限类型',
    `path` VARCHAR(200) DEFAULT '' COMMENT '前端路由路径',
    `icon` VARCHAR(100) DEFAULT '' COMMENT '图标',
    `sort_order` INT DEFAULT 0,
    `status` TINYINT DEFAULT 1,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 用户-角色关联表
CREATE TABLE IF NOT EXISTS `user_roles` (
    `user_id` INT NOT NULL,
    `role_id` INT NOT NULL,
    PRIMARY KEY (`user_id`, `role_id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`role_id`) REFERENCES `roles`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 角色-权限关联表
CREATE TABLE IF NOT EXISTS `role_permissions` (
    `role_id` INT NOT NULL,
    `permission_id` INT NOT NULL,
    PRIMARY KEY (`role_id`, `permission_id`),
    FOREIGN KEY (`role_id`) REFERENCES `roles`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`permission_id`) REFERENCES `permissions`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 应用注册表
CREATE TABLE IF NOT EXISTS `applications` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `code` VARCHAR(50) NOT NULL UNIQUE COMMENT '应用编码',
    `description` VARCHAR(500) DEFAULT '',
    `url` VARCHAR(500) NOT NULL COMMENT '应用访问地址',
    `icon` VARCHAR(100) DEFAULT 'AppstoreOutlined',
    `cover` VARCHAR(500) DEFAULT '' COMMENT '封面图',
    `sort_order` INT DEFAULT 0,
    `status` TINYINT DEFAULT 1 COMMENT '1:启用 0:禁用',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 操作审计日志表
CREATE TABLE IF NOT EXISTS `audit_logs` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT DEFAULT NULL,
    `username` VARCHAR(50) DEFAULT '',
    `action` VARCHAR(50) NOT NULL COMMENT '操作类型: login/create/update/delete',
    `resource_type` VARCHAR(50) DEFAULT '' COMMENT '资源类型: user/role/permission/application',
    `resource_id` VARCHAR(50) DEFAULT '',
    `detail` TEXT COMMENT '操作详情',
    `ip_address` VARCHAR(50) DEFAULT '',
    `user_agent` VARCHAR(500) DEFAULT '',
    `status` ENUM('success', 'fail') DEFAULT 'success',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_action` (`action`),
    INDEX `idx_created_at` (`created_at`),
    INDEX `idx_resource_type` (`resource_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- 初始化数据
-- ============================================

-- 默认管理员用户 (密码: admin123, bcrypt hash)
INSERT INTO `users` (`username`, `password_hash`, `nickname`, `email`, `status`) VALUES
('admin', '$2b$12$FMHxzrxSUkzUf7mhSNvs.OuPM5SAEiba2cMzhLywKle5ps6KNxx/u', '超级管理员', 'admin@yw.ops.com', 1);

-- 默认角色
INSERT INTO `roles` (`name`, `code`, `description`) VALUES
('超级管理员', 'admin', '拥有所有权限'),
('只读用户', 'readonly', '默认只读访问权限');

-- 默认权限 (树形结构)
-- 应用级权限
INSERT INTO `permissions` (`id`, `parent_id`, `name`, `code`, `type`, `icon`, `sort_order`) VALUES
(1, 0, 'AgenticOps 智能运维', 'app:agenticops', 'app', 'CloudServerOutlined', 1),
(2, 0, 'Agent 自动化平台', 'app:agent', 'app', 'RobotOutlined', 2),
(3, 0, 'Daily 数据工具', 'app:daily', 'app', 'DatabaseOutlined', 3);

-- 系统管理菜单权限
INSERT INTO `permissions` (`id`, `parent_id`, `name`, `code`, `type`, `path`, `icon`, `sort_order`) VALUES
(10, 0, '控制台', 'menu:dashboard', 'menu', '/dashboard', 'DashboardOutlined', 0),
(11, 0, '应用中心', 'menu:app-center', 'menu', '/app-center', 'AppstoreOutlined', 1),
(20, 0, '系统管理', 'menu:system', 'menu', '/system', 'SettingOutlined', 99),
(21, 20, '用户管理', 'menu:system:user', 'menu', '/system/users', 'UserOutlined', 1),
(22, 20, '角色管理', 'menu:system:role', 'menu', '/system/roles', 'TeamOutlined', 2),
(23, 20, '权限管理', 'menu:system:permission', 'menu', '/system/permissions', 'SafetyOutlined', 3),
(24, 20, '审计日志', 'menu:system:audit', 'menu', '/system/audit-log', 'FileSearchOutlined', 4),
(25, 20, '应用管理', 'menu:application', 'menu', '/system/applications', 'AppstoreAddOutlined', 5);

-- 按钮级权限 (用户管理)
INSERT INTO `permissions` (`parent_id`, `name`, `code`, `type`, `sort_order`) VALUES
(21, '创建用户', 'btn:user:create', 'button', 1),
(21, '编辑用户', 'btn:user:edit', 'button', 2),
(21, '删除用户', 'btn:user:delete', 'button', 3),
(21, '重置密码', 'btn:user:reset-pwd', 'button', 4),
(21, '分配角色', 'btn:user:assign-role', 'button', 5);

-- 按钮级权限 (角色管理)
INSERT INTO `permissions` (`parent_id`, `name`, `code`, `type`, `sort_order`) VALUES
(22, '创建角色', 'btn:role:create', 'button', 1),
(22, '编辑角色', 'btn:role:edit', 'button', 2),
(22, '删除角色', 'btn:role:delete', 'button', 3),
(22, '分配权限', 'btn:role:assign-perm', 'button', 4);

-- 按钮级权限 (应用管理)
INSERT INTO `permissions` (`parent_id`, `name`, `code`, `type`, `sort_order`) VALUES
(25, '注册应用', 'btn:application:create', 'button', 1),
(25, '编辑应用', 'btn:application:edit', 'button', 2),
(25, '删除应用', 'btn:application:delete', 'button', 3),
(25, '启用/禁用应用', 'btn:application:toggle', 'button', 4);

-- 超级管理员角色分配所有权限
INSERT INTO `role_permissions` (`role_id`, `permission_id`)
SELECT r.id, p.id
FROM `roles` r
CROSS JOIN `permissions` p
WHERE r.code = 'admin';

-- 只读角色分配基础可见权限
INSERT INTO `role_permissions` (`role_id`, `permission_id`)
SELECT r.id, p.id
FROM `roles` r
JOIN `permissions` p ON p.code IN (
  'menu:dashboard',
  'menu:app-center',
  'app:agenticops',
  'app:agent',
  'app:daily'
)
WHERE r.code = 'readonly';

-- 默认只读用户 (密码: readonly123, bcrypt hash)
INSERT INTO `users` (`username`, `password_hash`, `nickname`, `email`, `status`) VALUES
('readonly', '$2b$12$aAV2EQjM4eb3zKcL0xdi1u7oJPd4kTL4jNX.UNYNx/2Vt7XOA06MS', '只读用户', 'readonly@yw.ops.com', 1);

-- 用户分配角色
INSERT INTO `user_roles` (`user_id`, `role_id`)
SELECT u.id, r.id
FROM `users` u
JOIN `roles` r ON r.code = 'admin'
WHERE u.username = 'admin';

INSERT INTO `user_roles` (`user_id`, `role_id`)
SELECT u.id, r.id
FROM `users` u
JOIN `roles` r ON r.code = 'readonly'
WHERE u.username = 'readonly';
