import cv2
import time

import threading
import asyncio
import websockets

class WebsocketServer:

    def __init__(self, screen_capturer, process_message, port):
        self.screen_capturer = screen_capturer
        self.process_message = process_message

        self.port = port
        self.clients = []

        self.active = True

    def screen_share(self):
        while self.active:
            if self.clients:
                try:
                    start_time = time.time()

                    screen_np = self.screen_capturer.get_last_frame()
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

    async def send_frame(self, jpeg_bytes):  
        tasks = [asyncio.create_task(self.send_to_client(client, jpeg_bytes)) for client in self.clients]

        await asyncio.wait(tasks)   

    async def send_to_client(self, client, message):
        try:
            await client.send(message)
        except Exception as e:
            print(">> ERROR AL ENVIAR: " + str(e))

    async def echo(self, websocket, _):
        self.clients.append(websocket)
        print(f">> ENTRADA: Nuevo cliente conectado: {websocket.remote_address[0]}:{websocket.remote_address[1]} " +
              f"(Conexiones activas: {len(self.clients)})")

        try:
            async for message in websocket:
                self.process_message(message)
        except Exception as e:
            print(">> ERROR AL RECIBIR: " + str(e))
        finally:
            self.clients.remove(websocket)
            print(f">> SALIDA: Cliente desconectado: {websocket.remote_address[0]}:{websocket.remote_address[1]} " +
                  f"(Conexiones activas: {len(self.clients)})")

    def start(self):
        socket_thread = threading.Thread(target=self.execute_socket_thread)
        socket_thread.start()

        self.screen_share()

    def execute_socket_thread(self):
        asyncio.run(self.socket_thread())

    async def socket_thread(self):
        print("Iniciando websocket...")

        async with websockets.serve(self.echo, "0.0.0.0", self.port):
            while self.active:
                await asyncio.sleep(1)
        print("Cerrando websocket...")