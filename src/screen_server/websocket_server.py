import json
import cv2
import time
import signal

import threading
import asyncio
import websockets

import dxcam
import pyautogui


class WRC:

    def __init__(self, get_last_frame, process_message):
        self.get_last_frame = get_last_frame
        self.process_message = process_message

        self.clients = []

        self.screen_width = pyautogui.size().width
        self.screen_height = pyautogui.size().height

        self.camera = dxcam.create(output_color="BGR")
        self.camera.start(target_fps=120)

        self.active = True

    def screen_share(self):
        while self.active:
            if self.clients:
                try:
                    start_time = time.time()

                    screen_np = self.camera.get_latest_frame()
                    capture_time = time.time() - start_time

                    jpeg_bytes= cv2.imencode(".jpg", screen_np)[1].tobytes()
                    jpg_time = time.time() - (capture_time + start_time)
                
                    asyncio.run(self.send_frame(jpeg_bytes))
                    send_time = time.time() - (jpg_time + capture_time + start_time)

                    print(f"FPS de envío: {round(1 / (time.time() - start_time), 2)}, " +
                          f"CAPTURE: {round(capture_time, 4)}" +
                          f", JPG: {round(jpg_time, 4)}, SEND: {round(send_time, 4)}")
                except Exception as e:
                    print(">> ERROR: " + str(e))
            else:
                time.sleep(0.1)

        print("Saliendo del bucle de envio...")
            
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
                self.do_click(real_x, real_y)
        except Exception as e:
            print(">> ERROR AL RECIBIR: " + str(e))
        finally:
            self.clients.remove(websocket)
            print(f">> SALIDA: Cliente desconectado: {websocket.remote_address[0]}:{websocket.remote_address[1]} (Conexiones activas: {len(self.clients)})")

    def do_click(self, x, y):
        (old_x, old_y) = pyautogui.position()
        pyautogui.click(x, y)
        pyautogui.moveTo(old_x, old_y)

    async def send_frame(self, jpeg_bytes):     
        try:
            for client in self.clients:
                await client.send(jpeg_bytes)
        except Exception:
            pass

    async def socket_thread(self):
        print("Iniciando websocket...")

        async with websockets.serve(self.echo, "0.0.0.0", 8765):
            while self.active:
                await asyncio.sleep(1)
        print("Cerrando websocket...")

    def execute_socket_thread(self):
        asyncio.run(self.socket_thread())

    def signal_handler(self, sig, frame):
        self.active = False
        print("\CTRL + C detectado. Apagando...")

def main(args=None):
    wrc = WRC()
    signal.signal(signal.SIGINT, wrc.signal_handler)

    socket_thread = threading.Thread(target=wrc.execute_socket_thread)  # Escucha clientes
    socket_thread.start()

    wrc.screen_share()

if __name__ == "__main__":
    main()