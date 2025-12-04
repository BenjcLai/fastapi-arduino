from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import FileResponse
import uvicorn
import pymssql
from datetime import datetime
import os
import openai

app = FastAPI()

received_data = []
uploaded_files = []

server = "192.168.1.217"
user = "sa"
password = "ben26382535"
port =1433

# 建立上傳資料夾
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# optional; defaults to `os.environ['OPENAI_API_KEY']`
openai.api_key = "sk-z3w8zKSpr4jzIPCGCe81406cCc6e4047943cC118360c39F4"

# all client options can be configured just like the `OpenAI` instantiation counterpart
openai.base_url = "https://free.v36.cm/v1/"
openai.default_headers = {"x-foo": "true"}

def databaseconnect():
    try :
        conn = pymssql.connect(server = server ,user = user ,password = password , port = port)
        cursor = conn.cursor()
        sql = """SELECT TOP (1000) [s1]
              ,[s2]
              ,[s3]
            FROM [lala].[dbo].[test1]
             """
        cursor.execute(sql)
        result =cursor.fetchall()
        print(result)
        return result
    except Exception as e:
        print("資料庫連線或查詢失敗：", e)
        return []
        

@app.get("/")
async def root():
    result = databaseconnect()
    print(result)
    return result

# POST 接收 Arduino 資料
@app.post("/receive-data")
async def receive_data(request: Request):
    try:
        data = await request.json()  # 解析 Arduino 送來的 JSON
        print("收到資料:", data)     # 印出到終端
        data["received_time"] = datetime.now()
        received_data.append(data)
        return {"status": "ok", "received": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/data")
async def get_data():
    """在 API 介面顯示目前收到的所有資料"""
    return {"received_data": received_data}

# 上傳圖片
@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    uploaded_files.append({
        "filename": file.filename,
        "upload_time": datetime.now()
    })
    
    return {"message": "上傳成功", "file_path": f"/{UPLOAD_FOLDER}/{file.filename}"}

@app.get("/upload-records")
async def get_upload_records():
    return uploaded_files

# 下載圖片
@app.get("/uploads/{filename}")
def download_image(filename: str):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        return {"error": "檔案不存在"}

#取得ai回答結果
@app.get("/fireresponse")
def getfireresponse():
    completion1 = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "請分析這張圖片是否為火災。請只回答：是火災、不是火災"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "https://fastapi-arduino-1.onrender.com/uploads/fire.jpg"
                        }
                    }
                ]
            }
        ],
    )

    print(completion1.choices[0].message.content)
    return completion1.choices[0].message.content

 
if __name__ == "__main__":
    # 0.0.0.0 監聽所有網路介面，Arduino 也能連線
    uvicorn.run(app, host="0.0.0.0", port=5000)

#傳資料到這個api
# curl -X POST http://192.168.1.217:5000/receive-data -H "Content-Type: application/json" -d "{\"temperature\":25,\"humidity\":60}"
#{"status":"ok","received":{"temperature":25,"humidity":60}}











