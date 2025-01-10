import os
import uuid
import aiofiles
import json
from typing import Dict, Optional
import logging


logger = logging.getLogger(__name__)

class MediaStorage:
    def __init__(self, base_path: str = "media_storage"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
        self.media_registry_path = os.path.join(base_path, "media_registry.json")
        self.media_registry: Dict[str, Dict] = self.load_media_registry()

    async def save_media(self, file, content_type: str):
        # Создание уникального имени
        logger.info("Сохранение контента запушено...")
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(self.base_path, unique_filename)

        # Сохранение файла
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)

        # Сохранение информации о контенте
        media_info = {
            "filename": unique_filename,
            "original_name": file.filename,
            "content_type": content_type,
            "path": file_path,
            "size": len(content)
        }
        media_id = unique_filename
        self.media_registry[media_id] = media_info
        self.save_media_registry()
        logger.info(f"Сохранение контента завершено: {media_id}")
        return media_id, media_info

    def get_media_info(self, media_id: str) -> Optional[Dict]:
        logger.info(f"Получение контента {media_id}")
        return self.media_registry.get(media_id)

    def delete_media(self, media_id: str) -> bool:
        logger.info(f"Удаление контента {media_id}")
        media_info = self.media_registry.get(media_id)
        if media_info:
            try:
                os.remove(media_info['path'])
                del self.media_registry[media_id]
                self.save_media_registry()
                logger.info(f"Контент {media_id} удален")
                return True
            except Exception as e:
                logger.error(f"Произошла ошибка при удалении контента {media_id}: {e}")
                return False
        logger.info(f"Контент {media_id} не найден")
        return False

    def load_media_registry(self) -> Dict[str, Dict]:
        logger.info("Загрузка регистр медиа")
        if os.path.exists(self.media_registry_path):
            with open(self.media_registry_path, 'r') as f:
                return json.load(f)
        logger.info("Регистр медиа не найден")
        return {}

    def save_media_registry(self) -> None:
        logger.info("Сохраняю регистр медиа")
        with open(self.media_registry_path, 'w') as f:
            json.dump(self.media_registry, f)