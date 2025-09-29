from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app import models, schemas, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()
connections: dict[int, list[WebSocket]] = {}

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/send")
def send_message(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    db_msg = models.Message(**message.dict())
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)
    receiver = message.receiver_id
    if receiver in connections:
        for ws in connections[receiver]:
            import asyncio
            asyncio.create_task(ws.send_json(message.dict()))
    return db_msg

@app.get("/messages/{user_id}")
def get_messages(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.Message).filter(
        (models.Message.sender_id==user_id) | (models.Message.receiver_id==user_id)
    ).all()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    if user_id not in connections:
        connections[user_id] = []
    connections[user_id].append(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            receiver_id = data["receiver_id"]
            if receiver_id in connections:
                for conn in connections[receiver_id]:
                    await conn.send_json(data)
    except WebSocketDisconnect:
        connections[user_id].remove(websocket)

@app.get("/health")
async def health():
    return {"status": "ok"}
