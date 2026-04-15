from collections import defaultdict
from fastapi import WebSocket


# class ConnectionManager:
#     def __init__(self) -> None:
#         self.active_connections: dict[int, list[WebSocket]] = defaultdict(list)

#     async def connect(self, document_id: int, websocket: WebSocket) -> None:
#         await websocket.accept()
#         self.active_connections[document_id].append(websocket)

#     def disconnect(self, document_id: int, websocket: WebSocket) -> None:
#         connections = self.active_connections.get(document_id, [])
#         if websocket in connections:
#             connections.remove(websocket)
#         if not connections and document_id in self.active_connections:
#             del self.active_connections[document_id]

#     async def broadcast_except_sender(
#         self,
#         document_id: int,
#         message: bytes,
#         sender: WebSocket,
#     ) -> None:
#         for connection in list(self.active_connections.get(document_id, [])):
#             if connection is sender:
#                 continue
#             await connection.send_bytes(message)


# manager = ConnectionManager()