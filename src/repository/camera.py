import cv2
import asyncio
import numpy as np
from src.conf.config import settings

IP = settings.ip


async def get_video_stream(camera_port):
    reader, writer = await asyncio.open_connection(IP, camera_port)

    try:
        while True:
            # Assume that the first 100 bytes include the frame length as a string
            data = await reader.read(100)  # Read data for frame size
            if not data:
                break
            # Extract frame size from data
            frame_length = int(data.decode('utf-8').strip())  # Decoding only the size part, which is in text format

            # Now read the exact amount of data for the frame
            frame_data = b''
            while len(frame_data) < frame_length:
                chunk = await reader.read(frame_length - len(frame_data))
                frame_data += chunk

            # Process the image data directly
            frame = np.frombuffer(frame_data, dtype=np.uint8)
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
            ret, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    finally:
        writer.close()
