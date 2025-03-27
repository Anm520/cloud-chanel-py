
 1. 打包docker镜像命令
 docker build -t cloud-chanel-py .
 2.运行容器命令
 docker run -d -p 3001:80 --name cloud-chanel-serve cloud-chanel-py 
 3.保存镜像命令
 docker save -o cloud-chanel-py.tar cloud-chanel-py
 使用说明
搜索接口
 http://localhost:3001/search?q=滤镜

查询列表 before是消息的id，不填写查最新的消息 写了查询这个id之前的消息
http://localhost:3001/messages?before=2165


服务器源码直接运行
gunicorn -w 2 -k eventlet -b 0.0.0.0:3001 --access-logfile - --error-logfile - main:app
