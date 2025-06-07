from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
import sqlite3
from typing import List
import os

# FastAPI 앱 인스턴스 생성
app = FastAPI()

# 정적 파일 마운트
app.mount("/static", StaticFiles(directory="static"), name="static")

# 템플릿 설정
templates = Jinja2Templates(directory="static")

# SQLite 데이터베이스 초기화
def init_db():
    conn = sqlite3.connect('values.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS value_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT (datetime('now', 'localtime'))
        )
    ''')
    conn.commit()
    conn.close()

# 앱 시작시 DB 초기화
@app.on_event("startup")
async def startup_event():
    init_db()

# Pydantic 모델 정의
class Value(BaseModel):
    content: str

class ValueResponse(BaseModel):
    id: int
    content: str
    created_at: str

# 라우트 정의
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("values.html", {"request": request})

@app.post("/api/values/", response_model=ValueResponse)
async def create_value(value: Value):
    conn = sqlite3.connect('values.db')
    c = conn.cursor()
    try:
        now = datetime.now(timezone(timedelta(hours=9))).strftime('%Y-%m-%d %H:%M:%S')  # KST
        c.execute('INSERT INTO value_items (content, created_at) VALUES (?, ?)', (value.content, now))
        value_id = c.lastrowid
        c.execute('SELECT id, content, created_at FROM value_items WHERE id = ?', (value_id,))
        result = c.fetchone()
        conn.commit()
        return ValueResponse(
            id=result[0],
            content=result[1],
            created_at=result[2]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/values/", response_model=List[ValueResponse])
async def get_values():
    conn = sqlite3.connect('values.db')
    c = conn.cursor()
    try:
        c.execute('SELECT id, content, created_at FROM value_items ORDER BY created_at DESC')
        values = c.fetchall()
        return [
            ValueResponse(
                id=value[0],
                content=value[1],
                created_at=value[2]
            )
            for value in values
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.delete("/api/values/{value_id}")
async def delete_value(value_id: int):
    conn = sqlite3.connect('values.db')
    c = conn.cursor()
    try:
        c.execute('DELETE FROM value_items WHERE id = ?', (value_id,))
        conn.commit()
        if c.rowcount == 0:
            raise HTTPException(status_code=404, detail="Value not found")
        return {"message": "Value deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
