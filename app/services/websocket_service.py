"""
WebSocket Service - Real-time Chat & Notifications
"""

import json
import logging
from typing import Dict, Set, Any
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        # Active connections by user_id
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # Room connections
        self.rooms: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Connect user"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
        logger.info(f"✅ User {user_id} connected")
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Disconnect user"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        logger.info(f"❌ User {user_id} disconnected")
    
    async def send_personal_message(
        self,
        message: str,
        user_id: int
    ):
        """Send message to specific user"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message)
                except:
                    pass
    
    async def broadcast(self, message: str):
        """Broadcast to all connected users"""
        for user_connections in self.active_connections.values():
            for connection in user_connections:
                try:
                    await connection.send_text(message)
                except:
                    pass
    
    async def join_room(self, websocket: WebSocket, room: str):
        """Join chat room"""
        if room not in self.rooms:
            self.rooms[room] = set()
        
        self.rooms[room].add(websocket)
        logger.info(f"✅ User joined room: {room}")
    
    async def leave_room(self, websocket: WebSocket, room: str):
        """Leave chat room"""
        if room in self.rooms:
            self.rooms[room].discard(websocket)
    
    async def send_to_room(self, message: str, room: str):
        """Send message to room"""
        if room in self.rooms:
            for connection in self.rooms[room]:
                try:
                    await connection.send_text(message)
                except:
                    pass
    
    def get_active_users(self) -> int:
        """Get count of active users"""
        return len(self.active_connections)
    
    def get_user_status(self, user_id: int) -> str:
        """Check if user is online"""
        return "online" if user_id in self.active_connections else "offline"


# Global connection manager
manager = ConnectionManager()


# ==================== MESSAGE TYPES ====================

class MessageType:
    """WebSocket message types"""
    CHAT = "chat"
    NOTIFICATION = "notification"
    TYPING = "typing"
    STATUS = "status"
    SYSTEM = "system"
    ERROR = "error"


async def handle_chat_message(
    websocket: WebSocket,
    user_id: int,
    data: Dict[str, Any]
):
    """Handle chat message"""
    recipient_id = data.get("recipient_id")
    message_text = data.get("message")
    
    # TODO: Save message to database
    
    # Prepare message
    message = {
        "type": MessageType.CHAT,
        "from": user_id,
        "message": message_text,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Send to recipient
    await manager.send_personal_message(
        json.dumps(message),
        recipient_id
    )
    
    # Send back confirmation
    await websocket.send_json({
        "type": "confirmation",
        "status": "sent"
    })


async def handle_typing_indicator(
    user_id: int,
    data: Dict[str, Any]
):
    """Handle typing indicator"""
    recipient_id = data.get("recipient_id")
    is_typing = data.get("is_typing", False)
    
    message = {
        "type": MessageType.TYPING,
        "from": user_id,
        "is_typing": is_typing
    }
    
    await manager.send_personal_message(
        json.dumps(message),
        recipient_id
    )


async def send_notification(
    user_id: int,
    title: str,
    message: str,
    notification_type: str = "info"
):
    """Send notification to user"""
    notification = {
        "type": MessageType.NOTIFICATION,
        "title": title,
        "message": message,
        "notification_type": notification_type,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.send_personal_message(
        json.dumps(notification),
        user_id
    )


async def broadcast_system_message(message: str):
    """Broadcast system message"""
    system_msg = {
        "type": MessageType.SYSTEM,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.broadcast(json.dumps(system_msg))


def get_connection_manager() -> ConnectionManager:
    """Get connection manager instance"""
    return manager
