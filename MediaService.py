import requests
from typing import Union, BinaryIO, Optional
import logging


logger = logging.getLogger(__name__)

class MediaServiceClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Инициализация MediaServiceClient с базовым URL микросервиса
        
        :param base_url: Базовый URL микросервиса хранения медиа
        """
        self.base_url = base_url.rstrip('/')

    def upload(self, file: Union[str, BinaryIO]) -> Optional[str]:
        """
        Загрузить файл медиа на сервис
        
        :param file: Путь к файлу или файлоподобный объект
        :return: ID медиа загруженного файла или None, если не удалось
        """
        url = f"{self.base_url}/upload"

        # Обработка разных типов ввода
        if isinstance(file, str):
            # Если файл - это путь, открыть его
            with open(file, 'rb') as f:
                files = {'file': (file.split('/')[-1], f)}
                response = requests.post(url, files=files)
        else:
            # Если файл - это объект, просто передать его
            files = {'file': (getattr(file, 'name', 'uploaded_file'), file)}
            response = requests.post(url, files=files)
        
        # Вернет None при ошибке
        try:
            response.raise_for_status()
        except requests.RequestException:
            return None
        
        # Вернет ID медиа
        return response.json().get('media_id')

    def get(self, media_id: str, save_path: str = None) -> Optional[bytes]:
        """
        Получить файл медиа
        
        :param media_id: Уникальный идентификатор медиа
        :param save_path: Необязательный путь для сохранения скачанного файла
        :return: Контент файла в виде байтов или None, если не удалось
        """
        url = f"{self.base_url}/media/{media_id}"
        
        # Скачать файл
        response = requests.get(url)
        try:
            response.raise_for_status()
        except requests.RequestException:
            return None
        
        # Получить контент файла
        file_content = response.content
        
        # Сохранить файл если путь указан
        if save_path:
            with open(save_path, 'wb') as f:
                f.write(file_content)
        
        return file_content

    def delete(self, media_id: str) -> Optional[bool]:
        """
        Удалить файл медиа
        
        :param media_id: Уникальный идентификатор медиа, который нужно удалить
        :return: Булевое значение, указывающее на успешное удаление, или None, если не удалось
        """
        url = f"{self.base_url}/media/{media_id}"
        
        response = requests.delete(url)
        try:
            response.raise_for_status()
        except requests.RequestException:
            return None
        
        return response.json().get('message') == "Media deleted successfully"