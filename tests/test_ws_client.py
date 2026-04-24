import asyncio
import requests
import websockets
from y_py import YDoc, apply_update, encode_state_as_update

BASE = "http://localhost:8000"
WS = "ws://localhost:8000/ws"


def create_user(email):
    r = requests.post(f"{BASE}/auth/register", json={
        "email": email,
        "password": "1234"
    })
    return r.json()


def login(email):
    r = requests.post(f"{BASE}/auth/login", json={
        "email": email,
        "password": "1234"
    })
    return r.json()["access_token"]


def create_doc(token):
    r = requests.post(
        f"{BASE}/documents/",
        json={
            "title": "test",
            "content": ""
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    return r.json()["id"]


def share_doc(token, doc_id, user_id):
    requests.post(
        f"{BASE}/documents/{doc_id}/share",
        params={"user_id": user_id, "role": "editor"},
        headers={"Authorization": f"Bearer {token}"}
    )


async def client(token, doc_id, name):
    async with websockets.connect(f"{WS}/{doc_id}?token={token}") as ws:
        print(f"{name} connected")

        # ✅ локальный YDoc
        doc = YDoc()
        text = doc.get_text("shared")

        # ✅ получаем snapshot
        snapshot = await ws.recv()
        apply_update(doc, snapshot)

        async def receiver():
            while True:
                msg = await ws.recv()
                apply_update(doc, msg)
                print(f"{name} state:", str(text))

        async def sender():
            await asyncio.sleep(2)

            with doc.begin_transaction() as txn:
                text.insert(txn, 0, f"{name}-edit ")

            update = encode_state_as_update(doc)
            await ws.send(update)

        await asyncio.gather(receiver(), sender())


async def main():
    u1 = create_user("aboba1@test.com")
    u2 = create_user("aboba2@test.com")

    t1 = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyMCIsImV4cCI6MTc3NjI0ODUyNn0.2mpeMhTI-YbomOrbq4qk7kG07o5F530v7D1LTgq2NLY'
    t2 = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyMSIsImV4cCI6MTc3NjI0ODU0OX0.-w6Njf8H3suwXjTCajDcnpe3SbcKH4fMu8Z8UxkaO9M'

    doc_id = 8

    share_doc(t1, doc_id, 21)

    await asyncio.gather(
        client(t1, doc_id, "user1"),
        client(t2, doc_id, "user2"),
    )


asyncio.run(main())