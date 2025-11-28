from ultralytics import YOLO
import cv2
import numpy as np
import os
from typing import Dict, List, Any, Optional

# Модель загружается лениво при первом использовании
_model: Optional[YOLO] = None


def _find_model_path() -> str:
    """
    Ищет файл модели YOLO в нескольких возможных местах.
    Возвращает путь к модели или выбрасывает FileNotFoundError.
    """
    # Сначала проверяем переменную окружения
    env_path = os.getenv("YOLO_MODEL_PATH")
    if env_path and os.path.isfile(env_path):
        return env_path

    # Затем ищем в текущей директории и в папке backend
    possible_paths = [
        "best.pt",
        os.path.join(os.path.dirname(__file__), "best.pt"),
        os.path.join(os.path.dirname(__file__), "..", "best.pt"),
    ]

    for path in possible_paths:
        abs_path = os.path.abspath(path)
        if os.path.isfile(abs_path):
            return abs_path

    # Если не нашли, выбрасываем ошибку с подсказкой
    raise FileNotFoundError(
        "Модель YOLO не найдена. Поместите файл best.pt в папку backend/ "
        "или укажите путь через переменную окружения YOLO_MODEL_PATH"
    )


def _get_model() -> YOLO:
    """
    Ленивая загрузка модели YOLO.
    Загружает модель только при первом вызове.
    """
    global _model
    if _model is None:
        model_path = _find_model_path()
        _model = YOLO(model_path)
    return _model

# Цвета для разных классов (на случай, если будет несколько)
colors = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255),
    (255, 0, 255), (192, 192, 192), (128, 128, 128), (128, 0, 0), (128, 128, 0),
    (0, 128, 0), (128, 0, 128), (0, 128, 128), (0, 0, 128), (72, 61, 139),
    (47, 79, 79), (47, 79, 47), (0, 206, 209), (148, 0, 211), (255, 20, 147)
]


def _run_yolo(image_path: str) -> tuple:
    """
    Общая часть: читаем картинку, запускаем YOLO, забираем боксы.
    Возвращаем (image, classes_names, classes, boxes, grouped_objects).
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Не удалось прочитать изображение: {image_path}")

    model = _get_model()
    results = model(image)[0]

    image = results.orig_img
    classes_names = results.names
    classes = results.boxes.cls.cpu().numpy()
    boxes = results.boxes.xyxy.cpu().numpy().astype(np.int32)

    grouped_objects: Dict[str, List[List[int]]] = {}
    for class_id, box in zip(classes, boxes):
        class_name = classes_names[int(class_id)]
        grouped_objects.setdefault(class_name, []).append(box.tolist())

    return image, classes_names, classes, boxes, grouped_objects


def process_image(image_path: str) -> str:
    """
    Старый вариант: обрабатываем картинку и сохраняем результат
    РЯДОМ с исходником (имя + _yolo.ext), плюс txt с координатами.
    Удобно для локальных тестов.
    """
    image, classes_names, classes, boxes, grouped_objects = _run_yolo(image_path)

    # Рисуем боксы
    for class_id, box in zip(classes, boxes):
        class_name = classes_names[int(class_id)]
        color = (4, 44, 252)

        x1, y1, x2, y2 = box
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 10)
        cv2.putText(
            image,
            class_name,
            (x1, max(0, y1 - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            1,
        )

    root, ext = os.path.splitext(image_path)
    new_image_path = root + "_yolo" + ext
    cv2.imwrite(new_image_path, image)

    text_file_path = root + "_data.txt"
    with open(text_file_path, "w", encoding="utf-8") as f:
        for class_name, details in grouped_objects.items():
            f.write(f"{class_name}:\n")
            for detail in details:
                f.write(
                    f"Coordinates: ({detail[0]}, {detail[1]}, {detail[2]}, {detail[3]})\n"
                )

    print(f"Processed {image_path}")
    print(f"Saved bounding-box image to {new_image_path}")
    print(f"Saved data to {text_file_path}")

    return new_image_path


def process_ai_image(input_path: str, output_path: str) -> str:
    """
    Вариант специально для бекенда:
    - читаем картинку input_path;
    - запускаем YOLO;
    - сохраняем результат В ТОЧНО ЗАДАННЫЙ output_path (обычно в tmp{i}/ai);
    - рядом создаём *.txt с координатами.
    Возвращаем путь до output_path.
    """
    image, classes_names, classes, boxes, grouped_objects = _run_yolo(input_path)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Рисуем боксы
    for class_id, box in zip(classes, boxes):
        class_name = classes_names[int(class_id)]
        color = colors[int(class_id) % len(colors)]

        x1, y1, x2, y2 = box
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            image,
            class_name,
            (x1, max(0, y1 - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            1,
        )

    cv2.imwrite(output_path, image)

    root, _ = os.path.splitext(output_path)
    text_file_path = root + "_data.txt"
    with open(text_file_path, "w", encoding="utf-8") as f:
        for class_name, details in grouped_objects.items():
            f.write(f"{class_name}:\n")
            for detail in details:
                f.write(
                    f"Coordinates: ({detail[0]}, {detail[1]}, {detail[2]}, {detail[3]})\n"
                )

    return output_path