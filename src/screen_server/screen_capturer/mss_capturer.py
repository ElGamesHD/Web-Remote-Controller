import numpy as np
import pyautogui
from mss import mss

from .screen_capturer import ScreenCapturer

class MSSCapturer(ScreenCapturer):
    def __init__(self):
        self.screen_width = pyautogui.size().width
        self.screen_height = pyautogui.size().height

        self.sct = mss()
        self.monitor = {"top": 0, "left": 0, "width": self.screen_width, "height": self.screen_height}
    
    def get_last_frame(self):
        return np.array(self.sct.grab(self.monitor))