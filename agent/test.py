from loguru import logger

if __name__ == '__main__':
    print("Hello, World!")

    # curl -X POST "http://localhost:8089/aihuman/task/anonymous/submit" -H "accept: */*" -H "Content-Type: multipart/form-data" -F "taskName=rest" -F "file=@test_audio.wav;type=audio/wav"