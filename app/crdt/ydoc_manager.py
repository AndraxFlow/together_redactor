from __future__ import annotations

import asyncio
from typing import Dict, Set, Optional

from fastapi import WebSocket
from y_py import YDoc, apply_update, encode_state_as_update


class DocumentState:
    def __init__(self, snapshot: Optional[bytes] = None):
        self.lock = asyncio.Lock()
        self.clients: Set[WebSocket] = set()
        self.ydoc = YDoc()

        if snapshot:
            apply_update(self.ydoc, snapshot)

    def snapshot(self) -> bytes:
        return encode_state_as_update(self.ydoc)


class YDocManager:
    def __init__(self):
        self.docs: Dict[int, DocumentState] = {}
        self.global_lock = asyncio.Lock()
        
    async def get(self, document_id: int, snapshot: bytes | None = None):
        if document_id not in self.docs:
            state = DocumentState()
            if snapshot:
                apply_update(state.ydoc, snapshot)
            self.docs[document_id] = state
        return self.docs[document_id]

    async def remove_if_empty(self, document_id: int):
        async with self.global_lock:
            state = self.docs.get(document_id)
            if state and not state.clients:
                del self.docs[document_id]


ydoc_manager = YDocManager()