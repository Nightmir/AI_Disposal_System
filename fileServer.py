# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import requests
import numpy as np
import cv2
import os
from multiprocessing import Value
from flask import request
import io
import PIL.Image as Imagew
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs

hostName = "192.168.2.10"
serverPort = 8080
counter = Value('i', 0)


def save_img(img):
    with counter.get_lock():
        counter.value += 1
        count = counter.value
    img_dir = "esp32_imgs"
    if not os.path.isdir(img_dir):
        os.mkdir(img_dir)
    cv2.imwrite(os.path.join(img_dir, "img_" + str(count) + ".jpg"), img)


# print("Image Saved", end="\n") # debug
def index():
    return "ESP32-CAM Flask Server", 200


def upload(BaseHTTPRequestHandler):
    received = request
    img = None
    if received.files:
        print(received.files['imageFile'])
        # convert string of image data to uint8
        file = received.files['imageFile']
        nparr = np.fromstring(file.read(), np.uint8)
        # decode image
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        save_img(img)

        return "[SUCCESS] Image Received", 201
    else:
        return "[FAILED] Image Not Received", 204


class MyServer(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))

    def do_POST(self):
        # Get content length
        length = int(self.headers['Content-Length'])
        print(self.rfile.readline())
        print(self.rfile.readline())
        print(self.rfile.readline())
        print(self.rfile.readline())
        # Get contents
        data = self.rfile.read()
        # Print data
        print(data)
        with open("espcapture.jpg", "wb") as f:
            f.write(data)
        print("new image received")
        self.send_response(200)
        # Send message back to client
        self.wfile.write(bytes("Image received", "utf-8"))
        self.end_headers()

if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
