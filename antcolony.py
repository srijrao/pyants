import settings
import random

class Anthill:
    def __init__(self, position=None, size=settings.Anthill_size):
        if position is None:
            self.randompositionsetter()
        else:
            self.position = position
        self.size = size
        self.color = settings.WHITE
        self.visual_packet = None
            
    def randompositionsetter(self):
        barrier = settings.Anthill_size
        position = [
            random.randint(barrier, settings.width - barrier),
            random.randint(barrier, settings.height - barrier),
        ]
        self.position = position


    def visual(self):
        self.visual_packet = {"position": self.position, "size": self.size, "color": self.color}
        return self.visual_packet