import glob
import os
import shutil
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from fly import fly_start
from grabber import grab_images
from ai import process_image

TMP_ROOT = "tmp"

app = FastAPI(title=" backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================== ВСПОМОГАТЕЛЬНЫЕ ШТУКИ ДЛЯ СЕССИЙ ==================

def _ensure_tmp_root() -> None:
    os.makedirs(TMP_ROOT, exist_ok=True)


def _list_session_ids() -> List[int]:
    _ensure_tmp_root()
    ids: List[int] = []
    for name in os.listdir(TMP_ROOT):
        if name.startswith("tmp") and name[3:].isdigit():
            ids.append(int(name[3:]))
    return sorted(ids)


def _create_session() -> int:
    """
    Создаёт новую папку tmp{i} с подпапками data, metashape, ai.
    Возвращает i.
    """
    ids = _list_session_ids()
    next_id = (max(ids) + 1) if ids else 1

    session_dir = os.path.join(TMP_ROOT, f"tmp{next_id}")
    os.makedirs(session_dir, exist_ok=True)

    for sub in ("data", "metashape", "ai"):
        os.makedirs(os.path.join(session_dir, sub), exist_ok=True)

    return next_id


def _get_current_session_id() -> int:
    """
    Возвращает id последней сессии или кидает 404.
    """
    ids = _list_session_ids()
    if not ids:
        raise HTTPException(status_code=404, detail="Сессий ещё нет")
    return ids[-1]


def _require_session(session_id: int) -> None:
    """
    Проверяем, что tmp{session_id} существует.
    """
    path = os.path.join(TMP_ROOT, f"tmp{session_id}")
    if not os.path.isdir(path):
        raise HTTPException(status_code=404, detail=f"Сессия tmp{session_id} не найдена")


def _get_paths(session_id: int) -> Dict[str, str]:
    """
    Возвращает пути до папок data, metashape, ai для данной сессии.
    """
    base = os.path.join(TMP_ROOT, f"tmp{session_id}")
    return {
        "base": base,
        "data": os.path.join(base, "data"),
        "metashape": os.path.join(base, "metashape"),
        "ai": os.path.join(base, "ai"),
    }


def _list_images(folder: str) -> List[str]:
    """
    Список файлов-изображений в папке.
    """
    patterns = ("*.jpg", "*.jpeg", "*.png", "*.tif", "*.tiff", "*.bmp")
    files: List[str] = []
    for p in patterns:
        files.extend(glob.glob(os.path.join(folder, p)))
    return sorted(files)


# =========================== DATA: ЗАГРУЗКА ===========================


async def _save_uploads_to_data(
    session_id: int,
    files: List[UploadFile],
) -> List[str]:
    """
    Сохранение загруженных картинок в tmp{session_id}/data.
    """
    paths = _get_paths(session_id)
    data_dir = paths["data"]
    os.makedirs(data_dir, exist_ok=True)

    saved: List[str] = []

    for index, upload in enumerate(files, start=1):
        if not upload.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail=f"Файл {upload.filename} не является изображением",
            )

        # нормальное имя файла
        _, ext = os.path.splitext(upload.filename or "")
        if not ext:
            ext = ".jpg"
        filename = f"{index:04d}{ext}"
        dest_path = os.path.join(data_dir, filename)

        content = await upload.read()
        with open(dest_path, "wb") as f:
            f.write(content)

        saved.append(filename)

    return saved


# ========================= ВРЕМЕННАЯ ИММИТАЦИЯ РАБОТЫ METASHAPE =========================


def _require_data_not_empty(session_id: int) -> None:
    paths = _get_paths(session_id)
    images = _list_images(paths["data"])
    if not images:
        raise HTTPException(
            status_code=400,
            detail="Нельзя запускать Metashape: в папке data нет изображений",
        )


def process_metashape(session_id: int) -> str:
    """
    Упрощённая версия proccess_metashape:
    берём первое изображение из data и копируем в metashape с суффиксом _metashape.
    Возвращаем путь до нового файла.
    """
    paths = _get_paths(session_id)
    data_dir = paths["data"]
    metashape_dir = paths["metashape"]
    os.makedirs(metashape_dir, exist_ok=True)

    images = _list_images(data_dir)
    if not images:
        # На всякий случай, но по идее сюда не дойдём из-за _require_data_not_empty
        raise HTTPException(
            status_code=400,
            detail="В папке data нет изображений",
        )

    src = images[0]
    base_name = os.path.basename(src)
    name, ext = os.path.splitext(base_name)
    dst = os.path.join(metashape_dir, f"{name}_metashape{ext}")

    shutil.copy2(src, dst)
    return dst


# ============================= AI: ПРОЦЕСС =============================


def _require_metashape_not_empty(session_id: int) -> None:
    paths = _get_paths(session_id)
    images = _list_images(paths["metashape"])
    if not images:
        raise HTTPException(
            status_code=400,
            detail="Нельзя запускать AI: в папке metashape нет изображений",
        )


def process_ai_for_session(session_id: int) -> str:
    """
    Берём первую картинку из metashape, прогоняем через YOLO (из ai.py),
    результат сохраняем в tmp{session_id}/ai и возвращаем путь к результату.
    """
    paths = _get_paths(session_id)
    metashape_dir = paths["metashape"]
    ai_dir = paths["ai"]
    os.makedirs(ai_dir, exist_ok=True)

    images = _list_images(metashape_dir)

    if not images:
        raise HTTPException(
            status_code=400,
            detail="В папке metashape нет изображений",
        )

    input_path = images[0]
    base_name = os.path.basename(input_path)
    name, ext = os.path.splitext(base_name)
    output_path = os.path.join(ai_dir, f"{name}_ai{ext}")

    # Зовём нашу функцию из ai.py
    result_path = process_image(input_path, output_path)

    return result_path


# =============================== ENDPOINTЫ ===============================


@app.get("/session/new")
def create_session() -> Dict[str, Any]:
    """
    Создать новую tmp{i}.
    """
    session_id = _create_session()
    return {"session_id": session_id, "tmp_folder": f"tmp{session_id}"}


@app.get("/session/current")
def get_current_session() -> Dict[str, Any]:
    """
    Получить id последней созданной tmp{i}.
    """
    session_id = _get_current_session_id()
    return {"session_id": session_id, "tmp_folder": f"tmp{session_id}"}


@app.post("/data/upload")
async def upload_data(
    files: List[UploadFile] = File(..., description="Список изображений"),
    session_id: Optional[int] = Query(
        default=None,
        description="ID сессии (если не передан — создаётся новая)",
    ),
) -> Dict[str, Any]:
    """
    Вариант №2: заполнение папки data через POST загрузку файлов.
    Если файлов нет — 400.
    """
    if not files:
        raise HTTPException(
            status_code=400,
            detail="Нужно загрузить хотя бы один файл",
        )

    if session_id is None:
        session_id = _create_session()
    else:
        _require_session(session_id)

    saved_filenames = await _save_uploads_to_data(session_id, files)
    paths = _get_paths(session_id)

    return {
        "session_id": session_id,
        "data_dir": paths["data"],
        "saved_files": saved_filenames,
    }


@app.post("/start/fly")
def start_fly() -> Dict[str, Any]:
    """
    Вариант №1: старт пайплайна через fly_start() и grab_images().

    Тут только создаём новую tmp{i} и вызываем две функции.
    Реализацию fly_start / grab_images ты делаешь сам.
    """
    session_id = _create_session()

    fly_start()
    grab_images()

    paths = _get_paths(session_id)
    return {
        "session_id": session_id,
        "data_dir": paths["data"],
        "message": "Пайплайн съёмки запущен (fly_start + grab_images)",
    }


@app.get("/metashape/run")
def run_metashape_endpoint(
    session_id: int = Query(..., description="ID сессии tmp{i}"),
) -> FileResponse:
    """
    Запуск proccess_metashape:
    - проверяем, что есть сессия и картинки в data;
    - заполняем папку metashape;
    - возвращаем один результирующий файл.
    """
    _require_session(session_id)
    _require_data_not_empty(session_id)

    result_path = process_metashape(session_id)

    if not os.path.isfile(result_path):
        raise HTTPException(
            status_code=500,
            detail="Metashape не вернул результат",
        )

    return FileResponse(
        result_path,
        media_type="image/jpeg",
        filename=os.path.basename(result_path),
    )


@app.get("/ai/run")
def run_ai_endpoint(
    session_id: int = Query(..., description="ID сессии tmp{i}"),
) -> FileResponse:
    """
    Кнопка AI-процесса:
    - проверяем, что есть результат Metashape;
    - прогоняем через YOLO из ai.py;
    - возвращаем картинку из папки ai как FileResponse.
    """
    _require_session(session_id)
    _require_metashape_not_empty(session_id)

    result_path = process_ai_for_session(session_id)

    if not os.path.isfile(result_path):
        raise HTTPException(
            status_code=500,
            detail="AI не вернул результирующее изображение",
        )

    return FileResponse(
        result_path,
        media_type="image/jpeg",
        filename=os.path.basename(result_path),
    )