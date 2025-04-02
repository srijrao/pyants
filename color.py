import random
import colorsys


class Color:
    """
    Represents a color in the simulation.
    """

    def __init__(self):
        self.color = None

    def create_any_color(self):
        """
        Generate a random RGB color value.

        Returns:
            tuple: A tuple representing the RGB color value.
        """
        self.color = (
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(100, 255),
        )
        return self.color

    def create_color_from_hue(self, hue, lightness=None, saturation=None):
        """
        Generate a color based on the given hue, lightness, and saturation.

        Args:
            hue (float): The hue value (0-1)
            lightness (float): The lightness value (0-1), default 0.5
            saturation (float): The saturation value (0-1), default 1.0

        Returns:
            tuple: A tuple representing the RGB color value.
        """
        if lightness is None:
            lightness = random.uniform(0.1, 0.9)  # Default lightness
        if saturation is None:
            saturation = random.uniform(0.3, 1.0)  # Default saturation
        # Convert HLS to RGB
        hls = (hue, lightness, saturation)
        rgb = colorsys.hls_to_rgb(*hls)
        return (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))

    def convert_rgb_to_hls(self, rgb):
        """
        Convert RGB color value to hls.

        Args:
            rgb (tuple): A tuple representing the RGB color value (0-255).

        Returns:
            tuple: A tuple representing the hls color value (H: 0-1, L: 0-1, S: 0-1).
        """
        r, g, b = rgb
        return colorsys.rgb_to_hls(
            r / 255.0, g / 255.0, b / 255.0
        )  # Note: colorsys returns HLS

    def convert_hls_to_rgb(self, hls):
        """
        Convert hls color value to rgb.

        Args:
            hls (tuple): A tuple representing the hls color value (H: 0-1, L: 0-1, S: 0-1).

        Returns:
            tuple: A tuple representing the RGB color value (0-255).
        """
        h, l, s = hls
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return (int(r * 255), int(g * 255), int(b * 255))
