import json
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client_queues: List[asyncio.Queue] = []

@app.get("/")
def main():
    return "Test"

@app.websocket("/ws")
async def esp_endpoint(ws: WebSocket):
    await ws.accept()
    print("ESP32 connected")
    
    try:
        while True:
            # Receive data from ESP32
            data = await ws.receive_text()
            packet = json.loads(data)
            # print(f"Received from ESP32: {packet}")
            
            for queue in client_queues:
                await queue.put(packet)
                
    except Exception as e:
        print(f"ESP32 disconnected: {e}")

@app.websocket("/ws/client")
async def client_endpoint(ws: WebSocket):
    await ws.accept()
    print("Frontend client connected")
    
    queue = asyncio.Queue()
    client_queues.append(queue)
    
    try:
        while True:
            data = await queue.get()
            await ws.send_json(data)
            
    except Exception as e:
        print(f"Frontend client disconnected: {e}")
    finally:
        client_queues.remove(queue)