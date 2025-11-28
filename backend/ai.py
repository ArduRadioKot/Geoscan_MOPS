from ultralytics import YOLO
import cv2
import numpy as np
import os
from typing import Dict, List, Optional, Tuple

# Модель загружается лениво при первом использовании
_model: Optional[YOLO] = None


def _find_model_path() -> str:
    """
    Ищет файл модели YOLO в нескольких возможных местах.
    Возвращает путь к модели или выбрасывает FileNotFoundError.
    """
    env_path = os.getenv("YOLO_MODEL_PATH")
    if env_path and os.path.isfile(env_path):
        return env_path

    possible_paths = [
        "best.pt",
        os.path.join(os.path.dirname(__file__), "best.pt"),
        os.path.join(os.path.dirname(__file__), "..", "best.pt"),
    ]

    for path in possible_paths:
        abs_path = os.path.abspath(path)
        if os.path.isfile(abs_path):
            return abs_path

    raise FileNotFoundError(
        "Модель YOLO не найдена. Поместите файл best.pt в папку backend/ "
        "или укажите путь через переменную окружения YOLO_MODEL_PATH"
    )


def _get_model() -> YOLO:
    """Ленивая загрузка модели YOLO."""
    global _model
    if _model is None:
        model_path = _find_model_path()
        _model = YOLO(model_path)
    return _model


def _compute_iou(box: np.ndarray, boxes: np.ndarray) -> np.ndarray:
    """Вычисляет IoU между боксом и массивом боксов."""
    if boxes.size == 0:
        return np.array([])

    x1 = np.maximum(box[0], boxes[:, 0])
    y1 = np.maximum(box[1], boxes[:, 1])
    x2 = np.minimum(box[2], boxes[:, 2])
    y2 = np.minimum(box[3], boxes[:, 3])

    inter_area = np.maximum(0, x2 - x1) * np.maximum(0, y2 - y1)
    box_area = (box[2] - box[0]) * (box[3] - box[1])
    boxes_area = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    union_area = box_area + boxes_area - inter_area

    return inter_area / np.maximum(union_area, 1e-6)


def _split_image_into_tiles(
    image: np.ndarray,
    tile_size: int = 1200,
    overlap: float = 0.165,
) -> List[Tuple[np.ndarray, int, int]]:
    """Разбивает изображение на пересекающиеся тайлы."""
    h, w = image.shape[:2]
    tiles: List[Tuple[np.ndarray, int, int]] = []
    step = max(1, int(tile_size * (1 - overlap)))

    for y in range(0, h, step):
        for x in range(0, w, step):
            x2 = min(x + tile_size, w)
            y2 = min(y + tile_size, h)
            tile = image[y:y2, x:x2]

            if tile.shape[0] < tile_size // 4 or tile.shape[1] < tile_size // 4:
                continue

            tiles.append((tile, x, y))

    return tiles


def _merge_detections(
    detections: List[Tuple[np.ndarray, np.ndarray, np.ndarray]],
    iou_threshold: float = 0.5,
) -> Tuple[np.ndarray, np.ndarray]:
    """Объединяет детекции с разных тайлов с применением NMS."""
    if not detections:
        return np.array([]), np.array([])

    all_boxes: List[np.ndarray] = []
    all_classes: List[np.ndarray] = []
    all_scores: List[np.ndarray] = []

    for boxes, classes, scores in detections:
        if boxes.size == 0:
            continue
        all_boxes.append(boxes)
        all_classes.append(classes)
        all_scores.append(scores)

    if not all_boxes:
        return np.array([]), np.array([])

    boxes = np.concatenate(all_boxes, axis=0)
    classes = np.concatenate(all_classes, axis=0)
    scores = np.concatenate(all_scores, axis=0)

    final_boxes: List[np.ndarray] = []
    final_classes: List[int] = []

    for cls in np.unique(classes):
        idxs = np.where(classes == cls)[0]
        cls_boxes = boxes[idxs]
        cls_scores = scores[idxs]
        order = np.argsort(cls_scores)[::-1]

        while order.size > 0:
            current = order[0]
            final_boxes.append(cls_boxes[current])
            final_classes.append(int(cls))
            if order.size == 1:
                break
            rest = order[1:]
            ious = _compute_iou(cls_boxes[current], cls_boxes[rest])
            rest = rest[ious <= iou_threshold]
            order = rest

    return np.array(final_boxes), np.array(final_classes)


def _run_yolo_tiled(
    image_path: str,
    tile_size: int = 640,
    overlap: float = 0.3,
) -> Tuple[np.ndarray, Dict[int, str], np.ndarray, np.ndarray, Dict[str, List[List[int]]]]:
    """Запускает YOLO на изображении, разбитом на тайлы."""
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Не удалось прочитать изображение: {image_path}")

    model = _get_model()
    tiles = _split_image_into_tiles(image, tile_size, overlap)
    detections: List[Tuple[np.ndarray, np.ndarray, np.ndarray]] = []
    names: Dict[int, str] = model.names if isinstance(model.names, dict) else {int(k): v for k, v in enumerate(model.names)}

    for tile, offset_x, offset_y in tiles:
        results = model(tile, verbose=False)[0]
        boxes = results.boxes.xyxy.cpu().numpy()
        classes = results.boxes.cls.cpu().numpy().astype(int)
        scores = results.boxes.conf.cpu().numpy()

        if boxes.size == 0:
            continue

        boxes[:, [0, 2]] += offset_x
        boxes[:, [1, 3]] += offset_y
        detections.append((boxes, classes, scores))

    boxes, classes = _merge_detections(detections)

    grouped_objects: Dict[str, List[List[int]]] = {}
    for cls, box in zip(classes, boxes):
        class_name = names.get(int(cls), str(cls))
        grouped_objects.setdefault(class_name, []).append(box.astype(int).tolist())

    return image, names, classes, boxes, grouped_objects


def process_image(image_path: str) -> str:
    """Обрабатывает изображение и сохраняет результат рядом с исходником."""
    image, class_names, classes, boxes, grouped_objects = _run_yolo_tiled(image_path)

    for class_id, box in zip(classes, boxes):
        class_name = class_names.get(int(class_id), str(class_id))
        color = (4, 44, 252)
        x1, y1, x2, y2 = box.astype(int)
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            image,
            class_name,
            (x1, max(0, y1 - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2,
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

    return new_image_path


def process_ai_image(input_path: str, output_path: str) -> str:
    """Вариант для бекенда: сохраняет результат в точный путь."""
    image, class_names, classes, boxes, grouped_objects = _run_yolo_tiled(input_path)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    for class_id, box in zip(classes, boxes):
        class_name = class_names.get(int(class_id), str(class_id))
        color = (4, 44, 252)
        x1, y1, x2, y2 = box.astype(int)
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 4)
        cv2.putText(
            image,
            class_name,
            (x1, max(0, y1 - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            color,
            2,
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


def _run_yolo(image_path: str) -> tuple:
    """Обратная совместимость с предыдущим API."""
    return _run_yolo_tiled(image_path)