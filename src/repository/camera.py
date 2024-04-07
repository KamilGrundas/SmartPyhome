from fastapi import HTTPException
import websockets

IP = "192.168.1.131"
PORT = 8765
SERVER_ADDRESS = f"ws://{IP}:{PORT}"

async def video_generator():
    try:
        async with websockets.connect(SERVER_ADDRESS) as video_ws:
            async for frame in video_ws:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    except websockets.exceptions.ConnectionClosedError:
        raise HTTPException(status_code=500, detail="Połączenie z serwerem wideo zostało zerwane.")
