#!/usr/bin/env python

import asyncio
import garbageIdentifier
from websockets.server import serve

ip = "192.168.145.115"
model = "16_100__350_0.8463114500045776.h5"
async def test(websocket):
    print("Client Found")
    while True:
        imgdata = await websocket.recv()
        with open("espcapture.jpg", "wb") as f:
            f.write(imgdata)
        print("Image received")
        guess = garbageIdentifier.guess(model, "espcapture.jpg")
        await websocket.send(guess)
        print("Sent", guess)
async def main():
    async with serve(test, ip, 8080):
        print("Server started")
        await asyncio.Future()  # run forever

asyncio.run(main())