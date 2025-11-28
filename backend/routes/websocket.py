from __future__ import annotations

import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..vad.detector import VADState

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/audio")
async def websocket_audio(websocket: WebSocket) -> None:
    await websocket.accept()
    logger.info("Client connected")

    vad = VADState()

    try:
        while True:
            message = await websocket.receive()

            if message["type"] == "websocket.receive" and message.get("bytes") is not None:
                raw = message["bytes"]
                if not raw:
                    continue

                text = await vad.process_chunk(raw)
                if text:
                    await websocket.send_json({"text": text})
                continue

            if message["type"] == "websocket.receive" and message.get("text") is not None:
                if message["text"] == "stop":
                    final_text = await vad.flush()
                    if final_text:
                        await websocket.send_json({"text": final_text})
                    await websocket.close()
                    return
                continue

            if message["type"] == "websocket.disconnect":
                raise WebSocketDisconnect(message.get("code", 1000))

    except WebSocketDisconnect:
        logger.info("Client disconnected")

    except Exception as e:
        logger.exception("WebSocket error: %s", e)
        try:
            await websocket.close()
        except Exception as e:
            logger.exception("Failed to close WebSocket: %s", e)
