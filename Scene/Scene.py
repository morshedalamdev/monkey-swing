class AbstractScene:
    """Base class for all game scenes."""

    def __init__(self):
        self.handler = None

    def render(self, screen):
        pass

    def handle(self, events):
        pass

    def update(self):
        pass
