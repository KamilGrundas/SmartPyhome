from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field
import socket

load_dotenv()


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


class Settings(BaseSettings):
    ip: str = Field(default_factory=get_ip)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
settings.ip = get_ip()
