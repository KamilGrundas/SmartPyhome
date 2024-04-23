import asyncio
import cv2
import numpy as np
import datetime
from multiprocessing import Process
from src.conf.config import settings
from camera_service import port_connection

IP = settings.ip

PORTS_FILE = "camera_service/ports.bin"


class VideoServer:
    def __init__(self, host, port, viewer_port):
        self.host = host
        self.port = port
        self.viewer_port = viewer_port
        self.viewers = set()
        self.connected_ports = set()

    async def camera_handler(self, reader, writer):
        address = writer.get_extra_info('peername')
        print(f"Camera connected on port {self.port} from {address}")
        port_connection.add_port_to_file(PORTS_FILE, self.port)
        today_date = datetime.datetime.now().strftime("%d-%m-%Y__%H-%M-%S")
        out = None

        try:
            while True:
                data = await reader.read(100)
                if not data:
                    break
                frame_length = int(data.decode().strip())
                frame_data = b''

                while len(frame_data) < frame_length:
                    chunk = await reader.read(frame_length - len(frame_data))
                    if not chunk:
                        break
                    frame_data += chunk

                frame = np.frombuffer(frame_data, dtype=np.uint8)
                frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

                if frame is not None:
                    if out is None:
                        height, width, _ = frame.shape
                        out = cv2.VideoWriter(f'records/camera_port_{self.port}_{today_date}.mp4',
                                              cv2.VideoWriter_fourcc(*'mp4v'), 10.0, (width, height))
                    out.write(frame)
                    # Send frame to all connected viewers
                    encoded_frame = cv2.imencode('.jpg', frame)[1].tobytes()
                    message = str(len(encoded_frame)).encode().ljust(100) + encoded_frame
                    for viewer in list(self.viewers):
                        try:
                            viewer.write(message)
                            await viewer.drain()
                        except Exception as e:
                            print(f"Failed to send to viewer: {e}")
                            self.viewers.remove(viewer)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            if out is not None:
                out.release()
            writer.close()
            port_connection.remove_specific_port(PORTS_FILE, self.port)
            print(f"Camera disconnected on port {self.port} from {address}")

    async def viewer_handler(self, reader, writer):
        self.viewers.add(writer)
        try:
            await reader.read()  # Oczekiwanie na dane od klienta, które nigdy nie mogą nadejść
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
    camera_ports = [6001, 6002]  # Define the ports for each camera
    viewer_ports = [7001, 7002]  # Define the viewer ports for each camera
    processes = []
    for cam_port, view_port in zip(camera_ports, viewer_ports):
        process = Process(target=start_server_process, args=(IP, cam_port, view_port))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()  # Wait for all processes to finish (they won't unless manually stopped)
