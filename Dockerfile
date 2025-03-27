# 基础镜像
FROM python:3.9-alpine

# 设置工作目录
WORKDIR /app

# # 安装系统依赖
# RUN apt-get update && apt-get install -y \
#     gcc \
#     && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 复制项目文件
COPY . .

# 环境变量
ENV FLASK_ENV=production
ENV CHANNEL_NAME=tianyirigeng
ENV PORT=3001

# 暴露端口
EXPOSE 3001

# 启动命令
CMD ["gunicorn", "-w", "1", "-k", "eventlet", "-b", "0.0.0.0:3001", "--access-logfile", "-", "--error-logfile", "-", "main:app"]