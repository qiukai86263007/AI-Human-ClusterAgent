from loguru import logger

if __name__ == '__main__':
    print("Hello, World!")

    # curl -X POST "http://localhost:8089/aihuman/task/anonymous/submit" -H "accept: */*" -H "Content-Type: multipart/form-data" -F "taskName=rest" -F "file=@test_audio.wav;type=audio/wav"
    # curl -X POST "http://localhost:8089/aihuman/task/anonymous/submit" -H "accept: */*" -H "Content-Type: multipart/form-data" -F "clientId=463bc68a-ce3a-415c-a9f7-c755921edaba" -F "materialId=sun" -F "parentTaskId=818c6df0-3f16-4bcc-b67e-ead92f31e134" -F "userId=kaikai" -F "file=@test_audio.wav;type=audio/wav"