from fastapi import HTTPException, FastAPI, WebSocket
import websockets

IP = "192.168.1.131"
PORT = 8765
SERVER_ADDRESS = f"ws://{IP}:{PORT}"

clients = set()


async def video_stream(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    print(f"Client connected: {websocket}")
    try:
        while True:
            # Odbierz dane z serwera wideo (adres: SERVER_ADDRESS)
            async with websockets.connect(SERVER_ADDRESS) as video_ws:
                async for data in video_ws:
                    # Przekaż dane do wszystkich klientów WebSocket
                    for client in clients:
                        await client.send_text(data)
    finally:
        clients.remove(websocket)
