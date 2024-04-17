import cv2
import socket


def send_frame(frame, client_socket):
    _, buffer = cv2.imencode('.jpg', frame)
    data = buffer.tobytes()
    frame_length = len(data)
    client_socket.sendall(str(frame_length).encode().ljust(100))
    client_socket.sendall(data)


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('192.168.1.128', 8888))
    cap = cv2.VideoCapture(0)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            send_frame(frame, client_socket)
    finally:
        cap.release()
        client_socket.close()


if __name__ == '__main__':
    main()
