import requests
from typing import Union, BinaryIO, Optional

class MediaServiceClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize MediaServiceClient with base URL of the microservice
        
        :param base_url: Base URL of the media storage microservice
        """
        self.base_url = base_url.rstrip('/')

    def upload(self, file: Union[str, BinaryIO]) -> Optional[str]:
        """
        Upload a media file to the service
        
        :param file: Path to file or file-like object
        :return: Media ID of the uploaded file or None if failed
        """
        url = f"{self.base_url}/upload"
        
        # Handle different input types
        if isinstance(file, str):
            # If file is a path, open it
            with open(file, 'rb') as f:
                files = {'file': (file.split('/')[-1], f)}
                response = requests.post(url, files=files)
        else:
            # If file is a file-like object
            files = {'file': (getattr(file, 'name', 'uploaded_file'), file)}
            response = requests.post(url, files=files)
        
        # Return None on bad responses
        try:
            response.raise_for_status()
        except requests.RequestException:
            return None
        
        # Return the media ID
        return response.json().get('media_id')

    def get(self, media_id: str, save_path: str = None) -> Optional[bytes]:
        """
        Retrieve a media file
        
        :param media_id: Unique identifier of the media
        :param save_path: Optional path to save the downloaded file
        :return: File content as bytes or None if failed
        """
        url = f"{self.base_url}/media/{media_id}"
        
        # Download the file
        response = requests.get(url)
        try:
            response.raise_for_status()
        except requests.RequestException:
            return None
        
        # Get file content
        file_content = response.content
        
        # Save file if path is provided
        if save_path:
            with open(save_path, 'wb') as f:
                f.write(file_content)
        
        return file_content

    def delete(self, media_id: str) -> Optional[bool]:
        """
        Delete a media file
        
        :param media_id: Unique identifier of the media to delete
        :return: Boolean indicating successful deletion or None if failed
        """
        url = f"{self.base_url}/media/{media_id}"
        
        response = requests.delete(url)
        try:
            response.raise_for_status()
        except requests.RequestException:
            return None
        
        return response.json().get('message') == "Media deleted successfully"