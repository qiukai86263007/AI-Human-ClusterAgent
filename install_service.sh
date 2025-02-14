#!/bin/bash

# 检查是否以root权限运行
if [ "$(id -u)" != "0" ]; then
   echo "此脚本需要root权限运行" 
   exit 1
fi

# 设置安装目录
INSTALL_DIR="/opt/cluster-agent"
SERVICE_NAME="cluster-agent"

# 创建安装目录
echo "创建安装目录..."
mkdir -p "$INSTALL_DIR"

# 复制项目文件
echo "复制项目文件..."
cp -r agent "$INSTALL_DIR/"
cp -r utils "$INSTALL_DIR/"
cp -r conf "$INSTALL_DIR/"
cp -r requirements.txt "$INSTALL_DIR/"

# 从config.yaml中读取Python解释器路径
echo "读取配置文件..."
PYTHON_PATH=$(grep -A1 'env_bin:' "$INSTALL_DIR/conf/config.yaml" | tail -n1 | awk '{print $2}')
echo "Python解析器路径:$PYTHON_PATH"
if [ -z "$PYTHON_PATH" ]; then
    echo "未找到Python解释器配置,请在config.yaml配置"
    exit 1
fi

# 安装Python依赖
echo "安装Python依赖..."
if [ -x "$PYTHON_PATH" ]; then
    echo "执行命令: $PYTHON_PATH -m pip install -r \"$INSTALL_DIR/requirements.txt\""
    "$PYTHON_PATH" -m pip install -r "$INSTALL_DIR/requirements.txt"
else
    echo "错误：Python解释器路径 '$PYTHON_PATH' 不存在或不可执行"
    exit 1
fi

# 替换service文件中的Python路径
echo "配置系统服务..."
sed -i "s|\${PYTHON_PATH}|$PYTHON_PATH|g" "$INSTALL_DIR/conf/cluster-agent.service"

# 复制服务文件
echo "安装系统服务..."
cp "$INSTALL_DIR/conf/cluster-agent.service" /etc/systemd/system/

# 重新加载systemd配置
systemctl daemon-reload

# 启用并启动服务
echo "启用并启动服务..."
systemctl enable $SERVICE_NAME
systemctl start $SERVICE_NAME

echo "服务安装完成！"
echo "使用以下命令管理服务："
echo "启动服务: systemctl start $SERVICE_NAME"
echo "停止服务: systemctl stop $SERVICE_NAME"
echo "重启服务: systemctl restart $SERVICE_NAME"
echo "查看状态: systemctl status $SERVICE_NAME"