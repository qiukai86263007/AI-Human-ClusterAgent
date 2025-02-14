from loguru import logger

from utils.logger_manager import LoggerManager

# 获取已配置的logger对象
logger = LoggerManager.get_logger()

# 使用logger进行日志记录
logger.info("这是一条测试日志信息")
logger.debug("这是一条调试日志信息")
logger.error("这是一条错误日志信息")

if __name__ == '__main__':
    print("Hello, World!")

    # curl -X POST "http://localhost:8089/aihuman/task/anonymous/submit" -H "accept: */*" -H "Content-Type: multipart/form-data" -F "taskName=rest" -F "file=@test_audio.wav;type=audio/wav"
    # curl -X POST "http://localhost:8089/aihuman/task/anonymous/submit" -H "accept: */*" -H "Content-Type: multipart/form-data" -F "clientId=463bc68a-ce3a-415c-a9f7-c755921edaba" -F "materialId=sun" -F "parentTaskId=818c6df0-3f16-4bcc-b67e-ead92f31e134" -F "userId=kaikai" -F "file=@test_audio.wav;type=audio/wav"
    # curl -X GET "http://localhost:8089/aihuman/task/anonymous/download?taskUUID=test_audio" -H "accept: */*"