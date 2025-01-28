import asyncio
import cv2
import numpy as np
import datetime
import time
from multiprocessing import Pool
from src.conf.config import settings
from camera_service import port_connection

IP = settings.ip
PORTS_FILE = "camera_service/ports.bin"

# Optimization settings
MAX_FRAME_SIZE = 10 * 1024 * 1024  # 10 MB (frame size limitation)
VIEWER_TIMEOUT = 60  # 30 seconds viewer timeout
FRAME_RESOLUTION = (640, 480)  # Reduce frame resolution for viewers
TARGET_FPS = 30  # Target FPS (can be customized)
MIN_FPS = 10  # Minimum FPS to avoid slow recording
TEXT_AREA_HEIGHT = 50  # Height of the text area (in pixels)

class VideoServer:
    def __init__(self, host, port, viewer_port):
        self.host = host
        self.port = port
        self.viewer_port = viewer_port
        self.viewers = set()
        self.connected_ports = set()
        self.frame_queue = asyncio.Queue(maxsize=10)  # Frame buffering

    async def camera_handler(self, reader, writer):
        address = writer.get_extra_info('peername')
        print(f"Camera connected on port {self.port} from {address}")
        port_connection.add_port_to_file(PORTS_FILE, self.port)
        today_date = datetime.datetime.now().strftime("%d-%m-%Y__%H-%M-%S")
        out = None
        last_frame_time = time.time()  # Last frame time
        frame_count = 0  # Frame counter

        try:
            while True:
                # Getting frame size
                data = await reader.read(100)
                if not data:
                    break
                frame_length = int(data.decode().strip())

                # Protection against oversized frames
                if frame_length > MAX_FRAME_SIZE:
                    print(f"Frame size {frame_length} exceeds limit. Disconnecting camera.")
                    break

                # Receiving frame data
                frame_data = b''
                while len(frame_data) < frame_length:
                    chunk = await reader.read(min(4096, frame_length - len(frame_data)))
                    if not chunk:
                        break
                    frame_data += chunk

                # Frame decoding
                frame = np.frombuffer(frame_data, dtype=np.uint8)
                frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

                if frame is not None:
                    # Calculating time between frames
                    current_time = time.time()
                    time_diff = current_time - last_frame_time
                    last_frame_time = current_time

                    # Skipping frames if they come in too slow
                    if time_diff > 1 / MIN_FPS:
                        print(f"Frame dropped due to slow arrival (time_diff: {time_diff:.2f}s)")
                        continue

                    # Increasing frame size to make room for text
                    height, width, _ = frame.shape
                    new_height = height + TEXT_AREA_HEIGHT
                    extended_frame = np.zeros((new_height, width, 3), dtype=np.uint8)  # Nowa klatka z czarnym tłem
                    extended_frame[:height, :width] = frame  # Umieszczenie oryginalnego obrazu w górnej części

                    # Adding a text with date and time
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 0.7
                    font_color = (255, 255, 255)  # White color
                    font_thickness = 2
                    text_position = (10, height + 30)  # Text position

                    # Placing text on the frame
                    cv2.putText(extended_frame, timestamp, text_position, font, font_scale, font_color, font_thickness)

                    # Save video
                    if out is None:
                        out = cv2.VideoWriter(
                            f'records/camera_port_{self.port}_{today_date}.mp4',
                            cv2.VideoWriter_fourcc(*'mp4v'), TARGET_FPS, (width, new_height)
                        )

                    out.write(extended_frame)
                    frame_count += 1

                    # Reduce resolution for viewers
                    resized_frame = cv2.resize(extended_frame, FRAME_RESOLUTION)
                    encoded_frame = cv2.imencode('.jpg', resized_frame)[1].tobytes()

                    # Sending frame to viewers
                    message = str(len(encoded_frame)).encode().ljust(100) + encoded_frame
                    await self.broadcast_to_viewers(message)

        except Exception as e:
            print(f"Error: {e}")
        finally:
            if out is not None:
                out.release()
            writer.close()
            port_connection.remove_specific_port(PORTS_FILE, self.port)
            print(f"Camera disconnected on port {self.port} from {address}")

    async def broadcast_to_viewers(self, message):
        """Wysyła klatkę do wszystkich widzów równolegle."""
        tasks = []
        for viewer in list(self.viewers):
            try:
                viewer.write(message)  # Saving data to buffer
                tasks.append(viewer.drain())  # Waiting for data to be sent
            except Exception as e:
                print(f"Failed to send to viewer: {e}")
                self.viewers.remove(viewer)
        if tasks:
            await asyncio.gather(*tasks)

    async def viewer_handler(self, reader, writer):
        self.viewers.add(writer)
        print(f"Viewer connected on port {self.viewer_port}")
        try:
            while True:
                try:
                    await asyncio.wait_for(reader.read(1), timeout=VIEWER_TIMEOUT)
                except asyncio.TimeoutError:
                    print(f"Viewer on port {self.viewer_port} timed out.")
                    break
        except ConnectionResetError:
            print(f"Viewer on port {self.viewer_port} disconnected unexpectedly.")
        except Exception as e:
            print(f"Error with viewer on port {self.viewer_port}: {e}")
        finally:
            if writer in self.viewers:
                self.viewers.remove(writer)
            writer.close()
            print(f"Viewer disconnected from port {self.viewer_port}")

    async def run_server(self):
        server = await asyncio.start_server(self.camera_handler, self.host, self.port)
        viewer_server = await asyncio.start_server(self.viewer_handler, self.host, self.viewer_port)
        async with server, viewer_server:
            print(f"Server started on {self.host}:{self.port} for cameras")
            print(f"Server started on {self.host}:{self.viewer_port} for viewers")
            await asyncio.gather(server.serve_forever(), viewer_server.serve_forever())


def start_server_process(host, camera_port, viewer_port):
    server = VideoServer(host, camera_port, viewer_port)
    asyncio.run(server.run_server())


if __name__ == "__main__":
    port_connection.clear_ports_file(PORTS_FILE)
    camera_ports = [6001, 6002]  # Ports for cameras
    viewer_ports = [7001, 7002]  # Ports for viewers

    with Pool(processes=len(camera_ports)) as pool:
        pool.starmap(start_server_process, [(IP, cam_port, view_port) for cam_port, view_port in zip(camera_ports, viewer_ports)])