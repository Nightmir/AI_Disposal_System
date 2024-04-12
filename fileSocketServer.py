import asyncio
import os

import garbageIdentifier
from websockets.server import serve
import socket

hostname = socket.getfqdn()
print("IP Address:", socket.gethostbyname_ex(hostname)[2][0])

ip = hostname
model = "possiblyTheBestModel.h5"
garbageIdentifier.guess(model, "spoon.jpg")


async def test(websocket):
    print("Client Found")
    while True:
        # on every interaction with the garbage bin, the server will receive a label and  data
        print("Waiting for label...")
        label = await websocket.recv()
        print("Received label:", label)
        print("Waiting for data...")
        data = await websocket.recv()
        print("Data received!")

        # Auto Mode
        if label == "auto":
            # Write the image to a file
            print("Capturing image...")
            with open("espcapture.jpg", "wb") as f:
                f.write(data)
            print("Image captured!")

            # Guess the image and send result to client
            print("Identifying image...")
            guess = garbageIdentifier.guess(model, "espcapture.jpg")
            await websocket.send(guess)  # MAYBE REMOVE AWAIT?
            print("Identification successful. Sent message:", guess)

        # Manual Mode
        elif label == "blue" or label == "black" or label == "green":
            if data == "timeout":
                print("Item undetected. Waiting timed out.")
            else:
                # Write a new image to the dataset based on the label

                # Determine target directory
                targetFolder = "garbage_dataset_custom/" + label

                # Find unique filename
                i = 0
                while os.path.exists(f"{targetFolder}{'/'}{label}{i}.jpg"):
                    i += 1

                # Save image to dataset
                print("Saving image to dataset...")
                filename = "{}/{}{}.jpg".format(targetFolder, label, i)
                with open(filename, "wb") as f:
                    f.write(data)
                print("Image saved to", filename)

        # Print mode for debugging
        elif label == "print":
            print(data)

        else:
            print("Label or data invalid.")
        print()


async def main():
    async with serve(test, ip, 8080):
        print("Server started")
        await asyncio.Future()  # run forever


asyncio.run(main())
