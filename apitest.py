from fastapi import FastAPI, Request
import uvicorn
import pymssql
from datetime import datetime

app = FastAPI()

received_data = []

server = "192.168.1.217"
user = "sa"
password = "ben26382535"
port =1433

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
        data_with_time = {
            "data": data,
            "received_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        received_data.append(data_with_time)
        return {"status": "ok", "received": data_with_time}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/data")
async def get_data():
    """在 API 介面顯示目前收到的所有資料"""
    return {"received_data": received_data}

@app.post("/clear-data")
async def clear_data():
    """清空 received_data 列表"""
    received_data.clear()  # 或者 received_data = [] 也可以
    return {"status": "ok", "message": "資料已清空"}
    
if __name__ == "__main__":
    # 0.0.0.0 監聽所有網路介面，Arduino 也能連線
    uvicorn.run(app, host="0.0.0.0", port=5000)

#傳資料到這個api
# curl -X POST http://192.168.1.217:5000/receive-data -H "Content-Type: application/json" -d "{\"temperature\":25,\"humidity\":60}"
#{"status":"ok","received":{"temperature":25,"humidity":60}}

