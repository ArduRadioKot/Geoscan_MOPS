import os
import time
from typing import Union

import cv2
import numpy as np


def wait_image(image_path: str, timeout: float = 60.0) -> str:
    deadline = time.time() + timeout

    while time.time() < deadline:
        if os.path.exists(image_path) and os.path.getsize(image_path) > 0:
            return image_path
        time.sleep(0.1)

    raise TimeoutError(f"Image '{image_path}' not found within {timeout} seconds")


def image_raw2cv(image: Union[str, bytes, bytearray, np.ndarray]) -> np.ndarray:

    if isinstance(image, np.ndarray):
        return image

    if isinstance(image, str):
        img = cv2.imread(image)
        if img is None:
            raise ValueError(f"Failed to read image from path: {image}")
        return img

    if isinstance(image, (bytes, bytearray)):
        nparr = np.frombuffer(image, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Failed to decode image from raw bytes")
        return img

    raise TypeError(f"Unsupported image type: {type(image)}")