import asyncio
import websockets
import json
import cv2
import numpy as np
from PIL import ImageGrab
from mss import mss
import pyautogui
import time

FULL_HD = (1920, 1080)
HD = (1080, 720)
P480 = (640, 480)

sct = mss()

screen_size = pyautogui.size()
screen_width = screen_size.width
screen_height = screen_size.height

monitor = {"top": 0, "left": 0, "width": screen_width, "height": screen_height}

def click_mouse(x, y):
    (old_x, old_y) = pyautogui.position()
    pyautogui.click(x, y)
    pyautogui.moveTo(old_x, old_y)

async def send_screenshot(websocket): # Hay que mejorar mucho el framerate
    try:
        while True:
            start_time = time.time()

            screen_data = sct.grab(monitor)
            screen_np = np.array(screen_data)
            capture_time = time.time() - start_time

            _, buffer = cv2.imencode('.jpg', screen_np, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            jpeg_bytes = buffer.tobytes()
            jpg_time = time.time() - (capture_time + start_time)

            await websocket.send(jpeg_bytes)
            send_time = time.time() - (jpg_time + capture_time + start_time)

            elapsed_time = time.time() - start_time
            print(f"FPS de envío: {round(1 / elapsed_time, 2)}, CAPTURE: {round(capture_time,4)}" +
                  f", JPG: {round(jpg_time,4)}, SEND: {round(send_time,4)}")

            await asyncio.sleep(0.05)

    except websockets.exceptions.ConnectionClosedError:
        pass

async def receive_messages(websocket):
    try:
        async for message in websocket:
            print("Mensaje del cliente:", message)

            try:
                data = json.loads(message)

                x, y, img_w, img_h = data['x'], data['y'], data['img_w'], data['img_h']

                real_x = screen_width * (x / img_w)
                real_y = screen_height * (y / img_h)

                print("Coordenadas del ratón:", int(real_x), int(real_y))
                click_mouse(real_x, real_y)
            except json.JSONDecodeError:
                print("Mensaje del cliente no válido:", message)
    except websockets.exceptions.ConnectionClosedError:
        pass

async def main(websocket, path):
    print("Nuevo cliente conectado")
    
    send_task = asyncio.create_task(send_screenshot(websocket))
    receive_task = asyncio.create_task(receive_messages(websocket))

    await asyncio.gather(send_task, receive_task)

start_server = websockets.serve(main, "0.0.0.0", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
