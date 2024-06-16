import json
import signal

import pyautogui

from websocket_server import WebsocketServer
from screen_capturer.mss_capturer import MSSCapturer

class Controller:

    def __init__(self, screen_capturer):
        self.screen_width = pyautogui.size().width
        self.screen_height = pyautogui.size().height

        self.server = WebsocketServer(screen_capturer, self.process_message)

    def signal_handler(self, sig, frame):
        self.server.active = False
        print("\nCTRL + C detectado. Apagando...")

    def start(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        self.server.start()

    def process_message(self, message):
        print(f">> LOG: Mensaje recibido desde el cliente: {message}")

        data = json.loads(message)

        x, y, img_w, img_h = data['x'], data['y'], data['img_w'], data['img_h']

        real_x = self.screen_width * (x / img_w)
        real_y = self.screen_height * (y / img_h)

        print("Coordenadas del ratón:", int(real_x), int(real_y))
        self.do_click(real_x, real_y)

    def do_click(self, x, y):
        (old_x, old_y) = pyautogui.position()
        pyautogui.click(x, y)
        pyautogui.moveTo(old_x, old_y)

def main(args=None):
    screen_capturer = MSSCapturer()

    controller = Controller(screen_capturer)
    controller.start()

if __name__ == "__main__":
    main()
