#!/usr/bin/env python

import asyncio
import os

import garbageIdentifier
from websockets.server import serve

ip = "192.168.241.115"
model = "16_100__350_0.8463114500045776.h5"


async def test(websocket):
    print("Client Found")
    while True:
        # on every interaction with the garbage bin, the server will receive a label and  data
        label = await websocket.recv()
        data = await websocket.recv()

        if label == "auto":
            # Write the image to a file
            with open("espcapture.jpg", "wb") as f:
                f.write(data)
            print("Image received")

            # Guess the image and send result to client
            guess = garbageIdentifier.guess(model, "espcapture.jpg")
            await websocket.send(guess)
            print("Sent", guess)

        elif data == "timeout":
            print("Timed out while waiting for image")

        elif label == "print":
            print("Received print request")
            print(data)

        else:
            # Write a new image to the dataset based on the label
            targetFolder = "garbage_dataset_large_condensed/" + label
            files = os.listdir(targetFolder)
            with open("{}/{}{}.jpg".format(targetFolder,label, len(files)),"wb") as f:
                f.write(data)
            print("Image saved to " + label)


async def main():
    async with serve(test, ip, 8080):
        print("Server started")
        await asyncio.Future()  # run forever


asyncio.run(main())