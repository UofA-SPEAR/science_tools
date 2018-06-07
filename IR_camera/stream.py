from io import BytesIO
from picamera import PiCamera


record_time = input("Enter a specified record time(s)")
stream = BytesIO()
camera = PiCamera()


camera.resolution = (640, 480)
camera.start_recording(stream, format='h264', quality=23)
camera.wait_recording(record_time)
camera.stop_recording()


