# PDF文档托管平台 - 开发文档

## 项目概述

### 1.1 项目简介
本文档描述了一个PDF文档托管平台的技术方案和实现细节。该平台旨在为用户提供专业的PDF文档存储、阅读、下载服务，并通过会员体系实现商业化运营。

平台采用前后端分离架构，前端使用Vue 3框架实现响应式界面，后端使用Python FastAPI框架构建RESTful API服务，数据存储采用MySQL数据库，文件存储使用阿里云OSS对象存储服务。整体设计注重用户体验和系统性能，确保在低成本条件下实现稳定、高效的服务。

平台支持PC端和移动端的自适应展示，用户可以在任何设备上便捷地浏览和阅读PDF文档。会员系统提供了灵活的付费模式，包括普通会员和终身会员两种类型，满足不同用户群体的需求。管理后台功能完善，支持文档管理、用户管理、兑换码管理和数据统计等核心业务功能。

### 1.2 技术栈概览

前端技术选型方面，本项目采用Vue 3作为核心框架，配合Vite构建工具实现快速开发和热更新。UI组件库选择Element Plus，该组件库提供了丰富的企业级组件，能够满足复杂的界面交互需求。PDF阅读功能使用pdf.js库实现，这是Mozilla官方维护的PDF解析库，在浏览器端具有良好的兼容性和性能表现。状态管理采用Pinia，这是Vue官方推荐的状态管理方案，相比Vuex具有更简洁的API和更好的TypeScript支持。路由管理使用Vue Router 4，实现单页应用的路由控制。

后端技术选型方面，本项目采用Python FastAPI作为Web框架。FastAPI是一个现代化的高性能Python Web框架，原生支持异步操作，具有自动生成API文档、类型检查、数据验证等特性。数据库ORM层使用SQLAlchemy，它是Python生态中最成熟的ORM框架，支持多种数据库后端。认证模块采用JWT（JSON Web Token）方案，实现无状态的分布式认证。文件上传和存储集成阿里云OSS SDK，支持大文件分片上传和断点续传。

数据库选用MySQL 8.0版本，这是目前最流行的开源关系型数据库之一，具有成熟的生态系统和良好的性能表现。文件存储采用阿里云OSS对象存储服务，该服务提供高可用、高可靠、低成本的云端存储能力，支持CDN加速和图片处理等增值功能。

### 1.3 系统架构

系统整体采用前后端分离架构，各模块之间通过RESTful API进行数据交互。前端负责用户界面渲染和交互逻辑处理，后端负责业务逻辑处理和数据持久化，数据库负责结构化数据存储，OSS负责非结构化文件存储。这种架构设计使得系统各组件可以独立扩展和维护，提高了系统的可维护性和可扩展性。

前端应用部署时采用动静分离策略，静态资源通过CDN加速分发，API请求转发到后端服务器。后端应用采用Uvicorn作为ASGI服务器运行FastAPI应用，支持异步请求处理。数据库和文件存储使用云服务，降低了运维复杂度和基础设施成本。

---

## 数据库设计

### 2.1 数据库概览

本项目使用MySQL 8.0作为主数据库，设计了完善的数据模型来支撑业务需求。数据库设计遵循第三范式，通过合理的主键设计和外键约束确保数据完整性和一致性。同时，考虑到查询性能需求，在高频访问的字段上创建了适当的索引。

数据库实例建议配置如下：字符集选择utf8mb4，以支持完整的Unicode字符集，包括表情符号；排序规则选择utf8mb4_unicode_ci，提供准确的Unicode排序和比较；存储引擎使用InnoDB，支持事务和外键约束。

### 2.2 数据表设计

#### 2.2.1 用户表（users）

用户表存储所有注册用户的基本信息，是整个平台业务的核心基础表之一。

```sql
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username` varchar(50) NOT NULL COMMENT '用户名，唯一',
  `email` varchar(100) NOT NULL COMMENT '邮箱地址，唯一',
  `password_hash` varchar(255) NOT NULL COMMENT '密码哈希值',
  `avatar` varchar(500) DEFAULT NULL COMMENT '头像URL',
  `role` enum('user','admin','super_admin') NOT NULL DEFAULT 'user' COMMENT '用户角色',
  `status` enum('active','inactive','banned') NOT NULL DEFAULT 'active' COMMENT '账户状态',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `last_login_at` datetime DEFAULT NULL COMMENT '最后登录时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`),
  UNIQUE KEY `uk_email` (`email`),
  KEY `idx_status` (`status`),
  KEY `idx_role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';
```

用户名字段长度限制为50个字符，足够满足常规用户名需求，同时通过唯一约束防止重复注册。邮箱字段同样设置唯一约束，支持用户通过邮箱找回密码和接收系统通知。密码采用哈希存储，不存储明文密码，使用bcrypt或argon2算法进行加密，提高安全性。

角色字段区分普通用户、管理员和超级管理员三级权限体系。普通用户只能访问前台功能，管理员可以管理文档和用户，超级管理员拥有最高权限，可以进行系统级配置。

#### 2.2.2 文档表（documents）

文档表存储所有PDF文档的元数据信息，是平台内容管理的核心表。

```sql
CREATE TABLE `documents` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '文档ID',
  `title` varchar(200) NOT NULL COMMENT '文档标题',
  `description` text COMMENT '文档描述',
  `category_id` int DEFAULT NULL COMMENT '分类ID',
  `cover_image` varchar(500) DEFAULT NULL COMMENT '封面图片URL',
  `file_path` varchar(500) NOT NULL COMMENT 'OSS文件路径',
  `file_name` varchar(255) NOT NULL COMMENT '原始文件名',
  `file_size` bigint NOT NULL COMMENT '文件大小（字节）',
  `page_count` int DEFAULT NULL COMMENT 'PDF页数',
  `view_count` int NOT NULL DEFAULT 0 COMMENT '浏览次数',
  `download_count` int NOT NULL DEFAULT 0 COMMENT '下载次数',
  `status` enum('draft','published','archived') NOT NULL DEFAULT 'draft' COMMENT '文档状态',
  `is_delete` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否删除（软删除）',
  `created_by` int NOT NULL COMMENT '创建者ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `published_at` datetime DEFAULT NULL COMMENT '发布时间',
  PRIMARY KEY (`id`),
  KEY `idx_category` (`category_id`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`),
  KEY `idx_title` (`title`(100)),
  FULLTEXT KEY `ft_title_desc` (`title`,`description`) WITH PARSER ngram
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文档表';
```

文档标题限制200字符，支持中文和英文描述。描述字段使用TEXT类型，可以存储较长文本内容。文件路径存储阿里云OSS中的相对路径，结合配置的OSS域名可以拼装出完整的文件访问URL。

全文索引支持中文分词搜索，使用ngram解析器实现中文关键词检索。文档状态区分草稿、已发布和归档三种状态，支持内容的分阶段发布和管理。

#### 2.2.3 分类表（categories）

分类表用于组织文档的分类层级结构，支持多级分类。

```sql
CREATE TABLE `categories` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '分类ID',
  `name` varchar(50) NOT NULL COMMENT '分类名称',
  `slug` varchar(50) NOT NULL COMMENT '分类别名（URL友好）',
  `description` varchar(255) DEFAULT NULL COMMENT '分类描述',
  `parent_id` int DEFAULT NULL COMMENT '父分类ID',
  `icon` varchar(100) DEFAULT NULL COMMENT '分类图标',
  `sort_order` int NOT NULL DEFAULT 0 COMMENT '排序序号',
  `is_active` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_slug` (`slug`),
  KEY `idx_parent` (`parent_id`),
  KEY `idx_sort` (`sort_order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='分类表';
```

分类支持无限层级嵌套，通过parent_id外键实现父子关系。slug字段用于生成URL别名，要求唯一且只包含字母、数字和连字符。sort_order字段支持手动排序，数值越小排序越靠前。

#### 2.2.4 标签表（tags）

标签表提供文档的标签功能，支持多对多关系。

```sql
CREATE TABLE `tags` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '标签ID',
  `name` varchar(30) NOT NULL COMMENT '标签名称',
  `slug` varchar(30) NOT NULL COMMENT '标签别名',
  `color` varchar(20) DEFAULT NULL COMMENT '标签颜色（前端展示用）',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_name` (`name`),
  UNIQUE KEY `uk_slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='标签表';

CREATE TABLE `document_tags` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '关系ID',
  `document_id` int NOT NULL COMMENT '文档ID',
  `tag_id` int NOT NULL COMMENT '标签ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_doc_tag` (`document_id`,`tag_id`),
  KEY `idx_document` (`document_id`),
  KEY `idx_tag` (`tag_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文档标签关联表';
```

标签名称限制30字符，避免过长影响界面展示。通过中间表document_tags实现文档和标签的多对多关系，复合唯一键防止重复关联。

#### 2.2.5 会员表（memberships）

会员表记录用户的会员状态和权益信息。

```sql
CREATE TABLE `memberships` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '会员记录ID',
  `user_id` int NOT NULL COMMENT '用户ID',
  `type` enum('free','normal','lifetime') NOT NULL DEFAULT 'free' COMMENT '会员类型',
  `expires_at` datetime DEFAULT NULL COMMENT '过期时间',
  `download_quota` int NOT NULL DEFAULT 0 COMMENT '下载额度',
  `download_used` int NOT NULL DEFAULT 0 COMMENT '已使用下载次数',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user` (`user_id`),
  KEY `idx_type` (`type`),
  KEY `idx_expires` (`expires_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='会员表';
```

会员类型区分免费会员（默认）、普通会员和终身会员三种。免费会员不限制有效期，但下载额度较少。普通会员的expires_at字段记录有效期，download_quota记录年度下载额度。终身会员的expires_at设置为NULL表示永不过期。

下载额度的计算逻辑：对于普通会员，每年重置一次下载额度，重置时间为会员到期日的当天；对于终身会员，download_quota设置为-1表示无限下载。

#### 2.2.6 兑换码表（redeem_codes）

兑换码表用于管理会员兑换码的生成和使用。

```sql
CREATE TABLE `redeem_codes` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '兑换码ID',
  `code` varchar(50) NOT NULL COMMENT '兑换码',
  `type` enum('normal','lifetime') NOT NULL COMMENT '兑换类型',
  `uses_total` int NOT NULL DEFAULT 1 COMMENT '总使用次数',
  `uses_remaining` int NOT NULL DEFAULT 1 COMMENT '剩余使用次数',
  `expires_at` datetime DEFAULT NULL COMMENT '过期时间',
  `is_active` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
  `created_by` int NOT NULL COMMENT '创建者ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `used_at` datetime DEFAULT NULL COMMENT '最后使用时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_code` (`code`),
  KEY `idx_type` (`type`),
  KEY `idx_expires` (`expires_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='兑换码表';
```

兑换码采用随机字符串生成，支持设置使用次数（单次或多次）和有效期。创建者ID记录兑换码的创建人，便于审计追溯。

#### 2.2.7 兑换记录表（redemptions）

兑换记录表详细记录每次兑换码使用的具体信息。

```sql
CREATE TABLE `redemptions` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '兑换记录ID',
  `user_id` int NOT NULL COMMENT '用户ID',
  `redeem_code_id` int NOT NULL COMMENT '兑换码ID',
  `membership_type` enum('normal','lifetime') NOT NULL COMMENT '兑换后的会员类型',
  `old_expires_at` datetime DEFAULT NULL COMMENT '原会员到期时间',
  `new_expires_at` datetime DEFAULT NULL COMMENT '新会员到期时间',
  `old_quota` int DEFAULT NULL COMMENT '原下载额度',
  `new_quota` int DEFAULT NULL COMMENT '新下载额度',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '兑换时间',
  PRIMARY KEY (`id`),
  KEY `idx_user` (`user_id`),
  KEY `idx_code` (`redeem_code_id`),
  KEY `idx_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='兑换记录表';
```

兑换记录详细保存了兑换前后的会员状态变更，便于追溯会员权益变化历史。old_*和new_*字段分别记录兑换前后的状态快照。

#### 2.2.8 下载记录表（downloads）

下载记录表用于记录每次文档下载的详细信息，支持下载次数统计和用户行为分析。

```sql
CREATE TABLE `downloads` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '下载记录ID',
  `user_id` int NOT NULL COMMENT '用户ID',
  `document_id` int NOT NULL COMMENT '文档ID',
  `ip_address` varchar(45) DEFAULT NULL COMMENT 'IP地址',
  `user_agent` varchar(500) DEFAULT NULL COMMENT '用户代理',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '下载时间',
  PRIMARY KEY (`id`),
  KEY `idx_user` (`user_id`),
  KEY `idx_document` (`document_id`),
  KEY `idx_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='下载记录表';
```

下载记录关联用户和文档，便于统计用户下载行为和文档受欢迎程度。IP地址和用户代理字段支持地理分布分析和异常检测。

#### 2.2.9 阅读记录表（reading_history）

阅读记录表用于记录用户的PDF阅读历史，支持阅读进度追踪和个性化推荐。

```sql
CREATE TABLE `reading_history` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `user_id` int NOT NULL COMMENT '用户ID',
  `document_id` int NOT NULL COMMENT '文档ID',
  `last_page` int NOT NULL DEFAULT 1 COMMENT '最后阅读页码',
  `total_time` int NOT NULL DEFAULT 0 COMMENT '累计阅读时长（秒）',
  `is_completed` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否读完',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_doc` (`user_id`,`document_id`),
  KEY `idx_document` (`document_id`),
  KEY `idx_updated` (`updated_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='阅读记录表';
```

每个用户对每篇文档只有一条阅读记录，通过UNIQUE KEY确保唯一性。last_page字段保存用户最后阅读的页码，支持断点续读功能。total_time字段累计阅读时长，支持阅读统计分析。

#### 2.2.10 订单表（orders）

订单表用于记录会员购买订单信息（预留支付功能扩展）。

```sql
CREATE TABLE `orders` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '订单ID',
  `order_no` varchar(50) NOT NULL COMMENT '订单号',
  `user_id` int NOT NULL COMMENT '用户ID',
  `product_type` enum('normal_member','lifetime_member') NOT NULL COMMENT '产品类型',
  `amount` decimal(10,2) NOT NULL COMMENT '订单金额',
  `status` enum('pending','paid','cancelled','refunded') NOT NULL DEFAULT 'pending' COMMENT '订单状态',
  `pay_method` varchar(50) DEFAULT NULL COMMENT '支付方式',
  `transaction_id` varchar(100) DEFAULT NULL COMMENT '第三方交易号',
  `paid_at` datetime DEFAULT NULL COMMENT '支付时间',
  `expired_at` datetime DEFAULT NULL COMMENT '订单过期时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_order_no` (`order_no`),
  KEY `idx_user` (`user_id`),
  KEY `idx_status` (`status`),
  KEY `idx_paid` (`paid_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单表';
```

订单表设计支持未来扩展第三方支付功能。order_no字段生成规则建议采用时间戳+随机数的组合，确保全局唯一。状态机设计支持订单完整生命周期管理。

### 2.3 数据库优化建议

针对高频查询场景，建议创建以下复合索引以提升查询性能：

文档列表查询索引：CREATE INDEX idx_documents_list ON documents(status, category_id, created_at DESC)

用户下载统计索引：CREATE INDEX idx_downloads_user_month ON downloads(user_id, created_at)

阅读历史查询索引：CREATE INDEX idx_reading_user_recent ON reading_history(user_id, updated_at DESC)

对于数据量较大的表（如下载记录、阅读历史），建议按月进行分区存储，或者定期归档历史数据到归档表，保持主表的数据量在可控范围内。分区可以显著提升查询性能，同时简化历史数据的清理工作。

---

## API接口设计

### 3.1 接口规范

本项目API接口遵循RESTful设计规范，采用JSON格式进行数据交换。接口URL使用名词复数形式，HTTP方法表示操作类型，返回状态码遵循HTTP标准定义。

请求头需要包含Content-Type: application/json和Authorization: Bearer {token}（需要认证的接口）。响应数据采用统一的JSON结构，包含code（业务状态码）、message（提示信息）和data（业务数据）三个字段。

```
成功响应格式：
{
  "code": 0,
  "message": "success",
  "data": {
    // 业务数据
  }
}

失败响应格式：
{
  "code": 1001,
  "message": "用户名或密码错误",
  "data": null
}
```

### 3.2 认证模块接口

#### 3.2.1 用户注册

用户注册接口用于创建新用户账户，支持用户名和邮箱两种注册方式。

**接口信息：**
- URL: POST /api/v1/auth/register
- 认证：不需要
- 限流：每IP每分钟最多10次

**请求参数：**

| 参数名 | 类型 | 必填 | 长度限制 | 说明 |
|--------|------|------|----------|------|
| username | string | 是 | 3-50 | 用户名 |
| email | string | 是 | 最大100 | 邮箱地址 |
| password | string | 是 | 最小8位 | 密码 |
| confirm_password | string | 是 | - | 确认密码 |

**请求示例：**
```json
{
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "password": "Password123",
  "confirm_password": "Password123"
}
```

**响应示例：**
```json
{
  "code": 0,
  "message": "注册成功",
  "data": {
    "user_id": 10001,
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "membership": {
      "type": "free",
      "expires_at": null,
      "download_quota": 5
    }
  }
}
```

**业务规则：**
- 用户名不能重复
- 邮箱格式必须正确
- 两次密码输入必须一致
- 密码必须包含字母和数字
- 注册成功后自动创建免费会员记录
- 注册成功后自动登录，返回access_token和refresh_token

#### 3.2.2 用户登录

用户登录接口支持用户名或邮箱+密码的登录方式，登录成功后返回JWT令牌。

**接口信息：**
- URL: POST /api/v1/auth/login
- 认证：不需要
- 限流：每IP每分钟最多20次

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| account | string | 是 | 用户名或邮箱 |
| password | string | 是 | 密码 |
| remember | boolean | 否 | 记住登录状态，默认false |

**请求示例：**
```json
{
  "account": "zhangsan",
  "password": "Password123",
  "remember": true
}
```

**响应示例：**
```json
{
  "code": 0,
  "message": "登录成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 86400,
    "token_type": "Bearer",
    "user_info": {
      "id": 10001,
      "username": "zhangsan",
      "avatar": null,
      "membership": {
        "type": "normal",
        "expires_at": "2027-02-05T00:00:00",
        "download_quota": 100,
        "download_used": 5
      }
    }
  }
}
```

**业务规则：**
- 账号可以是用户名或邮箱（邮箱需验证格式）
- 密码错误5次后锁定账号15分钟
- 登录成功更新last_login_at时间
- remember为true时access_token有效期7天，否则1天
- refresh_token有效期30天，用于刷新access_token

#### 3.2.3 刷新令牌

当access_token过期时，使用refresh_token获取新的access_token。

**接口信息：**
- URL: POST /api/v1/auth/refresh
- 认证：不需要（需要refresh_token）

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| refresh_token | string | 是 | 刷新令牌 |

**响应示例：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "access_token": "新的access_token",
    "refresh_token": "新的refresh_token",
    "expires_in": 86400
  }
}
```

#### 3.2.4 用户登出

用户登出接口使当前令牌失效。

**接口信息：**
- URL: POST /api/v1/auth/logout
- 认证：需要

**响应示例：**
```json
{
  "code": 0,
  "message": "登出成功",
  "data": null
}
```

**业务规则：**
- 将当前token加入黑名单（Redis存储）
- 清除客户端的token存储

### 3.3 用户模块接口

#### 3.3.1 获取用户信息

获取当前登录用户的详细信息。

**接口信息：**
- URL: GET /api/v1/users/profile
- 认证：需要

**响应示例：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 10001,
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "avatar": "https://oss.example.com/avatars/avatar.png",
    "role": "user",
    "status": "active",
    "created_at": "2025-02-05T10:30:00",
    "last_login_at": "2026-02-05T19:26:11",
    "membership": {
      "type": "normal",
      "expires_at": "2027-02-05T00:00:00",
      "download_quota": 100,
      "download_used": 5,
      "days_remaining": 365
    }
  }
}
```

#### 3.3.2 修改用户名

修改当前用户的用户名，每月限制修改1次。

**接口信息：**
- URL: PUT /api/v1/users/username
- 认证：需要

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| new_username | string | 是 | 新用户名 |
| password | string | 是 | 当前密码 |

**请求示例：**
```json
{
  "new_username": "lisi",
  "password": "Password123"
}
```

**响应示例：**
```json
{
  "code": 0,
  "message": "用户名修改成功",
  "data": {
    "username": "lisi"
  }
}
```

**业务规则：**
- 新用户名不能与现有用户名重复
- 每月1日重置修改次数
- 需要验证当前密码
- 普通用户每月限1次，VIP用户不限次数

#### 3.3.3 修改密码

修改当前用户的登录密码。

**接口信息：**
- URL: PUT /api/v1/users/password
- 认证：需要

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| old_password | string | 是 | 当前密码 |
| new_password | string | 是 | 新密码 |
| confirm_password | string | 是 | 确认密码 |

**业务规则：**
- 新密码必须包含字母和数字
- 新密码不能与最近3次使用的密码相同
- 修改成功后所有令牌失效，需要重新登录

#### 3.3.4 修改邮箱

修改当前用户的邮箱地址。

**接口信息：**
- URL: PUT /api/v1/users/email
- 认证：需要

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| new_email | string | 是 | 新邮箱 |
| password | string | 是 | 当前密码 |

**业务规则：**
- 新邮箱不能与现有邮箱重复
- 需要验证当前密码
- 建议发送验证邮件确认新邮箱所有权

### 3.4 文档模块接口

#### 3.4.1 获取文档列表

获取已发布文档的分页列表。

**接口信息：**
- URL: GET /api/v1/documents
- 认证：不需要

**请求参数：**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| page | int | 否 | 1 | 当前页码 |
| page_size | int | 否 | 20 | 每页数量 |
| category_id | int | 否 | - | 分类ID筛选 |
| tag_id | int | 否 | - | 标签ID筛选 |
| keyword | string | 否 | - | 关键词搜索 |
| sort | string | 否 | latest | 排序方式：latest/popular/downloads |

**响应示例：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1001,
        "title": "Python编程指南",
        "description": "一本全面的Python入门教程",
        "category": {
          "id": 1,
          "name": "编程开发"
        },
        "cover_image": "https://oss.example.com/covers/python.png",
        "file_size": 5242880,
        "page_count": 328,
        "view_count": 1520,
        "download_count": 325,
        "tags": [
          {"id": 1, "name": "Python", "color": "#357ABD"}
        ],
        "created_at": "2026-01-15T10:00:00"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 156,
      "total_pages": 8
    }
  }
}
```

#### 3.4.2 获取文档详情

获取单篇文档的详细信息。

**接口信息：**
- URL: GET /api/v1/documents/:id
- 认证：不需要

**响应示例：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1001,
    "title": "Python编程指南",
    "description": "一本全面的Python入门教程，从基础语法到项目实战...",
    "category": {
      "id": 1,
      "name": "编程开发",
      "slug": "programming"
    },
    "cover_image": "https://oss.example.com/covers/python.png",
    "file_path": "documents/python-guide.pdf",
    "file_size": 5242880,
    "page_count": 328,
    "view_count": 1520,
    "download_count": 325,
    "status": "published",
    "tags": [
      {"id": 1, "name": "Python", "color": "#357ABD"},
      {"id": 5, "name": "入门", "color": "#28A745"}
    ],
    "created_by": {
      "id": 1,
      "username": "admin"
    },
    "created_at": "2026-01-15T10:00:00",
    "updated_at": "2026-01-20T14:30:00"
  }
}
```

#### 3.4.3 获取文档阅读地址

获取PDF在线阅读的访问地址。

**接口信息：**
- URL: GET /api/v1/documents/:id/read
- 认证：需要

**响应示例：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "read_url": "https://oss.example.com/read/python-guide.pdf?token=xxx",
    "expires_in": 3600,
    "document_info": {
      "id": 1001,
      "title": "Python编程指南",
      "page_count": 328,
      "current_page": 15
    }
  }
}
```

**业务规则：**
- 需要用户登录
- 返回的read_url有效期1小时
- 更新文档view_count
- 如果用户之前阅读过，返回上次阅读位置

#### 3.4.4 获取文档下载链接

获取PDF文档的下载链接。

**接口信息：**
- URL: GET /api/v1/documents/:id/download
- 认证：需要

**响应示例：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "download_url": "https://oss.example.com/downloads/python-guide.pdf?token=xxx",
    "expires_in": 3600,
    "file_name": "Python编程指南.pdf",
    "file_size": 5242880
  }
}
```

**业务规则：**
- 需要用户登录
- 验证用户下载权限
- 免费用户每月限5次
- 普通会员检查年度下载额度
- 终身会员无限制
- 记录下载日志

### 3.5 会员模块接口

#### 3.5.1 获取会员状态

获取当前用户的会员状态和权益信息。

**接口信息：**
- URL: GET /api/v1/membership/status
- 认证：需要

**响应示例：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "type": "normal",
    "expires_at": "2027-02-05T00:00:00",
    "download_quota": 100,
    "download_used": 5,
    "download_remaining": 95,
    "days_remaining": 365,
    "can_upgrade": true,
    "benefits": [
      "无限阅读所有文档",
      "年度下载额度100篇",
      "可叠加续费延长有效期"
    ]
  }
}
```

#### 3.5.2 使用兑换码

使用兑换码开通或续期会员。

**接口信息：**
- URL: POST /api/v1/membership/redeem
- 认证：需要

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | 兑换码 |

**请求示例：**
```json
{
  "code": "ABC123XYZ"
}
```

**响应示例：**
```json
{
  "code": 0,
  "message": "兑换成功",
  "data": {
    "membership_type": "lifetime",
    "expires_at": null,
    "download_quota": -1,
    "old_type": "normal",
    "old_expires_at": "2027-02-05T00:00:00",
    "benefits": [
      "终身有效",
      "无限下载所有文档"
    ]
  }
}
```

**业务规则：**
- 验证兑换码有效性
- 终身会员兑换码只能兑换一次
- 普通会员兑换码可叠加有效期和额度
- 兑换后更新会员状态
- 记录兑换历史

### 3.6 管理模块接口

#### 3.6.1 文档管理

管理员对文档进行增删改查操作。

**接口列表：**
- POST /api/v1/admin/documents - 创建文档
- PUT /api/v1/admin/documents/:id - 更新文档
- DELETE /api/v1/admin/documents/:id - 删除文档
- PUT /api/v1/admin/documents/batch/status - 批量更新状态
- DELETE /api/v1/admin/documents/batch - 批量删除

**创建文档请求参数：**
```json
{
  "title": "新文档标题",
  "description": "文档描述",
  "category_id": 1,
  "tag_ids": [1, 2, 3],
  "cover_image": "base64编码或OSS URL",
  "file": "multipart/form-data文件",
  "status": "published"
}
```

**业务规则：**
- 只有admin和super_admin角色可以访问
- 文件上传限制PDF格式，最大50MB
- 自动提取PDF页数
- 上传成功后异步处理封面生成

#### 3.6.2 兑换码管理

管理员生成和管理兑换码。

**接口列表：**
- POST /api/v1/admin/redeem-codes/generate - 批量生成
- GET /api/v1/admin/redeem-codes - 列表查询
- GET /api/v1/admin/redeem-codes/:id - 详情
- PUT /api/v1/admin/redeem-codes/:id - 更新
- DELETE /api/v1/admin/redeem-codes/:id - 删除

**批量生成请求参数：**
```json
{
  "type": "normal",
  "count": 100,
  "uses_per_code": 1,
  "expires_at": "2027-12-31",
  "prefix": "VIP2026"
}
```

**响应示例：**
```json
{
  "code": 0,
  "message": "生成成功",
  "data": {
    "total": 100,
    "codes": [
      "VIP2026A1B2C3D4",
      "VIP2026E5F6G7H8",
      // ...共100个
    ]
  }
}
```

#### 3.6.3 用户管理

管理员查看和管理用户信息。

**接口列表：**
- GET /api/v1/admin/users - 用户列表
- GET /api/v1/admin/users/:id - 用户详情
- PUT /api/v1/admin/users/:id - 更新用户
- PUT /api/v1/admin/users/:id/status - 更新状态
- GET /api/v1/admin/users/:id/downloads - 下载记录

**用户列表请求参数：**
```json
{
  "page": 1,
  "page_size": 20,
  "keyword": "搜索用户名或邮箱",
  "membership_type": "normal",
  "status": "active",
  "created_start": "2026-01-01",
  "created_end": "2026-12-31"
}
```

**用户详情响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 10001,
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "role": "user",
    "status": "active",
    "membership": {
      "type": "normal",
      "expires_at": "2027-02-05T00:00:00",
      "download_quota": 100,
      "download_used": 5
    },
    "statistics": {
      "total_downloads": 5,
      "total_reads": 23,
      "member_since": "2025-02-05T10:30:00"
    },
    "created_at": "2025-02-05T10:30:00",
    "last_login_at": "2026-02-05T19:26:11"
  }
}
```

**业务规则：**
- 只有admin和super_admin角色可以访问
- 普通管理员不能修改super_admin
- 用户名和邮箱不可修改
- 可以调整会员类型和有效期

#### 3.6.4 数据统计

管理员查看系统运营数据。

**接口信息：**
- URL: GET /api/v1/admin/stats
- 认证：需要（admin角色）

**请求参数：**
```json
{
  "start_date": "2026-01-01",
  "end_date": "2026-02-05",
  "type": "overview"  // overview/downloads/users/documents
}
```

**概览统计响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "overview": {
      "total_users": 1520,
      "total_documents": 328,
      "total_downloads": 15230,
      "total_views": 125680,
      "membership_stats": {
        "free": 980,
        "normal": 480,
        "lifetime": 60
      }
    },
    "period_stats": {
      "new_users": 156,
      "new_documents": 23,
      "downloads": 1523,
      "views": 12568
    },
    "trend": [
      {"date": "2026-01-01", "downloads": 52, "views": 420},
      {"date": "2026-01-02", "downloads": 48, "views": 385},
      // ...
    ]
  }
}
```

---

## 前端架构设计

### 4.1 项目结构

前端项目采用Vue 3 + Vite构建，使用TypeScript进行类型增强。目录结构清晰划分，职责明确，便于团队协作和代码维护。

```
frontend/
├── public/                     # 静态资源
│   ├── favicon.ico            # 网站图标
│   ├── robots.txt             # 爬虫协议
│   └── images/                # 公共图片
├── src/
│   ├── api/                   # API接口封装
│   │   ├── index.ts          # API出口
│   │   ├── auth.ts           # 认证接口
│   │   ├── user.ts           # 用户接口
│   │   ├── document.ts       # 文档接口
│   │   ├── membership.ts     # 会员接口
│   │   └── admin.ts          # 管理接口
│   ├── assets/               # 资源文件
│   │   ├── styles/           # 全局样式
│   │   │   ├── variables.scss # 样式变量
│   │   │   ├── mixins.scss    # 样式混入
│   │   │   └── global.scss    # 全局样式
│   │   └── fonts/            # 字体文件
│   ├── components/           # 公共组件
│   │   ├── common/           # 通用组件
│   │   │   ├── Loading.vue   # 加载组件
│   │   │   ├── Empty.vue     # 空状态组件
│   │   │   ├── Pagination.vue # 分页组件
│   │   │   └── ImagePreview.vue # 图片预览
│   │   ├── layout/           # 布局组件
│   │   │   ├── Header.vue    # 头部组件
│   │   │   ├── Footer.vue    # 底部组件
│   │   │   ├── Sidebar.vue   # 侧边栏组件
│   │   │   └── MobileNav.vue # 移动端导航
│   │   └── form/             # 表单组件
│   │       ├── Input.vue     # 输入框封装
│   │       ├── Select.vue    # 选择器封装
│   │       └── Upload.vue    # 上传组件
│   ├── composables/          # 组合式函数
│   │   ├── useAuth.ts        # 认证状态
│   │   ├── usePermission.ts  # 权限控制
│   │   ├── usePagination.ts  # 分页逻辑
│   │   └── useUpload.ts      # 上传逻辑
│   ├── router/               # 路由配置
│   │   ├── index.ts          # 路由入口
│   │   ├── routes.ts         # 路由定义
│   │   └── guard.ts          # 路由守卫
│   ├── stores/               # 状态管理
│   │   ├── index.ts          # Store入口
│   │   ├── auth.ts           # 认证状态
│   │   ├── user.ts          # 用户信息
│   │   └── app.ts           # 应用配置
│   ├── types/               # TypeScript类型
│   │   ├── api.ts           # API类型
│   │   ├── user.ts# 用户类型
│   │   ├── document.ts      # 文档类型
│   │   └── membership.ts    # 会员类型
│   ├── utils/               # 工具函数
│   │   ├── request.ts       # Axios封装
│   │   ├── auth.ts          # 认证工具
│   │   ├── format.ts        # 格式化工具
│   │   └── validate.ts      # 验证工具
│   ├── views/               # 页面视图
│   │   ├── Home/            # 首页模块
│   │   │   ├── index.vue    # 首页
│   │   │   └── components/  # 首页组件
│   │   ├── Document/        # 文档模块
│   │   │   ├── List.vue     # 文档列表
│   │   │   ├── Detail.vue   # 文档详情
│   │   │   ├── Reader.vue   # PDF阅读器
│   │   │   └── components/  # 文档组件
│   │   ├── User/            # 用户模块
│   │   │   ├── Login.vue    # 登录页
│   │   │   ├── Register.vue # 注册页
│   │   │   ├── Profile.vue  # 个人中心
│   │   │   ├── Membership.vue # 会员中心
│   │   │   └── History.vue  # 阅读历史
│   │   └── Admin/           # 管理后台
│   │       ├── Dashboard.vue # 仪表盘
│   │       ├── Documents/   # 文档管理
│   │       ├── Users.vue    # 用户管理
│   │       ├── RedeemCodes.vue # 兑换码管理
│   │       └── Statistics.vue # 数据统计
│   ├── App.vue              # 根组件
│   └── main.ts              # 应用入口
├── .env                     # 环境变量
├── .env.production          # 生产环境配置
├── .env.development        # 开发环境配置
├── index.html              # HTML模板
├── package.json            # 项目配置
├── tsconfig.json           # TypeScript配置
└── vite.config.ts          # Vite配置
```

### 4.2 核心技术方案

#### 4.2.1 响应式布局设计

前端采用移动优先的响应式设计策略，使用CSS Grid和Flexbox实现灵活布局。断点设置如下：

| 断点名称 | 屏幕宽度 | 典型设备 |
|----------|----------|----------|
| xs | < 576px | 手机竖屏 |
| sm | ≥ 576px | 手机横屏 |
| md | ≥ 768px | 平板竖屏 |
| lg | ≥ 992px | 平板横屏/小笔记本 |
| xl | ≥ 1200px | 桌面显示器 |
| xxl | ≥ 1400px | 大屏显示器 |

布局方案采用Element Plus的el-container组件体系实现整体布局结构。桌面端使用经典的三栏布局：左侧导航栏、中间内容区、右侧可选区域。移动端采用底部TabBar导航，页面以全宽卡片形式展示。

核心布局组件代码结构如下：

```vue
<!-- MainLayout.vue -->
<template>
  <el-container class="main-layout">
    <!-- 桌面端左侧导航 -->
    <el-aside v-if="!isMobile" width="220px">
      <Sidebar />
    </el-aside>
    
    <!-- 移动端遮罩层 -->
    <el-drawer
      v-model="sidebarVisible"
      direction="ltr"
      :show-close="false"
      size="280px"
    >
      <Sidebar />
    </el-drawer>
    
    <el-container>
      <!-- 顶部导航 -->
      <el-header height="60px">
        <Header @toggle-sidebar="toggleSidebar" />
      </el-header>
      
      <!-- 主内容区 -->
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>
```

#### 4.2.2 PDF阅读器集成

PDF阅读功能使用pdf.js库实现，这是Mozilla开发的开源PDF解析和渲染库。阅读器组件需要处理以下功能需求：

PDF文件加载和渲染：组件初始化时请求后端的阅读权限接口，获取带有时效性的OSS访问URL。使用pdf.js的getDocument方法加载PDF文档，支持大文件分页加载以优化内存使用。每一页使用独立的canvas元素渲染，支持清晰度自适应。

阅读进度保存：使用reading_history表记录用户的阅读进度。每次翻页时更新last_page字段，累计阅读时长通过setInterval定时器计算并更新total_time字段。下次打开同一文档时，自动跳转到上次阅读位置。

响应式适配：阅读器组件需要适配不同屏幕尺寸。移动端采用全屏阅读模式，隐藏顶部导航栏。桌面端可以采用侧边栏展示目录，当前页高亮定位。缩放控制支持双指缩放（移动端）和滚轮缩放（桌面端）。

```typescript
// usePdfViewer.ts
import { ref, onMounted, onUnmounted } from 'vue'
import * as pdfjsLib from 'pdfjs-dist'

export function usePdfViewer(pdfUrl: string) {
  const pdfDoc = ref(null)
  const currentPage = ref(1)
  const totalPages = ref(0)
  const scale = ref(1.0)
  const isLoading = ref(true)
  
  // 加载PDF文档
  const loadPdf = async () => {
    try {
      const loadingTask = pdfjsLib.getDocument(pdfUrl)
      pdfDoc.value = await loadingTask.promise
      totalPages.value = pdfDoc.value.numPages
      isLoading.value = false
    } catch (error) {
      console.error('PDF加载失败:', error)
    }
  }
  
  // 渲染当前页
  const renderPage = async (pageNum: number) => {
    if (!pdfDoc.value) return
    
    const page = await pdfDoc.value.getPage(pageNum)
    const viewport = page.getViewport({ scale: scale.value })
    
    // 渲染到canvas
    // ...渲染逻辑
  }
  
  // 页面跳转
  const goToPage = (page: number) => {
    if (page >= 1 && page <= totalPages.value) {
      currentPage.value = page
      renderPage(page)
    }
  }
  
  // 缩放控制
  const zoomIn = () => {
    scale.value = Math.min(scale.value + 0.25, 3.0)
    renderPage(currentPage.value)
  }
  
  const zoomOut = () => {
    scale.value = Math.max(scale.value - 0.25, 0.5)
    renderPage(currentPage.value)
  }
  
  onMounted(() => {
    loadPdf()
  })
  
  return {
    pdfDoc,
    currentPage,
    totalPages,
    scale,
    isLoading,
    goToPage,
    zoomIn,
    zoomOut
  }
}
```

#### 4.2.3 状态管理方案

使用Pinia进行全局状态管理，设计了auth、user、app三个核心Store。auth Store管理认证状态，包括登录状态、令牌信息、用户角色权限。user Store管理用户个人信息，包括基本资料、会员状态、阅读历史。app Store管理应用配置，包括侧边栏展开状态、主题设置、加载状态。

```typescript
// stores/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, logout, refreshToken } from '@/api/auth'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter()
  
  const accessToken = ref(localStorage.getItem('access_token') || '')
  const refreshTokenValue = ref(localStorage.getItem('refresh_token') || '')
  const tokenExpireAt = ref<number>(0)
  
  const isLoggedIn = computed(() => !!accessToken.value)
  
  const loginAction = async (account: string, password: string, remember: boolean) => {
    const res = await login({ account, password, remember })
    accessToken.value = res.data.access_token
    refreshTokenValue.value = res.data.refresh_token
    tokenExpireAt.value = Date.now() + res.data.expires_in * 1000
    
    localStorage.setItem('access_token', accessToken.value)
    localStorage.setItem('refresh_token', refreshTokenValue.value)
    
    return res.data.user_info
  }
  
  const logoutAction = async () => {
    try {
      await logout()
    } finally {
      accessToken.value = ''
      refreshTokenValue.value = ''
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      router.push('/login')
    }
  }
  
  const refreshTokenAction = async () => {
    try {
      const res = await refreshToken({ refresh_token: refreshTokenValue.value })
      accessToken.value = res.data.access_token
      refreshTokenValue.value = res.data.refresh_token
      tokenExpireAt.value = Date.now() + res.data.expires_in * 1000
      
      localStorage.setItem('access_token', accessToken.value)
      localStorage.setItem('refresh_token', refreshTokenValue.value)
    } catch (error) {
      logoutAction()
      throw error
    }
  }
  
  return {
    accessToken,
    refreshTokenValue,
    tokenExpireAt,
    isLoggedIn,
    loginAction,
    logoutAction,
    refreshTokenAction
  }
})
```

#### 4.2.4 请求拦截处理

对Axios进行二次封装，实现请求拦截和响应拦截的统一处理。请求拦截器自动添加Authorization头，处理令牌刷新逻辑。响应拦截器统一处理错误码，401错误自动跳转登录，业务错误码显示提示信息。

```typescript
// utils/request.ts
import axios, { AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000,
  withCredentials: true
})

// 请求拦截器
service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const authStore = useAuthStore()
    
    // 添加token
    if (authStore.accessToken) {
      config.headers.Authorization = `Bearer ${authStore.accessToken}`
    }
    
    // 请求唯一标识（防止重复请求）
    config.headers['X-Request-Id'] = generateRequestId()
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    const { code, message, data } = response.data
    
    if (code === 0) {
      return { code, message, data }
    }
    
    // 业务错误
    ElMessage.error(message || '请求失败')
    return Promise.reject(new Error(message || '请求失败'))
  },
  async (error) => {
    const { response } = error
    
    if (response) {
      switch (response.status) {
        case 401:
          // token过期，尝试刷新
          const authStore = useAuthStore()
          if (authStore.refreshTokenValue) {
            try {
              await authStore.refreshTokenAction()
              // 重新发送原请求
              return service.request(error.config)
            } catch {
              authStore.logoutAction()
            }
          } else {
            router.push('/login')
          }
          break
        case 403:
          ElMessage.error('没有权限访问')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器错误')
          break
        default:
          ElMessage.error(response.data?.message || '请求失败')
      }
    } else {
      ElMessage.error('网络连接失败，请检查网络')
    }
    
    return Promise.reject(error)
  }
)

export default service
```

### 4.3 核心页面设计

#### 4.3.1 首页

首页采用模块化设计，包含多个功能区块。顶部展示Banner轮播图，用于展示重要活动或推荐内容。主内容区分为左右两栏：左侧为主推文档区，采用大卡片形式展示精选内容；右侧为分类导航和热门文档列表。底部展示最新更新文档列表。

页面交互设计注重首屏加载性能，Banner图采用懒加载，文档列表采用虚拟滚动技术处理大数据量展示。搜索框固定在顶部显眼位置，支持全文搜索和分类筛选。

```vue
<!-- Home/index.vue -->
<template>
  <div class="home-page">
    <!-- 搜索区域 -->
    <div class="search-section">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索文档标题、描述..."
        size="large"
        prefix-icon="Search"
        @keyup.enter="handleSearch"
        class="search-input"
      />
      <el-button type="primary" @click="handleSearch">搜索</el-button>
    </div>
    
    <!-- 分类标签 -->
    <div class="category-tags">
      <el-tag
        v-for="category in categories"
        :key="category.id"
        :type="activeCategory === category.id ? 'primary' : 'info'"
        @click="selectCategory(category.id)"
        class="category-tag"
      >
        {{ category.name }}
      </el-tag>
    </div>
    
    <!-- 推荐文档 -->
    <section class="featured-section">
      <h2 class="section-title">精选推荐</h2>
      <div class="document-grid">
        <DocumentCard
          v-for="doc in featuredDocs"
          :key="doc.id"
          :document="doc"
          @click="goToDetail(doc.id)"
        />
      </div>
    </section>
    
    <!-- 最新更新 -->
    <section class="latest-section">
      <h2 class="section-title">最新更新</h2>
      <div class="document-list">
        <DocumentRow
          v-for="doc in latestDocs"
          :key="doc.id"
          :document="doc"
          @click="goToDetail(doc.id)"
        />
      </div>
      
      <!-- 分页 -->
      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          layout="prev, pager, next"
          @current-change="fetchLatestDocs"
        />
      </div>
    </section>
  </div>
</template>
```

#### 4.3.2 文档详情页

文档详情页展示PDF文档的完整信息，包含文档标题、描述、封面、标签等元数据。页面布局采用卡片式设计，将阅读按钮和下载按钮放在显眼位置。非会员用户点击下载时，弹出会员引导弹窗。

页面加载时自动调用阅读接口，记录用户开始阅读的行为。详情页底部展示相关文档推荐，推荐算法基于同分类和同标签的文档热度排序。

```vue
<!-- Document/Detail.vue -->
<template>
  <div class="document-detail" v-if="document">
    <!-- 文档信息卡片 -->
    <el-card class="info-card">
      <div class="doc-header">
        <el-image :src="document.cover_image" fit="cover" class="cover-image" />
        
        <div class="doc-info">
          <h1 class="doc-title">{{ document.title }}</h1>
          
          <div class="doc-meta">
            <span class="meta-item">
              <el-icon><Document /></el-icon>
              {{ document.page_count }}页
            </span>
            <span class="meta-item">
              <el-icon><Folder /></el-icon>
              {{ document.category.name }}
            </span>
            <span class="meta-item">
              <el-icon><View /></el-icon>
              {{ document.view_count }}次阅读
            </span>
            <span class="meta-item">
              <el-icon><Download /></el-icon>
              {{ document.download_count }}次下载
            </span>
          </div>
          
          <div class="doc-tags">
            <el-tag
              v-for="tag in document.tags"
              :key="tag.id"
              :color="tag.color"
              effect="dark"
              class="doc-tag"
            >
              {{ tag.name }}
            </el-tag>
          </div>
          
          <div class="doc-description">
            <h3>文档简介</h3>
            <p>{{ document.description }}</p>
          </div>
          
          <div class="action-buttons">
            <el-button type="primary" size="large" @click="handleRead">
              <el-icon><Reading /></el-icon>
              在线阅读
            </el-button>
            
            <el-button size="large" @click="handleDownload" :disabled="!canDownload">
              <el-icon><Download /></el-icon>
              下载文档
            </el-button>
            
            <el-button v-if="!isMember" type="warning" size="large" @click="goToMembership">
              开通会员，解锁无限下载
            </el-button>
          </div>
        </div>
      </div>
    </el-card>
    
    <!-- 相关推荐 -->
    <section class="related-section">
      <h2>相关文档</h2>
      <div class="related-grid">
        <DocumentCard
          v-for="doc in relatedDocs"
          :key="doc.id"
          :document="doc"
        />
      </div>
    </section>
  </div>
</template>
```

#### 4.3.3 会员中心

会员中心页面整合用户的所有会员相关信息。页面分为几个功能区块：会员状态总览显示当前会员类型、有效期、剩余下载额度；会员权益对比展示不同会员类型的权益说明；会员操作区提供兑换码输入框、续费按钮（如后续实现支付）；会员记录展示兑换历史和下载历史。

终身会员的兑换码输入框需要特殊处理：一旦用户成为终身会员，兑换码输入框应该禁用并显示"您已是终身会员，无需兑换"的提示信息。

```vue
<!-- User/Membership.vue -->
<template>
  <div class="membership-page">
    <!-- 当前会员状态 -->
    <el-card class="status-card">
      <template #header>
        <div class="card-header">
          <span>会员状态</span>
        </div>
      </template>
      
      <div class="membership-info">
        <div class="member-badge" :class="membership.type">
          <el-icon v-if="membership.type === 'lifetime'"><皇冠 /></el-icon>
          <el-icon v-else><Medal /></el-icon>
          <span>{{ membershipTypeText }}</span>
        </div>
        
        <div class="member-details">
          <div class="detail-item">
            <span class="label">有效期至</span>
            <span class="value">{{ membership.expires_at || '永久有效' }}</span>
          </div>
          
          <div class="detail-item" v-if="membership.type !== 'lifetime'">
            <span class="label">剩余天数</span>
            <span class="value">{{ membership.days_remaining }}天</span>
          </div>
          
          <div class="detail-item">
            <span class="label">下载额度</span>
            <span class="value">
              {{ membership.type === 'lifetime' 
                ? '无限' 
                : `${membership.download_remaining}/${membership.download_quota}` 
              }}
            </span>
          </div>
        </div>
      </div>
    </el-card>
    
    <!-- 会员权益 -->
    <el-card class="benefits-card">
      <template #header>
        <div class="card-header">
          <span>会员权益</span>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="8" v-for="benefit in currentBenefits" :key="benefit.title">
          <div class="benefit-item">
            <el-icon :size="40" :color="benefit.color">
              <component :is="benefit.icon" />
            </el-icon>
            <h4>{{ benefit.title }}</h4>
            <p>{{ benefit.description }}</p>
          </div>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- 兑换码兑换 -->
    <el-card class="redeem-card" v-if="membership.type !== 'lifetime'">
      <template #header>
        <div class="card-header">
          <span>兑换码兑换</span>
        </div>
      </template>
      
      <div class="redeem-form">
        <el-input
          v-model="redeemCode"
          placeholder="请输入兑换码"
          :disabled="isRedeeming"
        >
          <template #append>
            <el-button @click="handleRedeem" :loading="isRedeeming">
              兑换
            </el-button>
          </template>
        </el-input>
        
        <p class="redeem-tip">
          <el-icon><InfoFilled /></el-icon>
          输入兑换码即可开通或续期会员
        </p>
      </div>
    </el-card>
    
    <!-- 终身会员专属 -->
    <el-card v-else class="lifetime-card">
      <el-result
        icon="success"
        title="您已是终身会员"
        sub-title="享受所有文档的无限阅读和下载权益"
      >
        <template #extra>
          <el-button type="primary" @click="goToDocuments">
            浏览全部文档
          </el-button>
        </template>
      </el-result>
    </el-card>
  </div>
</template>
```

### 4.4 组件库使用规范

本项目使用Element Plus作为基础UI组件库，在其上进行二次封装以保持代码一致性和可维护性。

表单组件统一封装：所有表单使用el-form组件进行包裹，配置统一的label-width和验证规则。表单验证规则抽取到单独的validation.ts文件中，实现规则复用。表单提交使用useForm Hook封装loading状态和提交逻辑。

列表组件统一封装：使用el-table和el-pagination组合实现列表展示。列表查询参数使用useQuery Hook管理，自动同步URL查询参数。列表加载状态使用useLoad Hook封装，支持下拉刷新和上拉加载更多。

弹窗组件统一封装：所有弹窗使用el-dialog组件，封装通用的open/close事件和loading状态。弹窗内容组件通过props传递数据和事件回调，实现父子组件解耦。

---

## 后端架构设计

### 5.1 项目结构

后端项目采用FastAPI框架构建，使用SQLAlchemy作为ORM，遵循清晰的分层架构设计。

```
backend/
├── app/
│   ├── api/                   # API路由层
│   │   ├── v1/               # API版本
│   │   │   ├── auth.py       # 认证接口
│   │   │   ├── users.py      # 用户接口
│   │   │   ├── documents.py  # 文档接口
│   │   │   ├── membership.py  # 会员接口
│   │   │   └── admin.py       # 管理接口
│   │   ├── deps.py           # 依赖注入
│   │   └── router.py         # 路由注册
│   ├── core/                 # 核心配置
│   │   ├── config.py        # 配置管理
│   │   ├── security.py     # 安全相关
│   │   └── logging.py       # 日志配置
│   ├── models/              # 数据模型
│   │   ├── user.py         # 用户模型
│   │   ├── document.py     # 文档模型
│   │   ├── membership.py   # 会员模型
│   │   └── associations.py # 关联模型
│   ├── schemas/             # Pydantic模型
│   │   ├── user.py         # 用户Schema
│   │   ├── document.py     # 文档Schema
│   │   ├── token.py        # Token Schema
│   │   └── msg.py          # 消息Schema
│   ├── services/           # 业务逻辑层
│   │   ├── auth_service.py
│   │   ├── document_service.py
│   │   ├── membership_service.py
│   │   └── oss_service.py
│   ├── utils/              # 工具函数
│   │   ├── token.py       # Token工具
│   │   ├── password.py     # 密码工具
│   │   └── pagination.py  # 分页工具
│   ├── middleware/         # 中间件
│   │   ├── cors.py        # 跨域中间件
│   │   └── jwt.py         # JWT中间件
│   └── main.py            # 应用入口
├── alembic/               # 数据库迁移
│   ├── versions/         # 迁移版本
│   └── env.py
├── tests/                # 测试用例
│   ├── api/              # API测试
│   └── conftest.py       # 测试配置
├── logs/                 # 日志文件
├── .env                  # 环境变量
├── requirements.txt      # Python依赖
└── alembic.ini          # Alembic配置
```

### 5.2 核心依赖

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
pymysql==1.1.0
cryptography==42.0.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
httpx==0.26.0
aliyunoss3==2.0.2
python-dotenv==1.0.0
pydantic==2.5.3
pydantic-settings==2.1.0
```

### 5.3 配置管理

使用Pydantic Settings进行配置管理，支持环境变量和.env文件配置。

```python
# app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "PDF Platform"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    SECRET_KEY: str
    
    # 数据库配置
    DATABASE_HOST: str
    DATABASE_PORT: int = 3306
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    
    # JWT配置
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 1天
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # 阿里云OSS配置
    OSS_ENDPOINT: str
    OSS_ACCESS_KEY_ID: str
    OSS_ACCESS_KEY_SECRET: str
    OSS_BUCKET_NAME: str
    OSS_BUCKET_DOMAIN: str
    
    # 文件上传配置
    MAX_FILE_SIZE: int = 52428800  # 50MB
    ALLOWED_EXTENSIONS: list = ["pdf"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
```

### 5.4 数据库模型

使用SQLAlchemy 2.0风格的模型定义，支持异步操作。

```python
# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base import Base


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    avatar = Column(String(500), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    
    # 关系
    membership = relationship("Membership", back_populates="user", uselist=False)
    downloads = relationship("Download", back_populates="user")
    redemptions = relationship("Redemption", back_populates="user")
    reading_history = relationship("ReadingHistory", back_populates="user")
```

### 5.5 API路由实现

FastAPI路由实现采用依赖注入方式管理认证和权限。

```python
# app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.api.deps import get_current_user


router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """用户注册"""
    auth_service = AuthService(db)
    return await auth_service.register(request)


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    auth_service = AuthService(db)
    return await auth_service.login(request.account, request.password, request.remember)


@router.post("/logout")
async def logout(
    current_user = Depends(get_current_user)
):
    """用户登出"""
    # TODO: 将token加入黑名单
    return {"message": "登出成功"}


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user = Depends(get_current_user)
):
    """获取当前用户信息"""
    return current_user
```

### 5.6 业务逻辑服务

核心业务逻辑封装在Service层，保持API路由简洁。

```python
# app/services/membership_service.py
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.membership import Membership, MembershipType
from app.schemas.membership import MembershipResponse
from app.core.exceptions import BusinessError


class MembershipService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_membership(self, user_id: int) -> Optional[Membership]:
        """获取用户会员信息"""
        result = await self.db.execute(
            select(Membership).where(Membership.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def check_download_permission(
        self, 
        user_id: int, 
        document_id: int
    ) -> tuple[bool, str]:
        """
        检查下载权限
        返回: (是否允许, 提示信息)
        """
        membership = await self.get_membership(user_id)
        
        if not membership:
            # 免费用户
            return True, "ok"
        
        if membership.type == MembershipType.LIFETIME:
            return True, "ok"
        
        if membership.type == MembershipType.NORMAL:
            # 检查有效期
            if membership.expires_at and membership.expires_at < datetime.utcnow():
                return False, "会员已过期，请续费"
            
            # 检查下载额度
            if membership.download_used >= membership.download_quota:
                return False, "下载额度已用完，请升级或等待额度重置"
            
            return True, "ok"
        
        return True, "ok"
    
    async def record_download(
        self, 
        user_id: int, 
        document_id: int
    ) -> None:
        """
        记录下载行为，更新额度
        """
        membership = await self.get_membership(user_id)
        
        if membership and membership.type == MembershipType.NORMAL:
            membership.download_used += 1
            self.db.add(membership)
            await self.db.commit()
    
    async def apply_redeem_code(
        self,
        user_id: int,
        code: str
    ) -> MembershipResponse:
        """
        应用兑换码
        """
        membership = await self.get_membership(user_id)
        
        # 验证兑换码
        redeem_code = await self.validate_redeem_code(code)
        
        # 检查是否已经是终身会员
        if membership and membership.type == MembershipType.LIFETIME:
            raise BusinessError("您已是终身会员，无需兑换")
        
        # 计算新的会员有效期和额度
        if redeem_code.type == MembershipType.LIFETIME:
            # 终身会员
            new_type = MembershipType.LIFETIME
            new_expires_at = None
            new_quota = -1  # 无限
        else:
            # 普通会员
            new_type = MembershipType.NORMAL
            
            if membership:
                # 叠加
                current_expires = membership.expires_at or datetime.utcnow()
                new_expires_at = current_expires + timedelta(days=365)
                new_quota = membership.download_quota + 100
            else:
                # 新开通
                new_expires_at = datetime.utcnow() + timedelta(days=365)
                new_quota = 100
        
        # 保存记录
        # ...保存逻辑
        
        return MembershipResponse(
            type=new_type,
            expires_at=new_expires_at,
            download_quota=new_quota
        )
```

### 5.7 阿里云OSS集成

封装OSS操作，支持文件上传、下载和URL签名。

```python
# app/services/oss_service.py
import oss2
from typing import Optional
from datetime import datetime, timedelta
from app.core.config import settings


class OSSService:
    def __init__(self):
        self.bucket = oss2.Bucket(
            oss2.Auth(settings.OSS_ACCESS_KEY_ID, settings.OSS_ACCESS_KEY_SECRET),
            settings.OSS_ENDPOINT,
            settings.OSS_BUCKET_NAME
        )
        self.bucket_domain = settings.OSS_BUCKET_DOMAIN
    
    def generate_signed_url(
        self,
        object_name: str,
        expires: int = 3600,
        filename: Optional[str] = None
    ) -> str:
        """
        生成带签名的访问URL
        """
        # 设置响应头，支持下载
        params = {}
        if filename:
            params['response-content-disposition'] = f'attachment; filename="{filename}"'
        
        url = self.bucket.sign_url(
            'GET',
            object_name,
            expires,
            params=params
        )
        
        return f"https://{self.bucket_domain}/{object_name}?{url.split('?')[1]}"
    
    async def upload_file(
        self,
        file_content: bytes,
        object_name: str,
        content_type: str = "application/pdf"
    ) -> str:
        """
        上传文件到OSS
        """
        self.bucket.put_object(
            object_name,
            file_content,
            headers={'Content-Type': content_type}
        )
        
        return f"https://{self.bucket_domain}/{object_name}"
    
    async def delete_file(self, object_name: str) -> None:
        """
        删除OSS文件
        """
        self.bucket.delete_object(object_name)
    
    async def list_files(self, prefix: str) -> list:
        """
        列出前缀下的文件
        """
        files = []
        for obj in oss2.ObjectIterator(self.bucket, prefix=prefix):
            files.append({
                'name': obj.key,
                'size': obj.size,
                'mtime': obj.last_modified
            })
        return files
```

---

## 部署方案

### 6.1 服务器配置建议

**最低配置（个人/小规模使用）：**
- CPU: 2核
- 内存: 2GB
- 带宽: 5Mbps
- 硬盘: 50GB SSD
- 月费用: 约¥200-300

**推荐配置（中等规模运营）：**
- CPU: 4核
- 内存: 4GB
- 带宽: 10Mbps
- 硬盘: 100GB SSD
- 月费用: 约¥400-600

**高配置（大规模运营）：**
- CPU: 8核
- 内存: 8GB
- 带宽: 20Mbps
- 硬盘: 200GB SSD
- 月费用: 约¥800-1200

### 6.2 部署架构

```
                    ┌─────────────────────────────────────────────────┐
                    │                    用户访问                      │
                    └─────────────────────┬───────────────────────────┘
                                          │
                                          ▼
                    ┌─────────────────────────────────────────────────┐
                    │                CDN（静态资源加速）                 │
                    └─────────────────────┬───────────────────────────┘
                                          │
                    ┌─────────────────────▼───────────────────────────┐
                    │              负载均衡 Nginx                      │
                    │           （SSL终结、静态资源服务）                 │
                    └─────────────────────┬───────────────────────────┘
                                          │
                    ┌─────────────────────▼───────────────────────────┐
                    │              应用服务器 (多实例)                   │
                    │     ┌─────────────────────────────────┐         │
                    │     │  前端静态文件                      │         │
                    │     │  后端API服务 (Uvicorn/Gunicorn)   │         │
                    │     └─────────────────────────────────┘         │
                    └─────────────────────┬───────────────────────────┘
                                          │
                    ┌─────────────────────▼───────────────────────────┐
                    │               数据库 MySQL                       │
                    └─────────────────────┬───────────────────────────┘
                                          │
                    ┌─────────────────────▼───────────────────────────┐
                    │               缓存 Redis                        │
                    │           （Session、Token黑名单）                │
                    └─────────────────────┬───────────────────────────┘
                                          │
                    ┌─────────────────────▼───────────────────────────┐
│             阿里云 OSS                          │
                    │           （PDF文件存储）                         │
                    └─────────────────────────────────────────────────┘
```

### 6.3 Docker部署配置

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_HOST=mysql
      - REDIS_HOST=redis
    depends_on:
      - mysql
      - redis
    volumes:
      - ./backend/logs:/app/logs

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  mysql:
    image: mysql:8.0
    ports:
      - "3306:3306"
    environment:
      - MYSQL_ROOT_PASSWORD=root_password
      - MYSQL_DATABASE=pdf_platform
    volumes:
      - mysql_data:/var/lib/mysql

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  mysql_data:
  redis_data:
```

### 6.4 Nginx配置

```nginx
# nginx.conf
server {
    listen 80;
    server_name your-domain.com;
    
    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL配置
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    
    # 前端静态文件
    root /var/www/frontend/dist;
    index index.html;
    
    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json application/xml;
    
    # API代理
    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # OSS签名URL代理（可选，用于隐藏OSS域名）
    location /oss/ {
        proxy_pass https://your-bucket.oss-cn-hangzhou.aliyuncs.com/;
        proxy_set_header Host your-bucket.oss-cn-hangzhou.aliyuncs.com;
        proxy_set_header Authorization $http_authorization;
        proxy_pass_header Server;
    }
    
    # SPA路由支持
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 6.5 环境变量配置

```bash
# .env.production
# 应用配置
SECRET_KEY=your-production-secret-key
DEBUG=False

# 数据库配置
DATABASE_HOST=mysql
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=your-db-password
DATABASE_NAME=pdf_platform

# JWT配置
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=30

# 阿里云OSS配置
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
OSS_ACCESS_KEY_ID=your-access-key-id
OSS_ACCESS_KEY_SECRET=your-access-key-secret
OSS_BUCKET_NAME=your-bucket-name
OSS_BUCKET_DOMAIN=your-bucket.oss-cn-hangzhou.aliyuncs.com

# 文件上传配置
MAX_FILE_SIZE=52428800
```

### 6.6 监控和维护

#### 6.6.1 日志配置

```python
# app/core/logging.py
import logging
import sys
from pathlib import Path
from datetime import datetime
from app.core.config import settings

LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# 文件日志
file_handler = logging.FileHandler(
    LOG_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log",
    encoding="utf-8"
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# 控制台日志
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# 配置根日志器
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)

logger = logging.getLogger(__name__)
```

#### 6.6.2 备份策略

```bash
#!/bin/bash
# backup.sh - 数据库备份脚本

# 配置
BACKUP_DIR="/backup/mysql"
DATE=$(date +%%Y%m%d_%H%M%S)
DB_HOST="mysql"
DB_NAME="pdf_platform"
DB_USER="root"
DB_PASSWORD="your-password"
RETENTION_DAYS=7

# 创建备份目录
mkdir -p ${BACKUP_DIR}

# 执行备份
mysqldump -h${DB_HOST} -u${DB_USER} -p${DB_PASSWORD} \
    ${DB_NAME} | gzip > ${BACKUP_DIR}/${DB_NAME}_${DATE}.sql.gz

# 删除旧备份
find ${BACKUP_DIR} -name "*.sql.gz" -mtime +${RETENTION_DAYS} -delete

echo "Backup completed: ${DB_NAME}_${DATE}.sql.gz"
```

#### 6.6.3 系统监控

建议使用以下工具进行系统监控：
- Prometheus + Grafana：指标收集和可视化
- ELK Stack：日志收集和分析
- Uptime Robot：在线监控和告警
- New Relic/APM：应用性能监控

---

## 附录

### 附录A：数据库ER图

```
┌─────────────┐       ┌─────────────────┐       ┌─────────────┐
│   users      │       │  memberships    │       │ redeem_codes│
├─────────────┤       ├─────────────────┤       ├─────────────┤
│ id (PK)     │◄──────│ user_id (FK)    │       │ id (PK)     │
│ username    │1:1    │ type            │       │ code         │
│ email       │       │ expires_at      │       │ type         │
│ password    │       │ download_quota  │       │ uses_total   │
│ role        │       │ download_used   │       │ expires_at   │
│ status      │       └─────────────────┘       │ is_active    │
│ created_at  │                                 └─────────────┘
└─────────────┘                                         │
         │                              ┌───────────────┘
         │                              │
         │1:N                           │1:N
         ▼                              ▼
┌─────────────────┐           ┌─────────────────┐
│ downloads       │           │ redemptions     │
├─────────────────┤           ├─────────────────┤
│ id (PK)         │           │ id (PK)         │
│ user_id (FK)    │           │ user_id (FK)    │
│ document_id (FK)│           │ redeem_code_id  │
│ created_at      │           │ old_expires_at  │
└─────────────────┘           │ new_expires_at  │
         │                    └─────────────────┘
         │1:N                         │
         ▼                           │1:N
┌─────────────────┐                 │
│ documents       │                 ▼
├─────────────────┤         ┌───────────────┐
│ id (PK)         │         │   users       │
│ title           │         └───────────────┘
│ description     │
│ category_id (FK)│         ┌─────────────────┐
│ file_path       │         │ document_tags   │
│ file_size       │◄────────│ document_id (FK)│
│ view_count      │  N:M    │ tag_id (FK)     │
│ download_count  │         └─────────────────┘
│ status          │                  │
│ created_by (FK) │                  │N:1
└─────────────────┘                  ▼
         │                   ┌─────────────┐
         │1:N                 │    tags     │
         ▼                   ├─────────────┤
┌─────────────────┐           │ id (PK)     │
│ categories      │           │ name        │
├─────────────────┤           │ slug        │
│ id (PK)         │           │ color       │
│ name            │           └─────────────┘
│ slug            │
│ parent_id (FK)  │           ┌─────────────────┐
└─────────────────┘           │ reading_history │
                               ├─────────────────┤
                               │ id (PK)         │
                               │ user_id (FK)    │
                               │ document_id (FK)│
                               │ last_page       │
                               │ total_time      │
                               └─────────────────┘
```

### 附录B：API错误码定义

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 1001 | 用户名或密码错误 |
| 1002 | 用户名已存在 |
| 1003 | 邮箱已注册 |
| 1004 | 账号被锁定 |
| 1005 | 验证码错误 |
| 1006 | token无效 |
| 1007 | token过期 |
| 1008 | 无权限访问 |
| 2001 | 文档不存在 |
| 2002 | 文档已下架 |
| 2003 | 下载额度不足 |
| 2004 | 会员已过期 |
| 3001 | 兑换码无效 |
| 3002 | 兑换码已过期 |
| 3003 | 兑换码已使用完毕 |
| 4001 | 文件上传失败 |
| 4002 | 文件格式不支持 |
| 4003 | 文件过大 |
| 5001 | 系统错误 |
| 5002 | 数据库错误 |

### 附录C：第三方库许可证说明

本项目使用的开源库均遵循开源许可证，在商业使用时请注意各库的许可证限制：

- Vue 3: MIT License
- FastAPI: MIT License
- SQLAlchemy: MIT License
- Element Plus: MIT License
- pdf.js: Apache License 2.0
- axios: MIT License
- Pinia: MIT License

### 附录D：开发规范

**代码风格规范：**
- Python遵循PEP 8规范，使用Black格式化
- TypeScript遵循ESLint配置
- Git提交信息遵循Conventional Commits规范

**Git分支策略：**
- main: 生产环境代码
- develop: 开发环境代码
- feature/*: 新功能分支
- hotfix/*: 紧急修复分支
- release/*: 发布准备分支

**测试要求：**
- API接口必须有单元测试
- 核心业务逻辑覆盖率 > 80%
- 前端组件需要有基础的渲染测试

---

## 文档信息

- **版本**: 1.0
- **创建日期**: 2026-02-05
- **最后更新**: 2026-02-05
- **作者**: Matrix Agent
