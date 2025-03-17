import settings

class Dot:
    def __init__(self, position=[0, 0], type="to food"):
        self.position = position
        self.type = type
        self.setup()

    def setup(self):
        """ setup function for the dot """
        self.size = settings.dot_size
        self.timeleft = settings.dot_time
        self.active = True
        if self.type == "to food":
            self.color = settings.GREEN
        elif self.type == "to home":
            self.color = settings.PURPLE
        else:
            self.color = settings.WHITE

    def update(self):
        """ update function for the dot """
        self.timeleft -= 1
        if self.timeleft <= 0:
            self.active = False