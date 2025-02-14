# AI-Human-ClusterAgent

## 项目介绍
AI-Human-ClusterAgent 是一个分布式任务处理代理程序，主要用于处理AI人类交互相关的音视频任务。该代理程序可以与主节点保持心跳连接，自动获取并处理任务，并将处理结果回传给主节点。

## 主要特性
- 自动心跳检测：定期向主节点发送心跳信息，保持节点状态同步
- 任务自动获取：定期从主节点获取待处理的任务
- 文件处理：支持音频文件的下载和处理
- 结果上报：自动将处理结果和生成的文件上传至主节点
- 可配置性：支持通过YAML配置文件灵活配置节点参数
- 自动清理：任务完成后自动清理临时文件

## 环境要求
- Python 3.7+
- 依赖包：
  - requests==2.31.0
  - aiohttp==3.9.1
  - apscheduler==3.10.4
  - python-dotenv==1.0.0
  - loguru==0.7.2
  - PyYAML==6.0.1

## 安装部署

1. 克隆项目代码
```bash
git clone https://github.com/qiukai86263007/AI-Human-ClusterAgent
cd AI-Human-ClusterAgent
```

2. 填写配置文件
在 `conf/config.yaml` 中配置节点信息：
```yaml
node:
  id: [节点ID]
  master_url: [主节点URL]
  master_heartbeat_url: /aihuman/cluster/heartbeat/
  master_task_url: /aihuman/task/anonymous/

scheduler:
  heartbeat_interval: 5
  task_fetch_interval: 5

musetalk:
  base_dir: [MuseTalk安装目录]
  env_bin: [Python环境路径]
```

3. 一键安装服务，启动服务
```bash
# 修改 conf/cluster-agent.service 中的路径配置
sudo ./install_service.sh
```

### 手动启动
```bash
python agent/agent.py
```

## 日志查看
- 日志文件位置：`logs/cluster_agent.log`
- 查看系统服务日志：`journalctl -u cluster-agent`

## 配置说明

### 节点配置
- `node.id`: 节点唯一标识
- `node.master_url`: 主节点服务地址
- `node.master_heartbeat_url`: 心跳接口路径
- `node.master_task_url`: 任务接口路径

### 调度配置
- `scheduler.heartbeat_interval`: 心跳间隔（秒）
- `scheduler.task_fetch_interval`: 任务获取间隔（秒）

### MuseTalk配置
- `musetalk.base_dir`: MuseTalk安装目录
- `musetalk.env_bin`: Python环境路径
