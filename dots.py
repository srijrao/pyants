import settings


class Dot:
    def __init__(self, position=[0, 0], type="to home"):
        self.position = position
        self.type = type
        self.setup()

    def setup(self):
        """setup function for the dot"""
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
        """update function for the dot"""
        self.timeleft -= 1
        if self.timeleft <= 0:
            self.active = False

    def get_alpha(self):
        """Calculate the alpha value based on time left"""
        return int((self.timeleft / settings.dot_time) * 255)

    def visual(self):
        """Return the visual packet for the dot"""
        self.visual_packet = {
            "position": self.position,
            "size": self.size,
            "color": (self.color[0], self.color[1], self.color[2], self.get_alpha()),
        }
        return self.visual_packet
