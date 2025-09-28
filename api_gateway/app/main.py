from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Header, Query, HTTPException
import httpx
import asyncio
import json
from jose import jwt, JWTError
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
AUTH_URL = "http://auth-service:8001"
CHAT_URL = "http://chat-service:8002"
SECRET_KEY = "c9f3b8d7a6e4f1c2b5d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"  
ALGORITHM = "HS256"


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload 
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def post_with_retry(url, json_data, retries=5):
    for _ in range(retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=json_data)
                return response
        except httpx.ConnectError:
            await asyncio.sleep(1)
    raise httpx.ConnectError(f"Could not connect to {url}")

async def get_with_retry(url, retries=5):
    for _ in range(retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                return response
        except httpx.ConnectError:
            await asyncio.sleep(1)
    raise httpx.ConnectError(f"Could not connect to {url}")


@app.post("/register")
async def register(user: dict):
    response = await post_with_retry(f"{AUTH_URL}/register", user)
    return response.json()

@app.post("/login")
async def login(user: dict):
    response = await post_with_retry(f"{AUTH_URL}/login", user)
    return response.json()

@app.post("/send")
async def send_message(message: dict, authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    message["sender_id"] = payload["user_id"] 
    response = await post_with_retry(f"{CHAT_URL}/send", message)
    return response.json()

@app.get("/messages/{user_id}")
async def get_messages(user_id: int, authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    if payload["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    response = await get_with_retry(f"{CHAT_URL}/messages/{user_id}")
    return response.json()

@app.get("/health")
async def health():
    return {"status": "ok"}

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.setdefault(user_id, []).append(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket):
        self.active_connections.get(user_id, []).remove(websocket)

    async def send_personal_message(self, message: dict, user_id: int):
        for ws in self.active_connections.get(user_id, []):
            await ws.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    payload = verify_token(token)
    user_id = payload["user_id"]

    await manager.connect(user_id, websocket)

    try:
        response = await get_with_retry(f"{CHAT_URL}/messages/{user_id}")
        history = response.json()
        await manager.send_personal_message({"history": history}, user_id)
    except Exception:
        pass 

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            message["sender_id"] = user_id

            await post_with_retry(f"{CHAT_URL}/send", message)

            await manager.send_personal_message(message, message["receiver_id"])

            await manager.send_personal_message(message, user_id)

    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
