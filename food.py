import settings
import random


class Food:
    def __init__(self, position=None):
        self.size = settings.Anthill_size * 2
        if position is None:
            self.randompositionsetter()
        else:
            self.position = position
        self.color = settings.GREEN
        self.visual_packet = None
        

    def visual(self):
        self.visual_packet = {
            "position": self.position,
            "color": self.color,
            "size": self.size,
        }
        return self.visual_packet

    def randompositionsetter(self):
        barrier = self.size
        position = [
            random.randint(barrier, settings.width - barrier),
            random.randint(barrier, settings.height - barrier),
        ]
        self.position = position
