import asyncio
import websockets
import pyautogui
import json
import cv2
import numpy as np
from PIL import ImageGrab
import base64

FULL_HD = (1920, 1080)
HD = (1080, 720)
P480 = (640, 480)

# Función para mover el cursor del ratón a una posición específica y hacer clic
def click_mouse(x, y):
    (old_x, old_y) = pyautogui.position()
    pyautogui.click(x, y)  # Hacer clic en la posición
    pyautogui.moveTo(old_x, old_y)  # Mover el cursor del ratón a la posición especificada
    
# Función para capturar pantalla y convertirla en base64
def capture_screen():
    screen = ImageGrab.grab()  # Captura de pantalla
    #screen.thumbnail(HD)  # Reducir resolución
    img_np = np.array(screen)   # Convertir a matriz numpy
    img_rgb = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)  # Convertir de BGR a RGB
    return img_rgb

# Función para enviar la captura a todos los clientes conectados
async def send_screenshot(websocket, path):
    try:
        while True:
            screen_data = capture_screen()  # Capturar pantalla
            await websocket.send(base64.b64encode(cv2.imencode('.jpg', screen_data)[1]).decode('utf-8'))  # Enviar captura a cliente
            await asyncio.sleep(0)  # Esperar un poco antes de la siguiente captura
    except websockets.exceptions.ConnectionClosedError:
        pass

# Función para manejar las conexiones de WebSocket
async def main(websocket, path):
    print("Nuevo cliente conectado")
    send_task = asyncio.create_task(send_screenshot(websocket, path))  # Iniciar la tarea de enviar capturas de pantalla

    try:
        async for message in websocket:
            print("Mensaje del cliente:", message)
            # Manejar mensaje del cliente (si es necesario)
            try:
                data = json.loads(message)
 
                x, y, img_w, img_h = data['x'], data['y'], data['img_w'], data['img_h']

                screen_size = pyautogui.size()

                real_x = screen_size.width * (x / img_w)
                real_y = screen_size.height * (y / img_h)

                print("Coordenadas del ratón:", int(real_x), int(real_y))
                click_mouse(real_x, real_y)
            except json.JSONDecodeError:
                print("Mensaje del cliente no válido:", message)
    
    except websockets.exceptions.ConnectionClosedError:
        send_task.cancel()  # Cancelar la tarea de enviar capturas de pantalla si la conexión se cierra

# Configuración del servidor WebSocket
start_server = websockets.serve(main, "0.0.0.0", 8765)

# Iniciar el bucle de eventos
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
