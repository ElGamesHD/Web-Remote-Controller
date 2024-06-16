import asyncio
import websockets
import json
import cv2
import numpy as np
import threading
from mss import mss
import pyautogui
import time
import signal

class WRC:

    def __init__(self):
        self.clients = []
        self.sct = mss()

        self.screen_width = pyautogui.size().width
        self.screen_height = pyautogui.size().height
        self.monitor = {"top": 0, "left": 0, "width": self.screen_width, "height": self.screen_height}

        self.active = True

    def click_mouse(self, x, y):
        (old_x, old_y) = pyautogui.position()
        pyautogui.click(x, y)
        pyautogui.moveTo(old_x, old_y)

    def capture_screen(self):
        return self.sct.grab(self.monitor)

    def spin(self):
        while self.active:
            if self.clients:
                try:
                    start_time = time.time()

                    screen_data = self.capture_screen()
                    screen_np = np.array(screen_data)
                    capture_time = time.time() - start_time

                    _, buffer = cv2.imencode('.jpg', screen_np, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                    jpeg_bytes = buffer.tobytes()
                    jpg_time = time.time() - (capture_time + start_time)

                    asyncio.run(self.send_frames(jpeg_bytes))
                    send_time = time.time() - (jpg_time + capture_time + start_time)

                    elapsed_time = time.time() - start_time
                    print(f"FPS de envío: {round(1 / elapsed_time, 2)}, CAPTURE: {round(capture_time,4)}" +
                        f", JPG: {round(jpg_time,4)}, SEND: {round(send_time,4)}")
                except Exception as e:
                    print(">> ERROR: " + str(e))
            else:
                time.sleep(0.1)  # Evitar consumo excesivo de CPU cuando no hay clientes

        print("Saliendo del bucle de envio...")

    async def send_frames(self, jpeg_bytes):
        tasks = [asyncio.create_task(self.send_to_client(client, jpeg_bytes)) for client in self.clients]

        await asyncio.wait(tasks)

    async def send_to_client(self, client, message):
        try:
            await client.send(message)
        except Exception:
            pass

    async def echo(self, websocket, _):
        self.clients.append(websocket)
        print(f">> ENTRADA: Nuevo cliente conectado: {websocket.remote_address[0]}:{websocket.remote_address[1]} (Conexiones activas: {len(self.clients)})")

        try:
            async for message in websocket:
                print(f">> LOG: Mensaje recibido desde el cliente: {message}")

                data = json.loads(message)

                x, y, img_w, img_h = data['x'], data['y'], data['img_w'], data['img_h']

                real_x = self.screen_width * (x / img_w)
                real_y = self.screen_height * (y / img_h)

                print("Coordenadas del ratón:", int(real_x), int(real_y))
                self.click_mouse(real_x, real_y)
        except Exception as e:
            print(">> ERROR AL RECIBIR: " + str(e))
        finally:
            self.clients.remove(websocket)
            print(f">> SALIDA: Cliente desconectado: {websocket.remote_address[0]}:{websocket.remote_address[1]} (Conexiones activas: {len(self.clients)})")

    async def socket_thread(self):
        print("Iniciando websocket...")

        async with websockets.serve(self.echo, "0.0.0.0", 8765):
            while self.active:
                await asyncio.sleep(1)
        print("Deteniendo websocket...")
        await asyncio.sleep(2)

    def execute_socket_thread(self):
        asyncio.run(self.socket_thread())

wrc = WRC()
def signal_handler(sig, frame):
    wrc.active = False
    print("\nCtrl+C detectado. Apagando...")

def main(args=None):
    signal.signal(signal.SIGINT, signal_handler)

    socket_thread = threading.Thread(target=wrc.execute_socket_thread)  # Escucha clientes
    socket_thread.start()

    wrc.spin()  # Manda frames
    socket_thread.join()

if __name__ == "__main__":
    main()
