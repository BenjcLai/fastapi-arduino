from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import os

app = FastAPI()

# 建立上傳資料夾
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 上傳圖片
@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    return {"message": "上傳成功", "file_path": f"/{UPLOAD_FOLDER}/{file.filename}"}

# 下載圖片
@app.get("/uploads/{filename}")
def download_image(filename: str):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        return {"error": "檔案不存在"}
