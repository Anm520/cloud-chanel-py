# Telegram频道服务接口，AI生成的，仅供参考

## 服务概述
提供Telegram指定频道的消息抓取和搜索功能，支持容器化部署和传统部署两种方式
## 部署指南

### 环境要求
- Python 3.9+
- Docker 20.10+ (容器部署时)
- 服务器内存 ≥ 512MB

## 文件结构
```
.
├── main.py              # 主程序
├── requirements.txt     # Python依赖
├── Dockerfile           # 容器构建配置
├── .env                 # 环境变量配置
└── README.md            # 本文档
```

### 传统部署

# 1. 安装依赖
```bash
pip install -r requirements.txt
```
# 2. 配置文件说明
`.env` 文件配置项：
```ini
# 服务配置
FLASK_ENV=production
# 频道名称配置 默认为tianyirigeng 云盘资源日更频道
CHANNEL_NAME=tianyirigeng
# 运行端口配置。本地尽量不要用80端口，否则可能会被其他程序占用
PORT=3001
```
# 3. 启动服务 
【-w 2】为两个进程，自己用改为1即可，不用浪费进程，改4为4进程;  

【0.0.0.0:$PORT】 $PORT为上边环境变量设置的端口
```bash
gunicorn -w 2 -k gevent -b 0.0.0.0:3001 --access-logfile - --error-logfile - "main:app"
```
# 4. 容器部署

## 接口文档

### 1. 消息分页接口
`GET /messages`

**参数说明**：
| 参数名     | 类型   | 必填 | 默认值 | 说明                 |
|-----------|------- |------|--------|----------------------|
| before    | string | 否   | 空     | 分页标识符（消息ID） |

**示例请求**： 
```bash
# 测试消息接口
curl "http://localhost:3001/messages?before="
```

### 2. 消息搜索接口
`GET /search`

**参数说明**：
| 参数名 | 类型   | 必填 | 说明       |
|--------|--------|------|------------|
| q      | string | 是   | 搜索关键词 |

**示例请求**：
```bash
curl "http://localhost:3001/search?q=滤镜"
```



## 管理命令 (3001映射了80端口)
```bash
# 测试消息接口
curl "http://localhost:3001/messages?before="

# 测试搜索接口
curl "http://localhost:3001/search?q=滤镜"
```

## 技术支持
遇到问题请检查：
1. 容器日志：
2. 网络连通性：`telnet t.me 443`
3. 频道名称是否正确