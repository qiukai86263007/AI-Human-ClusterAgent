import asyncio
from datetime import datetime
import aiohttp
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from constants import Constants
import yaml
from pathlib import Path


class ClusterAgent:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'conf' / 'config.yaml'

        # 加载配置文件
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # 验证配置
        if not self.config or 'node' not in self.config or 'scheduler' not in self.config:
            raise ValueError('配置文件格式错误：缺少必要的配置项')

        # 设置节点配置
        node_config = self.config['node']
        self.node_id = node_config.get('id', 'default-node')
        self.master_url = node_config.get('master_url', 'http://localhost:1030')
        self.master_heartbeat_url = self.master_url + node_config.get('master_heartbeat_url',
                                                                      '/dev-api/aihuman/cluster/heartbeat/')
        self.master_task_url = self.master_url + node_config.get('master_task_url', '/dev-api/aihuman/task/anonymous/')

        # 设置调度配置
        scheduler_config = self.config['scheduler']
        self.heartbeat_interval = int(scheduler_config.get('heartbeat_interval', 30))
        self.task_fetch_interval = int(scheduler_config.get('task_fetch_interval', 30))

        # # 设置日志配置
        # if 'logger' in config:
        #     logger_config = config['logger']
        #     log_path = Path(
        #         logger_config.get('file_path', Path(__file__).parent.parent / 'logs' / 'cluster_agent.log'))
        #     log_path.parent.mkdir(parents=True, exist_ok=True)
        #
        #     # 移除默认的日志处理器
        #     logger.remove()
        # # 添加新的日志处理器
        # logger.add(
        #     log_path,
        #     level=logger_config.get('level', 'INFO'),
        #     format=logger_config.get('format', '{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}'),
        #     rotation=logger_config.get('rotation', '1 day'),
        #     retention=logger_config.get('retention', '7 days')
        # )

        self.scheduler = AsyncIOScheduler()
        self.session = None

    async def start(self):
        """启动Agent"""
        self.session = aiohttp.ClientSession()
        # 注册定时任务
        self.scheduler.add_job(self.send_heartbeat, 'interval', seconds=self.heartbeat_interval)
        self.scheduler.add_job(self.fetch_tasks, 'interval', seconds=self.task_fetch_interval)
        self.scheduler.start()
        logger.info(f"Agent {self.node_id} started")

    async def stop(self):
        """停止Agent"""
        if self.session:
            await self.session.close()
        self.scheduler.shutdown()
        logger.info(f"Agent {self.node_id} stopped")

    async def send_heartbeat(self):
        """发送心跳信息到主节点"""
        try:
            url = self.master_heartbeat_url + str(
                self.node_id)  # http://localhost:1030/dev-api/aihuman/cluster/heartbeat/
            async with self.session.post(url) as response:
                if response.status == 200:
                    resp_json = await response.json()
                    if resp_json.get('code') != 200:
                        logger.error(f"Failed to fetch tasks: response code {resp_json.get('code')}, message: {resp_json.get('msg')}")
                        return
                    logger.debug("Heartbeat to %s sent successfully" % url)
                else:
                    logger.error("Failed to send heartbeat to %s , status: %s" % (url, response.status))
        except Exception as e:
            logger.error(f"Error sending heartbeat: {e}")

    async def fetch_tasks(self):
        """从主节点获取任务"""
        try:
            url = self.master_task_url + f'dispatch?cluster_id={self.node_id}'
            async with self.session.get(url) as response:
                if response.status == 200:
                    # 检查响应头中是否包含文件下载相关信息
                    # 这是一个文件下载任务
                    task = {
                            'task_id': response.headers.get('Task-Id'),
                            'name': response.headers.get('Task-Name'),
                            'type': 'file_download',
                            'file_name': response.headers.get('Material-Name'),
                            'content': await response.read(),
                            'cluster_id': self.node_id,
                            'err_msg': None,
                        }
                    if await self.download_file(task):
                        await self.execute_python_script(task)
                        await self.upload_result(task)
                elif response.status == 204:
                    logger.info(f"No tasks available")
                else:
                    logger.error(f"Failed to fetch tasks: {response.status}")
        except Exception as e:
            logger.error(f"Error fetching tasks: {e}")

    async def download_file(self, task):
        """下载文件并保存到material目录"""
        try:
            file_name = task.get('file_name')
            content = task.get('content')
            
            if not file_name or content is None:
                task['err_msg'] = 'Invalid file download task: missing file_name or content'
                logger.error(f"Invalid file download task: missing file_name or content")
                return False

            material_dir = Path(__file__).parent.parent / 'material'
            material_dir.mkdir(exist_ok=True)
            file_path = material_dir / file_name

            with open(file_path, 'wb') as f:
                f.write(content)
            logger.info(f"File {file_name} downloaded successfully")
            return True
        except Exception as e:
            task['err_msg'] = 'download material file failed'
            logger.error(f"Error downloading file: {e}")
            return False

    async def execute_python_script(self, task):
        """执行配置文件中musetalk脚本"""
        try:
            musetalk_bin = self.config.get('musetalk', {}).get('bin')
            if musetalk_bin:
                # Todo：python3的路径要替换成 python_bin = self.config.get('musetalk', {}).get('python_bin')
                process = await asyncio.create_subprocess_exec(
                    'python3', musetalk_bin,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                logger.info(f"Output: {stdout.decode()}")
                if process.returncode == 0:
                    task['status'] = Constants.TASK_COMPLETED
                    logger.info(f"Successfully executed {musetalk_bin}")
                else:
                    task['status'] = Constants.TASK_FAILED
                    task['err_msg'] = stderr.decode()
                    logger.error(f"Failed to execute {musetalk_bin}: {stderr.decode()}")
            else:
                task['status'] = Constants.TASK_FAILED
                task['err_msg'] = "musetalk.bin not configured in config.yaml"
                logger.warning("musetalk.bin not configured in config.yaml")
        except Exception as e:
            task['err_msg'] = str(e)
            task['status'] = Constants.TASK_FAILED
            logger.error(f"Error executing musetalk script: {e}")

    async def upload_result(self, task):
        """执行任务并上报结果"""
        try:
            # 准备上传文件
            material_dir = Path(__file__).parent.parent / 'material'
            file_path = material_dir / task.get('file_name', '')
            
            if not file_path.exists():
                logger.error(f"File {file_path} not found for upload")
                task['err_msg'] = f"File {file_path} not found for upload"
                task['status'] = Constants.TASK_FAILED
                return
            
            # 准备multipart表单数据
            data = aiohttp.FormData()
            data.add_field('task_id', str(task.get('task_id')))
            data.add_field('status', 'success' if task.get('status') == Constants.TASK_COMPLETED else 'failed')
            data.add_field('cluster_id', str(task.get('cluster_id')))
            data.add_field('file', 
                          open(file_path, 'rb'),
                          filename=task.get('file_name'),
                          content_type='application/octet-stream')
            
            # 上报任务结果
            url = self.master_task_url + 'result'
            async with self.session.post(url, data=data) as response:
                if response.status == 200:
                    resp_json = await response.json()
                    if resp_json.get('code') != 200:
                        logger.error(f"Failed to fetch tasks: response code {resp_json.get('code')}, message: {resp_json.get('msg')}")
                        return
                    logger.info(f"Task {task.get('task_id')} result and file uploaded successfully")
                else:
                    logger.error(f"Failed to report task {task.get('task_id')} result: {response.status}")
        except Exception as e:
            logger.error(f"Error executing task {task.get('task_id', 'unknown')}: {e}")
            task['err_msg'] = str(e)
            task['status'] = Constants.TASK_FAILED


async def main():
    agent = ClusterAgent()
    try:
        await agent.start()
        # 保持程序运行
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == '__main__':
    asyncio.run(main())
