import yaml
from pathlib import Path


class ConfigManager:
    @staticmethod
    def load_config(config_path=None):
        """加载配置文件并返回配置对象"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'conf' / 'config.yaml'

        with open(config_path, 'r') as f:
            return yaml.safe_load(f)


    @staticmethod
    def create_task_config(directory_path, file_name, video_name, audio_name):
        """
        在指定目录创建任务配置文件
        :param directory_path: 目标目录路径
        :param file_name: 配置文件名称
        :param video_name: 视频文件名(素材)
        :param audio_name: 音频文件名
        """
        # 确保目录存在
        directory = Path(directory_path)
        directory.mkdir(parents=True, exist_ok=True)
        
        # 构建完整的文件路径
        file_path = directory / file_name
        
        # 如果文件存在则删除
        if file_path.exists():
            file_path.unlink()
        
        # 创建新的配置内容
        config_content = {
            'task_0': {
                'video_path': f'data/video/{video_name}.mp4',
                'audio_path': f'data/audio/{audio_name}'
            }
        }
        
        # 写入新文件
        with open(file_path, 'w') as f:
            yaml.dump(config_content, f, default_flow_style=False)
