import aiofiles
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from storage import MediaStorage
import logging

app = FastAPI(title="Media Storage Microservice")
media_storage = MediaStorage()


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logging.getLogger('httpx').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


@app.post("/upload")
async def upload_media(file: UploadFile = File(...)):
    """
    Endpoint to upload media content (photo, video, music)
    Returns media ID and metadata
    """
    logger.info("Поступил запрос на загрузку контента")
    media_id, media_info = await media_storage.save_media(file, file.content_type)
    logger.info("Контент загружен")
    return {
        "media_id": media_id,
        "metadata": media_info
    }

@app.get("/media/{media_id}")
async def get_media(media_id: str):
    """
    Endpoint to retrieve media file or metadata
    """
    logger.info("Поступил запрос на получение контента")
    media_info = media_storage.get_media_info(media_id)
    if not media_info:
        raise HTTPException(status_code=404, detail="Media not found")

    logger.info("Контент отрпавлен")
    return FileResponse(media_info['path'], 
    media_type=media_info['content_type'], 
    filename=media_info['original_name'])

@app.delete("/media/{media_id}")
async def delete_media(media_id: str):
    """
    Endpoint to delete media by ID
    """
    logger.info("Поступил запрос на удаление контента")
    success = media_storage.delete_media(media_id)
    if not success:
        logger.error(f"Произошла ошибка при удалении контента {media_id}")
        raise HTTPException(status_code=404, detail="Media not found")
    logger.info("Контент удален")
    return JSONResponse(content={"message": "Media deleted successfully"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)