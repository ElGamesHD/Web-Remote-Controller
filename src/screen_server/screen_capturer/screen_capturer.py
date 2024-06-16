from abc import ABC, abstractmethod

class ScreenCapturer(ABC):
    @abstractmethod
    def get_last_frame(self):
        pass