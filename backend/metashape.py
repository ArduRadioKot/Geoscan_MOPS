import os
import sys
from typing import Optional


def process_metashape(
    photos_folder: str,
    output_path: str,
    project_path: Optional[str] = None,
) -> str:
    """
    Обрабатывает фотографии через Metashape и создаёт ортомозаику.
    
    Args:
        photos_folder: Папка с входными фотографиями
        output_path: Путь для сохранения ортомозаики (например, mosaic.png)
        project_path: Путь к файлу проекта Metashape (опционально)
    
    Returns:
        Путь к созданной ортомозаике
    """
    try:
        import Metashape
    except ImportError:
        raise ImportError(
            "Модуль Metashape не установлен. "
            "Установите Agisoft Metashape и его Python API."
        )

    # Создаём папку для вывода, если её нет
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Если путь к проекту не указан, создаём временный
    if project_path is None:
        project_dir = os.path.dirname(output_path)
        project_path = os.path.join(project_dir, "metashape_project.psx")

    def find_files(folder: str, types: list) -> list:
        """Находит файлы указанных типов в папке."""
        if not os.path.isdir(folder):
            return []
        return [
            entry.path
            for entry in os.scandir(folder)
            if (entry.is_file() and os.path.splitext(entry.name)[1].lower() in types)
        ]

    # Создаём проект и чанк
    doc = Metashape.Document()
    doc.save(path=project_path)
    chunk = doc.addChunk()

    # Импортируем фотографии
    photos = find_files(photos_folder, [".jpg", ".jpeg", ".tif", ".tiff", ".png"])
    if not photos:
        raise ValueError(f"В папке {photos_folder} не найдено фотографий")

    chunk.addPhotos(photos)
    doc.save()

    # Сопоставление фотографий
    chunk.matchPhotos(
        keypoint_limit=40000,
        tiepoint_limit=10000,
        generic_preselection=True,
        reference_preselection=True,
    )
    doc.save()

    # Выравнивание камер
    chunk.alignCameras()
    doc.save()

    # Построение карт глубины
    chunk.buildDepthMaps(downscale=2, filter_mode=Metashape.MildFiltering)
    doc.save()

    # Построение модели
    chunk.buildModel()
    doc.save()

    # Построение DEM
    chunk.buildDem(source_data=Metashape.DepthMapsData)
    doc.save()

    # Построение ортомозаики
    chunk.buildOrthomosaic(surface_data=Metashape.ElevationData)
    doc.save()

    # Экспорт ортомозаики
    chunk.exportRaster(output_path, source_data=Metashape.OrthomosaicData)
    doc.save()

    # Закрываем Metashape (опционально, можно закомментировать для отладки)
    # Metashape.app.quit()

    return output_path


def proccess_metashape():
    """
    Старая функция для обратной совместимости.
    Использует жёстко заданные пути.
    """
    project_path = "Project.psx"
    photos_folder = "n/"
    ortho_folder = "out/mosaic.png"

    return process_metashape(photos_folder, ortho_folder, project_path)
