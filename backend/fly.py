import os
import socket
from contextlib import closing
from typing import Tuple

DEFAULT_HOST = "10.42.0.1"
DEFAULT_PORT = 8089
DEFAULT_TIMEOUT = 10


class DroneConnectionError(Exception):
    """Исключение при ошибке подключения к дрону"""


def _resolve_drone_endpoint() -> Tuple[str, int]:
    """Разрешает адрес и порт дрона из переменных окружения или использует значения по умолчанию"""
    host = os.getenv("DRONE_HOST", DEFAULT_HOST)
    port = int(os.getenv("DRONE_PORT", DEFAULT_PORT))
    return host, port


def fly_start(message: bytes = b"start") -> None:
    """
    Отправляет команду дрону через TCP-сокет.
    Raises:
        DroneConnectionError: если не удалось подключиться к дрону
    """
    host, port = _resolve_drone_endpoint()
    try:
        with closing(
            socket.create_connection((host, port), timeout=DEFAULT_TIMEOUT)
        ) as sock:
            sock.sendall(message)
    except OSError as exc:
        raise DroneConnectionError(
            f"Не удалось подключиться к контроллеру по адресу {host}:{port}"
        ) from exc
