"""Socket.IO manager for real-time event broadcasting."""

import logging
from typing import Any, Dict

import socketio

logger = logging.getLogger(__name__)


class SocketManager:
    """Centralized Socket.IO manager for real-time communication.
    
    This class manages the Socket.IO server, active clients,
    and event broadcasting. It has no business logic.
    """
    
    def __init__(self) -> None:
        """Initialize the Socket.IO manager."""
        self._sio = socketio.AsyncServer(
            async_mode="asgi",
            cors_allowed_origins="*",
            logger=False,
        )
        self._app = socketio.ASGIApp(self._sio)
        logger.info("SocketManager initialized")
    
    @property
    def app(self) -> socketio.ASGIApp:
        """Get the ASGI app for FastAPI integration.
        
        Returns:
            The Socket.IO ASGI app.
        """
        return self._app
    
    async def emit(self, event: str, data: Dict[str, Any], room: str = None) -> None:
        """Emit an event to connected clients.
        
        Args:
            event: The event name.
            data: The event data.
            room: Optional room to emit to.
        """
        logger.debug("Emitting Socket.IO event: %s, data: %s, room: %s", event, data, room)
        if room:
            await self._sio.emit(event, data, room=room)
        else:
            await self._sio.emit(event, data)
        logger.debug("Event emitted successfully: %s", event)
    
    async def join_room(self, sid: str, room: str) -> None:
        """Join a client to a room.
        
        Args:
            sid: The session ID.
            room: The room name.
        """
        await self._sio.enter_room(sid, room)
        logger.debug("Client %s joined room: %s", sid, room)
    
    async def leave_room(self, sid: str, room: str) -> None:
        """Remove a client from a room.
        
        Args:
            sid: The session ID.
            room: The room name.
        """
        await self._sio.leave_room(sid, room)
        logger.debug("Client %s left room: %s", sid, room)


# Global singleton
socket_manager = SocketManager()
