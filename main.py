import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from storage import MinioClient
import logging

app = FastAPI(title="Media Storage Microservice")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logging.getLogger('httpx').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


@app.post("/upload")
async def upload_media(file: UploadFile = File(...), backet_name='user.photos'):
    """
    Endpoint to upload media content (photo, video, music)
    Returns media ID and metadata
    """
    file_id = str(uuid.uuid4())
    file_name = f"{file_id}_{file.filename}"
    logger.info(f"файл получен {file_name}")
    try:
        logger.info('Отправка в хранилище')
        MinioClient(backet_name).save(file_name, file)

        return JSONResponse(status_code=200, content={
                    "media_id": file_name,
                })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/media/{media_id}")
async def get_media(media_id: str, backet_name='user.photos'):
    """
    Endpoint to retrieve media file or metadata
    """
    logger.info("Поступил запрос на получение контента")
    file = MinioClient(backet_name).get(media_id)
    return StreamingResponse(
        file.stream(32 * 1024),  # Чтение файла блоками по 32 КБ
        media_type="application/octet-stream",  # Универсальный тип для бинарных данных
        headers={"Content-Disposition": f"attachment; filename={media_id}"}
    )

@app.delete("/media/{media_id}")
async def delete_media(media_id: str, backet_name='user.photos'):
    """
    Endpoint to delete media by ID
    """
    logger.info("Поступил запрос на удаление контента")
    success = MinioClient(backet_name).delete_media(media_id)
    if not success:
        logger.error(f"Произошла ошибка при удалении контента {media_id}")
        raise HTTPException(status_code=404, detail="Media not found")
    logger.info("Контент удален")
    return JSONResponse(content={"message": "Media deleted successfully"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)