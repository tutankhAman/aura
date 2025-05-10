import asyncio
import json
import logging
from typing import Dict, Any
from fastapi import WebSocket
from .stt_handler import STTHandler
from .utils import setup_logger, format_audio_chunk

logger = logging.getLogger(__name__)

class VoiceWebSocketHandler:
    def __init__(self, stt_handler: STTHandler):
        self.stt_handler = stt_handler
        self.active_connections: Dict[str, WebSocket] = {}

    async def handle_websocket(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")

        try:
            while True:
                # Receive audio data
                audio_data = await websocket.receive_bytes()
                
                # Process audio with STT
                transcript = await self.stt_handler.process_audio(audio_data)
                
                if transcript:
                    # Send transcription back to client
                    response = {
                        "type": "transcription",
                        "text": transcript
                    }
                    await websocket.send_json(response)
                    logger.info(f"Sent transcription to client {client_id}: {transcript}")

        except Exception as e:
            logger.error(f"Error handling WebSocket for client {client_id}: {str(e)}")
        finally:
            if client_id in self.active_connections:
                del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected") 