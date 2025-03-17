import settings

class Anthill:
    def __init__(self, position, size=settings.Anthill_size):
        self.position = position
        self.size = size
        self.color = settings.WHITE
        self.visual_packet = None

    def visual(self):
        self.visual_packet = {"position": self.position, "size": self.size, "color": self.color}
        return self.visual_packet