import pyglet


class Display(pyglet.window.Window):
    def __init__(self, width, height, scale):
        super(Display, self).__init__()

        self.label = pyglet.text.Label("Hello world!")
        self.width = width
        self.height = height
        self.display_buffer = [[0] * width for _ in range(height)]
        self.scale = scale
        self.set_size(self.width * self.scale, self.height * self.scale)

    def on_draw(self):
        self.clear()
        self.label.draw()
