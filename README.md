# Trae to OpenAI API

为 Trae IDE 内置的大模型提供 OpenAI 兼容的 API

## 项目简介

本项目通过一个代理服务将 Trae IDE 内置的大模型暴露为 OpenAI 兼容的 API 接口，以在其他应用中使用

## 使用前提

1. 下载并安装 [Trae](https://www.trae.ai/download)，本项目目前仅支持 Trae 海外版
2. 浏览器需要安装 [油猴 Tampermonkey](https://www.tampermonkey.net) 扩展，用于安装脚本来获取并保存 Trae 登录凭证

## 快速开始

### 获取登录凭证

1. 安装油猴脚本 [auth.js](https://greasyfork.org/zh-CN/scripts/531978-%E8%8E%B7%E5%8F%96%E5%B9%B6%E4%BF%9D%E5%AD%98-trae-%E7%99%BB%E5%BD%95%E5%87%AD%E8%AF%81)
2. 打开 Trae IDE 进行登录，若已登录则先退出登录
3. 在自动打开的网页中，点击 `Login in and open Trae` 完成登录
4. 回到刚才的网页，点击 `Save token to clipboard` 获取并保存登录凭证到剪贴板

### 运行代理服务

```shell
# 克隆本项目仓库
git clone https://github.com/A-23187/trae-api.git
cd trae-api

# 编辑环境变量，填入前面通过脚本获取的凭证信息
cp .env.example .env
vim .env

# 运行服务，默认运行在 8000 端口
uv run server.py
```

### 设置 chat 客户端

> 以 [Cherry Studio](https://cherry-ai.com) 为例

1. 设置 > 模型服务 > 添加提供商 > 提供商类型选择 OpenAI
2. API 密钥填入 `TRAE_IDE_TOKEN`
3. API 地址填入 `http://localhost:8000`
4. 添加模型 > 模型 ID 填入 `gpt-4o`，支持的模型可以通过 `GET /v1/models` 获取

## API 说明

- `POST /v1/chat/completions` 创建聊天补全
- `GET /v1/models` 列出可用模型

## 其他

### 直接使用 uvicorn 运行

```shell
uv sync
source .venv/bin/activate

uvicorn --host 0.0.0.0 --port 8000 --reload --log-level debug src.app:app
```

### 使用 docker 部署

```shell
docker run --rm -p 8000:8000 -v /path/to/.env:/trae-api/.env ghcr.io/a-23187/trae-api:latest
```

## 免责声明

- 本项目仅供学习研究使用，请遵循 Trae 的使用条款

## 许可证

[MIT License](https://github.com/A-23187/trae-api/blob/main/LICENSE)
