from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Dict, List
from sqlalchemy.orm import Session
import jwt

from app.database import SessionLocal
from app import models
from app.config import JWT_SECRET

router = APIRouter(tags=["WebSocket"])

connections: Dict[int, List[WebSocket]] = {}

def verify_token(token: str):
    payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    return payload["sub"]

@router.websocket("/ws/{room_id}")
async def chat_websocket(websocket: WebSocket, room_id: int, token: str = Query(...)):
    try:
        user_id = verify_token(token)
    except Exception:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    if room_id not in connections:
        connections[room_id] = []
    connections[room_id].append(websocket)

    db: Session = SessionLocal()

    try:
        while True:
            data = await websocket.receive_text()

            new_msg = models.Message(room_id=room_id, sender_id=user_id, content=data)
            db.add(new_msg)
            db.commit()
            db.refresh(new_msg)

            for conn in connections[room_id]:
                await conn.send_text(f"[{new_msg.created_at}] User {user_id}: {new_msg.content}")

    except WebSocketDisconnect:
        connections[room_id].remove(websocket)
        if not connections[room_id]:
            del connections[room_id]
    finally:
        db.close()
