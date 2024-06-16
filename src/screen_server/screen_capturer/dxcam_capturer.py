import dxcam

from .screen_capturer import ScreenCapturer

class DXCamCapturer(ScreenCapturer):
    def __init__(self):
        self.camera = dxcam.create(output_color="BGR", device_idx=0)
        self.camera.start(target_fps=120)
    
    def get_last_frame(self):
        return self.camera.get_latest_frame()