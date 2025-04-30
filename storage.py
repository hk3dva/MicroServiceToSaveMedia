import os
import logging
from minio import Minio
from minio.error import S3Error
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class MinioClient:
    def __init__(self, bucket_name: str = "user.photos"):
        self.client = Minio(
                        os.getenv('MINIO_ENDPOINT', 'minio:9000'),
                        access_key=os.getenv('MINIO_ACCESS_KEY', 'minioadmin'),
                        secret_key=os.getenv('MINIO_SECRET_KEY', 'minioadmin'),
                        secure=False  # Используйте True для HTTPS
                    )
        self.bucket_name = bucket_name
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """
        Проверяет, существует ли бакет. Если нет, создает его.
        """
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Бакет '{self.bucket_name}' создан.")
        except S3Error as e:
            logger.error(f"Ошибка при создании бакета: {e}")
            raise HTTPException(status_code=500, detail=f"Ошибка MinIO: {e}")

    def save(self, file_name, file):
        """
        Сохраняет файл в MinIO.

        :param file_name: Имя файла.
        :param file: Файл (объект UploadFile из FastAPI).
        """
        try:
            self.client.put_object(
                self.bucket_name,
                file_name,
                file.file,
                length=-1,  # Автоматически определяет длину файла
                part_size=10 * 1024 * 1024  # 10MB
            )
            logger.info(f"Файл '{file_name}' успешно сохранен в бакет '{self.bucket_name}'.")
        except S3Error as e:
            logger.error(f"Ошибка при сохранении файла: {e}")
            raise HTTPException(status_code=500, detail=f"Ошибка MinIO: {e}")

    def get(self, file_name):
        """
        Получает файл из MinIO.

        :param file_name: Имя файла.
        :return: Объект файла.
        """
        try:
            response = self.client.get_object(self.bucket_name, file_name)
            logger.info(f"Файл '{file_name}' успешно получен из бакета '{self.bucket_name}'.")
            return response
        except S3Error as e:
            logger.error(f"Ошибка при получении файла: {e}")
            raise HTTPException(status_code=404, detail=f"Файл не найден: {e}")
        except Exception as e:
            logger.error(f"Неизвестная ошибка: {e}")
            raise HTTPException(status_code=500, detail=f"Ошибка MinIO: {e}")

    def delete(self, file_name):
        """
        Удаляет файл из MinIO.

        :param file_name: Имя файла.
        """
        try:
            self.client.remove_object(self.bucket_name, file_name)
            logger.info(f"Файл '{file_name}' успешно удален из бакета '{self.bucket_name}'.")
        except S3Error as e:
            logger.error(f"Ошибка при удалении файла: {e}")
            raise HTTPException(status_code=500, detail=f"Ошибка MinIO: {e}")
